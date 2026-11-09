'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const pkg = require('../package.json');

const CLI = path.join(__dirname, '..', 'bin', 'cli.js');

function cli(...args) {
  return spawnSync(process.execPath, [CLI, ...args], {
    encoding: 'utf8',
    cwd: path.join(__dirname, '..'),
  });
}

test('--help explains the commands and options', () => {
  const result = cli('--help');
  assert.equal(result.status, 0);
  assert.match(result.stdout, /Usage:/);
  assert.match(result.stdout, /install/);
  assert.match(result.stdout, /--target/);
  assert.match(result.stdout, /--community/);
});

test('--version prints the package version', () => {
  const result = cli('--version');
  assert.equal(result.status, 0);
  assert.equal(result.stdout.trim(), pkg.version);
});

test('list shows first-party and community skills', () => {
  const result = cli('list');
  assert.equal(result.status, 0);
  assert.match(result.stdout, /animation-quality-review/);
  assert.match(result.stdout, /gbro-collage-broll/);
  assert.match(result.stdout, /lemo-opuscar/);
});

test('targets lists the supported tools', () => {
  const result = cli('targets');
  assert.equal(result.status, 0);
  for (const name of ['claude', 'codex', 'cursor', 'gemini', 'windsurf', 'cline', 'continue', 'copilot']) {
    assert.match(result.stdout, new RegExp(`^${name}`, 'm'));
  }
});

test('a dry-run install writes nothing', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'acvs-cli-'));
  try {
    const result = cli('install', '--dry-run', '--target', 'claude', '--dir', directory);
    assert.equal(result.status, 0);
    assert.match(result.stdout, /Would install/);
    assert.ok(!fs.existsSync(path.join(directory, '.claude')));
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('an unknown target is an error', () => {
  const result = cli('install', '--target', 'not-a-tool');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /unknown target/);
});

test('an unknown skill is an error', () => {
  const result = cli('install', '--skill', 'not-a-skill');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /unknown skill/);
});

test('doctor checks the bundled tools', () => {
  const result = cli('doctor');
  assert.match(result.stdout, /animation-quality-review/);
  assert.match(result.stdout, /video_tools\.py/);
});
