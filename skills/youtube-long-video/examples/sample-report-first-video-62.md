# Video QA: my-first-long-video.mp4 (first 15 minutes)

`my-first-long-video.mp4` · 0:00–15:00 · plan from `timeline.json`

**Overall score: 62 / 100**

Whole range: map 48 %, narrator 28 %, story 0 %, image 4 %, card 20 %, text 0 %; story scenes 0; longest map-family stretch 268 s

## Cadence (hard rules: within every X seconds, Y must happen)

| Rule | Every | Worst gap | Status |
|---|---|---|---|
| something new on screen (a plan event, a cut, or >= 1 % of pixels changing in 0.5 s) | 4 s | 2.9 | **PASS**  |
| at least 3 new on-screen events (pins, labels, cards, poses, lines, counters) in any 10 s | 10 s | 2 | **FAIL**  |
| a camera move or a cut (no frozen picture) | 4 s | 3.0 | **PASS**  |
| the picture type changes (map / narrator / story scene / image / card / text) | 28 s | 20.5 | **PASS**  |
| leave the map at least once | 40 s | 268.0 | **FAIL**  |
| the narrator appears | 60 s | 38.0 | **PASS**  |
| a cartoon story scene appears | 140 s | 900.0 | **FAIL**  |
| a full-screen image ends (max hold) | 9 s | 7.0 | **PASS**  |
| inside a story scene: a pose or expression change | 3 s | – | **N/A** no story scenes in the timeline |
| inside a story scene: a spoken line or bubble appears | 6 s | – | **N/A** no story scenes in the timeline |

## All rules

| Rule | Window | Median | Target | Status | Windows P/W/F |
|---|---|---|---|---|---|
| Whole: map share | whole | 0.481 | 0.28–0.42 | **FAIL** | // |
| Whole: Narrator share | whole | 0.283 | 0.3–0.4 | **WARN** | // |
| Whole: story-scene share | whole | 0.0 | 0.15–0.22 | **FAIL** | // |
| Whole: full-screen image share | whole | 0.037 | 0.03–0.1 | **PASS** | // |
| Whole: small photo cards on maps | whole | 0.199 | None–0.05 | **FAIL** | // |
| Whole: longest stretch without leaving the map (s) | whole | 267.5 | None–40 | **FAIL** | // |
| Map share per minute | 60 s | 0.483 | 0.13–0.563 | **PASS** | 23/6/0 |
| Narrator share per minute | 60 s | 0.292 | 0.18–0.59 | **PASS** | 27/2/0 |
| Story-scene share per 2 min | 120 s | 0.0 | 0.084–None | **FAIL** | 0/0/14 |
| Story scenes per 2 min | 120 s | 0.0 | 1–None | **FAIL** | 0/0/14 |
| Small photo-card share per minute | 60 s | 0.175 | None–0.1 | **FAIL** | 1/3/25 |
| Full-screen image share per minute | 60 s | 0.0 | None–0.3 | **PASS** | 29/0/0 |
| Text/chart card share per minute | 60 s | 0.0 | None–0.2 | **PASS** | 29/0/0 |
| Longest map run (s) | 60 s | 11.0 | None–30 | **PASS** | 29/0/0 |
| Longest narrator beat (s) | 60 s | 7.5 | None–21 | **PASS** | 29/0/0 |
| Longest story scene (s) | 60 s | 0.0 | None–20 | **PASS** | 29/0/0 |
| Longest full-screen image (s) | 60 s | 0.0 | None–9 | **PASS** | 29/0/0 |
| Longest small card (s) | 60 s | 5.0 | None–6 | **WARN** | 21/4/4 |
| Longest stretch without leaving the map (s) | 60 s | 60.0 | None–40 | **FAIL** | 9/0/20 |
| Picture-type changes per minute | 60 s | 10.0 | 4.0–9.0 | **WARN** | 14/8/7 |
| New on-screen events per 10 s (timeline only) | 30 s | 15.33 | 3–None | **PASS** | 59/0/0 |
| Motion energy (mean frame difference, 0-255) | 60 s | 12.5 | 8.506–15.83 | **PASS** | 28/0/1 |
| Pixels changed per 0.5 s, median % | 60 s | 28.55 | 4.092–29.028 | **WARN** | 15/11/3 |
| Hard cuts per minute | 60 s | 2.0 | 3.6–8.0 | **FAIL** | 12/2/15 |
| Longest static hold (s) | 60 s | 0.0 | None–2.5 | **PASS** | 29/0/0 |
| Visual complexity (edge density) | 60 s | 0.173 | 0.141–0.204 | **PASS** | 22/6/1 |
| Colourfulness (Hasler-Suesstrunk) | 60 s | 84.1 | 49.6–74.0 | **FAIL** | 2/3/24 |
| Mean brightness (0-255) | 60 s | 129.9 | 125.96–168.96 | **PASS** | 25/2/2 |
| Contrast (luma std) | 60 s | 40.7 | 37.94–51.44 | **WARN** | 17/10/2 |
| Cadence: something new on screen (a plan event, a cut, or >= 1 % of pixels changing in 0.5 s) | every 4 s | 2.9 | None–4 | **PASS** | // |
| Cadence: at least 3 new on-screen events (pins, labels, cards, poses, lines, counters) in any 10 s | every 10 s | 2 | 3–None | **FAIL** | // |
| Cadence: a camera move or a cut (no frozen picture) | every 4 s | 3.0 | None–4 | **PASS** | // |
| Cadence: the picture type changes (map / narrator / story scene / image / card / text) | every 28 s | 20.5 | None–28 | **PASS** | // |
| Cadence: leave the map at least once | every 40 s | 268.0 | None–40 | **FAIL** | // |
| Cadence: the narrator appears | every 60 s | 38.0 | None–60 | **PASS** | // |
| Cadence: a cartoon story scene appears | every 140 s | 900.0 | None–140 | **FAIL** | // |
| Cadence: a full-screen image ends (max hold) | every 9 s | 7.0 | None–9 | **PASS** | // |

