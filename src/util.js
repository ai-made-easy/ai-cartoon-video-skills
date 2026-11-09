'use strict';

const fs = require('node:fs');
const path = require('node:path');

const SKIP_NAMES = new Set([
  '.git',
  '.DS_Store',
  'node_modules',
  '__pycache__',
  '.venv',
  'venv',
]);

function exists(target) {
  try {
    fs.accessSync(target);
    return true;
  } catch {
    return false;
  }
}

function isDirectory(target) {
  try {
    return fs.statSync(target).isDirectory();
  } catch {
    return false;
  }
}

function ensureDir(target) {
  fs.mkdirSync(target, { recursive: true });
}

function readText(target) {
  return fs.readFileSync(target, 'utf8');
}

function writeText(target, text) {
  ensureDir(path.dirname(target));
  fs.writeFileSync(target, text, 'utf8');
}

function remove(target) {
  fs.rmSync(target, { recursive: true, force: true });
}

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

/**
 * Copy a skill folder, skipping local junk. Shell and Python files stay executable.
 */
function copyDir(source, destination) {
  ensureDir(path.dirname(destination));
  fs.cpSync(source, destination, {
    recursive: true,
    force: true,
    filter: (entry) => !SKIP_NAMES.has(path.basename(entry)),
  });
  for (const file of walkFiles(destination)) {
    if (file.endsWith('.sh') || file.endsWith('.py')) {
      try {
        fs.chmodSync(file, 0o755);
      } catch {
        // Best effort: some filesystems refuse chmod. The interpreter still runs it.
      }
    }
  }
}

/**
 * True when two folder trees contain the same files with the same bytes.
 * Used so re-running the installer does not make a backup of an unchanged skill.
 */
function sameTree(source, destination) {
  if (!isDirectory(source) || !isDirectory(destination)) return false;
  const sourceFiles = walkFiles(source).map((file) => path.relative(source, file)).sort();
  const destinationFiles = walkFiles(destination).map((file) => path.relative(destination, file)).sort();
  if (sourceFiles.length !== destinationFiles.length) return false;
  for (let index = 0; index < sourceFiles.length; index += 1) {
    if (sourceFiles[index] !== destinationFiles[index]) return false;
    const left = fs.readFileSync(path.join(source, sourceFiles[index]));
    const right = fs.readFileSync(path.join(destination, destinationFiles[index]));
    if (!left.equals(right)) return false;
  }
  return true;
}

/**
 * Replace a destination. By default the old version is kept beside it with a
 * timestamp, so a local edit is never silently lost. Identical copies are left
 * alone, so a second install is quiet.
 */
function installCopy(source, destination, options = {}) {
  const { force = false, dryRun = false, log = () => {} } = options;
  let backup = null;
  if (exists(destination)) {
    if (sameTree(source, destination)) {
      log(`  unchanged ${destination}`);
      return { destination, backup: null, changed: false };
    }
    if (force) {
      if (!dryRun) remove(destination);
      log(dryRun ? `  would replace ${destination} (--force)` : `  replaced ${destination} (--force)`);
    } else {
      backup = `${destination}.bak-${timestamp()}`;
      if (!dryRun) {
        fs.renameSync(destination, backup);
      }
      log(dryRun ? `  would back up the old copy to ${backup}` : `  backed up the old copy to ${backup}`);
    }
  }
  if (!dryRun) {
    copyDir(source, destination);
  }
  log(dryRun ? `  would copy to ${destination}` : `  copied to ${destination}`);
  return { destination, backup, changed: true };
}

function walkFiles(root) {
  const found = [];
  if (!isDirectory(root)) return found;
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    if (SKIP_NAMES.has(entry.name)) continue;
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) {
      found.push(...walkFiles(full));
    } else if (entry.isFile()) {
      found.push(full);
    }
  }
  return found;
}

function listDirectories(root) {
  if (!isDirectory(root)) return [];
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
    .map((entry) => path.join(root, entry.name));
}

function relativePath(from, to) {
  const value = path.relative(from, to);
  return value === '' ? '.' : value;
}

module.exports = {
  copyDir,
  ensureDir,
  exists,
  installCopy,
  isDirectory,
  listDirectories,
  readText,
  relativePath,
  remove,
  sameTree,
  timestamp,
  walkFiles,
  writeText,
};
