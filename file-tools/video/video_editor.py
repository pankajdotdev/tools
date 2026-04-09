#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║           🎬 VIDEO EDITOR TOOL by Dev               ║
║   Resolution • Split • Compress • Extract • More    ║
╚══════════════════════════════════════════════════════╝

Requirements:
    pip install moviepy tqdm rich
    Also install ffmpeg: https://ffmpeg.org/download.html
"""

import os
import sys
import math
import argparse
import subprocess
from pathlib import Path

# ── Try importing optional rich UI ──────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import track
    from rich.table import Table
    from rich import print as rprint
    console = Console()
    RICH = True
except ImportError:
    RICH = False
    console = None

# ── Try importing moviepy ────────────────────────────────
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips
    MOVIEPY = True
except ImportError:
    MOVIEPY = False


# ════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════

def log(msg, style=""):
    if RICH:
        console.print(msg, style=style)
    else:
        print(msg)


def file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)


def get_video_info(path):
    """Return dict with duration, resolution, fps, size using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-of", "default=noprint_wrappers=1",
        str(path)
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
        info = {}
        for line in out.strip().splitlines():
            key, _, val = line.partition("=")
            info[key.strip()] = val.strip()

        # Parse fps like "30000/1001"
        fps_raw = info.get("r_frame_rate", "30/1")
        num, _, den = fps_raw.partition("/")
        fps = round(int(num) / int(den), 2) if den != "0" else 30.0

        return {
            "width":    int(info.get("width", 0)),
            "height":   int(info.get("height", 0)),
            "fps":      fps,
            "duration": float(info.get("duration", 0)),
            "size_mb":  file_size_mb(path),
        }
    except Exception as e:
        log(f"[red]ffprobe error: {e}[/red]" if RICH else f"ffprobe error: {e}")
        return {}


def show_info(path):
    info = get_video_info(path)
    if not info:
        return
    if RICH:
        t = Table(title=f"📹 Video Info: {Path(path).name}", show_lines=True)
        t.add_column("Property", style="cyan")
        t.add_column("Value",    style="yellow")
        t.add_row("Resolution", f"{info['width']} x {info['height']}")
        t.add_row("FPS",        str(info["fps"]))
        t.add_row("Duration",   f"{info['duration']:.2f} seconds")
        t.add_row("File Size",  f"{info['size_mb']:.2f} MB")
        console.print(t)
    else:
        print(f"Resolution : {info['width']} x {info['height']}")
        print(f"FPS        : {info['fps']}")
        print(f"Duration   : {info['duration']:.2f} sec")
        print(f"File Size  : {info['size_mb']:.2f} MB")


# ════════════════════════════════════════════════════════
#  FEATURE 1 — CHANGE RESOLUTION
# ════════════════════════════════════════════════════════

def change_resolution(input_path, output_path, width, height):
    """Re-encode video at given resolution."""
    log(f"\n[bold cyan]🔧 Changing resolution → {width}x{height}[/bold cyan]" if RICH
        else f"\nChanging resolution → {width}x{height}")

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", f"scale={width}:{height}",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"[green]✅ Saved: {output_path}  ({file_size_mb(output_path):.2f} MB)[/green]" if RICH
            else f"✅ Saved: {output_path}  ({file_size_mb(output_path):.2f} MB)")
    else:
        log(f"[red]❌ Error:\n{result.stderr}[/red]" if RICH else f"❌ Error:\n{result.stderr}")


# ════════════════════════════════════════════════════════
#  FEATURE 2 — SPLIT VIDEO (by size OR by duration)
# ════════════════════════════════════════════════════════

