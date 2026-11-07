#!/usr/bin/env python3
"""Create Lone Wolf full song + 1:59 excerpt from the user's ORIGINAL MP3.
Uses validated 119-second lyric visual as the source. Captions remain provisional.
No song audio is committed to GitHub.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run(*argv):
    print("+", " ".join(str(x) for x in argv))
    subprocess.run([str(x) for x in argv], check=True)

def duration(path):
    d = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(path)
    ], text=True))
    return float(d["format"]["duration"])

def retime_srt(source, destination, factor, limit=None):
    if not source.is_file():
        return
    source_text = source.read_text(encoding="utf-8-sig")
    times = re.compile(r"(\\d{2}):(\\d{2}):(\\d{2}),(\\d{3})")
    def parse_time(m):
        h, m_, s, ms = map(int, m.groups())
        return (h * 3600 + m_ * 60 + s + ms / 1000) * factor
    def stamp(seconds):
        millis = round(max(0, seconds) * 1000)
        return f"{millis // 3600000:02}:{(millis // 60000) % 60:02}:{(millis // 1000) % 60:02},{millis % 1000:03}"
    blocks = []
    for block in re.split(r"\\n\\s*\\n", source_text.strip()):
        lines = block.splitlines()
        if len(lines) < 3 or " --> " not in lines[1]:
            continue
        orig_start, orig_end = lines[1].split(" --> ", 1)
        sm, em = times.fullmatch(orig_start), times.fullmatch(orig_end)
        if not sm or not em:
            continue
        start, end = parse_time(sm), parse_time(em)
        if limit is not None and start >= limit:
            break
        if limit is not None:
            end = min(end, limit)
        if end > start:
            blocks.append((start, end, "\\n".join(lines[2:])))
    destination.write_text("".join(
        f"{i}\\n{stamp(s)} --> {stamp(e)}\\n{body}\\n\\n"
        for i, (s, e, body) in enumerate(blocks, 1)
    ), encoding="utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", required=True, type=Path, help="Owner's original You Chose Violence MP3")
    p.add_argument("--output", default=ROOT / "output" / "with-original-audio", type=Path)
    p.add_argument("--silent-video", type=Path, help="Optional existing 119-second visual MP4")
    a = p.parse_args()
    if not a.audio.is_file():
        p.error("Original audio file does not exist at --audio path.")
    a.output.mkdir(parents=True, exist_ok=True)
    if a.silent_video:
        source = a.silent_video
        source_dir = source.parent
    else:
        source_dir = a.output / "source"
        source = source_dir / "Queensbro_Lone_Wolf_1m59_Visual_Draft.mp4"
        if not source.is_file():
            run("python", ROOT / "render.py", "--output", source_dir)
    if not source.is_file():
        p.error(f"Missing silent master: {source}")
    audio_sec = duration(a.audio)
    video_sec = duration(source)
    if not 170 <= audio_sec <= 240:
        p.error(f"Expected a full-song recording near 3:05.6, got {audio_sec:.3f}s. Refusing to match a different edit automatically.")
    if abs(video_sec - 119) > 0.3:
        p.error(f"Expected 119s silent master, got {video_sec:.3f}s")
    factor = audio_sec / video_sec
    full = a.output / "Queensbro_Lone_Wolf_FULL_original_audio.mp4"
    teaser = a.output / "Queensbro_Lone_Wolf_1m59_original_audio_excerpt.mp4"
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", source, "-i", a.audio, "-filter:v",
        f"setpts={factor:.10f}*(PTS-STARTPTS),fps=30", "-map", "0:v:0",
        "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-b:a", "256k", "-t", f"{audio_sec:.3f}",
        "-movflags", "+faststart", full)
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", full, "-t", "119", "-map", "0:v:0", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "256k",
        "-movflags", "+faststart", teaser)
    srt = source_dir / "Queensbro_Lone_Wolf_Provisional.srt"
    retime_srt(srt, a.output / "FULL_caption_TIMING_PROVISIONAL.srt", factor)
    retime_srt(srt, a.output / "1m59_excerpt_TIMING_PROVISIONAL.srt", factor, 119)
    print(f"Full: {full} ({duration(full):.2f}s)")
    print(f"1:59 excerpt: {teaser} ({duration(teaser):.2f}s)")
    print("Lyric cue alignment is PROVISIONAL, not verified against actual vocal entries.")

if __name__ == "__main__":
    main()
