---
name: youtube-long-video
license: MIT
description: Plan, check and fix a LONG animated video (8 to 20 minutes, with a narrator character, animated maps and cartoon story scenes) so it keeps attention. Use it when the user wants to make or improve a long animated explainer or history-style video, says a long video feels flat or boring, wants to copy the rhythm of a reference video, or asks for a deterministic quality check (mix of picture types, "something new every few seconds", voice pace) before rendering or uploading. It measures a reference video from screenshots taken every 3 seconds, turns that into rules, and tests our own plan and rendered MP4 with a Python script. It does not judge taste, story or facts.
---

# Long video animation: measure a reference, then test your own video

A first long animated video can look fine and still feel flat. The reason is usually rhythm and variety, not the single pictures: too long on the same kind of picture, too few things happening, a voice that is fast and flat. Rhythm and variety can be measured. This skill measures a reference video you admire, turns it into numbers, and then checks our own plan and our own render against those numbers with a script that gives the same answer every time.

Everything the skill needs is in this folder. Paths below are relative to it (usually `~/.claude/skills/youtube-long-video/`).

## What the skill can and cannot do

It measures: share of each picture type, how long we stay on one type, how often something new appears, cuts per minute, motion, voice pace. It does not judge whether the story is good, whether the facts are right, whether the drawings are beautiful, or whether the jokes work. A video can pass every rule and still be dull. Say this to the user at the start and at the end.

## Workflow

### a. Pick a reference video

Ask the user for one long video (8 to 20 minutes) whose feel they want, in the same kind of format (narrator character, maps, story scenes). One is enough, but say plainly that one video shows what one video does. Take the first 15 minutes. If it has a sponsor read, note its start and end in seconds: it will be excluded.

Get the file however the user prefers (their own download, a screen recording). Do not ship or publish frames of someone else's video; keep them local.

### b. Take a screenshot every 3 seconds and tag each one

Run:

    python3 scripts/make_sheets.py --video reference.mp4 --out work/ref --end 900

This writes one frame every 3 seconds and contact sheets of 30 frames (6 columns by 5 rows, 90 seconds per sheet, time in the corner of every tile). For 15 minutes that is 300 frames and 10 sheets.

Look at each sheet (read the JPG) and tag every tile with one code. The codes are in `references/labels.md`. Short version:

- M map
- NG narrator over a greyed map
- NW narrator on a plain wall
- ND narrator in a drawn set
- S cartoon story scene
- P full-screen photo or painting
- C photo card on a map
- T text or title card
- O sponsor or other

Use exactly this prompt for each sheet (paste it, then attach the sheet image):

    This image is a contact sheet of 30 frames from one video: 6 columns by 5 rows, read left to right, top to bottom.
    Every tile is 3 seconds after the previous one. The time of each tile is written in yellow in its bottom-left corner.
    Give exactly ONE code per tile, 30 codes in total (fewer only on the last sheet):
    M   an animated map is the main picture (labels, pins, armies, growing regions are still M)
    NG  a narrator character stands over a map or picture that is greyed or blurred behind it
    NW  a narrator character on a plain or lightly patterned wall or flat colour
    ND  a narrator character inside a drawn place (a room, a ruin, a museum)
    S   a cartoon story scene: drawn characters acting in a painted set, often with speech lines
    P   a real photo, painting or artefact filling most of the screen
    C   a photo or painting as a small card on top of a map (less than about 45 % of the width)
    T   a text card, title card, chart or counter with no map or scene behind it
    O   a sponsor read, ad, logo screen, black frame, subscribe ending, or anything else
    When two codes fit, choose by what fills most of the frame. A narrator with a card beside him is still a narrator code.
    Do not describe the pictures. Do not skip tiles. Reply with ONE line in this exact form and nothing else:
    SHEET <number>: <code> <code> <code> ... (30 codes separated by single spaces)

Save the codes in order, one per 3 seconds, in a plain text file (`work/tags-ref.txt`). Check the count: 15 minutes must give 300 codes. If a sheet comes back with the wrong number of codes, ask again for that sheet only.

### c. Turn the tags into the mix and the "within every X seconds, Y must happen" rules

Run:

    python3 scripts/tags_to_rules.py work/tags-ref.txt --exclude 282-351

(leave out `--exclude` if there is no sponsor read). It prints the mix (share of each type) and the worst gap of each kind. X for each cadence rule is the reference's worst gap rounded up to a whole second, so the reference passes its own test. For example, if the reference never stays on a map longer than 39 seconds, the rule becomes "leave the map within every 40 seconds".

