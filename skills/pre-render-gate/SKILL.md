---
name: pre-render-gate
license: MIT
description: Catch overlay, caption and timing defects in a video plan before rendering, so a draft costs one render instead of five. Checks a resolved plan (text overlays, counters, stamps, captions placement) for collisions, text wider than the safe area, off-screen or out-of-zone text, duplicated on-screen text and impossible label timings, and prints each problem with the overlay number and the exact change. Use this when an animated video, cartoon, motion-graphics piece, explainer, Short, Reel or title sequence is about to be rendered and the plan already exists — especially when the same video has already been rendered more than once to fix plan-level mistakes, when renders take minutes each, or when the user asks how to stop the render-and-review loop. Not a video analyzer and not a renderer: it reads a JSON plan, not pixels.
---

# Pre-render gate

Rendering is the expensive step. Almost every "render, look, fix, render again" cycle comes from a defect that was
already visible in the plan: two counters counting at the same moment, a stamp wider than the frame, a label that
outlives its number, the same line of text on screen twice, a pill 40 px off-screen. Those are milliseconds of JSON
checking, not ten minutes of 4K encoding.

This skill turns that check into a gate. It ships `scripts/check_overlays.py`, needs only Python 3, and prints
messages an agent can act on directly: which overlay, which frames, what to set.

## When to run it

- **Before the first render**, once the plan's timings are resolved (real voice/word timings, not placeholder ones).
- **Again after any plan edit** — a changed word timing can turn a clear band into a collision.
- **Before a re-render**, never after: if the gate is clean and the render still looks wrong, the defect is in the
  renderer or a visual judgment, and re-rendering the same plan cannot fix it.

## Proven result (case study, 2026-11-09)

A 98-second history Short was rendered five times in 55 minutes and never uploaded. Every render chased a plan defect:

| Render | What the frame review found | Was it in the plan? |
|---|---|---|
| 1 | two counters counting simultaneously | yes — two `counter` overlays overlapped in the top band |
| 2 | label outlived its counter | yes — `labelAt` past the counter's end |
| 3 | stamp clipped at the frame edge | yes — text 145 px wider than the safe width |
| 4 | duplicate stamp wording | yes — two overlays with identical text |
| 5 | the previous 4 fixes | — |

After adding this gate, the plan check found the surviving defects in under a second and the next render was the
last. The gate is calibrated to be silent on plans that shipped well: run it on your own finished videos first.

## Use

```bash
python3 -I scripts/check_overlays.py plan.json
python3 -I scripts/check_overlays.py plan.json --config zones.json   # your own types / geometry
```

Exit code 0 = clean, 1 = errors (`WARN` lines never fail). The plan is your renderer's **resolved** plan, in frames:

```json
{
  "width": 1080, "height": 1920,
  "safe": {"margin": 40, "top": 220, "bottom": 1500},
  "overlays": [
    {"type": "counter", "from": 100, "dur": 60, "label": "LEFT EAST", "value": 3, "y": 250, "size": 132},
    {"type": "stamp",   "from": 300, "until": 380, "text": "AN ISLAND IN THE EAST", "y": 980, "size": 47}
  ]
}
```

Rules applied:

- **one band at a time** among `counter`, `year`, `ribbon`, `hud` (default `top` list) — anything overlapping by more
  than the 8-frame dissolve is an error; lower-zone stacking (a stamp under a pill) is a warning for the full-size look;
- **text fits the safe width** (`width - 2 * margin`) with the maximum size or character count printed;
- **text stays in the safe vertical zone**;
- **no text twice at once**;
- **`labelAt` lies inside its counter**.

## Wire it into the render command

A gate nobody runs is a comment. Make the render script refuse:

```bash
python3 -I scripts/check_overlays.py public/<id>/timeline.json || {
  echo "pre-render gate FAILED — nothing rendered."
  echo "Fix the ERROR lines in your plan, rebuild the timeline, run the gate again."
  exit 1
}
node render.mjs <id>
```

The rebuild must come before the gate (timings change), and the gate before the encoder.

## Review rules that go with it

- A **contact sheet** is for motion: is something changing every second, are there blank or black frames, do
  transitions jump? It is the wrong tool for text — a 540×960 thumbnail cannot show whether a stamp is clipped.
- **Text and edges are checked at full size**: render the specific frames at 1× and look at crops, or ask a
  separate image checker with the context ("is this stamp fully inside the frame at this word?").
- **At most one re-render.** After the second render, ship unless a fact is wrong or text is unreadable.
- **Never stop a running render for a cosmetic fix.** Let it finish, review it, fold every fix into the one allowed
  re-render.
- If the same defect appears in two videos, fix the plan template or the renderer — not the video.

## Make the geometry yours

`scripts/check_overlays.py --config` takes a JSON file that overrides, per overlay type:

```json
{
  "zones":  {"counter": {"y": 250, "h": 240}, "stamp": {"y": 760, "h": null}},
  "widths": {"stamp": {"per": 0.68, "pad": 94}, "pill": {"per": 0.62, "pad": "=size"}},
  "top":    ["counter", "year", "ribbon", "hud"]
}
```

- `zones.<type>.y` is the layout default; `h` is the height below it (`null` = `size + 48`).
- `widths.<type>` models `width = chars * per * size + pad`; `pad` may be `"=size"` or `"=0.1size"`.
  Measure one render of the type and fit `per` — it is the only number worth tuning.
- Types not listed there are not width-checked (their `zones` entry still participates in band collisions).

Read the constants from the renderer's own components once, and update them in the same change when the layout moves.
Keep the gate silent on videos that already shipped well; a gate that cries wolf gets skipped.

## Not this skill

- Judging whether the animation is good, or measuring a rendered video: a frame-by-frame video analysis skill.
- Writing the script or the shot list: the project's own content skill.
- Rendering: the gate says "go", it does not encode.