def split_video(input_path, output_dir, max_size_mb=None, segment_seconds=None):
    """
    Split video into parts.
      - max_size_mb     : split so each part ≤ X MB
      - segment_seconds : split every N seconds
    """
    info = get_video_info(input_path)
    if not info:
        return

    duration   = info["duration"]
    total_mb   = info["size_mb"]
    out_dir    = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem       = Path(input_path).stem

    if max_size_mb:
        # Estimate how many seconds per chunk
        bitrate_mbps   = total_mb / duration          # MB/sec
        segment_seconds = max_size_mb / bitrate_mbps
        log(f"\n[bold cyan]✂️  Splitting by size (max {max_size_mb} MB/part → ~{segment_seconds:.1f}s each)[/bold cyan]"
            if RICH else
            f"\nSplitting by size (max {max_size_mb} MB → ~{segment_seconds:.1f}s each)")
    else:
        log(f"\n[bold cyan]✂️  Splitting every {segment_seconds}s[/bold cyan]"
            if RICH else f"\nSplitting every {segment_seconds}s")

    num_parts = math.ceil(duration / segment_seconds)
    log(f"Total parts: [yellow]{num_parts}[/yellow]" if RICH else f"Total parts: {num_parts}")

    parts = []
    for i in range(num_parts):
        start = i * segment_seconds
        out   = out_dir / f"{stem}_part{i+1:03d}.mp4"
        cmd   = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(input_path),
            "-t", str(segment_seconds),
            "-c:v", "libx264", "-crf", "23", "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k",
            str(out)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            sz = file_size_mb(out)
            parts.append((str(out), sz))
            log(f"  [green]Part {i+1:03d}: {out.name}  ({sz:.2f} MB)[/green]"
                if RICH else f"  Part {i+1:03d}: {out.name}  ({sz:.2f} MB)")
        else:
            log(f"  [red]Part {i+1} failed[/red]" if RICH else f"  Part {i+1} failed")

    log(f"\n[bold green]✅ {len(parts)} parts saved in: {out_dir}[/bold green]"
        if RICH else f"\n✅ {len(parts)} parts saved in: {out_dir}")


# ════════════════════════════════════════════════════════
#  FEATURE 3 — COMPRESS VIDEO (target size in MB)
# ════════════════════════════════════════════════════════

def compress_video(input_path, output_path, target_mb):
    """Two-pass compression to hit a target file size."""
    info = get_video_info(input_path)
    if not info:
        return

    duration       = info["duration"]
    target_kbits   = target_mb * 8 * 1024           # MB → kbits
    audio_kbps     = 128
    video_kbps     = int(target_kbits / duration) - audio_kbps

    if video_kbps < 100:
        log("[red]❌ Target too small — video bitrate would be < 100kbps[/red]"
            if RICH else "❌ Target too small for this duration")
        return

    log(f"\n[bold cyan]🗜️  Compressing → target {target_mb} MB  (video {video_kbps} kbps)[/bold cyan]"
        if RICH else f"\nCompressing → target {target_mb} MB  (video {video_kbps} kbps)")

    log_file = str(Path(output_path).with_suffix("")) + "_2pass"

    # Pass 1
    cmd1 = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-c:v", "libx264", "-b:v", f"{video_kbps}k",
        "-pass", "1", "-passlogfile", log_file,
        "-an", "-f", "null", os.devnull
    ]
    subprocess.run(cmd1, capture_output=True)

    # Pass 2
    cmd2 = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-c:v", "libx264", "-b:v", f"{video_kbps}k",
        "-pass", "2", "-passlogfile", log_file,
        "-c:a", "aac", "-b:a", f"{audio_kbps}k",
        str(output_path)
    ]
    result = subprocess.run(cmd2, capture_output=True, text=True)

    # Cleanup pass log files
    for ext in ["-0.log", "-0.log.mbtree"]:
        try: os.remove(log_file + ext)
        except: pass

    if result.returncode == 0:
        actual = file_size_mb(output_path)
        log(f"[green]✅ Saved: {output_path}  (actual: {actual:.2f} MB)[/green]"
            if RICH else f"✅ Saved: {output_path}  (actual: {actual:.2f} MB)")
    else:
        log(f"[red]❌ Error:\n{result.stderr}[/red]" if RICH else f"❌ Error:\n{result.stderr}")


