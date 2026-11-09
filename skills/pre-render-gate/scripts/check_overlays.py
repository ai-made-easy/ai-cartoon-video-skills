#!/usr/bin/env python3
"""Pre-render gate for any 2D overlay / motion-graphics plan: catch text and timing defects before a render.

    python3 -I scripts/check_overlays.py plan.json [--config zones.json] [--quiet]

The plan is your renderer's *resolved* plan: every overlay already in frames (not "at cue X"). Build the timeline
first, then run this — it is deterministic and takes milliseconds. Exit 0 = clean, 1 = errors. Every ERROR names the
overlay by its index in "overlays" and says what to change.

plan.json:
{
  "fps": 30, "width": 1080, "height": 1920,
  "safe": {"margin": 40, "top": 220, "bottom": 1500},     (all optional)
  "overlays": [
    {"type": "counter", "from": 100, "dur": 60, "label": "LEFT", "value": 3, "y": 250, "size": 132},
    {"type": "stamp",   "from": 300, "until": 380, "text": "AN ISLAND", "y": 980, "size": 47}
  ]
}
`dur` or `until` (end frame) per overlay. Types come from DEFAULT_ZONES; add or override under "zones" in --config.

Defects caught: two overlays of the same band on screen together, text wider than the safe width, text outside the
safe vertical zone, the same text twice at once, a label starting outside its counter. Sleeping on these is how a
draft turns into five 4K renders (see SKILL.md).
"""
import argparse, json, pathlib, sys

DEFAULT_SAFE = {"margin": 40, "top": 220, "bottom": 1500}
DISSOLVE = 8    # a short cross-fade between items is by design; more overlap is a collision

# type -> (default y, height below y). Height None = size + 48 (a stamp).
DEFAULT_ZONES = {
    "counter": {"y": 250, "h": 240},
    "year":    {"y": 250, "h": 300},
    "ribbon":  {"y": 300, "h": 300},
    "hud":     {"y": 240, "h": 80},
    "stamp":   {"y": 760, "h": None},
    "pill":    {"y": 900, "h": 80},
    "label":   {"y": 900, "h": 80},
    "icons":   {"y": 640, "h": 430},
    "stats":   {"y": 560, "h": 470},
    "vs":      {"y": 560, "h": 300},
    "board":   {"y": 560, "h": 440},
}
# text width model: width = chars * per * size + pad  ("=size" / "=0.1size" mean pad scales with size)
DEFAULT_WIDTHS = {
    "stamp":  {"per": 0.68, "pad": 94},
    "pill":   {"per": 0.62, "pad": "=size"},
    "label":  {"per": 0.62, "pad": "=size"},
    "year":   {"per": 0.62, "pad": "=0.1size"},
    "ribbon": {"per": 0.66, "pad": "=size"},
    "hud":    {"per": 0.58, "pad": 80},
}
DEFAULT_SIZES = {"stamp": 72, "pill": 34, "label": 34, "year": 150, "ribbon": 54, "hud": 36, "counter": 132}
# zones whose members must never share the screen (the ones where collisions look broken, not layered)
DEFAULT_TOP = ["counter", "year", "ribbon", "hud"]


def load_config(path):
    cfg = {"zones": dict(DEFAULT_ZONES), "widths": dict(DEFAULT_WIDTHS), "top": list(DEFAULT_TOP)}
    if path:
        extra = json.loads(pathlib.Path(path).read_text())
        if "zones" in extra:
            cfg["zones"].update(extra["zones"])
        if "widths" in extra:
            cfg["widths"].update(extra["widths"])
        if "top" in extra:
            cfg["top"] = list(extra["top"])
    return cfg


def height_of(o, cfg):
    h = cfg["zones"].get(o["type"], {}).get("h", 0)
    return (o.get("size") or DEFAULT_SIZES.get(o["type"], 72)) + 48 if h is None else h


def y_of(o, cfg):
    return o.get("y", cfg["zones"].get(o["type"], {}).get("y", 0))


