# Video QA: sample-timeline.json

`(plan only)` · 0:00-3:00 · plan from `sample-timeline.json`

**Overall score: 100 / 100**

Whole range: map 35 %, narrator 38 %, story 20 %, image 7 %, card 0 %, text 0 %; story scenes 3; longest map-family stretch 14 s

## Cadence (hard rules: within every X seconds, Y must happen)

| Rule | Every | Worst gap | Status |
|---|---|---|---|
| something new on screen (a plan event, a cut, or >= 1 % of pixels changing in 0.5 s) | 4 s | 2.5 | **PASS**  |
| at least 3 new on-screen events (pins, labels, cards, poses, lines, counters) in any 10 s | 10 s | 5 | **PASS**  |
| a camera move or a cut (no frozen picture) | 4 s | - | **N/A** needs a video (pixel layer) |
| the picture type changes (map / narrator / story scene / image / card / text) | 28 s | 12.0 | **PASS**  |
| leave the map at least once | 40 s | 14.5 | **PASS**  |
| the narrator appears | 60 s | 22.5 | **PASS**  |
| a cartoon story scene appears | 140 s | 48.5 | **PASS**  |
| a full-screen image ends (max hold) | 9 s | 4.0 | **PASS**  |
| inside a story scene: a pose or expression change | 3 s | 2.5 | **PASS**  |
| inside a story scene: a spoken line or bubble appears | 6 s | 4 | **PASS**  |

## All rules

| Rule | Window | Median | Target | Status | Windows P/W/F |
|---|---|---|---|---|---|
| Whole: map share | whole | 0.35 | 0.28-0.42 | **PASS** | // |
| Whole: Narrator share | whole | 0.383 | 0.3-0.4 | **PASS** | // |
| Whole: story-scene share | whole | 0.2 | 0.15-0.22 | **PASS** | // |
| Whole: full-screen image share | whole | 0.067 | 0.03-0.1 | **PASS** | // |
| Whole: small photo cards on maps | whole | 0.0 | None-0.05 | **PASS** | // |
| Whole: longest stretch without leaving the map (s) | whole | 14.0 | None-40 | **PASS** | // |
| Map share per minute | 60 s | 0.35 | 0.13-0.563 | **PASS** | 5/0/0 |
| Narrator share per minute | 60 s | 0.383 | 0.18-0.59 | **PASS** | 5/0/0 |
| Story-scene share per 2 min | 120 s | 0.2 | 0.084-None | **PASS** | 2/0/0 |
| Story scenes per 2 min | 120 s | 2.0 | 1-None | **PASS** | 2/0/0 |
| Small photo-card share per minute | 60 s | 0.0 | None-0.1 | **PASS** | 5/0/0 |
| Full-screen image share per minute | 60 s | 0.067 | None-0.3 | **PASS** | 5/0/0 |
| Text/chart card share per minute | 60 s | 0.0 | None-0.2 | **PASS** | 5/0/0 |
| Longest map run (s) | 60 s | 9.0 | None-30 | **PASS** | 5/0/0 |
| Longest narrator beat (s) | 60 s | 9.0 | None-21 | **PASS** | 5/0/0 |
| Longest story scene (s) | 60 s | 12.0 | None-20 | **PASS** | 5/0/0 |
| Longest full-screen image (s) | 60 s | 4.0 | None-9 | **PASS** | 5/0/0 |
| Longest small card (s) | 60 s | 0.0 | None-6 | **PASS** | 5/0/0 |
| Longest stretch without leaving the map (s) | 60 s | 14.0 | None-40 | **PASS** | 5/0/0 |
| Picture-type changes per minute | 60 s | 7.0 | 4.0-9.0 | **PASS** | 5/0/0 |
| New on-screen events per 10 s (timeline only) | 30 s | 5.67 | 3-None | **PASS** | 11/0/0 |
| Cadence: something new on screen (a plan event, a cut, or >= 1 % of pixels changing in 0.5 s) | every 4 s | 2.5 | None-4 | **PASS** | // |
| Cadence: at least 3 new on-screen events (pins, labels, cards, poses, lines, counters) in any 10 s | every 10 s | 5 | 3-None | **PASS** | // |
| Cadence: the picture type changes (map / narrator / story scene / image / card / text) | every 28 s | 12.0 | None-28 | **PASS** | // |
| Cadence: leave the map at least once | every 40 s | 14.5 | None-40 | **PASS** | // |
| Cadence: the narrator appears | every 60 s | 22.5 | None-60 | **PASS** | // |
| Cadence: a cartoon story scene appears | every 140 s | 48.5 | None-140 | **PASS** | // |
| Cadence: a full-screen image ends (max hold) | every 9 s | 4.0 | None-9 | **PASS** | // |
| Cadence: inside a story scene: a pose or expression change | every 3 s | 2.5 | None-3 | **PASS** | // |
| Cadence: inside a story scene: a spoken line or bubble appears | every 6 s | 4 | None-6 | **PASS** | // |

## Windows that miss the target