# ════════════════════════════════════════════════════════
#  FEATURE 4 — EXTRACT AUDIO
# ════════════════════════════════════════════════════════

def extract_audio(input_path, output_path):
    """Extract audio track as MP3."""
    log(f"\n[bold cyan]🎵 Extracting audio...[/bold cyan]" if RICH else "\nExtracting audio...")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vn", "-c:a", "mp3", "-b:a", "192k",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"[green]✅ Audio saved: {output_path}[/green]"
            if RICH else f"✅ Audio saved: {output_path}")
    else:
        log(f"[red]❌ Error:\n{result.stderr}[/red]" if RICH else f"❌ Error")


# ════════════════════════════════════════════════════════
#  FEATURE 5 — TRIM VIDEO (start–end)
# ════════════════════════════════════════════════════════

def trim_video(input_path, output_path, start, end):
    """Trim video from start to end (seconds)."""
    log(f"\n[bold cyan]✂️  Trimming {start}s → {end}s[/bold cyan]"
        if RICH else f"\nTrimming {start}s → {end}s")
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-to", str(end),
        "-i", str(input_path),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"[green]✅ Trimmed: {output_path}[/green]"
            if RICH else f"✅ Trimmed: {output_path}")
    else:
        log(f"[red]❌ Error:\n{result.stderr}[/red]" if RICH else "❌ Error")


# ════════════════════════════════════════════════════════
#  FEATURE 6 — ADD WATERMARK TEXT
# ════════════════════════════════════════════════════════

def add_watermark(input_path, output_path, text, position="bottomright"):
    """Burn text watermark into video."""
    pos_map = {
        "topleft":     "x=10:y=10",
        "topright":    "x=W-tw-10:y=10",
        "bottomleft":  "x=10:y=H-th-10",
        "bottomright": "x=W-tw-10:y=H-th-10",
        "center":      "x=(W-tw)/2:y=(H-th)/2",
    }
    xy  = pos_map.get(position, pos_map["bottomright"])
    vf  = (
        f"drawtext=text='{text}':fontcolor=white:fontsize=36:"
        f"box=1:boxcolor=black@0.5:boxborderw=5:{xy}"
    )
    log(f"\n[bold cyan]💧 Adding watermark: '{text}'[/bold cyan]"
        if RICH else f"\nAdding watermark: '{text}'")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "copy",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"[green]✅ Saved: {output_path}[/green]" if RICH else f"✅ Saved: {output_path}")
    else:
        log(f"[red]❌ Error:\n{result.stderr}[/red]" if RICH else "❌ Error")


# ════════════════════════════════════════════════════════
#  FEATURE 7 — EXTRACT FRAMES (thumbnails)
# ════════════════════════════════════════════════════════

