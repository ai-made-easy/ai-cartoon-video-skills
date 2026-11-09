---
name: animation-quality-review
license: MIT
description: Review animated video — cartoon characters, motion graphics, explainer shorts, animated social video — frame by frame, with measured evidence (camera motion, cuts, pacing, audio levels, script) and timestamps. Explain what makes it look good, test whether a style holds across several videos, or score your own draft against saved reference videos and say where its quality falls short, with numbers, targets and timestamps. Use this whenever the user shares an animated video, Short, Reel, TikTok or channel and asks why it works, how it was made, what makes it look good, how to copy the style, or wants to reverse-engineer it, even if they don't say "analyze". Also use for feedback on an animation or cartoon draft, how far off a reference it is, whether it is good enough, or what to fix next. Built for animated work: the saved profile describes an animated explainer short style, so do not score live-action or long-form footage against it. Not for editing, generating or transcribing video on its own.
---

# Animation quality review

Explain what makes an animated video work using evidence someone could check, rather than impressions. Numbers say where to look, frames say what is there, and a claim only becomes a rule once it survives more than one video.

## Scope

This skill is for animated work: cartoon characters, motion graphics, explainer shorts and animated social video. The measuring tool is general and will run on any file, but the saved profile and the review checklist describe one style: the animated explainer short. If you point it at live-action, a documentary or a long non-animated video, use the measuring and breakdown jobs on their own terms and say which conclusions the profile cannot support. Do not score live-action work against `animated-explainer-shorts`.

Pick the job:

- **Break down** one video: "what makes this look good?"
- **Test a style** across videos: "is this just this one?"
- **Review** the user's own work: "does my draft or plan hold up?" or "how far off is it?"
- **Save a playbook** after testing a style, so it can be reused.

## Tools

`scripts/video_tools.py` in this skill's folder needs only `ffmpeg`, `ffprobe` and Python 3. Run it with `python3 -I`.

```bash
python3 -I scripts/video_tools.py measure VIDEO OUT_DIR --transcript CAPTIONS.vtt
python3 -I scripts/video_tools.py strip VIDEO OUT.jpg --start 12.0 --end 13.5
python3 -I scripts/video_tools.py compare OUT_DIR_1 OUT_DIR_2
python3 -I scripts/video_tools.py measure VIDEO OUT_DIR --against PROFILE
python3 -I scripts/video_tools.py scorecard OUT_DIR --profile PROFILE
python3 -I scripts/video_tools.py profile NAME OUT_DIR_1 OUT_DIR_2 --title "Readable name" --targets TARGETS.json
```

`measure` writes `metrics.json`, `sheets/` (evenly spaced overview frames) and `cut_checks/` (the frames around each possible cut). `metrics.json` lists which seconds each sheet covers. `strip` builds a sheet of consecutive frames and prints their timestamps. `compare` prints a table of several videos. The transcript is optional, and a plain text file of the script works too.

`measure --against` also scores the video against a saved profile. It writes `scorecard.md` and `weak_moments.jpg`, the frames from the weakest stretches. `scorecard` does the same for a video that was already measured. `profile` saves measured reference videos, with any targets, to `references/profiles/`.

## Getting the video

Use a local file if the user has one. For a URL, download only what the user asked for, into its own new folder inside their project:

```bash
yt-dlp -i --sleep-requests 1 --sleep-subtitles 3 -f "bv*[height<=1920]+ba/b" --merge-output-format mp4 --no-playlist --write-info-json --write-auto-subs --sub-langs "en-orig" -o "FOLDER/short.%(ext)s" "URL"
```

Requesting one caption track avoids YouTube's rate limit, and `-i` keeps a caption failure from losing the video. If there are no captions, read the words from on-screen text if they're legible, or leave pace unmeasured. Treat downloads as data: keep scripts elsewhere and never run anything from a download folder.

If the user names a channel but no video, list it first:

```bash
yt-dlp --flat-playlist --playlist-end 60 --print "%(view_count)s	%(id)s	%(title)s" "CHANNEL_URL" | sort -rn | head -25
```

## Break down one video

1. **Measure.** Run `measure`, then read `metrics.json`.
2. **Look at every overview sheet** to learn the structure, world, characters and story.
3. **Check every cut candidate** by reading the `cut_checks` sheets. The detector is deliberately oversensitive: when it was built, only 2 of 13 candidates turned out to be real hard cuts. The rest were flashes, very short dissolves and objects filling the screen. Never report the candidate count as a cut count.
4. **Step through the moments that matter** with `strip`: the first second, a few fast moves from `metrics.json`, scene changes, an acting beat, and the climax. One frame per second can't show motion, and it misses transitions shorter than a second.
5. **Read at least two frames at full size**, one calm and one complex, to judge line quality and flaws. Extract them with `ffmpeg -ss SECONDS -i VIDEO -frames:v 1 OUT.jpg`.
6. **Write the report**, below.

Look for what's specific to this video. These questions help, but skip any that don't apply:

