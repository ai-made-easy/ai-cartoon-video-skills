# Examples

- `sample-timeline.json`: a small, valid 3-minute plan in the timeline format (a sample written for this skill, not from a real video). It passes the plan layer.
- `sample-tags.txt`: the same plan as hand tags (one code per 3 seconds), to try `tags_to_rules.py` and `--labels`.
- `console-plan-layer.txt` and `real-report-plan-layer.md`: the real console output and report of the plan layer on the sample timeline.
- `console-pixel-layer.txt` and `real-report-pixel-layer.md`: the real console output and report of the pixel layer on a 3-minute 480p test clip of a dark, mostly static screen-recording style video. It fails most pixel rules, which is correct: that clip has little motion and almost no cuts. It is here to show what a FAIL report looks like, not as a good example.
- `sample-report-first-video-62.md`: the report of a first 15-minute long video that scored 62 out of 100 (the plan layer plus the pixel layer). Its FAILs are the ones the skill is made to find: no story scenes, a long stretch without leaving the map, too many small cards, too few cuts, too much colour.
