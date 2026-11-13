# Tag codes (labels)

Every 3-second screenshot of a video gets exactly one code. The same codes are used for the reference video and for our own video, so the two can be compared.

| Code | Meaning | Becomes plan type |
|---|---|---|
| M | An animated map is the main picture (pins, labels, growing regions, armies are still M) | map |
| NG | A narrator character over a map or picture that is greyed or blurred behind it | narrator, over a map |
| NW | A narrator character on a plain or lightly patterned wall or flat colour | narrator |
| ND | A narrator character inside a drawn place (a room, a ruin, a museum) | narrator |
| S | A cartoon story scene: drawn characters acting in a painted set, often with speech lines | story |
| P | A real photo, painting or artefact filling most of the screen | image |
| C | A photo or painting as a small card on a map (less than about 45 % of the width) | card |
| T | A text card, title card, chart or counter with no map or scene behind it | text |
| O | A sponsor read, ad, logo screen, black frame, subscribe ending, anything else | other (skipped in shares) |

Tie-breaks: choose by what fills most of the frame. A narrator with a portrait card beside him is still a narrator code. A map with a small photo card is C only while the card is on screen; otherwise M.

## How to tag

1. `python3 scripts/make_sheets.py --video v.mp4 --out work/v --end 900` makes frames and contact sheets (30 frames each, 6 x 5, time in the corner).
2. Look at each sheet and use the labelling prompt in SKILL.md (one line of 30 codes per sheet).
3. Join the sheets in order into one file, codes separated by spaces. Fifteen minutes = 300 codes. Tile number k is the picture at k x 3 seconds.

## File formats the scripts accept (`--labels`)

Plain file: just codes separated by spaces or new lines.

    M M M NG NG S S S M M ...

Or a block with a name per video, so reference and ours live in one file. Use `--labels tags.md:ref` or `--labels tags.md:ours`:

    ```labels
    ref 1 M M NG NG S S P P M M ...
    ref 2 M M M NW NW S S S M M ...
    ours 1 M M M M M C C C M M ...
    ```

The second field (the minute) is only for humans; lines of the same name are joined in order.

## Limits of tagging

The tags are every 3 seconds, so every length is rounded to 3 seconds (plus or minus 1.5 s). The model that tags can make mistakes; if a result looks surprising (a story scene at a time you know has none), open that sheet and look yourself. Hand tags carry no "new events" information, so the events rule only works with a timeline.
