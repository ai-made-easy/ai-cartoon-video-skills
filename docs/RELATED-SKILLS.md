# Related video skills

These are the projects worth knowing about when you build animated videos with a coding agent.
Some are vendored into this repository; the rest are linked because their licence, size or shape
makes copying a bad idea.

## At a glance

| Project | What it gives you | License | In this repo? |
|---|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) | HTML/CSS/JS → deterministic MP4, plus 9 published agent skills and a Studio app. | Apache-2.0 | Linked |
| [OneTake](https://github.com/feitangyuan/onetake) | Product launch films and feature demos as one continuous take; a strong skill for motion that carries between beats. | PolyForm Noncommercial 1.0.0 | Linked |
| [gbro-collage-broll](https://github.com/pyang5166/gbro-collage-broll) | Turns one ~5 second voiceover line into a halftone paper-collage B-roll clip with Gemini Omni Flash. | MIT | Vendored |
| [Claude Animation Base](https://github.com/JohnHeibel/ClaudeAnimationBase) | A p5.js + p5.brush starter kit for animating hand-painted cartoons with Claude. Not packaged as a skill; the rules live in `ANIMATION_GUIDE.md`. | MIT | Linked |
| [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 66 code-made film styles; the skill fetches the library and directs a short in the style you pick. | MIT (code) / CC BY 4.0 (styles and films) | Vendored wrapper |

## Vendored

### `gbro-collage-broll`

```bash
npx github:ai-made-easy/ai-cartoon-video-skills --target claude --community --skill gbro-collage-broll
```

A three-gate workflow: confirm the visual metaphor, confirm the still frame, then generate the
clip. The gates are the point — they stop a bad idea from spending video-generation money.

Requirements: a Codex environment with the built-in `image_gen` tool for the still frame,
`GEMINI_API_KEY`, Python 3.10 or newer, `google-genai >= 2.10.0`, and `ffmpeg` / `ffprobe`.
The skill's first run checks all of this and prints only what is missing.

The upstream skill is written in Chinese. It is vendored unchanged so it does not drift.

### `lemo-opuscar`

```bash
npx github:ai-made-easy/ai-cartoon-video-skills --target claude --community --skill lemo-opuscar
```

This is the thin plugin skill from the Lemo-Opuscar repository. It clones or updates the library
(about 191 MB) into `~/lemo-opuscar`, installs the core tools, and then follows the library's own
`AGENTS.md` to choose a style, write a treatment, produce the film and deliver it.

The wrapper code is MIT. The library it fetches — the film styles and demo films — is CC BY 4.0,
so keep the attribution when you reuse a style.

## Linked, not vendored

### HyperFrames

HyperFrames is the most complete of these. It renders HTML, CSS, media and seekable animations to
MP4, and it ships its own skills:

```bash
npx hyperframes skills update
```

That installs the core set: `/hyperframes`, `/hyperframes-cli`, `/hyperframes-registry`,
`/media-use`, `/reverse-any-video` and `/style-sampling`. The extra skills — `/slideshow`,
`/remotion-to-hyperframes` and `/figma` — install on demand.

It is not vendored here for two reasons: the repository is about 412 MB, and its skills are
versioned to the CLI that runs them. Copying them would go stale and break the version match.
HyperFrames is Apache-2.0, so vendoring would be allowed; linking is simply better.

### OneTake

OneTake is a single, very good skill about one idea: every beat should grow out of the one before
it instead of replacing it. It is for product launch films, teasers and feature demos, not for
long-form editing.

It is **PolyForm Noncommercial 1.0.0**. That means free for noncommercial use only. It cannot be
vendored into this MIT repository without changing the licence of the whole package, so it is
linked:

```bash
git clone https://github.com/feitangyuan/onetake.git ~/.agents/skills/onetake
```

If you make films for clients or a business, the author sells a commercial licence.

### Claude Animation Base

This is not an agent skill. It is a starter kit: `src/clawd.js` draws the character, `render.mjs`
renders in headless Chrome, and `ANIMATION_GUIDE.md` holds the rules the model follows —
handmade, alive, one piece, no text, transitions always, something happens in every scene.

Clone it and point the agent at the guide:

```bash
git clone https://github.com/JohnHeibel/ClaudeAnimationBase.git
```

> Read `ANIMATION_GUIDE.md`, then make a 15-second video of Clawd trying to catch a butterfly.

It is MIT, so a wrapper skill could be added later. It is not wrapped yet because the guide is the
product and a wrapper would add a layer without adding knowledge.

## What belongs in this factory

Before adding a skill to `skills/` or `skills/community/`, check:

- [ ] The licence allows redistribution. MIT, Apache-2.0 and BSD do. PolyForm Noncommercial,
      "source available" and no-licence repos do not.
- [ ] The skill is self-contained: `SKILL.md` plus every script and reference it names.
- [ ] It contains no API keys, personal paths, email addresses or private channel data.
- [ ] Its requirements are written down, especially paid APIs and large downloads.
- [ ] The folder is a sensible size. Demo videos and multi-hundred-megabyte libraries stay out.
- [ ] `npx github:ai-made-easy/ai-cartoon-video-skills doctor` passes against it.

If a project fails one of those, link it here instead of copying it. The catalog is more useful
when it is honest about why something is not in the box.
