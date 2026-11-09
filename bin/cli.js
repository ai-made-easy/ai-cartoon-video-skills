#!/usr/bin/env node
'use strict';

const os = require('node:os');
const path = require('node:path');
const pkg = require('../package.json');
const {
  doctor,
  install,
  listSkills,
  printInstallSummary,
  printTargets,
} = require('../src/install');
const HELP = `ai-cartoon-video-skills ${pkg.version}

Install reusable agent skills for Claude Code, Codex, Cursor, Gemini CLI,
Windsurf, Cline, Continue.dev and GitHub Copilot.

Usage:
  npx ai-cartoon-video-skills [install] [options]
  npx github:ai-made-easy/ai-cartoon-video-skills [options]

Commands:
  install   Install skills (the default). Writes the full skill folder plus
            the rule file each tool reads.
  list      List the skills bundled in this package.
  targets   Show where each tool installs skills and rules.
  doctor    Check Node, ffmpeg, ffprobe, python3 and the bundled skill files.
  help      Show this help.

Options:
  -t, --target <names>   Comma-separated tools, or "all" / "auto".
                         Default: auto-detect the tools already used by the project.
                         Examples: claude,codex,cursor,agents
  -s, --skill <names>    Comma-separated skill names, or "all".
                         Default: every first-party skill.
  --community            Include the community skills in skills/community/.
  --all-skills           Shortcut for --skill all together with community.
  --scope <where>        "project" (default) or "global" (your home directory).
  --dir <path>           Project directory. Default: the current directory.
  --home <path>          Home directory. Default: your home directory.
  --force                Replace an existing install without keeping a backup.
  --dry-run              Print what would be written, write nothing.
  -h, --help             Show this help.
  -v, --version          Print the version.

Examples:
  npx ai-cartoon-video-skills
  npx ai-cartoon-video-skills --target claude,codex,cursor
  npx ai-cartoon-video-skills --scope global --target claude,agents,cursor
  npx ai-cartoon-video-skills --target all --community
  npx ai-cartoon-video-skills doctor
`;

function takeValue(args, index, flag) {
  const value = args[index];
  if (!value || value.startsWith('-')) {
    throw new Error(`${flag} needs a value`);
  }
  return value;
}

function parseArgs(argv) {
  const args = [...argv];
  let command = 'install';
  if (args[0] && !args[0].startsWith('-')) {
    command = args.shift();
  }

  const options = {
    command,
    targets: [],
    skills: [],
    community: false,
    scope: 'project',
    projectDir: process.cwd(),
    homeDir: os.homedir(),
    force: false,
    dryRun: false,
    help: false,
    version: false,
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    const [flag, inline] = arg.startsWith('--') && arg.includes('=') ? arg.split('=', 2) : [arg, null];
    const value = () => {
      if (inline !== null) return inline;
      const next = takeValue(args, index + 1, flag);
      index += 1;
      return next;
    };
    const pushList = (field) => {
      options[field].push(...value().split(',').map((item) => item.trim()).filter(Boolean));
    };

    switch (flag) {
      case '-h':
      case '--help':
        options.help = true;
        break;
      case '-v':
      case '--version':
        options.version = true;
        break;
      case '-t':
      case '--target':
        pushList('targets');
        break;
      case '-s':
      case '--skill':
        pushList('skills');
        break;
      case '--community':
        options.community = true;
        break;
      case '--all-skills':
        options.community = true;
        options.skills = ['all'];
        break;
      case '--scope':
        options.scope = value();
        if (!['project', 'global'].includes(options.scope)) {
          throw new Error('--scope must be "project" or "global"');
        }
        break;
      case '--dir':
        options.projectDir = path.resolve(value());
        break;
      case '--home':
        options.homeDir = path.resolve(value());
        break;
      case '--force':
        options.force = true;
        break;
      case '--dry-run':
        options.dryRun = true;
        break;
      case '--yes':
      case '-y':
        break;
      default:
        throw new Error(`unknown option: ${arg}`);
    }
  }

  return options;
}

function main(argv) {
  let options;
  try {
    options = parseArgs(argv);
  } catch (error) {
    console.error(`ai-cartoon-video-skills: ${error.message}\n`);
    console.error(HELP);
    return 2;
  }

  if (options.help || options.command === 'help') {
    console.log(HELP);
    return 0;
  }
  if (options.version) {
    console.log(pkg.version);
    return 0;
  }

  try {
    switch (options.command) {
      case 'install': {
        const summary = install({
          targets: options.targets,
          skills: options.skills,
          community: options.community,
          scope: options.scope,
          projectDir: options.projectDir,
          homeDir: options.homeDir,
          force: options.force,
          dryRun: options.dryRun,
          log: (message) => console.log(message),
        });
        if (summary.results.length === 0) {
          console.log('Nothing to install. Check --target and --skill.');
          return 1;
        }
        printInstallSummary(summary);
        return 0;
      }
      case 'list':
        listSkills({ homeDir: options.homeDir });
        return 0;
      case 'targets':
        printTargets({ projectDir: options.projectDir, homeDir: options.homeDir });
        return 0;
      case 'doctor':
        return doctor({ projectDir: options.projectDir, homeDir: options.homeDir });
      default:
        throw new Error(`unknown command: ${options.command}. Try "help".`);
    }
  } catch (error) {
    console.error(`ai-cartoon-video-skills: ${error.message}`);
    return 1;
  }
}

if (require.main === module) {
  process.exitCode = main(process.argv.slice(2));
}

module.exports = { main, parseArgs };