def width_of(o, cfg, safe_w):
    """(width px, fix suggestion) for the widest piece of the overlay."""
    t, txt = o["type"], o.get("text") or ""
    s = o.get("size") or DEFAULT_SIZES.get(t, 40)
    if t == "counter":
        val = o.get("value") or 0
        val = val[1] if isinstance(val, (list, tuple)) and len(val) > 1 else val
        num = (o.get("prefix") or "") + str(val) + (o.get("suffix") or "")
        lab = o.get("label") or ""
        w_num, per_lab, pad_lab = len(num) * 0.62 * s, 0.70 * 34, 34
        w_lab = len(lab) * per_lab + pad_lab
        if w_lab > w_num:
            if w_lab > safe_w:
                return w_lab, f'shorten "label" to <= {int((safe_w - pad_lab) / per_lab)} characters'
            return w_lab, ""
        if w_num > safe_w:
            return w_num, f'set "size" to <= {int(safe_w / (max(1, len(num)) * 0.62))} or shorten prefix/suffix'
        return w_num, ""
    spec = cfg["widths"].get(t)
    if not spec:
        return 0, ""
    pad = spec["pad"]
    pad = s if pad == "=size" else (0.1 * s if pad == "=0.1size" else pad)
    w = len(txt) * spec["per"] * s + pad
    if w <= safe_w:
        return w, ""
    if pad == s:                                  # pad scales with size: solve for size
        max_size = int(safe_w / (max(1, len(txt)) * spec["per"] + 1))
    else:
        max_size = int((safe_w - pad) / (max(1, len(txt)) * spec["per"]))
    max_chars = int((safe_w - pad) / (spec["per"] * s))
    return w, f'set "size" to <= {max(20, max_size)} or shorten the text to <= {max(1, max_chars)} characters'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--config", help="JSON: {\"zones\": {...}, \"widths\": {...}, \"top\": [...]}")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    plan = json.loads(pathlib.Path(a.plan).read_text())
    cfg = load_config(a.config)
    safe = {**DEFAULT_SAFE, **plan.get("safe", {})}
    width = plan.get("width", 1080)
    safe_w = width - 2 * safe["margin"]
    ovs = plan.get("overlays", [])
    errs, warns = [], []

    for i, o in enumerate(ovs):
        t = o["type"]
        f0 = int(o.get("from", 0))
        f1 = int(o.get("until", f0 + o.get("dur", 0)))
        name = (o.get("text") or o.get("label") or "").strip()
        where = f"overlay #{i} {t} '{name}' (frames {f0}-{f1})"
        if f1 <= f0:
            errs.append(f"{where}: zero length — end it after it starts")
            continue
        y, h = y_of(o, cfg), height_of(o, cfg)
        if y < safe["top"] - 20:
            errs.append(f'{where}: y={y} is above the safe top {safe["top"]}; set "y" to {safe["top"]}')
        if y + h > safe["bottom"] and t not in ("icons", "stats", "board"):
            errs.append(f'{where}: y={y} puts the bottom at {int(y + h)}, past the safe bottom {safe["bottom"]};'
                        f' set "y" to <= {safe["bottom"] - h}')
        w, fix = width_of(o, cfg, safe_w)
        if w > safe_w:
            errs.append(f"{where}: text is ~{int(w)} px wide, {int(w - safe_w)} px past the {safe_w} px safe width — {fix}")
        if t == "counter" and o.get("label") and o.get("labelAt") is not None:
            if not (0 <= o["labelAt"] <= f1 - f0):
                errs.append(f'{where}: labelAt={o["labelAt"]} is outside the counter (0-{f1 - f0})')

    for i, a1 in enumerate(ovs):
        for j in range(i + 1, len(ovs)):
            b1 = ovs[j]
            a0, a2 = int(a1.get("from", 0)), int(a1.get("until", a1.get("from", 0) + a1.get("dur", 0)))
            b0, b2 = int(b1.get("from", 0)), int(b1.get("until", b1.get("from", 0) + b1.get("dur", 0)))
            overlap = min(a2, b2) - max(a0, b0)
            if overlap <= DISSOLVE:
                continue
            ta = (y_of(a1, cfg), y_of(a1, cfg) + height_of(a1, cfg))
            tb = (y_of(b1, cfg), y_of(b1, cfg) + height_of(b1, cfg))
            n1 = f"overlay #{i} {a1['type']} '{(a1.get('text') or a1.get('label') or '')}' (frames {a0}-{a2})"
            n2 = f"overlay #{j} {b1['type']} '{(b1.get('text') or b1.get('label') or '')}' (frames {b0}-{b2})"
            if min(ta[1], tb[1]) - max(ta[0], tb[0]) > 4:
                if a1["type"] in cfg["top"] and b1["type"] in cfg["top"]:
                    errs.append(f"{n1} and {n2} share the top zone for {overlap} frames ({max(a0, b0)}-{min(a2, b2)})."
                                f" Fix: end the earlier one >= {DISSOLVE} frames before the later starts"
                                f" (#{i}: end by frame {b0 - DISSOLVE}) or move one to another y, or chain them.")
                else:
                    warns.append(f"{n1} and {n2} overlap {overlap} frames in a lower zone"
                                 f" ({max(a0, b0)}-{min(a2, b2)}) — check that moment at full size")
            if (a1.get("text") or "").strip() and (a1.get("text") or "").strip() == (b1.get("text") or "").strip():
                errs.append(f"{n1} and {n2} show the same text '{a1.get('text')}' — remove one or reword it")

    if not a.quiet:
        print(f"{a.plan}: {len(ovs)} overlays, safe {safe['top']}-{safe['bottom']}, width {safe_w} px")
        for w in warns:
            print("WARN ", w)
        for e in errs:
            print("ERROR", e)
    if errs:
        print(f"\n{len(errs)} error(s): fix the fields above, rebuild the timeline, run this gate again."
              " Nothing renders until it is clean.")
        sys.exit(1)
    if not a.quiet:
        print("pre-render gate: clean — render once.")


if __name__ == "__main__":
    main()
