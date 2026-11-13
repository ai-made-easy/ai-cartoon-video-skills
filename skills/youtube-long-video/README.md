# youtube-long-video (free Claude Code skill)

Make long animated videos (8 to 20 minutes, with a narrator character, animated maps and cartoon story scenes) that hold attention, by measuring a reference video you admire and then checking your own video with a script that gives the same answer every time.

This skill is FREE to use and share. It is the long-video companion of a short-animation skill.

## What it is

A first long video often looks fine and still feels flat. The reason is usually rhythm and variety: too long on one kind of picture, too few things happening, a voice that is fast and flat. This skill measures those things.

1. You pick a reference video.
2. Claude takes a screenshot every 3 seconds, tags each one (map, narrator, story scene, photo...), and turns the tags into a mix and into rules like "leave the map within every 40 seconds".
3. Claude writes your plan as a small JSON timeline and the checker tests it before you render anything. After rendering, the checker also looks at the real MP4 (cuts, motion, colour).
4. You fix every FAIL it reports, with exact times, and rerun.

## What you get

- `SKILL.md`: the workflow Claude follows, including the exact labelling prompt.
- `scripts/video_qa.py`: the checker (plan layer and pixel layer). Standalone, no project needed.
- `scripts/make_sheets.py`: one frame every 3 seconds, tiled into contact sheets of 30 (6 x 5) with time labels.
- `scripts/tags_to_rules.py`: from tags to the mix and the worst gaps.
- `data/long-video-spec.json`: the rules: 29 scored rules and 10 "within every X seconds, Y must happen" rules.
- `references/`: tag codes, the rules in plain words with numbers, the timeline format, voice rules, character and background rules, and a short "what we learned".
- `examples/`: a sample timeline, sample tags, real checker output for both layers, and a sample report of a first video that scored 62 out of 100.

## Requirements

- Python 3.9 or newer
- numpy (for `video_qa.py`)
- Pillow (only for `make_sheets.py`)
- ffmpeg and ffprobe on your PATH (the checker uses them to read the MP4; the sheet maker uses ffmpeg)
- Claude Code, to run the workflow (the scripts also work on their own)

Tested on macOS with Python 3.13, numpy 2.5, Pillow 13 and ffmpeg 9. Not tested on Windows or Linux; nothing in the scripts is platform specific.

With `uv` you need no install: `uv run --with numpy python3 scripts/video_qa.py ...` and `uv run --with pillow python3 scripts/make_sheets.py ...`. With pip: `pip install numpy pillow`.

## Install

Copy this folder to your Claude Code skills folder:

    cp -r youtube-long-video ~/.claude/skills/youtube-long-video

(or into `.claude/skills/` inside a project to use it only there). Start Claude Code; the skill is picked up when you ask for something it covers, for example "check my long video's rhythm against this reference".

## 5 minute quick start (no reference needed)

You can try the checker right now on the sample plan:

    cd youtube-long-video
    python3 scripts/video_qa.py --timeline examples/sample-timeline.json --out qa-out
    cat qa-out/qa-plan.md

That runs the plan layer (a few seconds). Now try the pixel layer on any MP4, for example a 3-minute copy of one of your videos:

    ffmpeg -i my-video.mp4 -t 180 -vf scale=854:480 -c:v libx264 -crf 28 -an check.mp4
    python3 scripts/video_qa.py --video check.mp4 --out qa-out
    cat qa-out/qa.md

You will most likely see FAILs on a first video (too few cuts, too little motion). Each line names the rule, your value and the target range. `examples/console-pixel-layer.txt` shows what this looks like.

## How to use it with Claude Code, step by step

1. Tell Claude: "I want to make a long animated video about X and I want it to feel like this reference: <file>." Claude follows `SKILL.md`.
2. Claude runs `make_sheets.py` on the reference (first 15 minutes), reads each contact sheet and tags it with the prompt in `SKILL.md`. You get a tags file and the mix.
3. Claude runs `tags_to_rules.py` and tells you the reference's mix and worst gaps. You can keep the shipped numbers or ask to re-make them from your reference (`--calibrate`).
4. Claude writes your plan (`plan.json`) from your script and runs the plan check. It fixes failures by changing the plan, not the rules, and reruns until the plan layer has no FAIL.
5. You render. Claude runs the checker on the MP4 with the plan and fixes what it reports (cuts, motion, colour, flat stretches).
6. Claude also applies the voice, character and background rules in `references/` while writing the narration and the shots.
7. At the end Claude tells you plainly what the score does and does not mean.

## Limits and honest caveats

- It measures rhythm and variety. It does not judge story, facts, drawings, humour or taste. A video can score 100 and be dull; a video can score low and still be loved.
- The numbers come from one reference video. They describe what that video does, not a law of YouTube, and they say nothing about views or retention.
- The tags are made from screenshots every 3 seconds by a model, so lengths are rounded to 3 seconds and a tag can be wrong. Look at the sheet when a result surprises you.
- The pixel layer works on a 256 x 144 sample at 2 frames a second. It sees motion, cuts, colour and brightness, not meaning.
- The voice rules are advice written down from what worked for us; the skill ships no voice tools.
- Using the reference's own worst gaps as limits means the reference passes its own test by design. That proves the test is consistent, not that the limits are right.

## Where the numbers come from (how these numbers were made)

One reference video, the first 15 minutes, sponsor read excluded. 300 frames, one every 3 seconds, tagged by eye (by a model, with a human check). The mix targets are that video's shares, rounded to a range. The "within every X seconds" values are that video's worst gap of each kind, rounded up to a whole second. The pixel targets are that video's 10th to 90th percentile in sliding 60-second windows (sampled at 2 frames a second, 256 x 144). The acting rules come from short high-frame-rate bursts of its dialogue scenes. Judging: inside the range is PASS, up to a quarter of the range width outside is WARN, beyond is FAIL.

The spec contains only numbers and rule names. To make your own, tag your reference, run `tags_to_rules.py`, then run `video_qa.py --video reference.mp4 --labels tags.txt --calibrate --spec my-spec.json` on a copy of the spec.

## Folder map

    youtube-long-video/
      SKILL.md
      README.md
      scripts/    video_qa.py  make_sheets.py  tags_to_rules.py
      data/       long-video-spec.json
      references/ labels.md  rules.md  timeline-format.md  voice-rules.md
                  character-and-background-rules.md  what-we-learned.md
      examples/   sample-timeline.json  sample-tags.txt  console-plan-layer.txt
                  console-pixel-layer.txt  real-report-plan-layer.md
                  real-report-pixel-layer.md  sample-report-first-video-62.md