The shipped spec, `data/long-video-spec.json`, already contains numbers made this way from one reference (see README and `references/rules.md`). Using it as it is, is fine. If the user's reference is different (shorter jokes, no maps, a different style), re-make the numbers: copy the spec, edit the "cadence" and "rules" values, or run the checker on the reference MP4 with `--labels work/tags-ref.txt --calibrate --spec my-spec.json` to write the pixel targets from it. Then pass `--spec my-spec.json` in every later run.

### d. Write our own plan, then run the checker

Write the plan as a timeline JSON, one entry per shot, in the format described in `references/timeline-format.md` (start and duration in seconds, the picture type, whether the narrator is over a map, the on-screen events and, for story scenes, the pose changes and spoken lines). See `examples/sample-timeline.json`.

Plan layer, before rendering anything:

    python3 scripts/video_qa.py --timeline plan.json --out qa-plan

Render. Then the pixel layer on the rendered MP4 together with the plan:

    python3 scripts/video_qa.py --video final.mp4 --timeline plan.json --out qa-final

It writes `qa.md` and `qa.json`. The report has a cadence table with the exact times of every gap that is too long, then every rule with its target and PASS, WARN or FAIL, then the windows that miss. Exit code 1 means at least one FAIL.

For a quick look at a long render you can speed things up: make a 480p copy (`ffmpeg -i final.mp4 -vf scale=854:480 -c:v libx264 -crf 28 -an check.mp4`) and run the pixel layer on that. The numbers are measured at 256x144 anyway.

### e. Fix every FAIL, rerun

Read the report from the top. Fix in this order:

1. Cadence FAILs. They carry exact times ("leave the map: 5:06 to 13:48, 8 min 42 s"). Insert a story scene, a narrator beat, a full-screen image or a chart in that stretch. Do not move things elsewhere to hide the gap.
2. Whole-video mix FAILs (map too high, no story scenes, too many small cards).
3. Pixel FAILs (too few cuts, too saturated, too flat). These depend on the render, so change the shots, then render again.
4. WARNs last, and only if cheap.

After each batch of fixes, rerun the plan layer (seconds, no render). Only render when the plan layer is clean. Do not change a number in the spec to make a FAIL go away unless the user agrees that the reference really is different.

### f. Voice, character and background rules for long videos

Read `references/voice-rules.md` and `references/character-and-background-rules.md` before writing the narration and the shots. Short version of the voice rules:

- Pace around 130 words a minute (120 to 140). A fast short-video pace (200 or more) is wrong for 15 minutes.
- Pitch moves inside a range, about 12 semitones from low to high, with real movement from sentence to sentence. Flat is the failure; theatrical is also a failure.
- Real pauses between sentences, a longer one before "But", "Yet" and a question that follows a statement.
- No dashes inside a word (do not spell a name out as "bab-ih-lon"); the voice reads each part separately and it sounds choppy. Never respell a common word. Use the plain spelling and check the recording by speech-to-text.

Short version of the character and background rules:

- The narrator is on screen at least once a minute, never for long in one go, and never on a plain colour wall: put them over the live map, beside a portrait card, or inside a drawn place.
- Story scenes: two main characters plus a few small background people, a still camera, hard cuts in and out, a pose change every 1 to 3 seconds, a short line of dialogue written on screen above the speaker.
- Maps always move: a camera that eases, regions that grow, armies or routes that travel.
- Photos are big for a few seconds, not tiny cards left on a map.

### g. Say what the tool cannot do

When you report the result, say in plain words: the score measures rhythm and variety against one reference; a high score does not mean the video is good; story, facts, taste and humour were not tested; the numbers come from one reference video and are descriptions of what it does, not laws of YouTube. Suggest the user also watch the video once with the sound off (does the picture alone still move?) and once with the picture off (does the voice alone hold attention?).

## Files in this skill

- `scripts/video_qa.py`: the checker (plan layer and pixel layer).
- `scripts/make_sheets.py`: one frame every 3 seconds, contact sheets of 30.
- `scripts/tags_to_rules.py`: tags to mix and worst gaps.
- `data/long-video-spec.json`: the rules (29 scored rules and 10 cadence rules).
- `references/labels.md`, `rules.md`, `timeline-format.md`, `voice-rules.md`, `character-and-background-rules.md`, `what-we-learned.md`.
- `examples/`: sample timeline, sample tags, a real report and console output of each layer, and a sample report of a first video that scored 62 out of 100.
- `README.md`: install and quick start for people.

## Requirements

Python 3.9 or newer, numpy, Pillow (only for the contact sheets), ffmpeg and ffprobe on the PATH. With `uv`: `uv run --with numpy python3 scripts/video_qa.py ...` and `uv run --with pillow python3 scripts/make_sheets.py ...` need no install.
