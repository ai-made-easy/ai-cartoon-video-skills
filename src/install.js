'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const {
  ensureDir,
  exists,
  installCopy,
  readText,
  timestamp,
  walkFiles,
  writeText,
} = require('./util');
const {
  discoverSkills,
  selectSkills,
  validateSkill,
} = require('./skills');
const {
  DEFAULT_GLOBAL_TARGETS,
  TARGETS,
  detectTargets,
  displayPath,
  planInstall,
  resolveTargets,
} = require('./targets');

function writeIfChanged(filePath, content, { force = false, dryRun = false, log = () => {} } = {}) {
  if (exists(filePath) && readText(filePath) === content) {
    log(`  unchanged ${filePath}`);
    return { path: filePath, changed: false, backup: null };
  }
  let backup = null;
  if (exists(filePath) && !force) {
    backup = `${filePath}.bak-${timestamp()}`;
    if (!dryRun) fs.renameSync(filePath, backup);
    log(dryRun ? `  would back up the old rule to ${backup}` : `  backed up the old rule to ${backup}`);
  }
  if (!dryRun) writeText(filePath, content);
  log(dryRun ? `  would write ${filePath}` : `  wrote ${filePath}`);
  return { path: filePath, changed: true, backup };
}

function upsertAgentsSection(filePath, section, { dryRun = false, log = () => {} } = {}) {
  const current = exists(filePath) ? readText(filePath) : '';
  const startMarker = section.split('\n')[0];
  const endMarker = section.trim().split('\n').pop();
  const start = current.indexOf(startMarker);
  let next;
  if (start !== -1) {
    const end = current.indexOf(endMarker, start);
    if (end !== -1) {
      next = `${current.slice(0, start)}${section.trim()}${current.slice(end + endMarker.length)}`;
    } else {
      next = `${current.trimEnd()}\n\n${section}`;
    }
  } else {
    next = current.trim() ? `${current.trimEnd()}\n\n${section}` : `# Agent instructions\n\n${section}`;
  }
  if (next === current) {
    log(`  unchanged ${filePath}`);
    return { path: filePath, changed: false };
  }
  if (!dryRun) writeText(filePath, next);
  log(dryRun ? `  would write ${filePath}` : `  wrote ${filePath}`);
  return { path: filePath, changed: true };
}

function install(options) {
  const {
    targets: requestedTargets,
    skills: requestedSkills,
    community = false,
    scope = 'project',
    projectDir = process.cwd(),
    homeDir = require('node:os').homedir(),
    force = false,
    dryRun = false,
    log = () => {},
  } = options;

  const allSkills = discoverSkills({ includeCommunity: true });
  const chosen = selectSkills(allSkills, { requested: requestedSkills, includeCommunity: community });

  if (chosen.length === 0) {
    throw new Error('no skills to install');
  }

  const problems = [];
  for (const skill of chosen) {
    for (const problem of validateSkill(skill)) {
      problems.push(`${skill.name}: ${problem}`);
    }
  }
  if (problems.length) {
    throw new Error(`invalid bundled skill:\n- ${problems.join('\n- ')}`);
  }

  const resolvedTargets =
    resolveTargets(requestedTargets) ||
    (scope === 'global' ? DEFAULT_GLOBAL_TARGETS : detectTargets(projectDir));

  const context = { scope, projectDir, homeDir, force, dryRun, log };
  const results = [];

  for (const skill of chosen) {
    log(`\n${skill.name} (${skill.source})`);
    const plan = planInstall(resolvedTargets, skill, context);
    for (const copy of plan.copies) {
      const result = installCopy(copy.source, copy.destination, { force, dryRun, log });
      results.push({ skill: skill.name, kind: 'skill', path: copy.destination, backup: result.backup });
    }
    for (const file of plan.files) {
      if (!dryRun) ensureDir(path.dirname(file.path));
      const result = writeIfChanged(file.path, file.content, { force, dryRun, log });
      results.push({ skill: skill.name, kind: 'rule', ...result });
    }
    for (const item of plan.sections) {
      if (!dryRun) ensureDir(path.dirname(item.path));
      const result = upsertAgentsSection(item.path, item.section, { dryRun, log });
      results.push({ skill: skill.name, kind: 'agents-md', ...result });
    }
  }

  return { skills: chosen, targets: resolvedTargets, results, scope, projectDir, homeDir, dryRun };
}

function printInstallSummary(summary) {
  const { skills, targets, results, dryRun } = summary;
  const line = dryRun ? 'Would install' : 'Installed';
  console.log(`\n${line} ${skills.map((skill) => skill.name).join(', ')} for: ${targets.join(', ')}`);
  console.log('');
  for (const result of results) {
    const shown = displayPath(result.path, summary.homeDir);
    const label = result.kind === 'skill' ? 'skill' : result.kind === 'rule' ? 'rule ' : 'agents';
    console.log(`  ${label}  ${shown}`);
  }
  if (dryRun) {
    console.log('\nDry run: nothing was written.');
  } else {
    console.log('\nNext: restart the agent (or start a new session) so it discovers the skill.');
    console.log('Try: "Break down this video and tell me why it looks good."');
  }
}

function listSkills({ homeDir = require('node:os').homedir() } = {}) {
  const skills = discoverSkills({ includeCommunity: true });
  console.log('Bundled skills\n');
  for (const skill of skills) {
    const source = skill.source === 'first-party' ? 'first-party' : 'community';
    const license = (skill.license || (skill.source === 'first-party' ? 'MIT' : 'see UPSTREAM.md'))
      .split(/[;]/)[0]
      .replace(/\.\s+The .*$/, '');
    console.log(`${skill.name}  [${source}]  ${license}`);
    console.log(`  ${skill.description}`);
    console.log(`  ${displayPath(skill.directory, homeDir)}\n`);
  }
}