def extract_frames(input_path, output_dir, fps=1):
    """Extract frames at given rate (default: 1 per second)."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log(f"\n[bold cyan]🖼️  Extracting frames @ {fps} fps[/bold cyan]"
        if RICH else f"\nExtracting frames @ {fps} fps")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", f"fps={fps}",
        str(out_dir / "frame_%04d.jpg")
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    frames = list(out_dir.glob("frame_*.jpg"))
    if result.returncode == 0:
        log(f"[green]✅ {len(frames)} frames saved in: {out_dir}[/green]"
            if RICH else f"✅ {len(frames)} frames saved in: {out_dir}")
    else:
        log(f"[red]❌ Error:\n{result.stderr}[/red]" if RICH else "❌ Error")


# ════════════════════════════════════════════════════════
#  FEATURE 8 — CHANGE SPEED
# ════════════════════════════════════════════════════════

def change_speed(input_path, output_path, speed=2.0):
    """Speed up or slow down (0.5 = half speed, 2.0 = double speed)."""
    vf  = f"setpts={1/speed}*PTS"
    atempo = min(max(speed, 0.5), 2.0)   # atempo only supports 0.5–2.0
    af  = f"atempo={atempo}"
    log(f"\n[bold cyan]⚡ Changing speed → {speed}x[/bold cyan]"
        if RICH else f"\nChanging speed → {speed}x")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", vf, "-af", af,
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"[green]✅ Saved: {output_path}[/green]" if RICH else f"✅ Saved: {output_path}")
    else:
        log(f"[red]❌ Error:\n{result.stderr}[/red]" if RICH else "❌ Error")


# ════════════════════════════════════════════════════════
#  CLI — ARGUMENT PARSER
# ════════════════════════════════════════════════════════

def build_parser():
    p = argparse.ArgumentParser(
        description="🎬 Video Editor Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    p.add_argument("input", help="Input video file path")

    sub = p.add_subparsers(dest="command", required=True)

    # info
    sub.add_parser("info", help="Show video info")

    # resolution
    r = sub.add_parser("resolution", help="Change resolution")
    r.add_argument("-W", "--width",  type=int, required=True)
    r.add_argument("-H", "--height", type=int, required=True)
    r.add_argument("-o", "--output", required=True)

    # split
    s = sub.add_parser("split", help="Split video")
    group = s.add_mutually_exclusive_group(required=True)
    group.add_argument("--max-mb",  type=float, help="Max MB per part")
    group.add_argument("--seconds", type=float, help="Seconds per part")
    s.add_argument("-o", "--output-dir", required=True)

    # compress
    c = sub.add_parser("compress", help="Compress to target MB")
    c.add_argument("--target-mb", type=float, required=True)
    c.add_argument("-o", "--output", required=True)

    # audio
    a = sub.add_parser("audio", help="Extract audio as MP3")
    a.add_argument("-o", "--output", required=True)

    # trim
    t = sub.add_parser("trim", help="Trim video")
    t.add_argument("--start", type=float, required=True, help="Start second")
    t.add_argument("--end",   type=float, required=True, help="End second")
    t.add_argument("-o", "--output", required=True)

    # watermark
    w = sub.add_parser("watermark", help="Add text watermark")
    w.add_argument("--text",     required=True)
    w.add_argument("--position", default="bottomright",
                   choices=["topleft","topright","bottomleft","bottomright","center"])
    w.add_argument("-o", "--output", required=True)

    # frames
    f = sub.add_parser("frames", help="Extract frames")
    f.add_argument("--fps",        type=float, default=1)
    f.add_argument("-o", "--output-dir", required=True)

    # speed
    sp = sub.add_parser("speed", help="Change speed")
    sp.add_argument("--factor", type=float, required=True, help="e.g. 0.5 or 2.0")
    sp.add_argument("-o", "--output", required=True)

    return p


# ════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════

def main():
    if RICH:
        console.print(Panel.fit(
            "[bold yellow]🎬 VIDEO EDITOR TOOL[/bold yellow]\n"
            "[dim]resolution • split • compress • trim • watermark • frames • speed[/dim]",
            border_style="cyan"
        ))

    parser = build_parser()
    args   = parser.parse_args()
    inp    = args.input

    if not os.path.exists(inp):
        log(f"[red]❌ File not found: {inp}[/red]" if RICH else f"❌ File not found: {inp}")
        sys.exit(1)

    cmd = args.command

    if cmd == "info":
        show_info(inp)

    elif cmd == "resolution":
        change_resolution(inp, args.output, args.width, args.height)

    elif cmd == "split":
        if args.max_mb:
            split_video(inp, args.output_dir, max_size_mb=args.max_mb)
        else:
            split_video(inp, args.output_dir, segment_seconds=args.seconds)

    elif cmd == "compress":
        compress_video(inp, args.output, args.target_mb)

    elif cmd == "audio":
        extract_audio(inp, args.output)

    elif cmd == "trim":
        trim_video(inp, args.output, args.start, args.end)

    elif cmd == "watermark":
        add_watermark(inp, args.output, args.text, args.position)

    elif cmd == "frames":
        extract_frames(inp, args.output_dir, args.fps)

    elif cmd == "speed":
        change_speed(inp, args.output, args.factor)


if __name__ == "__main__":
    main()