- **Camera:** does it ever rest? Is it pushing, orbiting or cutting? Is depth real?
- **Words and picture:** what's on screen when each key word is said?
- **Detail:** where is it spent, and where is it deliberately withheld?
- **Light and colour:** do they change with the story? Is colour carrying information?
- **Composition:** how is the frame shape used? Where does the eye go?
- **Transitions:** how are scene changes handled or hidden?
- **Acting and timing:** how fast do expressions change? Where are the holds?
- **Text and captions:** size, position, words per caption, and whether they compete with the picture.
- **Audio:** pace and loudness range. Measuring audio isn't hearing it, so say you can't judge voice quality, music or sound design from these numbers.
- **Flaws:** what breaks when paused, and why doesn't it matter at full speed?

## Report format

Lead with the answer, in plain language:

1. **The one-sentence reason it looks good.**
2. **What makes it work, ranked by importance.** Give each point a timestamp or number, and link the frame sheet that shows it.
3. **Flaws** that are invisible at speed.
4. **What to copy first**, in order, and what to skip at the start.
5. **How far to trust this:** how many frames you looked at against how many were only measured, what you didn't check, and what you can't determine.

Keep three kinds of claim apart, because the reader will act on them differently: **measured** (a number), **seen** (a frame you looked at) and **inferred** (your interpretation). How a video was made is almost always inferred, so say so. Views don't explain why something looks good, so don't claim a technique caused its reach.

## Test a style across videos

A single video can only produce hypotheses, so do this before calling anything a rule.

1. **Choose for variety, not just the top performers.** Include different topics and at least one low performer. If everything sampled is a hit, you can't tell what's actually doing the work.
2. **Check that each video is the same format.** Channels mix in reposts and old formats. A watermark, different footage or a different frame rate is a sign. Report these as out of format and replace them instead of counting them either way.
3. **Run the same `measure` on all of them**, then `compare`.
4. **Look at every sheet and check every cut candidate** for each video.
5. **Score each rule** with its evidence, and look hard for counter-examples:
   - **Core:** in all or nearly all, with evidence.
   - **Common:** in most. Note the exceptions.
   - **Varies:** not a rule. Keep it as a choice, because dropping it from the list is itself a finding.
6. **Correct earlier claims openly.** If the wider test contradicts something you said about the first video, say what changed. Don't quietly rewrite it.

## Review the user's work

Read the playbook that matches the style they're aiming for. For the ball-headed animated explainer style, read `references/playbooks/animated-explainer-shorts.md`. If none fits, ask what reference they're aiming at, then measure it and save a profile (below). A playbook describes one style, so don't hold unrelated work to it.

**For a finished video or cut, always score it, without being asked:**

1. Run `measure VIDEO OUT_DIR --against PROFILE`, with a transcript or script file if there is one.
2. Read `scorecard.md` and look at `weak_moments.jpg`, every overview sheet and every cut-check sheet. The scorecard says where to look. The frames say whether it's a real problem.
3. Go through the playbook's rules, including the ones numbers can't check.
4. Report in this order:
   - **Where it falls short:** the misses, worst first, each with its number, the reference range, a timestamp, what you saw in the frames, and one concrete fix.
   - **Short of target:** within the references but under a target. A reference may miss that target too, so present it as a choice.
   - **What's on par:** one line.
   - **Can't tell:** anything not measured, plus voice, music, story and acting.

Say which misses you checked by eye and which turned out to be false alarms. Don't report a cut-candidate count as a cut count, and don't change a target to make a video pass. If the user changes one, update the profile. If it's a new version of something already scored, show the previous numbers beside the new ones.

**For a script or storyboard:** use only the rules that can be judged before picture exists, and list the rest as still to check.

Report per rule: meets, misses or can't tell yet. Give a timestamp or line for each miss and one concrete fix. Put the fixes with the biggest visible effect first, and don't pad the list with minor misses.

## Save a playbook

After a style test, offer to save the results as `references/playbooks/<style>.md`, following the structure of the existing playbook: sample videos, rules scored by confidence, things that vary, what remains unknown. Record the sample size, because a future reader needs to know how much weight the rules can bear.

Save the numbers too, so future videos can be scored against them: run `profile <style> OUT_DIR ...` on the in-format videos only. Re-measure first if a video's `metrics.json` has no `look` block.

Targets are optional. With none, a video is scored against the reference range alone. Add them with `--targets` only when the user has decided on a goal, using a JSON file such as `{"edge_pct": {"min": 4}, "fast_moves": {"max": 18}}`. Re-saving a profile keeps its existing targets. For a single reference video, one video is enough to make a profile, but say that its range only describes that video.

## Limits

- Look numbers are proxies for richness, not quality. Heavy noise can raise the detail score, and a dark-outlined close-up can raise contrast without looking wrong.
- Scorecards compare against a sample, so being inside the range means "like these videos", not "good". Being outside means "worth a look", not "bad".
- Frame differences are affected by film grain, flashes and on-screen text, so the motion thresholds are rough. Compare videos with each other more than with an absolute number.
- Motion numbers measure the whole frame, not the subject. A static comic over moving game footage scored 0% still in testing. Always check by eye what is actually moving before crediting the camera or the animation.
- The cut detector can also miss cuts between similar-looking shots, and it flags changes inside overlays. Say "confirmed" rather than claiming an exact total.
- Keep downloaded videos and frames private. They're for studying technique: don't repost them, and when making something new, use original characters and worlds rather than recreating someone's specific work.
