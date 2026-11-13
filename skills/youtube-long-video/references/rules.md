# The rules in plain words, with the numbers

These come from `data/long-video-spec.json`. They were measured on the first 15 minutes of one reference video (sponsor read excluded). They describe what that video does. Change them if your reference is different.

## The mix (share of the whole video)

- Maps: 28 to 42 percent.
- Narrator character on screen: 30 to 40 percent.
- Cartoon story scenes: 15 to 22 percent, roughly one a minute.
- Full-screen photos or paintings: 3 to 10 percent.
- Small photo cards left on a map: 5 percent or less.
- The longest stretch without leaving the map (a map, a card on a map, or the narrator over a map): 40 seconds.

Per minute: the map share is 13 to 56 percent, the narrator 18 to 59 percent, small cards at most 10 percent, full-screen images at most 30 percent, text cards at most 20 percent. In any 2 minutes there is at least 1 story scene and story is at least 8 percent.

## How long one picture type may stay (per minute window)

Map 30 s, narrator beat 21 s, story scene 20 s, full-screen image 9 s, small card 6 s. The picture type changes 4 to 9 times a minute. At least 3 new on-screen events in any 10 seconds (timeline only).

## Cadence: within every X seconds, Y must happen

X is the reference's worst gap rounded up, so the reference passes its own test. Every gap that is too long is listed with its time.

| Within every | This must happen |
|---|---|
| 4 s | something new on screen: a plan event, a cut, or at least 1 percent of the pixels changing in half a second |
| 10 s | at least 3 new on-screen events (pins, labels, cards, poses, lines, counters) |
| 4 s | a camera move or a cut (no frozen picture) |
| 28 s | the picture type changes |
| 40 s | leave the map at least once |
| 60 s | the narrator appears |
| 140 s | a cartoon story scene appears |
| 9 s | a full-screen image ends (maximum hold) |
| 3 s | inside a story scene: a pose or expression change |
| 6 s | inside a story scene: a spoken line or bubble appears |

The last 35 seconds of a whole video (a subscribe ending) are exempt. Change `skip_end_s` in the spec to alter that.

## Pixel rules (rendered MP4, sampled at 2 frames a second, 256 x 144, per 60 s window)

| What | Range |
|---|---|
| Motion energy (mean frame difference, 0 to 255) | 8.5 to 15.8 |
| Pixels changed per half second, median | 4 to 29 percent |
| Hard cuts per minute | 3.6 to 8 |
| Longest static hold | at most 2.5 s |
| Visual complexity (edge density) | 0.141 to 0.204 |
| Colourfulness (Hasler and Suesstrunk measure) | 50 to 74 |
| Mean brightness (0 to 255) | 126 to 169 |
| Contrast (standard deviation of brightness) | 38 to 51 |

## How the verdict is made

For each window (30, 60 or 120 seconds, moving by half a window) the value is compared with the range. Inside: PASS. Outside by up to a quarter of the range width: WARN. Further: FAIL. A rule FAILs when fewer than half of its windows pass, WARNs from 50 to 80 percent, and PASSes at 80 percent or more. Cadence rules are hard: any gap too long is a FAIL. The score is the average of the rules with PASS = 1, WARN = 0.5, FAIL = 0.

## Honest note on the numbers

They are one video's behaviour. They are a good first target because a video that holds attention for 15 minutes does these things on purpose, but they are not a proven formula for views or retention.
