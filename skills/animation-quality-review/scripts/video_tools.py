#!/usr/bin/env python3
"""Measure videos and build frame sheets for close visual review.

  video_tools.py measure VIDEO OUT_DIR [--transcript FILE] [--every SECONDS] [--against PROFILE]
  video_tools.py strip VIDEO OUT.jpg --start SECONDS --end SECONDS [--step FRAMES]
  video_tools.py compare OUT_DIR [OUT_DIR ...]
  video_tools.py profile NAME OUT_DIR [OUT_DIR ...] [--title TEXT] [--targets FILE.json]
  video_tools.py scorecard OUT_DIR [--profile NAME]

measure      numbers and frame sheets for one video
strip        consecutive frames from one moment
compare      a table of several measured videos
profile      saves measured reference videos as a named standard to score against
scorecard    scores a measured video against a profile and says where it falls short

Needs ffmpeg and ffprobe on PATH. No Python packages. The numbers point at things
to look at. They are not verdicts, and cut candidates include many false alarms.
"""
import argparse
import datetime
import json
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path

SHEET_FRAMES = 12          # frames on one overview sheet
MAX_OVERVIEW_FRAMES = 120  # long videos get sampled more thinly, not more sheets
MAX_STRIP_FRAMES = 24
MAX_CUT_CHECKS = 30
NEAR_STILL = 0.5           # mean luma change (0-255) that counts as "not moving"
FAST_MOVE = 25             # mean luma change that counts as a fast camera move
FAST_MOVE_MIN_FRAMES = 3
SIZE_FILTER = "scale=w='if(gt(iw,ih),480,270)':h=-2"
PROFILES = Path(__file__).resolve().parent.parent / "references" / "profiles"
LOOK_RATE = 2              # frames per second sampled for the look numbers
WEAK_STRETCH_SAMPLES = 4   # a stretch must last this many samples (2s) to be reported


def fail(message):
    sys.exit(f"video_tools: {message}")


def run_ffmpeg(args, cwd=None):
    result = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args],
                            capture_output=True, text=True, cwd=cwd)
    return result


def probe(video):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,width,height,avg_frame_rate",
         "-show_entries", "format=duration", "-of", "json", str(video)],
        capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"cannot read {video}: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    picture = next((s for s in streams if s.get("codec_type") == "video"), None)
    if picture is None:
        fail(f"{video} has no video stream")
    num, _, den = picture.get("avg_frame_rate", "0/0").partition("/")
    fps = float(num) / float(den) if float(den or 0) and float(num or 0) else 30.0
    return {
        "width": picture["width"],
        "height": picture["height"],
        "fps": fps,
        "duration": float(data.get("format", {}).get("duration", 0)),
        "has_audio": any(s.get("codec_type") == "audio" for s in streams),
    }


def sheet_layout(info, frame_count):
    """Tall video reads best in wide rows; wide video needs fewer columns."""
    portrait = info["height"] >= info["width"]
    columns = min(6 if portrait else 4, max(frame_count, 1))
    rows = math.ceil(frame_count / columns)
    width = 300 if portrait else 480
    return columns, rows, width


def render_sheet(video, info, select_expr, frame_count, out_path):
    columns, rows, width = sheet_layout(info, frame_count)
    result = run_ffmpeg([
        "-y", "-i", str(video), "-vf",
        f"select='{select_expr}',scale={width}:-2,"
        f"tile={columns}x{rows}:padding=4:color=black",
        "-fps_mode", "passthrough", "-frames:v", "1", "-q:v", "3", str(out_path),
    ])
    if result.returncode != 0:
        fail(f"could not build {out_path}: {result.stderr.strip()[-300:]}")


def metadata_values(path, key):
    values = []
    for line in Path(path).read_text().splitlines():
        if line.startswith(key + "="):
            try:
                values.append(float(line.split("=", 1)[1]))
            except ValueError:
                values.append(0.0)
    return values


def find_runs(values, predicate, min_length):
    """Return (first_index, length) for each run of values matching predicate."""
    runs, start = [], None
    for index, value in enumerate(values + [None]):
        matched = value is not None and predicate(value)
        if matched and start is None:
            start = index
        elif not matched and start is not None:
            if index - start >= min_length:
                runs.append((start, index - start))
            start = None
    return runs


