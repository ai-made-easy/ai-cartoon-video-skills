#!/usr/bin/env python3
"""video_qa.py: a deterministic rhythm and variety check for LONG animated videos (8 to 20 minutes).

It measures; it does not judge taste, story or facts. Two layers, both plain numbers (numpy + ffmpeg pipes):

  plan   what kind of picture is on screen when. Read from a timeline JSON (see references/timeline-format.md)
         or from hand tags (--labels, one code per 3 seconds, see references/labels.md). Gives: share of each
         picture type, longest run of each type, longest stretch without leaving the map, type changes per minute,
         new on-screen events per 10 s, story scenes per window.
  pixel  sampled from the rendered MP4 at 2 fps, 256x144: motion energy, hard cuts per minute, static holds,
         edge density, colourfulness, brightness, contrast.

Every metric is computed in sliding windows (30, 60 and 120 s, half-window step) and compared with the ranges
in the spec (data/long-video-spec.json): PASS inside, WARN within 25 % of the range width outside, FAIL beyond.
A rule FAILs when fewer than 50 % of its windows pass. On top of that come the "cadence" rules: within every
X seconds, Y must happen. Every gap longer than X is reported with its time. Overall score: PASS = 1, WARN = 0.5.

Usage
  python3 video_qa.py --video my.mp4 --timeline timeline.json --out qa-out        # both layers
  python3 video_qa.py --timeline timeline.json --out qa-out                       # plan layer only (before rendering)
  python3 video_qa.py --video my.mp4 --out qa-out                                 # pixel layer only
  python3 video_qa.py --labels tags.md:ours --video my.mp4                         # hand tags instead of a timeline
  python3 video_qa.py --video reference.mp4 --labels tags.md:ref --exclude 282-351 --calibrate --spec my-spec.json
         # writes this video's p10 / p90 into a COPY of the spec as the new targets

Exit code 1 when any rule FAILs, 0 otherwise. Needs: python 3.9+, numpy, ffmpeg + ffprobe on the PATH.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import date

try:
    import numpy as np
except ImportError:  # pragma: no cover
    sys.exit("numpy is required: pip install numpy   (or: uv run --with numpy python video_qa.py ...)")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SPEC = os.path.join(os.path.dirname(HERE), "data", "long-video-spec.json")
FPS = 2.0                 # analysis sampling rate (samples per second)
W, H = 256, 144           # analysis frame size
TYPES = ["map", "narrator", "story", "image", "card", "text"]
# tag codes (references/labels.md) -> picture types
LABEL_TYPES = {"M": "map", "C": "card", "NG": "narrator", "NW": "narrator", "ND": "narrator", "S": "story",
               "P": "image", "T": "text", "O": "other"}
MAP_FAMILY = {"map", "card"}   # a narrator standing over a map also counts (over_map flag)


# ---------------------------------------------------------------- helpers
def need_tool(name):
    if not shutil.which(name):
        sys.exit(f"{name} not found on the PATH. Install ffmpeg (it brings ffprobe): https://ffmpeg.org/download.html")


def ffprobe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        sys.exit(f"ffprobe could not read the duration of {path}")


def windows(start, end, size):
    step = size / 2
    t = start
    while t + size <= end + 1e-6:
        yield (t, t + size)
        t += step


def fmt(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def judge(v, lo, hi):
    if v is None or (lo is None and hi is None):
        return "N/A"
    lo = -math.inf if lo is None else lo
    hi = math.inf if hi is None else hi
    if lo <= v <= hi:
        return "PASS"
    width = (hi - lo) if math.isfinite(hi - lo) else max(abs(lo if math.isfinite(lo) else hi), 1e-9)
    slack = 0.25 * width
    return "WARN" if (lo - slack) <= v <= (hi + slack) else "FAIL"


def excluded(a, b, excl):
    """window overlaps an excluded range by more than half"""
    return any(min(b, e) - max(a, s) > (b - a) / 2 for s, e in excl)


def parse_ranges(s):
    out = []
    for part in (s or "").split(","):
        if part.strip():
            a, b = part.split("-")
            out.append((float(a), float(b)))
    return out


# ---------------------------------------------------------------- plan layer
def load_timeline(tl):
    tl = tl if isinstance(tl, dict) else json.load(open(tl))
    shots = tl.get("shots")
    if not shots:
        sys.exit('timeline needs a "shots" list (see references/timeline-format.md)')
    for i, s in enumerate(shots):
        for k in ("start", "dur", "type"):
            if k not in s:
                sys.exit(f'shot {i} has no "{k}" (see references/timeline-format.md)')
        if s["type"] not in TYPES + ["other"]:
            sys.exit(f'shot {i}: unknown type "{s["type"]}"; use one of {TYPES + ["other"]}')
    return tl


def plan_from_timeline(tl, start, end):
    """per 0.5 s: (types, over_map flags, sorted event times in s, story scenes)"""
    tl = load_timeline(tl)
    if not end:
        end = max(s["start"] + s["dur"] for s in tl["shots"])
    n = int((end - start) * FPS)
    types, overmap, events, scenes = ["other"] * n, [False] * n, [], []

    def ev(t):
        if start <= t < end:
            events.append(t)

    for s in tl["shots"]:
        t0, d, typ = s["start"], s["dur"], s["type"]
        a = max(0, int((t0 - start) * FPS))
        b = min(n, int(math.ceil((t0 + d - start) * FPS)))
        om = bool(s.get("over_map")) and typ == "narrator"
        for i in range(a, b):
            types[i], overmap[i] = typ, om
        ev(t0)  # a shot starting is itself something new
        for e in s.get("events", []) or []:
            ev(t0 + e)
        if typ == "story":
            scenes.append({"t": t0, "dur": d, "cast": s.get("cast", 0)})
    return types, overmap, sorted(events), scenes


def plan_from_labels(spec_arg, start, end):
    """spec_arg = 'file[:name]'. The file either has a ```labels block with lines '<name> <minute> <codes...>' (use
    name to pick the video) or is just whitespace-separated codes, one per 3 seconds."""
    path, who = (spec_arg.rsplit(":", 1) + [None])[:2] if ":" in spec_arg and not os.path.exists(spec_arg) else (spec_arg, None)
    text = open(path).read()
    m = re.search(r"```labels\n(.*?)```", text, re.S)
    codes = []
    if m:
        for line in m.group(1).strip().splitlines():
            parts = line.split(None, 2)
            if len(parts) == 3 and (who is None or parts[0] == who):
                codes += parts[2].split()
    else:
        codes = text.split()
    bad = [c for c in codes if c not in LABEL_TYPES]
    if not codes or bad:
        sys.exit(f"label file problem: no codes, or unknown codes {sorted(set(bad))}; allowed {sorted(LABEL_TYPES)}")
    step = 3.0
    if not end:
        end = len(codes) * step
    n = int((end - start) * FPS)
    types, overmap = [], []
    for i in range(n):
        t = start + i / FPS
        c = codes[min(len(codes) - 1, int(t // step))]
        types.append(LABEL_TYPES[c])
        overmap.append(c == "NG")
    scenes, i = [], 0
    while i < len(codes):
        if codes[i] == "S":
            j = i
            while j < len(codes) and codes[j] == "S":
                j += 1
            if start <= i * step < end:
                scenes.append({"t": i * step, "dur": (j - i) * step})
            i = j
        else:
            i += 1
    return types, overmap, None, scenes, end


def plan_metrics(types, overmap, events, scenes, a, b, start):
    i0, i1 = int((a - start) * FPS), int((b - start) * FPS)
    seg, om = types[i0:i1], overmap[i0:i1]
    seg_ok = [t for t in seg if t != "other"]
    n = max(1, len(seg_ok))
    share = {t: round(sum(1 for x in seg_ok if x == t) / n, 3) for t in TYPES}
    runs = {t: 0.0 for t in TYPES}
    cur, ln, changes = None, 0, 0
    for x in seg + [None]:
        if x == cur:
            ln += 1
        else:
            if cur in runs:
                runs[cur] = max(runs[cur], ln / FPS)
            if cur is not None and x is not None and x != "other" and cur != "other":
                changes += 1
            cur, ln = x, 1
    fam, best = 0, 0
    for x, o in zip(seg, om):
        fam = fam + 1 if (x in MAP_FAMILY or (x == "narrator" and o)) else 0
        best = max(best, fam)
    out = {"share": share, "longest_run_s": runs, "map_family_run_s": best / FPS,
           "type_changes_per_min": round(changes / ((b - a) / 60), 2),
           "story_scenes": sum(1 for s in scenes if a <= s["t"] < b)}
    if events is not None:
        out["events_per_10s"] = round(sum(1 for t in events if a <= t < b) / ((b - a) / 10), 2)
    return out


# ---------------------------------------------------------------- pixel layer
def sample_frames(video, start, end):
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-t", str(end - start), "-i", video,
           "-vf", f"fps={FPS},scale={W}:{H}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def cut_times(video, start, end, thr=0.3):
    cmd = ["ffmpeg", "-nostdin", "-v", "info", "-ss", str(start), "-t", str(end - start), "-i", video, "-an",
           "-vf", f"scale=320:-2,select='gt(scene,{thr})',showinfo", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return [start + float(x) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def frame_stats(fr):
    rgb = fr.astype(np.float32)
    gray = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    gx = np.zeros_like(gray)
    gy = np.zeros_like(gray)
    gx[:, 1:-1] = gray[:, 2:] - gray[:, :-2]
    gy[1:-1, :] = gray[2:, :] - gray[:-2, :]
    edges = float((np.hypot(gx, gy) > 40).mean())
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    rg, yb = r - g, 0.5 * (r + g) - b
    colour = float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))
    return gray, edges, colour, float(gray.mean()), float(gray.std())


def pixel_series(video, start, end):
    frames = sample_frames(video, start, end)
    per, prev = [], None
    for fr in frames:
        gray, edges, colour, bright, contrast = frame_stats(fr)
        if prev is None:
            motion, changed = 0.0, 0.0
        else:
            d = np.abs(gray - prev)
            motion, changed = float(d.mean()), float((d > 12).mean())
        per.append({"motion": motion, "changed": changed, "edges": edges, "colour": colour,
                    "bright": bright, "contrast": contrast})
        prev = gray
    return per, cut_times(video, start, end)


def pixel_metrics(per, cuts, a, b, start):
    i0, i1 = int((a - start) * FPS), int((b - start) * FPS)
    seg = per[i0 + 1:i1] if i0 == 0 else per[i0:i1]
    if not seg:
        return {}
    arr = lambda k: np.array([x[k] for x in seg])
    static = arr("changed") < 0.002
    run = best = 0
    for s in static:
        run = run + 1 if s else 0
        best = max(best, run)
    return {"motion_mean": round(float(arr("motion").mean()), 2),
            "changed_pct_median": round(100 * float(np.median(arr("changed"))), 2),
            "cuts_per_min": round(sum(1 for t in cuts if a <= t < b) / ((b - a) / 60), 2),
            "longest_static_s": round(best / FPS, 1),
            "edge_density": round(float(arr("edges").mean()), 4),
            "colourfulness": round(float(arr("colour").mean()), 1),
            "brightness": round(float(arr("bright").mean()), 1),
            "contrast": round(float(arr("contrast").mean()), 1)}


# ---------------------------------------------------------------- analysis
def analyse(video, start, end, timeline=None, labels=None, excl=(), sizes=(30, 60, 120)):
    plan = None
    if timeline:
        plan = plan_from_timeline(timeline, start, end)
    elif labels:
        *plan, lab_end = plan_from_labels(labels, start, end)
        plan = tuple(plan)
        if not end:
            end = lab_end
    if video:
        dur = ffprobe_duration(video)
        end = min(end, dur) if end else dur
    elif not end:
        end = len(plan[0]) / FPS + start
    # plan lists were built for the (possibly open) range; rebuild exactly for the final end
    if timeline:
        plan = plan_from_timeline(timeline, start, end)
    elif labels:
        *plan, _ = plan_from_labels(labels, start, end)
        plan = tuple(plan)
    res = {"video": video or "(plan only)", "start": start, "end": end, "exclude": list(excl), "windows": {},
           "to_video_end": True}
    if plan:
        res["plan_source"] = timeline or labels
    per, cuts = (pixel_series(video, start, end) if video else (None, []))
    res["cuts"] = cuts
    res["series_changed"] = [round(x["changed"], 4) for x in per] if per else []
    for size in sizes:
        rows = []
        for a, b in windows(start, end, size):
            if excluded(a, b, excl):
                continue
            row = {"a": a, "b": b}
            if per:
                row["pixel"] = pixel_metrics(per, cuts, a, b, start)
            if plan:
                row["plan"] = plan_metrics(*plan, a, b, start)
            rows.append(row)
        res["windows"][str(size)] = rows
    if plan:
        res["plan_whole"] = plan_metrics(*plan, start, end, start)
        res["scenes"] = plan[3]
    res["_plan"] = plan
    res["_acting"] = acting_from_timeline(timeline, start, end) if timeline else None
    return res


# ---------------------------------------------------------------- cadence ("within every X seconds, Y must happen")
def acting_from_timeline(tl, start, end):
    """story shots: times of pose/expression changes and of spoken lines (for the two acting rules)"""
    tl = load_timeline(tl)
    out = []
    for s in tl["shots"]:
        if s["type"] != "story":
            continue
        t0, d = s["start"], s["dur"]
        poses = sorted(t0 + x for x in s.get("poses", []) or [])
        lines = sorted(t0 + x for x in s.get("lines", []) or [])
        if t0 + d > start and t0 < end:
            out.append({"t0": t0, "t1": t0 + d, "poses": poses, "lines": lines})
    return out


def _eff(excl):
    return lambda t: t - sum(max(0.0, min(t, e) - s0) for s0, e in excl)


def gap_check(times, start, end, excl, every):
    """largest gap between events (excluded spans do not count); every gap > every is a failure"""
    f = _eff(excl)
    edges = [x for s0, e in excl for x in (s0, e) if start < x < end]
    pts = [start] + sorted(set([t for t in times if start < t < end and not any(s0 <= t < e for s0, e in excl)] + edges)) + [end]
    worst, fails = 0.0, []
    for a, b in zip(pts, pts[1:]):
        g = f(b) - f(a)
        worst = max(worst, g)
        if g > every + 1e-6:
            fails.append(f"{fmt(a)}-{fmt(b)} ({g:.1f} s)")
    return round(worst, 1), fails


def run_check(flags, start, excl, every):
    """longest run of True samples (0.5 s each) must be <= every"""
    worst, fails, i = 0.0, [], 0
    while i < len(flags):
        if flags[i]:
            j = i
            while j < len(flags) and flags[j]:
                j += 1
            ln = (j - i) / FPS
            a = start + i / FPS
            if not any(s0 <= a < e for s0, e in excl):
                worst = max(worst, ln)
                if ln > every + 1e-6:
                    fails.append(f"{fmt(a)}-{fmt(a + ln)} ({ln:.1f} s)")
            i = j
        else:
            i += 1
    return round(worst, 1), fails


def cadence(res, spec, excl):
    start, end = res["start"], res["end"]
    if res.get("to_video_end"):  # the last seconds (subscribe ending) are exempt; set skip_end_s to 0 to switch off
        end -= spec.get("cadence", {}).get("skip_end_s", 0)
    plan = res.get("_plan")
    changed = res.get("series_changed")
    cuts = res.get("cuts", [])
    stimes = [start + i / FPS for i in range(len(changed or []))]
    out = []
    for r in spec.get("cadence", {}).get("rules", []):
        k, X = r["kind"], r["every_s"]
        val, fails, na = None, [], None
        if k == "new" and not changed and not (plan and plan[2]):
            na = "needs a video or a timeline"
        elif k == "new":
            ev = list(cuts)
            ev += [t for t, c in zip(stimes, changed or []) if c >= r.get("pixel_changed", 0.01)]
            if plan and plan[2]:
                ev += plan[2]
            val, fails = gap_check(ev, start, end, excl, X)
        elif k == "motion":
            if not changed:
                na = "needs a video (pixel layer)"
            else:
                ev = list(cuts) + [t for t, c in zip(stimes, changed) if c >= r.get("pixel_changed", 0.002)]
                val, fails = gap_check(ev, start, end, excl, X)
        elif k == "events":
            if not plan or plan[2] is None:
                na = "needs a timeline (hand tags carry no events)"
            else:
                ev, need, t, worst = plan[2], r.get("min_events", 3), start, None
                while t + X <= end + 1e-6:
                    if not any(min(t + X, e) - max(t, s0) > 0 for s0, e in excl):
                        n = sum(1 for x in ev if t <= x < t + X)
                        worst = n if worst is None else min(worst, n)
                        if n < need:
                            fails.append(f"{fmt(t)}-{fmt(t + X)} ({n})")
                    t += 1.0
                val = worst
        elif k in ("typechange", "offmap", "narrator", "story"):
            if not plan:
                na = "needs a timeline or hand tags"
            else:
                types, overmap = plan[0], plan[1]
                ts = [start + i / FPS for i in range(len(types))]
                if k == "typechange":
                    ev = [ts[i] for i in range(1, len(types)) if types[i] != types[i - 1] and "other" not in (types[i], types[i - 1])]
                elif k == "offmap":
                    ev = [t for t, x, o in zip(ts, types, overmap) if x not in MAP_FAMILY and x != "other" and not (x == "narrator" and o)]
                elif k == "narrator":
                    ev = [t for t, x in zip(ts, types) if x == "narrator"]
                else:
                    ev = [t for t, x in zip(ts, types) if x == "story"]
                val, fails = gap_check(ev, start, end, excl, X)
        elif k == "image_max":
            if not plan:
                na = "needs a timeline or hand tags"
            else:
                val, fails = run_check([x == "image" for x in plan[0]], start, excl, X)
        elif k in ("acting_pose", "acting_line"):
            act = res.get("_acting")
            if act is None:
                na = "needs a timeline"
            elif not act:
                na = "no story scenes in the timeline"
            else:
                worst = 0.0
                for sc in act:
                    ev = sc["poses"] if k == "acting_pose" else sc["lines"]
                    v, f = gap_check(ev, sc["t0"], sc["t1"], excl, X)
                    worst = max(worst, v)
                    fails += f
                val = worst
        status = "N/A" if na else ("PASS" if not fails else "FAIL")
        out.append({"id": r["id"], "text": r["text"], "every_s": X, "worst": val, "status": status,
                    "min": r.get("min_events"), "note": na or "", "fails": fails})
    return out


def add_cadence(checks, cad):
    """cadence rules are hard rules: a FAIL is a FAIL of the video"""
    for c in cad:
        if c["status"] == "N/A":
            continue
        checks.append({"rule": "cadence." + c["id"], "text": "Cadence: " + c["text"], "window": f"every {c['every_s']} s",
                       "value": c["worst"], "range": [c["min"], None] if c.get("min") else [None, c["every_s"]],
                       "status": c["status"], "fails": c["fails"],
                       "score": 1.0 if c["status"] == "PASS" else 0.0, "layer": "cadence"})
    sc = [c.get("score", 1.0 if c["status"] == "PASS" else 0.5 if c["status"] == "WARN" else 0.0) for c in checks]
    return checks, round(100 * sum(sc) / max(1, len(sc)))


def get(d, path):
    for p in path.split("."):
        if d is None:
            return None
        d = d.get(p) if isinstance(d, dict) else None
    return d


def judge_all(res, spec):
    checks = []
    for rule in spec["rules"]:
        size = str(rule.get("window", 60))
        if rule.get("scope") == "whole":
            v = get(res, rule["metric"])
            if v is None:
                continue
            checks.append({"rule": rule["id"], "text": rule["text"], "window": "whole", "value": v,
                           "range": [rule.get("min"), rule.get("max")], "status": judge(v, rule.get("min"), rule.get("max")),
                           "fails": [], "layer": "plan"})
            continue
        vals, fails, counts = [], [], {"PASS": 0, "WARN": 0, "FAIL": 0}
        for row in res["windows"].get(size, []):
            v = get(row, rule["metric"])
            if v is None:
                continue
            st = judge(v, rule.get("min"), rule.get("max"))
            if st == "N/A":
                continue
            counts[st] += 1
            vals.append(v)
            if st != "PASS":
                fails.append(f"{fmt(row['a'])}-{fmt(row['b'])} {st} ({v})")
        if not vals:
            continue
        total = sum(counts.values())
        score = (counts["PASS"] + 0.5 * counts["WARN"]) / total
        status = "PASS" if score >= 0.8 else ("WARN" if score >= 0.5 else "FAIL")
        checks.append({"rule": rule["id"], "text": rule["text"], "window": size + " s", "value": round(float(np.median(vals)), 3),
                       "range": [rule.get("min"), rule.get("max")], "status": status, "windows": counts,
                       "score": round(score, 2), "fails": fails, "layer": rule["metric"].split(".")[0]})
    sc = [c.get("score", 1.0 if c["status"] == "PASS" else 0.5 if c["status"] == "WARN" else 0.0) for c in checks]
    return checks, round(100 * sum(sc) / max(1, len(sc)))


def report_md(res, checks, score, title):
    L = [f"# Video QA: {title}", "", f"`{res['video']}` · {fmt(res['start'])}-{fmt(res['end'])}"
         + (f" · plan from `{res.get('plan_source')}`" if res.get("plan_source") else " · pixel layer only")
         + (f" · excluded {res['exclude']}" if res["exclude"] else ""), "", f"**Overall score: {score} / 100**", ""]
    if res.get("plan_whole"):
        pw = res["plan_whole"]
        L += ["Whole range: " + ", ".join(f"{k} {round(100 * v)} %" for k, v in pw["share"].items())
              + f"; story scenes {pw['story_scenes']}; longest map-family stretch {pw['map_family_run_s']:.0f} s", ""]
    if res.get("cadence"):
        L += ["## Cadence (hard rules: within every X seconds, Y must happen)", "", "| Rule | Every | Worst gap | Status |", "|---|---|---|---|"]
        for c in res["cadence"]:
            L.append(f"| {c['text']} | {c['every_s']} s | {c['worst'] if c['worst'] is not None else '-'} | **{c['status']}** {c['note']} |")
        L += ["", "## All rules", ""]
    L += ["| Rule | Window | Median | Target | Status | Windows P/W/F |", "|---|---|---|---|---|---|"]
    for c in checks:
        w = c.get("windows", {})
        L.append(f"| {c['text']} | {c['window']} | {c['value']} | {c['range'][0]}-{c['range'][1]} | **{c['status']}** | "
                 f"{w.get('PASS', '')}/{w.get('WARN', '')}/{w.get('FAIL', '')} |")
    L += ["", "## Windows that miss the target"]
    for c in checks:
        if c["fails"]:
            L.append(f"- **{c['text']}**: " + "; ".join(c["fails"][:40]) + (" ..." if len(c["fails"]) > 40 else ""))
    return "\n".join(L) + "\n"


def calibrate(spec, res, label):
    """this (reference) video's p10 / p50 / p90 per window -> the targets of every rule marked with 'calibrate'"""
    for rule in spec["rules"]:
        if not rule.get("calibrate"):
            continue
        size = str(rule.get("window", 60))
        vals = [get(r, rule["metric"]) for r in res["windows"].get(size, [])]
        vals = [v for v in vals if v is not None]
        if not vals:
            continue
        p10, p50, p90 = (round(float(np.percentile(vals, p)), 3) for p in (10, 50, 90))
        rule["reference"] = {"p10": p10, "p50": p50, "p90": p90, "n": len(vals)}
        mode = rule.get("calibrate")
        if mode == "low":
            rule["min"] = p10
        elif mode == "high":
            rule["max"] = p90
        else:
            rule["min"], rule["max"] = p10, p90
    spec["calibration"] = {"source": label, "date": str(date.today())}
    return spec


def finish(res, spec, excl):
    checks, score = judge_all(res, spec)
    res["cadence"] = cadence(res, spec, excl)
    checks, score = add_cadence(checks, res["cadence"])
    res["checks"], res["score"] = checks, score
    res.pop("_plan", None)
    res.pop("_acting", None)
    return checks, score


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", help="the rendered MP4 (pixel layer). Omit it to check the plan only.")
    ap.add_argument("--timeline", help="timeline JSON (plan layer); format in references/timeline-format.md")
    ap.add_argument("--labels", help="hand tags instead of a timeline: file[:name]; see references/labels.md")
    ap.add_argument("--spec", default=DEFAULT_SPEC, help="rules JSON (default: ../data/long-video-spec.json)")
    ap.add_argument("--out", default="qa-out", help="folder for qa.md and qa.json (default ./qa-out)")
    ap.add_argument("--start", type=float, default=0, help="first second to check")
    ap.add_argument("--end", type=float, default=0, help="last second to check (0 = whole video)")
    ap.add_argument("--exclude", default="", help="seconds to skip, e.g. 282-351 (a sponsor read)")
    ap.add_argument("--calibrate", action="store_true",
                    help="write this video's p10-p90 into the spec as the new targets (use a COPY via --spec)")
    a = ap.parse_args()
    if not (a.video or a.timeline or a.labels):
        ap.error("give --video, or --timeline / --labels for the plan layer only")
    if a.video:
        need_tool("ffmpeg")
        need_tool("ffprobe")
    spec = json.load(open(a.spec))
    excl = parse_ranges(a.exclude)
    res = analyse(a.video, a.start, a.end, a.timeline, a.labels, excl)
    if a.calibrate:
        label = f"{os.path.basename(a.video or a.labels or a.timeline)} {fmt(a.start)}-{fmt(res['end'])} excl {a.exclude or '-'}"
        spec = calibrate(spec, res, label)
        json.dump(spec, open(a.spec, "w"), indent=1, ensure_ascii=False)
        print(f"targets written to {a.spec}")
    checks, score = finish(res, spec, excl)
    os.makedirs(a.out, exist_ok=True)
    stem = "qa" if a.video else "qa-plan"
    json.dump(res, open(os.path.join(a.out, stem + ".json"), "w"), indent=1)
    title = os.path.basename(a.video or a.timeline or a.labels)
    open(os.path.join(a.out, stem + ".md"), "w").write(report_md(res, checks, score, title))
    print(f"score {score}/100 -> {os.path.join(a.out, stem + '.md')}")
    for c in checks:
        if c["status"] != "PASS":
            print(f"{c['status']:5} {c['text']}: {c['value']} (target {c['range'][0]}-{c['range'][1]})")
    sys.exit(1 if any(c["status"] == "FAIL" for c in checks) else 0)


if __name__ == "__main__":
    main()
