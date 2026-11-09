'use strict';

const path = require('node:path');
const { exists } = require('./util');

const TARGETS = {
  claude: {
    label: 'Claude Code',
    kind: 'skill',
    project: ['.claude/skills'],
    global: ['~/.claude/skills'],
    detect: ['.claude', '.claude/skills'],
    note: 'Personal or project skills, same SKILL.md format Anthropic uses.',
  },
  agents: {
    label: 'Cross-tool Agent Skills',
    kind: 'skill',
    project: ['.agents/skills'],
    global: ['~/.agents/skills'],
    detect: ['.agents', '.agents/skills'],
    note: 'The shared location read by Codex, Cursor, Gemini CLI, Windsurf, Cline and others.',
  },
  codex: {
    label: 'OpenAI Codex CLI',
    kind: 'skill',
    project: ['.agents/skills', '.codex/skills'],
    global: ['~/.agents/skills', '~/.codex/skills'],
    detect: ['.codex', '.codex/skills'],
    note: 'Installs to .agents/skills (documented) and mirrors .codex/skills for older builds.',
  },
  cursor: {
    label: 'Cursor',
    kind: 'cursor',
    project: ['.cursor/skills'],
    global: ['~/.cursor/skills'],
    detect: ['.cursor'],
    note: 'Native .cursor/skills copy plus a .cursor/rules/*.mdc rule for older Cursor builds.',
  },
  gemini: {
    label: 'Gemini CLI',
    kind: 'skill',
    project: ['.gemini/skills', '.agents/skills'],
    global: ['~/.gemini/skills', '~/.agents/skills'],
    detect: ['.gemini'],
    note: 'Installs to .gemini/skills and the shared .agents/skills location.',
  },
  windsurf: {
    label: 'Windsurf',
    kind: 'rule',
    project: ['.windsurf/rules'],
    global: ['~/.devin/rules'],
    detect: ['.windsurf', '.windsurfrules'],
    note: 'A model-decided rule; the full skill goes to .agents/skills.',
  },
  cline: {
    label: 'Cline',
    kind: 'rule',
    project: ['.clinerules'],
    global: ['~/Documents/Cline/Rules'],
    detect: ['.clinerules', '.cline'],
    note: 'A rule file; the full skill goes to .agents/skills.',
  },
  continue: {
    label: 'Continue.dev',
    kind: 'rule',
    project: ['.continue/rules'],
    global: ['~/.continue/rules'],
    detect: ['.continue'],
    note: 'A rule file; the full skill goes to .agents/skills.',
  },
  copilot: {
    label: 'GitHub Copilot',
    kind: 'rule',
    project: ['.github/instructions'],
    global: [],
    detect: ['.github/copilot-instructions.md', '.github/instructions'],
    note: 'A path-specific instructions file; the full skill goes to .agents/skills.',
  },
  'agents-md': {
    label: 'AGENTS.md',
    kind: 'agents-md',
    project: ['AGENTS.md'],
    global: ['~/.agents/AGENTS.md', '~/.codex/AGENTS.md'],
    detect: ['AGENTS.md'],
    note: 'A short section in AGENTS.md that points at the installed skill.',
  },
};

const DEFAULT_PROJECT_TARGETS = ['claude', 'codex', 'cursor', 'agents-md'];
const DEFAULT_GLOBAL_TARGETS = ['claude', 'codex', 'gemini', 'agents'];

function expand(value, { projectDir, homeDir }) {
  if (value === '~') return homeDir;
  if (value.startsWith('~/')) return path.join(homeDir, value.slice(2));
  return path.resolve(projectDir, value);
}

function resolveTargets(names) {
  if (!names || names.length === 0 || names.includes('auto')) return null;
  if (names.includes('all')) return Object.keys(TARGETS);
  const chosen = [];
  for (const name of names) {
    if (!TARGETS[name]) {
      throw new Error(`unknown target: ${name}. Available: ${Object.keys(TARGETS).join(', ')}, all, auto`);
    }
    chosen.push(name);
  }
  return chosen;
}

function detectTargets(projectDir) {
  const found = Object.entries(TARGETS)
    .filter(([, config]) => (config.detect || []).some((marker) => exists(path.join(projectDir, marker))))
    .map(([name]) => name);
  if (found.length) return found;
  return DEFAULT_PROJECT_TARGETS;
}

function displayPath(value, homeDir) {
  return value.startsWith(homeDir + path.sep) ? `~${value.slice(homeDir.length)}` : value;
}

function pointerText(skill, skillDir, homeDir) {
  const shown = displayPath(skillDir, homeDir);
  return [
    `# ${skill.name}`,
    '',
    skill.description,
    '',
    `**Skill folder:** \`${shown}\``,
    `**Read before starting:** \`${path.join(shown, 'SKILL.md')}\``,
    '',
    'Read the full SKILL.md before you start. Run its scripts from the skill folder with `python3 -I`.',
    '',
    '---',
    '',
    skill.body.trim(),
    '',
  ].join('\n');
}

function cursorRule(skill, skillDir, homeDir) {
  return [
    '---',
    `description: ${JSON.stringify(skill.description)}`,
    'globs:',
    'alwaysApply: false',
    '---',
    '',
    pointerText(skill, skillDir, homeDir),
  ].join('\n');
}

