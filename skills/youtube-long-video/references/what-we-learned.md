# What we learned

A short page of findings, so you know where the rules come from.

## The story in one paragraph

We made a first 15-minute animated video with maps, photos and a narrator voice. We watched it and it looked fine, picture by picture. Then we watched it next to a long video that people clearly enjoy and it felt flat. We could not say why, so we measured. We took a screenshot every 3 seconds of the first 15 minutes of both videos (300 each), tagged every one by hand, and compared.

## What the comparison showed

Mix of picture types over 15 minutes (percent of the time, sponsor read included in the reference, so its columns add up with 8 percent "other"):

| | Map | Narrator (all forms) | Story scene | Full-screen photo | Small card on map | Text |
|---|---|---|---|---|---|---|
| Reference | 34 | 35 (23 plain wall, 9 over a greyed picture, 3 in a drawn set) | 16 | 4 | 3 | 1 |
| Our first video | 47 | 28 | 0 | 4 | 20 | 0 |

Other differences:

- The reference never stayed on the map more than 39 seconds. Ours stayed 8 minutes 42 seconds by hand tags (268 seconds when measured from the plan; either way, far too long).
- The reference had about 15 cartoon story scenes in 15 minutes, in 11 of the 15 minutes. We had none.
- The reference changed picture 98 times (average 9.2 seconds). We did 137 times (6.6 seconds): more cuts, less variety. Cuts per minute in the pixel layer: the reference 3.6 to 8, ours 2.
- The reference told fewer events, each as a small story. By the 15 minute mark it had got through far less history than we had. Less coverage per minute, more story.
- Our colours were too saturated (colourfulness 84 against the reference's 50 to 74).
- Voice: the reference read at about 129 words a minute with 12.5 semitones of pitch range. Ours was at 173 words a minute with 9.4. Fast and flat.

## What a deterministic check gave us

We turned the comparison into a spec (29 scored rules plus 10 "within every X seconds, Y must happen" rules) and a script. On the same 15 minutes:

- Our first video: 62 out of 100 on the first version of the checker (52 out of 100 when the whole 18-minute plan was checked).
- The reference: 96 out of 100 (94 before the cadence rules were added). It passes because the limits were taken from its own worst gaps; the test is "a video that holds attention passes", so it is not independent evidence that the numbers are right. See the caveats.

`examples/sample-report-first-video-62.md` is the 62 out of 100 report. Most of the points lost were not taste: no story scenes, a stretch with no way out of the map, too many small cards, too few cuts, too much colour.

## What helped most, in order

1. Leave the map often. A map is one of three or four kinds of picture, not the default.
2. Cartoon story scenes about once a minute, with a short line of dialogue, then the narrator delivers the punchline.
3. A narrator character on screen at least once a minute, never on a plain colour.
4. Slow the voice to about 130 words a minute and give it pauses and pitch movement.
5. Something new on screen every few seconds, but not every second: a long video is calm, not frantic.
6. Fewer events, each told as a story.

## Caveats

- One reference video. It shows what one video does. Two or three references would give safer numbers; the script can calibrate on any of them.
- The tags were made by a model looking at contact sheets, with every length rounded to 3 seconds.
- The limits are the reference's worst gaps rounded up. A different good video may have different gaps.
- Nothing here measures whether viewers stay. It describes what a video that works does.
- The checker does not see the story, the facts, the jokes or the drawings. A high score means the rhythm and variety are right; it does not mean the video is good.
