'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const SCRIPT = path.join(__dirname, '..', 'skills', 'pre-render-gate', 'scripts', 'check_overlays.py');

function available(command, args) {
  const result = spawnSync(command, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  return !result.error && result.status === 0;
}

const skip = available('python3', ['--version']) ? false : 'python3 is required for this test';

function run(plan) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'acvs-gate-'));
  const file = path.join(dir, 'plan.json');
  fs.writeFileSync(file, JSON.stringify(plan));
  return spawnSync('python3', ['-I', SCRIPT, file], { encoding: 'utf8' });
}

test('pre-render gate passes a clean plan', { skip }, () => {
  const result = run({
    width: 1080,
    height: 1920,
    overlays: [
      { type: 'counter', from: 0, dur: 60, label: 'MEN', value: 1100, y: 250 },
      { type: 'stamp', from: 70, dur: 60, text: 'AN ISLAND', y: 980, size: 47 },
    ],
  });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stdout, /pre-render gate: clean/);
});

test('pre-render gate names every defect with the overlay number and the fix', { skip }, () => {
  const result = run({
    width: 1080,
    height: 1920,
    overlays: [
      { type: 'counter', from: 100, dur: 60, label: 'LEFT EAST GERMANY', value: 3, y: 250 },
      { type: 'counter', from: 130, dur: 60, label: 'MORE', value: 9, y: 250 },
      { type: 'stamp', from: 300, dur: 60, text: 'HALF THE CITY IMPRISONED BEHIND A WALL', y: 980, size: 72 },
      { type: 'stamp', from: 400, dur: 60, text: 'SAME WORDS HERE', y: 760, size: 40 },
      { type: 'stamp', from: 420, dur: 60, text: 'SAME WORDS HERE', y: 980, size: 40 },
      { type: 'pill', from: 700, dur: 30, text: 'TOO HIGH', y: 100, size: 34 },
    ],
  });
  assert.equal(result.status, 1, result.stdout + result.stderr);
  const out = result.stdout;
  assert.match(out, /overlay #0 counter.*and overlay #1 counter.*top zone/);
  assert.match(out, /overlay #2 stamp.*safe width.*set "size" to <=/);
  assert.match(out, /overlay #3 stamp.*overlay #4 stamp.*same text/);
  assert.match(out, /overlay #5 pill.*above the safe top/);
  assert.match(out, /Nothing renders until it is clean/);
});

test('pre-render gate accepts a config override for custom types', { skip }, () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'acvs-gate-cfg-'));
  const plan = path.join(dir, 'plan.json');
  const cfg = path.join(dir, 'zones.json');
  fs.writeFileSync(plan, JSON.stringify({
    overlays: [
      { type: 'titlecard', from: 0, dur: 60, text: 'A LONG TITLE CARD THAT WOULD RUN OFF SCREEN', size: 80 },
    ],
  }));
  fs.writeFileSync(cfg, JSON.stringify({
    zones: { titlecard: { y: 250, h: 200 } },
    widths: { titlecard: { per: 0.6, pad: 40 } },
  }));
  const result = spawnSync('python3', ['-I', SCRIPT, plan, '--config', cfg], { encoding: 'utf8' });
  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.match(result.stdout, /overlay #0 titlecard.*safe width/);
});
