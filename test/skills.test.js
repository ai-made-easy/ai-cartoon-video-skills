'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const {
  discoverSkills,
  missingReferences,
  parseFrontmatter,
  selectSkills,
  validateSkill,
} = require('../src/skills');

test('parses the animation-quality-review frontmatter', () => {
  const skills = discoverSkills();
  const skill = skills.find((item) => item.name === 'animation-quality-review');
  assert.ok(skill, 'animation-quality-review should be discovered');
  assert.match(skill.description, /Review animated video/);
  assert.equal(skill.source, 'first-party');
  assert.ok(
    skill.body.startsWith('\n# Animation quality review') ||
      skill.body.startsWith('# Animation quality review')
  );
});

test('discovers first-party and community skills', () => {
  const skills = discoverSkills({ includeCommunity: true });
  const names = skills.map((skill) => skill.name);
  assert.ok(names.includes('animation-quality-review'));
  assert.ok(names.includes('gbro-collage-broll'));
  assert.ok(names.includes('lemo-opuscar'));
});

test('every bundled skill passes validation', () => {
  for (const skill of discoverSkills({ includeCommunity: true })) {
    assert.deepEqual(validateSkill(skill), [], `${skill.name} should be valid`);
  }
});

test('reports a missing file referenced by SKILL.md', () => {
  const skills = discoverSkills();
  const skill = skills.find((item) => item.name === 'animation-quality-review');
  const broken = { ...skill, body: `${skill.body}\n\n\`scripts/does-not-exist.py\`` };
  assert.deepEqual(missingReferences(broken), ['scripts/does-not-exist.py']);
});

test('selects first-party skills by default and rejects unknown names', () => {
  const skills = discoverSkills({ includeCommunity: true });
  const defaults = selectSkills(skills, {});
  assert.deepEqual(defaults.map((skill) => skill.name), ['animation-quality-review']);

  assert.throws(
    () => selectSkills(skills, { requested: ['nope'] }),
    /unknown skill: nope/
  );

  assert.throws(
    () => selectSkills(skills, { requested: ['gbro-collage-broll'] }),
    /community skill/
  );

  const community = selectSkills(skills, { requested: ['gbro-collage-broll'], includeCommunity: true });
  assert.equal(community[0].name, 'gbro-collage-broll');
});

test('parses folded and quoted frontmatter values', () => {
  const parsed = parseFrontmatter(
    ['---', 'name: demo', 'description: >-', '  one line', '  and another', 'license: MIT', '---', '', 'Body'].join('\n')
  );
  assert.equal(parsed.data.name, 'demo');
  assert.equal(parsed.data.description, 'one line and another');
  assert.equal(parsed.data.license, 'MIT');
  assert.equal(parsed.body.trim(), 'Body');
});

test('skill folders match their frontmatter names', () => {
  for (const skill of discoverSkills({ includeCommunity: true })) {
    assert.equal(skill.name, path.basename(skill.directory));
  }
});
