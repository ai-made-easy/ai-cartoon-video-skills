'use strict';

const path = require('node:path');
const { exists, isDirectory, listDirectories, readText } = require('./util');

const REPO_ROOT = path.resolve(__dirname, '..');
const SKILLS_ROOT = path.join(REPO_ROOT, 'skills');
const COMMUNITY_ROOT = path.join(SKILLS_ROOT, 'community');

function splitFrontmatter(text) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text);
  if (!match) return { frontmatter: '', body: text };
  return { frontmatter: match[1], body: text.slice(match[0].length) };
}

function unquote(value) {
  const text = value.trim();
  if (text.length >= 2 && text.startsWith('"') && text.endsWith('"')) {
    return text.slice(1, -1).replace(/\\"/g, '"').replace(/\\n/g, '\n');
  }
  if (text.length >= 2 && text.startsWith("'") && text.endsWith("'")) {
    return text.slice(1, -1).replace(/''/g, "'");
  }
  return text;
}

/**
 * A small, tolerant frontmatter reader. It understands the fields skills use:
 * name, description, license and metadata.author. It is not a general YAML parser.
 */
function parseFrontmatter(text) {
  const { frontmatter, body } = splitFrontmatter(text);
  const data = {};
  let current = null;
  let block = false;

  for (const raw of frontmatter.split(/\r?\n/)) {
    const line = raw.replace(/\t/g, '  ');
    if (!line.trim()) continue;
    const top = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (top && !line.startsWith(' ')) {
      current = top[1];
      const value = top[2].trim();
      block = value === '>' || value === '>-' || value === '|' || value === '|-';
      data[current] = block ? '' : unquote(value);
      continue;
    }
    if (current && block) {
      const content = line.trim();
      const folded = /^[>]/.test(frontmatter.match(new RegExp(`^${current}:\\s*(.*)$`, 'm'))?.[1] || '');
      data[current] = data[current] ? `${data[current]}${folded ? ' ' : '\n'}${content}` : content;
    }
  }

  const author = /^\s+author:\s*(.+)$/m.exec(frontmatter);
  if (author) {
    data.author = unquote(author[1].trim());
  }
  return { data, body, frontmatter };
}

function loadSkill(directory, source) {
  const skillFile = path.join(directory, 'SKILL.md');
  const text = readText(skillFile);
  const parsed = parseFrontmatter(text);
  const folder = path.basename(directory);
  const name = parsed.data.name || folder;
  let license = parsed.data.license || '';
  if (!license && source === 'community') {
    const upstream = path.join(directory, 'UPSTREAM.md');
    if (exists(upstream)) {
      const match = /- \*\*License:\*\*\s*(.+)/.exec(readText(upstream));
      if (match) license = match[1].trim();
    }
  }
  return {
    name,
    folder,
    description: parsed.data.description || '',
    license,
    author: parsed.data.author || '',
    source,
    directory,
    skillFile,
    body: parsed.body,
    frontmatter: parsed.frontmatter,
  };
}

function discoverSkills({ includeCommunity = true } = {}) {
  const skills = [];
  for (const directory of listDirectories(SKILLS_ROOT)) {
    if (path.basename(directory) === 'community') continue;
    if (!exists(path.join(directory, 'SKILL.md'))) continue;
    skills.push(loadSkill(directory, 'first-party'));
  }
  if (includeCommunity) {
    for (const directory of listDirectories(COMMUNITY_ROOT)) {
      if (!exists(path.join(directory, 'SKILL.md'))) continue;
      skills.push(loadSkill(directory, 'community'));
    }
  }
  return skills.sort((a, b) => {
    if (a.source !== b.source) return a.source === 'first-party' ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
}

function selectSkills(skills, { requested, includeCommunity = false } = {}) {
  if (!requested || requested.length === 0) {
    return skills.filter((skill) => skill.source === 'first-party');
  }
  if (requested.includes('all')) return skills;
  const wanted = new Set(requested);
  const chosen = skills.filter((skill) => wanted.has(skill.name));
  const missing = [...wanted].filter((name) => !chosen.some((skill) => skill.name === name));
  if (missing.length) {
    const available = skills.map((skill) => skill.name).join(', ');
    throw new Error(`unknown skill: ${missing.join(', ')}. Available: ${available}`);
  }
  if (!includeCommunity) {
    const community = chosen.filter((skill) => skill.source === 'community');
    if (community.length) {
      throw new Error(
        `${community.map((s) => s.name).join(', ')} is a community skill. Add --community to install it.`
      );
    }
  }
  return chosen;
}

const REFERENCE_PATTERN = /\b(scripts|references|assets|agents|evals)\/[A-Za-z0-9._/-]+/g;

/**
 * Check the files a SKILL.md points at. Placeholder paths (with <, >, *, {, })
 * are examples, not files, so they are skipped.
 */
function missingReferences(skill) {
  const missing = [];
  const seen = new Set();
  for (const match of skill.body.matchAll(REFERENCE_PATTERN)) {
    let value = match[0].replace(/[.,;:)]+$/, '');
    if (/[<>*{}$]/.test(value) || value.endsWith('/')) continue;
    if (seen.has(value)) continue;
    seen.add(value);
    if (!exists(path.join(skill.directory, value))) {
      missing.push(value);
    }
  }
  return missing;
}

function validateSkill(skill) {
  const problems = [];
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(skill.name)) {
    problems.push(`name "${skill.name}" should be lowercase kebab-case`);
  }
  if (skill.name !== skill.folder) {
    problems.push(`name "${skill.name}" must match the folder "${skill.folder}"`);
  }
  if (!skill.description || skill.description.length < 20) {
    problems.push('description is missing or too short to trigger the skill');
  }
  if (!isDirectory(skill.directory)) {
    problems.push(`skill folder is missing: ${skill.directory}`);
  }
  const missing = missingReferences(skill);
  if (missing.length) {
    problems.push(`SKILL.md points at missing files: ${missing.join(', ')}`);
  }
  return problems;
}

module.exports = {
  COMMUNITY_ROOT,
  REFERENCE_PATTERN,
  REPO_ROOT,
  SKILLS_ROOT,
  discoverSkills,
  loadSkill,
  missingReferences,
  parseFrontmatter,
  selectSkills,
  splitFrontmatter,
  validateSkill,
};
