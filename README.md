# AI Cartoon Video Skills

A small, portable skill factory for people who make animated videos with AI coding agents.
It ships two first-party skills — one that measures a rendered video and one that checks the plan before
you render it — and installs them into the tools you already use:
Claude Code, Codex, Cursor, Gemini CLI, Windsurf, Cline, Continue.dev and GitHub Copilot.

The flagship skill is **`animation-quality-review`**: it measures a video frame by frame, shows you the
frames that matter, and says where a draft falls short of a reference style — with numbers and
timestamps, not adjectives.

The second is **`pre-render-gate`**: it checks the resolved plan for the defects that cost re-renders —
overlapping counters, text wider than the frame, duplicate stamps — and refuses the render until the
plan is clean. One draft, one render.

[Read the write-up](SUBSTACK.md) · [Related skills](docs/RELATED-SKILLS.md)

---

## Quick start

No clone and no global install:

```bash
npx github:ai-made-easy/ai-cartoon-video-skills
```

Or, once the package is on npm:

```bash
npx ai-cartoon-video-skills
```

The installer detects the agents already used by the current project and writes the skill in each
tool's own format. To choose the tools yourself:

```bash
npx github:ai-made-easy/ai-cartoon-video-skills --target claude,codex,cursor
```

For your home directory instead of one project:

```bash
npx github:ai-made-easy/ai-cartoon-video-skills --scope global --target claude,codex,gemini,agents
```

Then start a new agent session and ask:

> Break down this video and tell me why it looks good. Here is the file: `short.mp4`.

> Run the pre-render gate on my plan before I render it.

## What gets installed

Both first-party skills install the same way; the paths below are for one skill — use the name you asked for
(`animation-quality-review` or `pre-render-gate`).

| Tool | Where the skill goes | Extra file |
|---|---|---|
| Claude Code | `.claude/skills/animation-quality-review/` (or `~/.claude/skills/`) | — |
| Codex CLI | `.agents/skills/animation-quality-review/` and `.codex/skills/animation-quality-review/` | — |
| Cursor | `.cursor/skills/animation-quality-review/` | `.cursor/rules/animation-quality-review.mdc` |
| Gemini CLI | `.gemini/skills/animation-quality-review/` and `.agents/skills/` | — |
| Windsurf | `.agents/skills/animation-quality-review/` | `.windsurf/rules/animation-quality-review.md` |
| Cline | `.agents/skills/animation-quality-review/` | `.clinerules/animation-quality-review.md` |
| Continue.dev | `.agents/skills/animation-quality-review/` | `.continue/rules/animation-quality-review.md` |
| GitHub Copilot | `.agents/skills/animation-quality-review/` | `.github/instructions/animation-quality-review.instructions.md` |
| Any AGENTS.md reader | `.agents/skills/animation-quality-review/` | a marked section in `AGENTS.md` |

`.agents/skills/` is the shared location read by Codex, Cursor, Gemini CLI, Windsurf, Cline and
other tools. Claude Code, Cursor and Gemini CLI also get a native copy in their own folder, because
those agents read it first. Rule-based tools get a short rule that points at the full skill.

The full skill folder — `SKILL.md`, `scripts/`, `references/` — is always installed. Nothing
downloads at runtime.

## The animation-quality-review skill

It answers four kinds of question:

- **Break down one video:** "What makes this look good?"
- **Test a style across videos:** "Is this just this one?"
- **Review your own work:** "How far off is my draft?"
- **Save a playbook:** keep the numbers and rules for a style you want to reuse.

Built for animated work: cartoon characters, motion graphics, explainer shorts and animated social
video. The measuring tool runs on any file, but the saved profile and the review checklist describe
one style — the animated explainer short. For live-action, a documentary or a long non-animated
video, use the measurements on their own terms and say that the scoring does not apply.

### Requirements

- `ffmpeg` and `ffprobe` on `PATH`
- Python 3
- `yt-dlp` only if you want the skill to download a URL

No Python packages are needed.

### Commands

Run these from the skill folder:

```bash
python3 -I scripts/video_tools.py measure VIDEO OUT_DIR --transcript CAPTIONS.vtt
python3 -I scripts/video_tools.py strip VIDEO OUT.jpg --start 12.0 --end 13.5
python3 -I scripts/video_tools.py compare OUT_DIR_1 OUT_DIR_2
python3 -I scripts/video_tools.py measure VIDEO OUT_DIR --against PROFILE
python3 -I scripts/video_tools.py profile NAME OUT_DIR_1 OUT_DIR_2 --title "Readable name" --targets TARGETS.json
```

`measure` writes `metrics.json`, `sheets/` (evenly spaced overview frames) and `cut_checks/`
(the frames around each possible cut). `strip` builds a sheet of consecutive frames for one moment.
`compare` prints a table for several measured videos. `profile` turns measured references into a
named standard. `measure --against` and `scorecard` score a video against that standard and write
`scorecard.md` plus `weak_moments.jpg`.

