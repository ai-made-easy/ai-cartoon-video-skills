'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { install } = require('../src/install');
const { walkFiles } = require('../src/util');

function sandbox() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'acvs-'));
  const projectDir = path.join(root, 'project');
  const homeDir = path.join(root, 'home');
  fs.mkdirSync(projectDir, { recursive: true });
  fs.mkdirSync(homeDir, { recursive: true });
  return {
    root,
    projectDir,
    homeDir,
    cleanup: () => fs.rmSync(root, { recursive: true, force: true }),
  };
}

function run(options) {
  return install({ log: () => {}, ...options });
}

test('installs animation-quality-review for Claude, Codex, Cursor and AGENTS.md', () => {
  const box = sandbox();
  try {
    run({
      targets: ['claude', 'codex', 'cursor', 'agents-md'],
      skills: ['animation-quality-review'],
      projectDir: box.projectDir,
      homeDir: box.homeDir,
    });

    assert.ok(fs.existsSync(path.join(box.projectDir, '.claude/skills/animation-quality-review/SKILL.md')));
    assert.ok(fs.existsSync(path.join(box.projectDir, '.agents/skills/animation-quality-review/SKILL.md')));
    assert.ok(fs.existsSync(path.join(box.projectDir, '.codex/skills/animation-quality-review/SKILL.md')));
    assert.ok(fs.existsSync(path.join(box.projectDir, '.cursor/skills/animation-quality-review/SKILL.md')));
    assert.ok(fs.existsSync(path.join(box.projectDir, '.cursor/rules/animation-quality-review.mdc')));
    assert.ok(fs.existsSync(path.join(box.projectDir, '.agents/skills/animation-quality-review/scripts/video_tools.py')));
    assert.ok(
      fs.existsSync(
        path.join(box.projectDir, '.agents/skills/animation-quality-review/references/profiles/animated-explainer-shorts.json')
      )
    );

    const rule = fs.readFileSync(path.join(box.projectDir, '.cursor/rules/animation-quality-review.mdc'), 'utf8');
    assert.match(rule, /^---\n/);
    assert.match(rule, /alwaysApply: false/);
    assert.match(rule, /# Animation quality review/);

    const agents = fs.readFileSync(path.join(box.projectDir, 'AGENTS.md'), 'utf8');
    assert.match(agents, /ai-cartoon-video-skills:start animation-quality-review/);
    assert.match(agents, /\.agents\/skills\/animation-quality-review\/SKILL\.md/);
  } finally {
    box.cleanup();
  }
});

test('a second install changes nothing and makes no backups', () => {
  const box = sandbox();
  try {
    const options = {
      targets: ['claude', 'codex', 'cursor', 'agents-md'],
      skills: ['animation-quality-review'],
      projectDir: box.projectDir,
      homeDir: box.homeDir,
    };
    run(options);
    const first = walkFiles(box.projectDir).length;
    run(options);
    const second = walkFiles(box.projectDir).length;

    assert.equal(second, first, 'no files should be added on reinstall');
    assert.equal(
      walkFiles(box.projectDir).filter((file) => file.includes('.bak-')).length,
      0,
      'reinstall must not leave backup folders'
    );
    const agents = fs.readFileSync(path.join(box.projectDir, 'AGENTS.md'), 'utf8');
    assert.equal(agents.match(/ai-cartoon-video-skills:start animation-quality-review/g).length, 1);
  } finally {
    box.cleanup();
  }
});

test('installs globally into the supplied home directory', () => {
  const box = sandbox();
  try {
    run({
      targets: ['claude', 'agents'],
      skills: ['animation-quality-review'],
      scope: 'global',
      projectDir: box.projectDir,
      homeDir: box.homeDir,
    });
    assert.ok(fs.existsSync(path.join(box.homeDir, '.claude/skills/animation-quality-review/SKILL.md')));
    assert.ok(fs.existsSync(path.join(box.homeDir, '.agents/skills/animation-quality-review/SKILL.md')));
    assert.ok(!fs.existsSync(path.join(box.projectDir, '.claude')));
  } finally {
    box.cleanup();
  }
});

test('installs a community skill when asked, with its licence', () => {
  const box = sandbox();
  try {
    run({
      targets: ['claude'],
      skills: ['gbro-collage-broll'],
      community: true,
      projectDir: box.projectDir,
      homeDir: box.homeDir,
    });
    const installed = path.join(box.projectDir, '.claude/skills/gbro-collage-broll');
    assert.ok(fs.existsSync(path.join(installed, 'SKILL.md')));
    assert.ok(fs.existsSync(path.join(installed, 'scripts/generate_video.py')));
    assert.ok(fs.existsSync(path.join(installed, 'LICENSE')));
    assert.ok(fs.existsSync(path.join(installed, 'UPSTREAM.md')));
  } finally {
    box.cleanup();
  }
});

test('a dry run writes nothing', () => {
  const box = sandbox();
  try {
    run({
      targets: ['all'],
      skills: ['all'],
      community: true,
      projectDir: box.projectDir,
      homeDir: box.homeDir,
      dryRun: true,
    });
    assert.equal(walkFiles(box.projectDir).length, 0);
  } finally {
    box.cleanup();
  }
});

test('every target can be installed together', () => {
  const box = sandbox();
  try {
    run({
      targets: ['all'],
      skills: ['animation-quality-review'],
      projectDir: box.projectDir,
      homeDir: box.homeDir,
    });
    assert.ok(fs.existsSync(path.join(box.projectDir, '.windsurf/rules/animation-quality-review.md')));
    assert.ok(fs.existsSync(path.join(box.projectDir, '.clinerules/animation-quality-review.md')));
    assert.ok(fs.existsSync(path.join(box.projectDir, '.continue/rules/animation-quality-review.md')));
    assert.ok(
      fs.existsSync(path.join(box.projectDir, '.github/instructions/animation-quality-review.instructions.md'))
    );
    assert.ok(fs.existsSync(path.join(box.projectDir, 'AGENTS.md')));
  } finally {
    box.cleanup();
  }
});
