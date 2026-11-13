# Video QA: clip3min_480p.mp4

`clip3min_480p.mp4` · 0:00-3:00 · pixel layer only

**Overall score: 25 / 100**

## Cadence (hard rules: within every X seconds, Y must happen)

| Rule | Every | Worst gap | Status |
|---|---|---|---|
| something new on screen (a plan event, a cut, or >= 1 % of pixels changing in 0.5 s) | 4 s | 10.0 | **FAIL**  |
| at least 3 new on-screen events (pins, labels, cards, poses, lines, counters) in any 10 s | 10 s | - | **N/A** needs a timeline (hand tags carry no events) |
| a camera move or a cut (no frozen picture) | 4 s | 3.0 | **PASS**  |
| the picture type changes (map / narrator / story scene / image / card / text) | 28 s | - | **N/A** needs a timeline or hand tags |
| leave the map at least once | 40 s | - | **N/A** needs a timeline or hand tags |
| the narrator appears | 60 s | - | **N/A** needs a timeline or hand tags |
| a cartoon story scene appears | 140 s | - | **N/A** needs a timeline or hand tags |
| a full-screen image ends (max hold) | 9 s | - | **N/A** needs a timeline or hand tags |
| inside a story scene: a pose or expression change | 3 s | - | **N/A** needs a timeline |
| inside a story scene: a spoken line or bubble appears | 6 s | - | **N/A** needs a timeline |

## All rules

| Rule | Window | Median | Target | Status | Windows P/W/F |
|---|---|---|---|---|---|
| Motion energy (mean frame difference, 0-255) | 60 s | 1.99 | 8.506-15.83 | **FAIL** | 0/0/5 |
| Pixels changed per 0.5 s, median % | 60 s | 0.25 | 4.092-29.028 | **WARN** | 0/5/0 |
| Hard cuts per minute | 60 s | 0.0 | 3.6-8.0 | **FAIL** | 0/0/5 |
| Longest static hold (s) | 60 s | 2.5 | None-2.5 | **PASS** | 5/0/0 |
| Visual complexity (edge density) | 60 s | 0.082 | 0.141-0.204 | **FAIL** | 0/0/5 |
| Colourfulness (Hasler-Suesstrunk) | 60 s | 18.3 | 49.6-74.0 | **FAIL** | 0/0/5 |
| Mean brightness (0-255) | 60 s | 31.8 | 125.96-168.96 | **FAIL** | 0/0/5 |
| Contrast (luma std) | 60 s | 31.9 | 37.94-51.44 | **FAIL** | 0/0/5 |
| Cadence: something new on screen (a plan event, a cut, or >= 1 % of pixels changing in 0.5 s) | every 4 s | 10.0 | None-4 | **FAIL** | // |
| Cadence: a camera move or a cut (no frozen picture) | every 4 s | 3.0 | None-4 | **PASS** | // |

## Windows that miss the target
- **Motion energy (mean frame difference, 0-255)**: 0:00-1:00 FAIL (1.73); 0:30-1:30 FAIL (2.18); 1:00-2:00 FAIL (2.06); 1:30-2:30 FAIL (1.78); 2:00-3:00 FAIL (1.99)
- **Pixels changed per 0.5 s, median %**: 0:00-1:00 WARN (0.01); 0:30-1:30 WARN (0.25); 1:00-2:00 WARN (0.65); 1:30-2:30 WARN (0.29); 2:00-3:00 WARN (0.05)
- **Hard cuts per minute**: 0:00-1:00 FAIL (0.0); 0:30-1:30 FAIL (0.0); 1:00-2:00 FAIL (0.0); 1:30-2:30 FAIL (0.0); 2:00-3:00 FAIL (0.0)
- **Visual complexity (edge density)**: 0:00-1:00 FAIL (0.0827); 0:30-1:30 FAIL (0.0816); 1:00-2:00 FAIL (0.0815); 1:30-2:30 FAIL (0.0768); 2:00-3:00 FAIL (0.0964)
- **Colourfulness (Hasler-Suesstrunk)**: 0:00-1:00 FAIL (11.5); 0:30-1:30 FAIL (18.3); 1:00-2:00 FAIL (20.2); 1:30-2:30 FAIL (14.5); 2:00-3:00 FAIL (23.8)
- **Mean brightness (0-255)**: 0:00-1:00 FAIL (28.4); 0:30-1:30 FAIL (31.8); 1:00-2:00 FAIL (33.3); 1:30-2:30 FAIL (30.5); 2:00-3:00 FAIL (33.9)
- **Contrast (luma std)**: 0:00-1:00 FAIL (31.3); 0:30-1:30 FAIL (32.6); 1:00-2:00 FAIL (31.9); 1:30-2:30 FAIL (28.2); 2:00-3:00 FAIL (33.5)
- **Cadence: something new on screen (a plan event, a cut, or >= 1 % of pixels changing in 0.5 s)**: 0:04-0:10 (5.0 s); 0:16-0:26 (10.0 s); 0:56-1:01 (4.5 s); 1:34-1:40 (6.0 s); 2:20-2:25 (4.5 s)