The numbers point at things to look at. They are not verdicts. The cut detector is deliberately
oversensitive: in the six reference shorts, only 2 of 13 candidates were real hard cuts. The skill
tells the agent to check every candidate by eye before counting it.

## The pre-render-gate skill

Renders are the expensive step, and most "render, look, fix, render again" cycles chase a defect that was already
visible in the plan: two counters counting at once, a stamp wider than the frame, a label outliving its number, the
same text on screen twice. `pre-render-gate` checks the resolved plan (in frames, before rendering) for exactly those,
prints the overlay number and the change to make, and exits non-zero so a render command can refuse to run.

```bash
python3 -I scripts/check_overlays.py plan.json
```

No packages and no video needed — it reads JSON and finishes in milliseconds. Wire it in front of the encoder:

```bash
python3 -I scripts/check_overlays.py public/<id>/timeline.json || exit 1
node render.mjs <id>
```

The skill also carries the review rules that make one render enough: check motion on a contact sheet, check text at
full size (a 540×960 thumbnail cannot show a clipped stamp), allow at most one re-render, and never stop a running
render for a cosmetic fix. Geometry (zones, band heights, text-width factors) is configurable with `--config`, so it
fits any 2D overlay or motion-graphics renderer. The measured case study is in the skill's `SKILL.md`: five renders
in 55 minutes before the gate, one after.

## Install options

```bash
# Install everything, for every supported tool
npx github:ai-made-easy/ai-cartoon-video-skills --target all

# Install one skill for one tool, into a specific project
npx github:ai-made-easy/ai-cartoon-video-skills \
  --target cursor --skill animation-quality-review --dir ~/work/my-video

# Install the community skills too
npx github:ai-made-easy/ai-cartoon-video-skills --target all --community

# See what would happen, write nothing
npx github:ai-made-easy/ai-cartoon-video-skills --target all --dry-run
```

Useful commands:

```bash
npx github:ai-made-easy/ai-cartoon-video-skills list
npx github:ai-made-easy/ai-cartoon-video-skills targets
npx github:ai-made-easy/ai-cartoon-video-skills doctor
```

`doctor` checks Node, `ffmpeg`, `ffprobe`, `python3`, `yt-dlp`, every `SKILL.md`, every referenced
file, every Python file and every JSON file. Run it first when something does not work.

A second install is quiet: identical files are left alone, and no `.bak-` folders are made. If a
local edit differs, the old copy is kept beside the new one unless you pass `--force`.

## Community skills

The installer can also install two third-party skills that are small, self-contained and
permissively licensed:

| Skill | What it does | License |
|---|---|---|
| `gbro-collage-broll` | Turns a ~5 second voiceover line into a halftone paper-collage B-roll clip using Gemini Omni Flash. | MIT |
| `lemo-opuscar` | A thin wrapper that fetches the Lemo-Opuscar library and directs a short film in one of its 66 styles. | MIT (code) / CC BY 4.0 (styles) |

Install them with `--community`. They are vendored with their upstream licence and an
`UPSTREAM.md` that records the commit they came from. Their requirements are different from
`animation-quality-review`: read the skill's own setup section first.

The other projects worth looking at — HyperFrames, OneTake, Claude Animation Base — are not
vendored. Their licences or size make linking better than copying. See
[docs/RELATED-SKILLS.md](docs/RELATED-SKILLS.md).

## Add your own skill

This is a skill factory, not a single-skill repository.

1. Make a folder under `skills/` with a `SKILL.md` and optional `scripts/`, `references/` and
   `assets/`. The folder name must match the `name:` in the frontmatter.
2. Point at files with relative paths from the skill folder. The installer and `doctor` check that
   they exist.
3. Run `npm test`.

Third-party skills go under `skills/community/<name>/` with their `LICENSE` and an `UPSTREAM.md`.
Only vendor a skill when its licence allows redistribution. Link the rest from the catalog.

## Repository layout

```text
bin/cli.js                    the npx entry point
src/
  skills.js                   frontmatter, discovery and validation
  targets.js                  where each tool reads skills and rules
  install.js                  install, list, targets, doctor
skills/
  animation-quality-review/            the flagship skill
  pre-render-gate/                     plan checks before a render (+ review rules)
  community/                  vendored MIT skills
docs/RELATED-SKILLS.md        the wider video-skill ecosystem
test/                         node:test suite, including an ffmpeg integration test
```

## Development

```bash
npm test
npm pack --dry-run
```

The integration test builds a three-second test video with `ffmpeg`, then runs `measure`, `strip`,
`compare`, `profile` and `scorecard` on it. It skips when `ffmpeg`, `ffprobe` or `python3` is
missing.

## Privacy

The skills contain no personal paths, email addresses, API keys or channel handles. `video_tools.py`
runs `ffmpeg`, `ffprobe` and Python locally; it does not upload anything. Downloaded videos and
frames stay in the folder you choose. Keep them private and use them to study technique, not to
repost someone else's work.

## License

MIT for this repository. Each community skill keeps its upstream licence; see its `LICENSE` and
`UPSTREAM.md`.