## Windows that miss the target
- **Map share per minute**: 0:30-1:30 WARN (0.592); 1:00-2:00 WARN (0.608); 4:30-5:30 WARN (0.608); 5:00-6:00 WARN (0.65); 5:30-6:30 WARN (0.633); 11:00-12:00 WARN (0.617)
- **Narrator share per minute**: 1:00-2:00 WARN (0.175); 5:00-6:00 WARN (0.175)
- **Story-scene share per 2 min**: 0:00-2:00 FAIL (0.0); 1:00-3:00 FAIL (0.0); 2:00-4:00 FAIL (0.0); 3:00-5:00 FAIL (0.0); 4:00-6:00 FAIL (0.0); 5:00-7:00 FAIL (0.0); 6:00-8:00 FAIL (0.0); 7:00-9:00 FAIL (0.0); 8:00-10:00 FAIL (0.0); 9:00-11:00 FAIL (0.0); 10:00-12:00 FAIL (0.0); 11:00-13:00 FAIL (0.0); 12:00-14:00 FAIL (0.0); 13:00-15:00 FAIL (0.0)
- **Story scenes per 2 min**: 0:00-2:00 FAIL (0); 1:00-3:00 FAIL (0); 2:00-4:00 FAIL (0); 3:00-5:00 FAIL (0); 4:00-6:00 FAIL (0); 5:00-7:00 FAIL (0); 6:00-8:00 FAIL (0); 7:00-9:00 FAIL (0); 8:00-10:00 FAIL (0); 9:00-11:00 FAIL (0); 10:00-12:00 FAIL (0); 11:00-13:00 FAIL (0); 12:00-14:00 FAIL (0); 13:00-15:00 FAIL (0)
- **Small photo-card share per minute**: 0:00-1:00 FAIL (0.175); 0:30-1:30 FAIL (0.175); 1:00-2:00 FAIL (0.217); 1:30-2:30 FAIL (0.167); 2:00-3:00 WARN (0.125); 2:30-3:30 FAIL (0.175); 3:00-4:00 FAIL (0.183); 3:30-4:30 FAIL (0.15); 4:00-5:00 FAIL (0.133); 5:00-6:00 WARN (0.108); 5:30-6:30 FAIL (0.167); 6:00-7:00 WARN (0.125); 6:30-7:30 FAIL (0.15); 7:00-8:00 FAIL (0.217); 7:30-8:30 FAIL (0.2); 8:00-9:00 FAIL (0.25); 8:30-9:30 FAIL (0.283); 9:00-10:00 FAIL (0.275); 9:30-10:30 FAIL (0.258); 10:00-11:00 FAIL (0.175); 10:30-11:30 FAIL (0.15); 11:00-12:00 FAIL (0.175); 11:30-12:30 FAIL (0.233); 12:00-13:00 FAIL (0.342); 12:30-13:30 FAIL (0.308); 13:00-14:00 FAIL (0.175); 13:30-14:30 FAIL (0.208); 14:00-15:00 FAIL (0.308)
- **Longest small card (s)**: 0:00-1:00 WARN (6.5); 8:00-9:00 FAIL (9.0); 8:30-9:30 FAIL (10.0); 9:00-10:00 WARN (7.0); 9:30-10:30 WARN (7.0); 11:30-12:30 WARN (7.0); 12:00-13:00 FAIL (8.0); 12:30-13:30 FAIL (8.0)
- **Longest stretch without leaving the map (s)**: 0:00-1:00 FAIL (60.0); 0:30-1:30 FAIL (60.0); 1:00-2:00 FAIL (60.0); 1:30-2:30 FAIL (56.0); 2:30-3:30 FAIL (50.5); 5:00-6:00 FAIL (54.0); 5:30-6:30 FAIL (60.0); 6:00-7:00 FAIL (60.0); 6:30-7:30 FAIL (60.0); 7:00-8:00 FAIL (60.0); 7:30-8:30 FAIL (60.0); 8:00-9:00 FAIL (60.0); 9:00-10:00 FAIL (52.5); 9:30-10:30 FAIL (60.0); 10:00-11:00 FAIL (60.0); 10:30-11:30 FAIL (60.0); 11:00-12:00 FAIL (60.0); 11:30-12:30 FAIL (60.0); 12:00-13:00 FAIL (60.0); 12:30-13:30 FAIL (60.0)
- **Picture-type changes per minute**: 4:00-5:00 WARN (10.0); 6:30-7:30 WARN (10.0); 7:00-8:00 WARN (10.0); 7:30-8:30 WARN (10.0); 8:00-9:00 WARN (10.0); 8:30-9:30 FAIL (11.0); 9:00-10:00 FAIL (12.0); 9:30-10:30 FAIL (13.0); 10:00-11:00 FAIL (12.0); 10:30-11:30 WARN (10.0); 11:00-12:00 WARN (10.0); 11:30-12:30 WARN (10.0); 13:00-14:00 FAIL (12.0); 13:30-14:30 FAIL (13.0); 14:00-15:00 FAIL (13.0)
- **Motion energy (mean frame difference, 0-255)**: 11:00-12:00 FAIL (17.77)
- **Pixels changed per 0.5 s, median %**: 1:00-2:00 WARN (31.76); 1:30-2:30 WARN (31.76); 2:00-3:00 WARN (33.34); 5:00-6:00 WARN (32.99); 5:30-6:30 FAIL (37.72); 6:00-7:00 FAIL (39.12); 6:30-7:30 WARN (32.94); 7:00-8:00 WARN (30.04); 7:30-8:30 WARN (34.44); 8:00-9:00 WARN (35.18); 8:30-9:30 WARN (34.21); 10:30-11:30 WARN (32.68); 11:00-12:00 FAIL (40.15); 11:30-12:30 WARN (34.8)
- **Hard cuts per minute**: 0:00-1:00 FAIL (2.0); 0:30-1:30 FAIL (2.0); 1:00-2:00 FAIL (0.0); 1:30-2:30 FAIL (1.0); 3:00-4:00 FAIL (2.0); 5:00-6:00 FAIL (2.0); 5:30-6:30 FAIL (0.0); 6:00-7:00 FAIL (0.0); 6:30-7:30 FAIL (0.0); 7:00-8:00 FAIL (2.0); 9:00-10:00 WARN (3.0); 9:30-10:30 FAIL (2.0); 10:00-11:00 FAIL (1.0); 10:30-11:30 FAIL (1.0); 12:00-13:00 FAIL (2.0); 12:30-13:30 FAIL (1.0); 14:00-15:00 WARN (3.0)
- **Visual complexity (edge density)**: 0:00-1:00 WARN (0.1372); 3:00-4:00 FAIL (0.1198); 3:30-4:30 WARN (0.1382); 4:30-5:30 WARN (0.1372); 8:30-9:30 WARN (0.2067); 9:00-10:00 WARN (0.2073); 9:30-10:30 WARN (0.2044)
- **Colourfulness (Hasler-Suesstrunk)**: 0:00-1:00 FAIL (94.6); 0:30-1:30 FAIL (87.8); 1:00-2:00 FAIL (84.6); 1:30-2:30 FAIL (88.3); 2:00-3:00 FAIL (86.6); 2:30-3:30 FAIL (96.7); 3:00-4:00 FAIL (98.6); 3:30-4:30 FAIL (86.5); 4:00-5:00 FAIL (84.1); 4:30-5:30 FAIL (83.0); 5:00-6:00 FAIL (80.2); 5:30-6:30 WARN (79.9); 6:00-7:00 FAIL (86.4); 6:30-7:30 FAIL (94.0); 7:00-8:00 FAIL (94.7); 7:30-8:30 FAIL (84.4); 8:00-9:00 FAIL (80.9); 8:30-9:30 WARN (76.0); 9:00-10:00 WARN (76.7); 9:30-10:30 FAIL (83.1); 10:00-11:00 FAIL (82.5); 10:30-11:30 FAIL (83.0); 11:00-12:00 FAIL (84.9); 11:30-12:30 FAIL (85.2); 12:00-13:00 FAIL (83.3); 12:30-13:30 FAIL (82.9); 14:00-15:00 FAIL (83.9)
- **Mean brightness (0-255)**: 3:30-4:30 WARN (116.6); 4:00-5:00 FAIL (97.1); 4:30-5:30 FAIL (109.6); 7:30-8:30 WARN (125.4)
- **Contrast (luma std)**: 0:00-1:00 WARN (37.3); 0:30-1:30 WARN (34.9); 1:00-2:00 WARN (34.7); 1:30-2:30 WARN (36.9); 3:00-4:00 WARN (34.8); 3:30-4:30 FAIL (31.7); 4:00-5:00 FAIL (34.3); 4:30-5:30 WARN (36.8); 5:00-6:00 WARN (35.1); 5:30-6:30 WARN (36.2); 6:00-7:00 WARN (36.8); 6:30-7:30 WARN (35.4)
- **Cadence: at least 3 new on-screen events (pins, labels, cards, poses, lines, counters) in any 10 s**: 1:34-1:44 (2); 1:35-1:45 (2); 1:36-1:46 (2)
- **Cadence: leave the map at least once**: 0:00-2:26 (146.0 s); 2:39-3:30 (51.0 s); 5:06-9:01 (235.5 s); 9:07-13:35 (268.0 s)
- **Cadence: a cartoon story scene appears**: 0:00-15:00 (900.0 s)