function windsurfRule(skill, skillDir, homeDir) {
  return [
    '---',
    'trigger: model_decision',
    `description: ${JSON.stringify(skill.description)}`,
    '---',
    '',
    pointerText(skill, skillDir, homeDir),
  ].join('\n');
}

function continueRule(skill, skillDir, homeDir) {
  return [
    '---',
    `name: ${skill.name}`,
    `description: ${JSON.stringify(skill.description)}`,
    'alwaysApply: false',
    '---',
    '',
    pointerText(skill, skillDir, homeDir),
  ].join('\n');
}

function copilotRule(skill, skillDir, homeDir) {
  return [
    '---',
    'applyTo: "**"',
    '---',
    '',
    pointerText(skill, skillDir, homeDir),
  ].join('\n');
}

function clineRule(skill, skillDir, homeDir) {
  return `${pointerText(skill, skillDir, homeDir)}\n`;
}

const RULE_RENDERERS = {
  windsurf: windsurfRule,
  cline: clineRule,
  continue: continueRule,
  copilot: copilotRule,
};

function markerStart(name) {
  return `<!-- ai-cartoon-video-skills:start ${name} -->`;
}

function markerEnd(name) {
  return `<!-- ai-cartoon-video-skills:end ${name} -->`;
}

function agentsSection(skill, skillDir, homeDir) {
  const shown = displayPath(skillDir, homeDir);
  return [
    markerStart(skill.name),
    `## Skill: ${skill.name}`,
    '',
    skill.description,
    '',
    `Read the full skill before starting: \`${path.join(shown, 'SKILL.md')}\`.`,
    `Its scripts live in \`${path.join(shown, 'scripts')}\` and run with \`python3 -I\`.`,
    markerEnd(skill.name),
    '',
  ].join('\n');
}

/**
 * Work out every copy and file a target needs, without writing anything.
 * Plans are deduplicated by the installer, so overlapping targets are safe.
 */
function planTarget(targetName, skill, context) {
  const config = TARGETS[targetName];
  if (!config) throw new Error(`unknown target: ${targetName}`);
  const { scope, projectDir, homeDir } = context;
  const base = scope === 'global' ? homeDir : projectDir;
  const copies = [];
  const files = [];
  const sections = [];

  const addCopy = (directory) => {
    const destination = path.join(directory, skill.name);
    copies.push({ source: skill.directory, destination });
    return destination;
  };

  const dirsFor = (values) => values.map((value) => expand(value, { projectDir: base, homeDir }));
  const skillDirs = scope === 'global' ? config.global : config.project;

  if (config.kind === 'skill') {
    for (const directory of dirsFor(skillDirs)) addCopy(directory);
    return { copies, files, sections };
  }

  if (config.kind === 'cursor') {
    const skillDir = addCopy(dirsFor(skillDirs)[0]);
    const ruleDir = expand(scope === 'global' ? '~/.cursor/rules' : '.cursor/rules', { projectDir: base, homeDir });
    files.push({ path: path.join(ruleDir, `${skill.name}.mdc`), content: cursorRule(skill, skillDir, homeDir) });
    return { copies, files, sections };
  }

  if (config.kind === 'rule') {
    const payloadDir = expand(scope === 'global' ? '~/.agents/skills' : '.agents/skills', { projectDir: base, homeDir });
    const skillDir = addCopy(payloadDir);
    const ruleDirs = dirsFor(skillDirs);
    if (!ruleDirs.length) {
      return { copies, files, sections };
    }
    const extension = targetName === 'copilot' ? '.instructions.md' : '.md';
    const render = RULE_RENDERERS[targetName];
    files.push({ path: path.join(ruleDirs[0], `${skill.name}${extension}`), content: render(skill, skillDir, homeDir) });
    return { copies, files, sections };
  }

  if (config.kind === 'agents-md') {
    const payloadDir = expand(scope === 'global' ? '~/.agents/skills' : '.agents/skills', { projectDir: base, homeDir });
    const skillDir = addCopy(payloadDir);
    for (const file of dirsFor(skillDirs)) {
      sections.push({ path: file, section: agentsSection(skill, skillDir, homeDir) });
    }
    return { copies, files, sections };
  }

  throw new Error(`target ${targetName} has an unsupported kind: ${config.kind}`);
}

function planInstall(targetNames, skill, context) {
  const copies = new Map();
  const files = new Map();
  const sections = new Map();
  for (const target of targetNames) {
    const plan = planTarget(target, skill, context);
    for (const copy of plan.copies) {
      if (!copies.has(copy.destination)) copies.set(copy.destination, copy);
    }
    for (const file of plan.files) {
      if (!files.has(file.path)) files.set(file.path, file);
    }
    for (const item of plan.sections) {
      if (!sections.has(item.path)) sections.set(item.path, item);
    }
  }
  return {
    copies: [...copies.values()],
    files: [...files.values()],
    sections: [...sections.values()],
  };
}

module.exports = {
  DEFAULT_GLOBAL_TARGETS,
  DEFAULT_PROJECT_TARGETS,
  TARGETS,
  agentsSection,
  cursorRule,
  detectTargets,
  displayPath,
  expand,
  planInstall,
  planTarget,
  resolveTargets,
};