def transcript_words(path):
    seen, words = set(), []
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:")) or "-->" in line:
            continue
        text = re.sub(r"<[^>]*>", "", line).strip()
        if text and text not in seen:
            seen.add(text)
            words.extend(re.sub(r"\[[^\]]*\]", "", text).split())
    return words


def measure_audio(video):
    loud = run_ffmpeg(["-i", str(video), "-af", "loudnorm=print_format=summary",
                       "-vn", "-f", "null", "-"]).stderr

    def value(label):
        match = re.search(rf"Input {label}:\s*(-?[\d.]+)", loud)
        return float(match.group(1)) if match else None

    silence = run_ffmpeg(["-i", str(video), "-af", "silencedetect=noise=-35dB:d=0.15",
                          "-vn", "-f", "null", "-"]).stderr
    return {
        "integrated_lufs": value("Integrated"),
        "true_peak_dbtp": value("True Peak"),
        "loudness_range_lu": value("LRA"),
        "silences_over_0.15s": silence.count("silence_start"),
        "silence_times": [round(float(t), 2) for t in re.findall(r"silence_start: (-?[\d.]+)", silence)],
    }


def measure_look(video, info):
    """How visually rich the picture is: detail, colour, contrast, saturation.

    Frames are scaled to one small size first, so a 4K and a 1080p master score alike.
    These are proxies for richness, not verdicts on quality. A noisy frame can score
    high on detail without looking good, so always check the frames as well.
    """
    width, height = (270, 480) if info["height"] >= info["width"] else (480, 270)
    # Very long videos are sampled more thinly, so memory stays bounded.
    rate = min(LOOK_RATE, 600 / max(info["duration"], 1))

    def frames(extra):
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vf",
                   f"fps={rate},scale={width}:{height},{extra}", "-f", "rawvideo", "-"]
        return subprocess.run(command, capture_output=True, check=True).stdout

    rgb = frames("format=rgb24")
    edges = frames("format=gray,edgedetect=low=0.08:high=0.2")
    size = width * height
    colours, contrast, saturation = [], [], []
    for start in range(0, len(rgb) - size * 3 + 1, size * 3):
        frame = rgb[start:start + size * 3]
        seen, lumas, sat_total = set(), [], 0
        for i in range(0, len(frame), 12):  # every 4th pixel keeps this quick
            r, g, b = frame[i], frame[i + 1], frame[i + 2]
            seen.add((r >> 4, g >> 4, b >> 4))
            lumas.append((r * 3 + g * 6 + b) // 10)
            high, low = max(r, g, b), min(r, g, b)
            sat_total += 0 if high == 0 else (high - low) * 100 // high
        lumas.sort()
        colours.append(len(seen))
        contrast.append(lumas[len(lumas) * 95 // 100] - lumas[len(lumas) * 5 // 100])
        saturation.append(round(sat_total / len(lumas), 1))
    detail = []
    for start in range(0, len(edges) - size + 1, size):
        frame = edges[start:start + size]
        detail.append(round(100 * sum(1 for v in frame if v > 128) / size, 2))
    if not colours or not detail:
        return None
    return {
        "edge_pct": round(statistics.median(detail), 2),
        "colours": statistics.median(colours),
        "contrast": statistics.median(contrast),
        "saturation": round(statistics.median(saturation), 1),
        "samples_per_second": round(rate, 3),
        "samples": {"edge_pct": detail, "colours": colours, "contrast": contrast, "saturation": saturation},
    }


def measure(opts):
    video = Path(opts.video).resolve()
    out = Path(opts.out_dir).resolve()
    (out / "sheets").mkdir(parents=True, exist_ok=True)
    (out / "cut_checks").mkdir(exist_ok=True)
    info = probe(video)
    fps, duration = info["fps"], info["duration"]

    # Run from OUT_DIR so odd characters in the path cannot break ffmpeg's filter syntax.
    run_ffmpeg(["-y", "-i", str(video), "-vf",
                f"{SIZE_FILTER},format=gray,tblend=all_mode=difference,signalstats,"
                "metadata=print:key=lavfi.signalstats.YAVG:file=diffs.txt",
                "-an", "-f", "null", "-"], cwd=out)
    diffs = metadata_values(out / "diffs.txt", "lavfi.signalstats.YAVG")
    if not diffs:
        fail(f"{video} has too few frames to measure")

    run_ffmpeg(["-y", "-i", str(video), "-vf",
                f"{SIZE_FILTER},select='gte(scene,0)',metadata=print:file=scene.txt",
                "-an", "-f", "null", "-"], cwd=out)
    scores = metadata_values(out / "scene.txt", "lavfi.scene_score")

    # diffs[i] compares frame i with frame i+1. A real cut is a one-frame spike;
    # a camera move is a sustained run, so compare each value with its neighbours.
    candidates = []
    for index, value in enumerate(diffs):
        around = diffs[max(0, index - 3):index] + diffs[index + 1:index + 4]
        if around and value > 12 and value > 2.5 * statistics.median(around):
            frame = index + 1
            score = scores[frame] if frame < len(scores) else None
            if candidates and frame - candidates[-1]["frame"] <= 2:
                # One event often spikes on neighbouring frames: keep the stronger one.
                if value <= candidates[-1]["diff"]:
                    continue
                candidates.pop()
            candidates.append({
                "frame": frame,
                "t": round(frame / fps, 2),
                "diff": round(value, 1),
                "scene": None if score is None else round(score, 2),
            })

    check_sheets = []
    checked = candidates[:MAX_CUT_CHECKS]
    for group_index in range(0, len(checked), 3):
        group = checked[group_index:group_index + 3]
        expr = "+".join(f"between(n,{c['frame'] - 2},{c['frame'] + 1})" for c in group)
        name = f"cut_checks/check_{group_index // 3 + 1:02d}.jpg"
        render_sheet(video, info, expr, 4 * len(group), out / name)
        check_sheets.append({"file": name, "candidate_times_s": [c["t"] for c in group]})

    fast_runs = find_runs(diffs, lambda v: v > FAST_MOVE, FAST_MOVE_MIN_FRAMES)
    settle_ratios = []
    for start, length in fast_runs:
        peak = max(diffs[start:start + length])
        after = diffs[start + length + 5:start + length + 20]
        if after:
            settle_ratios.append(round(statistics.mean(after) / peak, 2))
    held_runs = find_runs(diffs, lambda v: v < NEAR_STILL, 3)
    ordered = sorted(diffs)

    every = opts.every or max(1, math.ceil(duration / MAX_OVERVIEW_FRAMES))
    columns, rows, width = sheet_layout(info, SHEET_FRAMES)
    run_ffmpeg(["-y", "-i", str(video), "-vf",
                f"fps=1/{every},scale={width}:-2,tile={columns}x{rows}:padding=4:color=black",
                "-q:v", "3", "sheets/sec_%03d.jpg"], cwd=out)
    sheets = []
    for index, path in enumerate(sorted((out / "sheets").glob("sec_*.jpg"))):
        start = index * SHEET_FRAMES * every
        sheets.append({
            "file": f"sheets/{path.name}",
            "start_s": start,
            "end_s": round(min(start + (SHEET_FRAMES - 1) * every, duration), 1),
        })

    metrics = {
        "video": str(video),
        "duration_s": round(duration, 2),
        "resolution": f"{info['width']}x{info['height']}",
        "fps": round(fps, 2),
        "frames_measured": len(diffs),
        "sheet_seconds_between_frames": every,
        "motion": {
            "mean_frame_diff": round(statistics.mean(diffs), 2),
            "median_frame_diff": round(statistics.median(diffs), 2),
            "p90_frame_diff": round(ordered[int(len(ordered) * 0.9)], 2),
            "pct_frames_near_still": round(100 * sum(v < NEAR_STILL for v in diffs) / len(diffs), 1),
            "longest_hold_frames": max((n for _, n in held_runs), default=0),
            "longest_hold_seconds": round(max((n for _, n in held_runs), default=0) / fps, 2),
            "holds": [{"t": round((s + 1) / fps, 2), "seconds": round(n / fps, 2)} for s, n in held_runs],
        },
        "look": measure_look(video, info),
        "cuts": {
            "candidate_count": len(candidates),
            "candidates": candidates,
            "unchecked_after_cap": max(0, len(candidates) - MAX_CUT_CHECKS),
            "check_sheets": check_sheets,
            "note": "Candidates are unverified. Look at every check sheet before counting one as a cut.",
        },
        "fast_moves": {
            "count": len(fast_runs),
            "runs": [{"t": round((s + 1) / fps, 2), "frames": n} for s, n in fast_runs],
            "in_first_third": sum(1 for s, _ in fast_runs if (s + 1) / fps < duration / 3),
            "settled": sum(r < 0.5 for r in settle_ratios),
            "settle_checked": len(settle_ratios),
        },
        "audio": measure_audio(video) if info["has_audio"] else None,
        "sheets": sheets,
    }
    if opts.transcript:
        if Path(opts.transcript).exists():
            words = transcript_words(opts.transcript)
            metrics["script"] = {
                "word_count": len(words),
                "words_per_minute": round(len(words) * 60 / duration) if duration else None,
                "text": " ".join(words),
            }
        else:
            metrics["script"] = None
            print(f"video_tools: transcript not found: {opts.transcript}", file=sys.stderr)

    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Wrote {out / 'metrics.json'}")
    print(f"{len(sheets)} overview sheets, {len(check_sheets)} cut-check sheets, "
          f"{len(candidates)} cut candidates, {len(fast_runs)} fast moves.")
    if opts.against:
        scorecard(argparse.Namespace(out_dir=str(out), profile=opts.against))


def strip(opts):
    video = Path(opts.video).resolve()
    out_path = Path(opts.out_jpg).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    first = int(opts.start * info["fps"])
    last = int(opts.end * info["fps"])
    if last <= first:
        fail("--end must be later than --start")
    span = last - first + 1
    step = opts.step or max(1, math.ceil(span / 12))
    if math.ceil(span / step) > MAX_STRIP_FRAMES:
        step = math.ceil(span / MAX_STRIP_FRAMES)
        print(f"Too many frames for one sheet, so showing every {step}th frame.")
    frames = list(range(first, last + 1, step))
    render_sheet(video, info, f"between(n,{first},{last})*not(mod(n-{first},{step}))",
                 len(frames), out_path)
    print(f"Wrote {out_path}")
    print("Frames, left to right, top to bottom: "
          + ", ".join(f"{n} ({n / info['fps']:.2f}s)" for n in frames))


def compare(opts):
    header = ["video", "views", "secs", "% still", "longest hold", "median motion",
              "fast moves", "settled", "early", "cut cand.", "wpm", "LUFS", "LRA", "fps"]
    print("| " + " | ".join(header) + " |")
    print("|" + "---|" * len(header))
    for directory in opts.out_dirs:
        path = Path(directory) / "metrics.json"
        if not path.exists():
            print(f"video_tools: skipping {directory}, no metrics.json", file=sys.stderr)
            continue
        m = json.loads(path.read_text())
        views = ""
        name = Path(m["video"]).parent.name
        for info_path in Path(m["video"]).parent.glob("*.info.json"):
            count = json.loads(info_path.read_text()).get("view_count")
            if count:
                views = f"{count / 1e6:.1f}M"
        audio = m.get("audio") or {}
        script = m.get("script") or {}
        fast = m["fast_moves"]
        row = [name, views, m["duration_s"], m["motion"]["pct_frames_near_still"],
               f"{m['motion']['longest_hold_seconds']}s", m["motion"]["median_frame_diff"],
               fast["count"], f"{fast['settled']}/{fast['settle_checked']}",
               fast["in_first_third"], m["cuts"]["candidate_count"],
               script.get("words_per_minute", ""), audio.get("integrated_lufs", ""),
               audio.get("loudness_range_lu", ""), m["fps"]]
        print("| " + " | ".join(str(v) for v in row) + " |")


# ---- Scoring a video against saved reference videos.
def settled_pct(m):
    fast = m["fast_moves"]
    return round(100 * fast["settled"] / fast["settle_checked"]) if fast["settle_checked"] else None


def audio_value(key):
    return lambda m: (m.get("audio") or {}).get(key)


def look_value(key):
    return lambda m: (m.get("look") or {}).get(key)


# key: label, how to read it from metrics.json, which way is good, what it means.
# "range" means the video should sit inside the references. "min" and "max" mean only one side
# counts. "target" means the references don't count, only a saved target does.
MEASURES = {
    "edge_pct": ("Fine detail (edge %)", look_value("edge_pct"), "min", "how much of the frame is fine line and texture"),
    "colours": ("Colours per frame", look_value("colours"), "min", "distinct colours, after grouping similar shades"),
    "contrast": ("Contrast", look_value("contrast"), "range", "brightness spread between darkest and lightest parts"),
    "saturation": ("Saturation", look_value("saturation"), "range", "average colour strength"),
    "median_motion": ("Median motion", lambda m: m["motion"]["median_frame_diff"], "range", "how much the picture changes per frame"),
    "pct_still": ("Near-still frames %", lambda m: m["motion"]["pct_frames_near_still"], "max", "frames where almost nothing moves"),
    "longest_hold": ("Longest hold (s)", lambda m: m["motion"]["longest_hold_seconds"], "max", "the longest the picture stays still"),
    "fast_moves": ("Fast camera moves", lambda m: m["fast_moves"]["count"], "max", "sustained fast motion"),
    "settled_pct": ("Fast moves that settle %", settled_pct, "min", "motion drops below half its peak afterwards"),
    "cut_candidates": ("Cut candidates", lambda m: m["cuts"]["candidate_count"], "max", "possible hard cuts, many of them false alarms"),
    "wpm": ("Words per minute", lambda m: (m.get("script") or {}).get("words_per_minute"), "range", "speaking pace, needs a transcript"),
    "lufs": ("Loudness (LUFS)", audio_value("integrated_lufs"), "range", "overall loudness"),
    "lra": ("Loudness range (LU)", audio_value("loudness_range_lu"), "range", "how much the loudness varies"),
    # Upload platforms rewrite peaks, so only the target counts here, not the references.
    "true_peak": ("True peak (dB)", audio_value("true_peak_dbtp"), "target", "the loudest instant"),
    "silences": ("Silent gaps", audio_value("silences_over_0.15s"), "max", "gaps over 0.15s below -35 dB"),
}
# Differences this small can't be heard, so they don't count as being outside the references.
TOLERANCE = {"lufs": 0.5, "lra": 0.3, "wpm": 10}
FRAME_CHECKS = {
    "edge_pct": ("thin on detail", True, False),
    "colours": ("few colours", True, False),
    "contrast": ("contrast outside the references", True, True),
    "saturation": ("colour strength outside the references", True, True),
}


def percentile(values, share):
    ordered = sorted(values)
    return ordered[min(int(len(ordered) * share), len(ordered) - 1)]


def load_metrics(directory):
    path = Path(directory) / "metrics.json"
    if not path.exists():
        fail(f"no metrics.json in {directory}: run measure first")
    return json.loads(path.read_text())


def profile(opts):
    videos = []
    for directory in opts.out_dirs:
        m = load_metrics(directory)
        if not m.get("look"):
            fail(f"{directory} was measured before look numbers existed: run measure again")
        videos.append((Path(m["video"]).parent.name, m))
    fps = {m["fps"] for _, m in videos}
    path = PROFILES / f"{opts.name}.json"
    previous = json.loads(path.read_text()) if path.exists() else {}
    # Targets are decisions, not measurements: keep them when the references are re-measured.
    targets = json.loads(Path(opts.targets).read_text()) if opts.targets else previous.get("targets", {})
    ranges = {}
    for key, (_, read, _, _) in MEASURES.items():
        values = [v for v in (read(m) for _, m in videos) if v is not None]
        if values:
            ranges[key] = {"low": min(values), "high": max(values), "median": statistics.median(values), "videos": len(values)}
    limits = {}
    for key, (_, low_side, high_side) in FRAME_CHECKS.items():
        pooled = [v for _, m in videos for v in m["look"]["samples"][key]]
        limits[key] = {}
        if low_side:
            limits[key]["low"] = percentile(pooled, 0.1)
        if high_side:
            limits[key]["high"] = percentile(pooled, 0.9)
    data = {
        "name": opts.name,
        "title": opts.title or previous.get("title", opts.name),
        "built": datetime.date.today().isoformat(),
        "fps": sorted(fps),
        "videos": [{"name": name, "values": {k: read(m) for k, (_, read, _, _) in MEASURES.items()}} for name, m in videos],
        "ranges": ranges,
        "frame_limits": limits,
        "targets": targets,
        "notes": opts.note or previous.get("notes", []),
    }
    PROFILES.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1))
    print(f"Wrote {path}: {len(videos)} videos, {len(targets)} targets.")
    if len(videos) < 3:
        print("Fewer than 3 videos: the ranges only describe these videos, so treat them as a rough guide.")


def choose_profile(name):
    available = sorted(PROFILES.glob("*.json"))
    if name:
        path = PROFILES / f"{name}.json"
        if not path.exists():
            fail(f"no profile {name}. Available: {', '.join(p.stem for p in available) or 'none'}")
        return path
    if len(available) == 1:
        return available[0]
    fail(f"choose one with --profile. Available: {', '.join(p.stem for p in available) or 'none'}")


def judge(key, value, standard):
    """Returns (rank, words): 0 meets, 1 short of the target but like the references, 2 outside them."""
    _, _, side, _ = MEASURES[key]
    span = standard["ranges"].get(key)
    target = standard["targets"].get(key, {})
    low_ref, high_ref = (span["low"], span["high"]) if span else (None, None)
    outside = False
    if span:
        slack = TOLERANCE.get(key, 0)
        outside = (side in ("min", "range") and value < low_ref - slack) or (side in ("max", "range") and value > high_ref + slack)
    slack = TOLERANCE.get(key, 0)
    missed = ("min" in target and value < target["min"] - slack) or ("max" in target and value > target["max"] + slack)
    if outside:
        return 2, "Falls short: outside the references"
    if missed:
        return 1, "Short of target, but within the references"
    return 0, "Meets"


def stretches(flags, rate):
    runs, start = [], None
    for index, flag in enumerate(flags + [False]):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            runs.append([start, index])
            start = None
    # Close one-sample gaps, so a single better frame doesn't split a weak stretch.
    merged = []
    for run in runs:
        if merged and run[0] - merged[-1][1] <= 1:
            merged[-1][1] = run[1]
        else:
            merged.append(run)
    keep = [r for r in merged if r[1] - r[0] >= WEAK_STRETCH_SAMPLES]
    keep.sort(key=lambda r: r[0] - r[1])
    return [(round(a / rate, 1), round(b / rate, 1)) for a, b in keep]


def weak_frames(m, standard):
    """Where the picture is as thin as the weakest tenth of the reference frames."""
    found = {}
    look = m.get("look")
    if not look:
        return found
    rate = look["samples_per_second"]
    for key, (words, _, _) in FRAME_CHECKS.items():
        limit = standard["frame_limits"].get(key, {})
        values = look["samples"][key]
        flags = [("low" in limit and v < limit["low"]) or ("high" in limit and v > limit["high"]) for v in values]
        found[key] = {"words": words, "pct": round(100 * sum(flags) / max(len(flags), 1)), "stretches": stretches(flags, rate)}
    return found


def number(value):
    return f"{value:g}" if isinstance(value, (int, float)) else "n/a"


def scorecard(opts):
    out = Path(opts.out_dir).resolve()
    m = load_metrics(out)
    path = choose_profile(opts.profile)
    standard = json.loads(path.read_text())
    rows, unmeasured = [], []
    for key, (label, read, _, meaning) in MEASURES.items():
        value = read(m)
        span = standard["ranges"].get(key)
        if value is None or span is None:
            unmeasured.append(label)
            continue
        rank, words = judge(key, value, standard)
        target = standard["targets"].get(key, {})
        goal = " to ".join(number(target[k]) for k in ("min", "max") if k in target) if "min" in target and "max" in target \
            else (f"{number(target['min'])}+" if "min" in target else (("none" if target["max"] == 0 else f"{number(target['max'])} or less") if "max" in target else "-"))
        # How far past the reference range, in units of that range, so the worst misses come first.
        spread = max(span["high"] - span["low"], abs(span["median"]) * 0.1, 0.01)
        past = max(span["low"] - value, value - span["high"], 0) / spread
        rows.append((rank, past, key, label, value, span, goal, words, meaning))
    rows.sort(key=lambda r: (-r[0], -r[1]))

    hard = [r for r in rows if r[0] == 2]
    soft = [r for r in rows if r[0] == 1]
    lines = [f"# Scorecard: {Path(m['video']).name}", "",
             f"Against **{standard['title']}** ({len(standard['videos'])} reference videos).", ""]
    if hard:
        lines.append(f"**Falls short on {len(hard)} of {len(rows)}: {', '.join(r[3].lower() for r in hard)}.**")
    else:
        lines.append(f"**Nothing falls outside the references on these {len(rows)} measures.**")
    if soft:
        lines.append(f"Short of target but within the references on {len(soft)}: {', '.join(r[3].lower() for r in soft)}.")
    if m["fps"] not in standard.get("fps", []):
        lines.append(f"Warning: this video is {m['fps']}fps and the references are {standard.get('fps')}fps, so the motion numbers aren't comparable.")
    lines += ["", "| Measure | This video | References | Target | Result |", "|---|---|---|---|---|"]
    for rank, _, key, label, value, span, goal, words, _ in rows:
        lines.append(f"| {label} | {number(value)} | {number(span['low'])} to {number(span['high'])} | {goal} | {words} |")

    where = []
    weak = weak_frames(m, standard)
    moments = []
    for key, item in weak.items():
        if item["pct"] <= 15 and not item["stretches"]:
            continue
        spans = ", ".join(f"{a:g}-{b:g}s" for a, b in item["stretches"][:5]) or "scattered, no long stretch"
        where.append(f"- **{item['words'].capitalize()}:** {item['pct']}% of frames (a reference averages about 10%). Longest stretches: {spans}.")
        moments += [(round((a + b) / 2, 1), item["words"]) for a, b in item["stretches"][:3]]
    missed = {r[2] for r in rows if r[0]}
    fps = m["fps"]
    if "fast_moves" in missed:
        where.append("- **Fast moves at:** " + ", ".join(f"{r['t']:g}s" for r in m["fast_moves"]["runs"]) + ".")
    if "cut_candidates" in missed:
        where.append("- **Cut candidates at:** " + ", ".join(f"{c['t']:g}s" for c in m["cuts"]["candidates"]) + ". Check `cut_checks/` by eye before calling any of these a cut.")
    if {"pct_still", "longest_hold"} & missed:
        where.append("- **Holds at:** " + ", ".join(f"{h['t']:g}s ({h['seconds']:g}s)" for h in sorted(m["motion"].get("holds", []), key=lambda h: -h["seconds"])[:8]) + ".")
    if "silences" in missed:
        where.append("- **Silent gaps at:** " + ", ".join(f"{t:g}s" for t in (m.get("audio") or {}).get("silence_times", [])[:12]) + ".")
    if where:
        lines += ["", "## Where to look", ""] + where

    sheet = None
    if moments and Path(m["video"]).exists():
        info = probe(m["video"])
        chosen, used = [], []
        for t, words in sorted(moments, key=lambda x: x[0]):
            if all(abs(t - u) >= 1 for u in used):
                used.append(t)
                chosen.append((t, words))
        chosen = chosen[:12]
        expression = "+".join(f"eq(n,{int(t * info['fps'])})" for t, _ in chosen)
        render_sheet(m["video"], info, expression, len(chosen), out / "weak_moments.jpg")
        sheet = out / "weak_moments.jpg"
        lines += ["", f"Frames from the weakest stretches are in `{sheet}`: " + ", ".join(f"{t:g}s ({w})" for t, w in chosen) + "."]

    lines += ["", "## How far to trust this", "",
              "- These numbers point at things to look at. A noisy frame can score high on detail without looking good, so check the frames before changing anything.",
              "- They can't judge story, acting, voice or music."]
    if unmeasured:
        lines.append(f"- Not measured: {', '.join(unmeasured).lower()}.")
    lines += [f"- {note}" for note in standard.get("notes", [])]
    text = "\n".join(lines) + "\n"
    (out / "scorecard.md").write_text(text)
    print(text)
    print(f"Wrote {out / 'scorecard.md'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("measure")
    p.add_argument("video")
    p.add_argument("out_dir")
    p.add_argument("--transcript")
    p.add_argument("--every", type=int, help="seconds between overview frames (default: auto)")
    p.add_argument("--against", help="after measuring, score against this profile")
    p.set_defaults(handler=measure)

    p = commands.add_parser("strip")
    p.add_argument("video")
    p.add_argument("out_jpg")
    p.add_argument("--start", type=float, required=True)
    p.add_argument("--end", type=float, required=True)
    p.add_argument("--step", type=int, help="show every Nth frame (default: about 12 frames)")
    p.set_defaults(handler=strip)

    p = commands.add_parser("compare")
    p.add_argument("out_dirs", nargs="+")
    p.set_defaults(handler=compare)

    p = commands.add_parser("profile")
    p.add_argument("name")
    p.add_argument("out_dirs", nargs="+")
    p.add_argument("--title", help="a readable name for this standard")
    p.add_argument("--targets", help="JSON file of targets, such as {\"edge_pct\": {\"min\": 4}}")
    p.add_argument("--note", action="append", help="a caveat printed on every scorecard (repeatable)")
    p.set_defaults(handler=profile)

    p = commands.add_parser("scorecard")
    p.add_argument("out_dir")
    p.add_argument("--profile", help="profile name (default: the only one, if there is only one)")
    p.set_defaults(handler=scorecard)

    opts = parser.parse_args()
    opts.handler(opts)


if __name__ == "__main__":
    main()
