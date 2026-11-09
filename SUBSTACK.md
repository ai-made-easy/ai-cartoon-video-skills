# Substack post

**Title:** I built a skill that measures why an animated Short looks good

**Subtitle:** It is not another prompt pack. It runs ffmpeg, counts motion, checks every cut by eye, and scores your video against six reference shorts. Install it with one npx command.

**Tags:** AI, video, animation, Claude, agents

---

I spent last week making two videos: one about a blue whale, and one about how to create animated videos with Claude. Somewhere in the middle of both, I noticed I kept asking the same question.

*Why does this shot look good?*

And I kept getting the same kind of answer. "It has energy." "The pacing is tight." "The style is consistent." All true, none useful. None of it told me what to change in the next cut.

So I stopped asking for adjectives and built a skill that measures the video instead.

## The shift: measure first, explain second

The skill is called `animation-quality-review`. You give it a video, and it runs `ffmpeg` over every frame. It measures how much the picture changes, how long it holds still, where a hard cut might be, how rich the colour and line work are, how loud the audio is, how fast the words go, and where the silent gaps are.

I did not call it `video-breakdown` because the saved profile describes animated explainer shorts. A general name would promise a live-action review the numbers cannot give. Point it at a long documentary and the measurements still run, but the scoring stops being meaningful. The skill says that out loud rather than letting the number look more certain than it is.

Then it does the part that matters: it puts the frames in front of the model and tells it to look at them.

Numbers say where to look. Frames say what is actually there. A claim only becomes a rule after it survives more than one video.

That last sentence is the whole design. One video can give you a hypothesis. It cannot give you a rule. So the skill has a separate job for testing a style across several videos, and it tells the model to include different topics and at least one low performer. If everything you sample is a hit, you cannot tell what is doing the work.

## What six animated shorts showed

I ran the skill on six animated explainer shorts from one public channel. Same format: 1080×1920, 30fps, under about a minute. A seventh was excluded because it was someone else's comic over game footage, not the same format.

The measured ranges were narrow:

- Near-still frames: 0.3% to 2% of the video.
- Longest hold: 0.1 to 0.33 seconds.
- Words per minute: 199 to 233.
- Loudness: -15.6 to -14 LUFS.
- Loudness range: 1.8 to 3.2 LU.
- Fast camera moves: 1 to 18.
- Silent gaps over 0.15 seconds: none.

That last one is not a typo. No dead air at all.

The same six videos looked quite different in other ways. Two were strongly 3D, with texture and reflections. One was clean, flat linework. One was a single dim room with diagrams. One had 18 fast moves. One had a single fast move and still reached 14.4 million views. So the numbers describe the style. They do not predict reach.

## The one-sentence reason

If I had to reduce the whole study to one line, it is this:

**The picture never rests, and every word being said has an image on screen at the same time.**

That is why the pace works at over 200 words a minute. You are not asked to hold a static frame while the narrator talks. The frame is already moving, and the thing being named is already there.

The second sentence is the one I keep coming back to. "A coin" puts a coin in the rail gap. "No work" shows an empty desk with outlines where the objects used to be. "Hull" shows the ball hitting the hull. The animation is not decoration laid over a script. It is the script, drawn.

There were other rules, and the skill scores them by confidence. Core rules appeared in all six. Common rules appeared in most, with named exceptions. "Varies" is its own category, because dropping something from the list is also a finding. The camera never rests is core. The world does not have to be rich is a choice.

## The cut detector is deliberately wrong

One detail I like: the cut detector is designed to oversensitise.

It flagged 13 candidates across the six videos. When I stepped through the frames, only 2 were real hard cuts. The rest were flashes, very short dissolves, or an object filling the screen for a moment.

The skill tells the model this. It says: never report the candidate count as a cut count. Check every candidate by eye. If you do not, you will write a confident paragraph about a cut that does not exist.

That is the tone of the whole thing. Measure, look, then make a smaller claim than you wanted to.

## What the skill actually does

It has five commands.

- `measure` runs a video through `ffmpeg` and writes `metrics.json`, overview frame sheets, and a sheet around every possible cut.
- `strip` builds a sheet of consecutive frames for one moment, so you can step through a transition that is shorter than a second.
- `compare` prints a table of several measured videos, so a style test is not six separate folders.
- `profile` turns measured reference videos into a named standard, with optional targets.
- `scorecard` scores a video against that standard and writes `scorecard.md` plus a sheet of the weakest moments.

The last one is the one I use most. You point it at a draft and a profile, and it tells you where the draft falls outside the reference range, where it is inside the range but short of a target, and where you cannot tell from the numbers. Each miss gets a timestamp, a reference range, and one concrete fix.

It also refuses to change a target just to make a video pass. If you want a different target, you change the profile. That sounds obvious. It is not, when the model is the one doing the scoring.

## How to install it

It works with Claude Code, Codex, Cursor, Gemini CLI, Windsurf, Cline, Continue.dev and GitHub Copilot. One command:

```bash
npx github:ai-made-easy/ai-cartoon-video-skills
```

The installer detects the agents in your project and writes the skill in each tool's own format. Claude Code gets `.claude/skills/`. Codex, Cursor, Gemini, Windsurf and Cline get the shared `.agents/skills/` copy. Rule-based tools get a short rule that points at the full skill. You can choose tools with `--target` and install into your home directory with `--scope global`.

You need `ffmpeg`, `ffprobe` and Python 3. There are no Python packages to install. `yt-dlp` is optional, and only needed if you want the skill to download a URL for you.

Then start a new session and ask:

> Break down this video and tell me why it looks good.

Or:

> Score my draft against the animated-explainer-shorts profile and tell me what to fix first.

## What it cannot tell you

The skill is honest about its limits, because the model will repeat those limits to you.

It cannot judge voice quality, music or sound design from numbers. It cannot judge story or acting. Look numbers are proxies for richness, not quality: heavy noise can raise the detail score, and a dark-outlined close-up can raise contrast without looking wrong. Motion numbers measure the whole frame, not the subject. A static comic over moving game footage scored 0% still in testing.

And being inside a reference range means "like these videos", not "good". Being outside means "worth a look", not "bad".

That is the point. The skill does not replace your taste. It gives your taste something to push against.

## Why a skill instead of a prompt

A prompt can tell a model to be careful. A skill can give it a tool, a standard, and a procedure for checking its own work.

This one gives the model `ffmpeg`, a profile built from real videos, and a rule that a claim only becomes a rule after more than one video. It also gives it a report format that separates what was measured, what was seen in a frame, and what was inferred. How a video was made is almost always inferred, and the skill says so.

That separation is the difference between a useful review and a confident one that happens to be wrong.

## Try it on something

If you make Shorts, Reels, TikToks or animated explainers, run it on one you like and one you made. The comparison is usually more interesting than either score on its own.

The repository is here:

**https://github.com/ai-made-easy/ai-cartoon-video-skills**

It includes the skill, the six-video playbook, the profile the scorecard uses, the installer, and a short catalog of other video skills worth knowing about — HyperFrames, OneTake, gbro-collage-broll, Claude Animation Base and Lemo-Opuscar.

If you run it and find something the numbers miss, tell me. That is usually where the next rule comes from.