function printTargets({ projectDir = process.cwd(), homeDir = require('node:os').homedir() } = {}) {
  console.log('Supported targets\n');
  for (const [name, config] of Object.entries(TARGETS)) {
    const project = (config.project || []).join(', ') || '-';
    const global = (config.global || []).join(', ') || '-';
    console.log(`${name}  (${config.label})`);
    console.log(`  project: ${project}`);
    console.log(`  global:  ${global}`);
    console.log(`  ${config.note}\n`);
  }
  console.log(`Auto-detect checks: ${Object.entries(TARGETS)
    .map(([name, config]) => `${name}=${(config.detect || []).join('|')}`)
    .join(', ')}`);
  console.log(`Project default when nothing is detected: ${require('./targets').DEFAULT_PROJECT_TARGETS.join(', ')}`);
  console.log(`Global default: ${DEFAULT_GLOBAL_TARGETS.join(', ')}`);
}

function commandVersion(command, args) {
  const result = spawnSync(command, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  if (result.error) return null;
  if (result.status !== 0) return null;
  return (result.stdout || '').split('\n')[0].trim() || 'installed';
}

function checkPython(file) {
  // Parse only: py_compile would leave __pycache__ folders inside the package.
  const result = spawnSync(
    'python3',
    [
      '-I',
      '-c',
      'import ast,sys; ast.parse(open(sys.argv[1], encoding="utf-8").read(), filename=sys.argv[1])',
      file,
    ],
    { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }
  );
  return result.status === 0;
}

function doctor(options = {}) {
  const { projectDir = process.cwd(), homeDir = require('node:os').homedir() } = options;
  const lines = [];
  let failures = 0;
  let warnings = 0;

  const pass = (text) => lines.push(`PASS  ${text}`);
  const warn = (text) => {
    warnings += 1;
    lines.push(`WARN  ${text}`);
  };
  const fail = (text) => {
    failures += 1;
    lines.push(`FAIL  ${text}`);
  };

  const nodeMajor = Number(process.versions.node.split('.')[0]);
  if (nodeMajor >= 18) pass(`Node ${process.versions.node}`);
  else fail(`Node ${process.versions.node}; this package needs Node 18 or newer`);

  const ffmpeg = commandVersion('ffmpeg', ['-version']);
  const ffprobe = commandVersion('ffprobe', ['-version']);
  const python = commandVersion('python3', ['--version']);
  const ytDlp = commandVersion('yt-dlp', ['--version']);

  if (ffmpeg) pass(`ffmpeg: ${ffmpeg}`); else warn('ffmpeg not found; measure, strip and scorecard need it');
  if (ffprobe) pass(`ffprobe: ${ffprobe}`); else warn('ffprobe not found; measure needs it');
  if (python) pass(`python3: ${python}`); else fail('python3 not found; video_tools.py needs it');
  if (ytDlp) pass(`yt-dlp: ${ytDlp} (optional)`); else warn('yt-dlp not found; optional, needed only to download a URL');

  for (const skill of discoverSkills({ includeCommunity: true })) {
    lines.push('');
    lines.push(`${skill.name} (${skill.source})`);
    const problems = validateSkill(skill);
    if (problems.length) {
      for (const problem of problems) fail(problem);
    } else {
      pass('SKILL.md frontmatter and referenced files');
    }

    const pythonFiles = walkFiles(skill.directory).filter((file) => file.endsWith('.py'));
    for (const file of pythonFiles) {
      if (!python) {
        warn(`cannot syntax-check ${path.relative(skill.directory, file)} without python3`);
      } else if (checkPython(file)) {
        pass(`${path.relative(skill.directory, file)} compiles`);
      } else {
        fail(`${path.relative(skill.directory, file)} does not compile`);
      }
    }

    const jsonFiles = walkFiles(skill.directory).filter((file) => file.endsWith('.json'));
    for (const file of jsonFiles) {
      try {
        JSON.parse(readText(file));
        pass(`${path.relative(skill.directory, file)} is valid JSON`);
      } catch (error) {
        fail(`${path.relative(skill.directory, file)} is invalid JSON: ${error.message}`);
      }
    }
  }

  const tool = path.join(__dirname, '..', 'skills', 'animation-quality-review', 'scripts', 'video_tools.py');
  if (exists(tool) && python) {
    lines.push('');
    lines.push('animation-quality-review tool');
    const result = spawnSync('python3', ['-I', tool, '--help'], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    if (result.status === 0) {
      const commands = ['measure', 'strip', 'compare', 'profile', 'scorecard'];
      const missing = commands.filter((command) => !result.stdout.includes(command));
      if (missing.length) fail(`video_tools.py is missing commands: ${missing.join(', ')}`);
      else pass('video_tools.py exposes measure, strip, compare, profile and scorecard');
    } else {
      fail(`video_tools.py --help failed: ${(result.stderr || '').trim().split('\n')[0]}`);
    }
  }

  console.log(lines.join('\n'));
  console.log(`\n${failures} failure(s), ${warnings} warning(s).`);
  return failures === 0 ? 0 : 1;
}

module.exports = {
  doctor,
  install,
  listSkills,
  printInstallSummary,
  printTargets,
  upsertAgentsSection,
  writeIfChanged,
};
