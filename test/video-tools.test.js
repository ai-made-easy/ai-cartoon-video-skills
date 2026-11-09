'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const SKILL = path.join(__dirname, '..', 'skills', 'animation-quality-review');

function available(command, args) {
  const result = spawnSync(command, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  return !result.error && result.status === 0;
}

const hasFfmpeg = available('ffmpeg', ['-version']);
const hasFfprobe = available('ffprobe', ['-version']);
const hasPython = available('python3', ['--version']);
const skip = hasFfmpeg && hasFfprobe && hasPython
  ? false
  : 'ffmpeg, ffprobe and python3 are required for this integration test';

test('video_tools.py measures, strips, profiles and scores a video', { skip }, () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'acvs-tools-'));
  try {
    // Work on a copy so `profile` writes into the copy, not the repository.
    const skill = path.join(root, 'skill');
    fs.cpSync(SKILL, skill, { recursive: true });
    const tool = path.join(skill, 'scripts', 'video_tools.py');

    const video = path.join(root, 'sample.mp4');
    const made = spawnSync(
      'ffmpeg',
      [
        '-hide_banner', '-loglevel', 'error', '-y',
        '-f', 'lavfi', '-i', 'testsrc=size=320x240:rate=30',
        '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000',
        '-t', '3', '-c:v', 'mpeg4', '-q:v', '5', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-shortest', video,
      ],
      { encoding: 'utf8' }
    );
    assert.equal(made.status, 0, made.stderr);

    const captions = path.join(root, 'captions.vtt');
    fs.writeFileSync(
      captions,
      'WEBVTT\n\n00:00:00.000 --> 00:00:03.000\nThis is a sample video for the test\n'
    );

    const out = path.join(root, 'measured');
    const measure = spawnSync('python3', ['-I', tool, 'measure', video, out, '--transcript', captions], {
      encoding: 'utf8',
    });
    assert.equal(measure.status, 0, measure.stderr);
    assert.ok(fs.existsSync(path.join(out, 'metrics.json')));
    assert.ok(fs.existsSync(path.join(out, 'sheets')));
    assert.ok(fs.existsSync(path.join(out, 'cut_checks')));

    const metrics = JSON.parse(fs.readFileSync(path.join(out, 'metrics.json'), 'utf8'));
    assert.equal(metrics.duration_s, 3);
    assert.ok(metrics.motion);
    assert.ok(metrics.look);
    assert.ok(metrics.script.word_count > 0);

    const strip = spawnSync(
      'python3',
      ['-I', tool, 'strip', video, path.join(root, 'strip.jpg'), '--start', '0.5', '--end', '1.0'],
      { encoding: 'utf8' }
    );
    assert.equal(strip.status, 0, strip.stderr);
    assert.ok(fs.existsSync(path.join(root, 'strip.jpg')));

    const compare = spawnSync('python3', ['-I', tool, 'compare', out], { encoding: 'utf8' });
    assert.equal(compare.status, 0, compare.stderr);
    assert.match(compare.stdout, /\| video \|/);

    const second = path.join(root, 'measured2');
    const measureAgain = spawnSync('python3', ['-I', tool, 'measure', video, second], { encoding: 'utf8' });
    assert.equal(measureAgain.status, 0, measureAgain.stderr);

    const targetsFile = path.join(root, 'targets.json');
    fs.writeFileSync(targetsFile, JSON.stringify({ edge_pct: { min: 1 }, pct_still: { max: 100 } }));
    const profile = spawnSync(
      'python3',
      ['-I', tool, 'profile', 'test-profile', out, second, '--title', 'Test profile', '--targets', targetsFile],
      { encoding: 'utf8' }
    );
    assert.equal(profile.status, 0, profile.stderr);
    assert.ok(fs.existsSync(path.join(skill, 'references', 'profiles', 'test-profile.json')));

    const scorecard = spawnSync('python3', ['-I', tool, 'scorecard', out, '--profile', 'test-profile'], {
      encoding: 'utf8',
    });
    assert.equal(scorecard.status, 0, scorecard.stderr);
    assert.ok(fs.existsSync(path.join(out, 'scorecard.md')));
    assert.match(fs.readFileSync(path.join(out, 'scorecard.md'), 'utf8'), /# Scorecard/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
