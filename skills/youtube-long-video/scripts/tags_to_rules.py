#!/usr/bin/env python3
"""tags_to_rules.py: turn the 3-second tags of a reference video into its mix and its worst gaps.

  python3 tags_to_rules.py tags.md[:name] [--exclude 282-351]

Prints (1) the share of each tag code, (2) the "within every X seconds, Y must happen" table where X is the
reference's worst gap rounded up to a whole second, and (3) the longest run of each picture type.
Copy the numbers into your own spec (data/long-video-spec.json, "cadence" block) or just keep using the shipped one.
Tag file format: references/labels.md.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_qa as q  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("labels")
    ap.add_argument("--exclude", default="", help="seconds to skip, e.g. 282-351")
    a = ap.parse_args()
    excl = q.parse_ranges(a.exclude)
    *plan, end = q.plan_from_labels(a.labels, 0, 0)
    types, overmap = plan[0], plan[1]
    ts = [i / q.FPS for i in range(len(types))]
    keep = [i for i, t in enumerate(ts) if not any(s <= t < e for s, e in excl)]
    codes_path = a.labels.rsplit(":", 1)[0] if ":" in a.labels and not os.path.exists(a.labels) else a.labels
    print(f"tags cover {q.fmt(end)}; excluded {a.exclude or 'nothing'}\n")
    n = max(1, len(keep))
    print("Mix (share of the time):")
    for t in q.TYPES:
        c = sum(1 for i in keep if types[i] == t)
        print(f"  {t:9} {100 * c / n:5.1f} %")
    print("\nWorst gaps (rounded up = X):")
    rows = [
        ("the picture type changes", lambda i: i > 0 and types[i] != types[i - 1]),
        ("leave the map", lambda i: types[i] not in q.MAP_FAMILY and types[i] != "other" and not (types[i] == "narrator" and overmap[i])),
        ("the narrator appears", lambda i: types[i] == "narrator"),
        ("a story scene appears", lambda i: types[i] == "story"),
    ]
    for name, fn in rows:
        ev = [ts[i] for i in range(len(types)) if fn(i)]
        worst, _ = q.gap_check(ev, 0, end, excl, 1e9)
        print(f"  within every {math.ceil(worst):4d} s: {name}")
    flags = [x == "image" for x in types]
    worst, _ = q.run_check(flags, 0, excl, 1e9)
    print(f"  a full-screen image is held at most {math.ceil(worst)} s")
    print("\nLongest run of each type (s):")
    for t in q.TYPES:
        best = cur = 0
        for x in types:
            cur = cur + 1 if x == t else 0
            best = max(best, cur)
        print(f"  {t:9} {best / q.FPS:5.1f}")
    print("\nNote: tags are every 3 s, so every length is rounded to 3 s (plus or minus 1.5 s).")


if __name__ == "__main__":
    main()
