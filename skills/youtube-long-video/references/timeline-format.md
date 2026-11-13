# Timeline format (the plan the checker reads)

A JSON file with a list of shots. Times are in seconds. Shots should follow each other without gaps (a gap counts as "other" and is skipped). See `examples/sample-timeline.json`.

    {
      "shots": [
        {"start": 0,  "dur": 9,  "type": "map", "events": [1, 3, 5, 7]},
        {"start": 9,  "dur": 9,  "type": "narrator", "events": [1, 3, 5, 7]},
        {"start": 18, "dur": 12, "type": "story", "events": [1, 3, 5, 7, 9, 11],
         "poses": [0.5, 2.5, 5, 7.5, 10], "lines": [1, 4.5, 8]},
        {"start": 30, "dur": 8,  "type": "narrator", "over_map": true, "events": [1, 3, 5, 7]}
      ]
    }

Fields of a shot:

- `start`, `dur`: seconds.
- `type`: one of `map`, `narrator`, `story`, `image` (full-screen photo or painting), `card` (a small photo card on a map), `text` (title card, chart, counter), `other` (sponsor read, black).
- `over_map` (narrator only): true when the narrator stands over a map. It counts as time on the map for "leave the map".
- `events`: offsets in seconds from the start of the shot of every new on-screen thing: a pin, a label, a card, a counter, a pose change, a line. The start of a shot is always counted as an event, so you do not need to list it.
- `poses` and `lines` (story shots only): offsets of pose or expression changes and of spoken or written lines. They feed the two acting rules.

A word-timed plan is better: put the events on the words that trigger them (a date, a name, "but"). The checker only needs the times.

Tip: have Claude write the plan from the narration and the voice timings (word times), one shot per sentence group, using the trigger table in `character-and-background-rules.md`.
