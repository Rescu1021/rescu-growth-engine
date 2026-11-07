#!/usr/bin/env python3
"""Render the 119-second Queensbro lyric visual with local FFmpeg.

No speech synthesis or music generation. The supplied timing is provisional.
Adding audio does not itself make the lyrics synchronized.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess

from PIL import ImageFont

ROOT = Path(__file__).resolve().parent
DURATION = 119.0
FPS = 30
WIDTH, HEIGHT = 1080, 1920
HOOK = "You chose violence destroyed the peace"
GOLD = "&H0067BFF1&"
IVORY = "&H00E5EFF7&"


def font_path() -> str:
    for item in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(item).is_file():
            return item
    raise RuntimeError("Install fonts-dejavu-core.")


def initial_timeline() -> dict:
    """Allocate by text length only; never claim this is vocal alignment."""
    lines = ROOT.joinpath("lyrics.txt").read_text(encoding="utf-8").splitlines()
    phrases = []
    section = 0
    for line in (line.strip() for line in lines):
        if not line:
            continue
        if line == HOOK:
            section += 1
            phrases.extend([
                ("You chose violence", "hook", section),
                ("destroyed the peace", "hook", section),
            ])
            continue
        words = line.split()
        # Preserve every supplied word, splitting only the longest lines.
        if len(words) > 12:
            middle = math.ceil(len(words) / 2)
            phrases.extend([
                (" ".join(words[:middle]), "verse", section),
                (" ".join(words[middle:]), "verse", section),
            ])
        else:
            phrases.append((line, "verse", section))
    weights = [0.6 + len(p[0].split()) * 0.22 for p in phrases]
    usable = 117.5 - 0.8
    units = usable / sum(weights)
    t = 0.8
    cues = []
    for i, ((words, kind, verse), weight) in enumerate(zip(phrases, weights)):
        end = round(t + weight * units, 2)
        cues.append({"id": i + 1, "start": round(t, 2), "end": end,
                     "text": words, "kind": kind, "verse": verse})
        t = end
    cues[-1]["end"] = 117.5
    return {
        "title": "Lone Wolf", "artist": "Queensbro",
        "duration_seconds": DURATION, "fps": FPS,
        "canvas": [WIDTH, HEIGHT], "timing_status": "provisional",
        "timing_method": "Text-length allocation; no recording was available.",
        "audio_status": "missing", "cues": cues,
    }


def validate(data: dict) -> None:
    if data.get("duration_seconds") != DURATION:
        raise ValueError("This project must stay exactly 119 seconds.")
    cues = data.get("cues", [])
    if not cues:
        raise ValueError("No lyric cues.")
    previous = 0.0
    for cue in cues:
        if not (previous <= cue["start"] < cue["end"] <= DURATION):
            raise ValueError(f"Invalid or overlapping cue: {cue}")
        if any(c in cue["text"] for c in "{}\\"):
            raise ValueError("Lyric text cannot contain ASS control characters.")
        previous = cue["end"]
    normalized = lambda text: " ".join(text.split())
    original = normalized(ROOT.joinpath("lyrics.txt").read_text(encoding="utf-8"))
    displayed = normalized(" ".join(cue["text"] for cue in cues))
    if original != displayed:
        raise ValueError("Timing cues must preserve every word of lyrics.txt in order.")


def timestamp(t: float, ass: bool = False) -> str:
    precision = 100 if ass else 1000
    value = round(t * precision)
    hours, value = divmod(value, 3600 * precision)
    minutes, value = divmod(value, 60 * precision)
    seconds, fraction = divmod(value, precision)
    if ass:
        return f"{hours}:{minutes:02}:{seconds:02}.{fraction:02}"
    return f"{hours:02}:{minutes:02}:{seconds:02},{fraction:03}"


def fit_text(text: str, kind: str) -> tuple[int, list[str]]:
    for size in range(92 if kind == "hook" else 78, 51, -2):
        font = ImageFont.truetype(font_path(), size)
        lines, current = [], ""
        for word in text.upper().split():
            trial = f"{current} {word}".strip()
            if font.getlength(trial) > 840 and current:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
        if len(lines) <= 3:
            return size, lines
    raise ValueError(f"Lyric card is too long: {text}")


def make_subtitles(data: dict, output: Path) -> dict:
    styles = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lyric,DejaVu Sans,78,&H00E5EFF7,&H0067BFF1,&H0020140E,&HAA000000,-1,0,0,0,100,100,0,0,1,2,1,5,90,130,60,1
Style: Small,DejaVu Sans,22,&H00B4C1CD,&H00B4C1CD,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,5,70,70,60,1
Style: Shape,DejaVu Sans,10,&H0067BFF1,&H0067BFF1,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []

    def event(start, end, body, style="Lyric", layer=1):
        events.append(f"Dialogue: {layer},{timestamp(start, True)},"
                      f"{timestamp(end, True)},{style},,0,0,0,,{body}")

    event(0, DURATION, r"{\pos(520,1740)}QUEENSBRO  /  LONE WOLF", "Small")
    event(0, DURATION,
          r"{\an7\pos(90,1792)\p1\1c&H00372C23&}m 0 0 l 900 0 900 3 0 3", "Shape", 0)
    event(0, DURATION,
          r"{\an7\pos(90,1792)\p1\clip(90,1792,90,1796)"
          r"\t(0,119000,\clip(90,1792,990,1796))}m 0 0 l 900 0 900 3 0 3", "Shape", 0)
    event(0, 0.8, r"{\pos(520,1430)\fs84\fad(100,90)}LONE WOLF")
    layout = []
    for cue in data["cues"]:
        size, lines = fit_text(cue["text"], cue["kind"])
        # A line break and colour change emphasize the final phrase without
        # pretending these are word-level timestamps derived from the audio.
        decorated = []
        for i, line in enumerate(lines):
            colour = GOLD if i == len(lines) - 1 else IVORY
            decorated.append("{\\1c" + colour + "}" + line)
        body = (f"{{\\an5\\move(520,1444,520,1430,0,150)\\fs{size}"
                f"\\fad(70,50)\\q2}}" + r"\N".join(decorated))
        event(cue["start"], cue["end"], body)
        font = ImageFont.truetype(font_path(), size)
        layout.append({"id": cue["id"], "font_size": size, "lines": lines,
                       "width": round(max(font.getlength(line) for line in lines), 2)})
    event(117.5, DURATION,
          r"{\pos(520,1400)\fs88\fad(130,300)}LONE WOLF"
          r"\N{\fs32\1c&H0067BFF1&}QUEENSBRO")
    ass_path = output / "lyrics.ass"
    ass_path.write_text(styles + "\n".join(events) + "\n", encoding="utf-8")
    srt = "\n\n".join(
        f"{i+1}\n{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{cue['text']}"
        for i, cue in enumerate(data["cues"])
    )
    (output / "Queensbro_Lone_Wolf_Provisional.srt").write_text(srt + "\n", encoding="utf-8")
    return {"card_count": len(layout), "max_text_width": max(x["width"] for x in layout),
            "smallest_font_size": min(x["font_size"] for x in layout), "cards": layout}


def probe(path: Path) -> dict:
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)
    ], text=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output")
    parser.add_argument("--audio", type=Path, help="Optional 119-second original recording.")
    parser.add_argument("--init-timing", action="store_true", help="Create an initial timeline if absent.")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--seconds", type=float, default=DURATION, help="Short local render check.")
    args = parser.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("Install FFmpeg and ffprobe.")
    timeline_path = ROOT / "timeline.json"
    if args.init_timing and not timeline_path.exists():
        timeline_path.write_text(json.dumps(initial_timeline(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    data = json.loads(timeline_path.read_text(encoding="utf-8"))
    validate(data)
    if not (0 < args.seconds <= DURATION):
        raise ValueError("Render duration must be between 0 and 119 seconds.")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    layout = make_subtitles(data, output)
    report = {
        "duration_seconds": args.seconds, "resolution": [WIDTH, HEIGHT], "fps": FPS,
        "timing_status": data["timing_status"],
        "timing_note": "Provisional text-length timing. Match every cue to the original recording before release.",
        "lyrics_preserved": True, "audio_included": bool(args.audio),
        "card_count": layout["card_count"], "max_text_width": layout["max_text_width"],
        "smallest_font_size": layout["smallest_font_size"],
    }
    (output / "layout.json").write_text(json.dumps(layout, indent=2), encoding="utf-8")
    if args.prepare_only:
        print(json.dumps(report, indent=2))
        return
    cover = ROOT / "assets" / "cover.jpg"
    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
               "-filter_complex_threads", "2", "-threads", "2",
               "-loop", "1", "-framerate", str(FPS), "-i", str(cover),
               "-f", "lavfi", "-i", f"color=c=0x090e16:s={WIDTH}x{HEIGHT}:r={FPS}"]
    if args.audio:
        args.audio = args.audio.resolve()
        audio_info = probe(args.audio)
        if not any(x.get("codec_type") == "audio" for x in audio_info["streams"]):
            raise ValueError("The supplied file does not have an audio stream.")
        if abs(float(audio_info["format"]["duration"]) - DURATION) > 0.25:
            raise ValueError("Supply the intended 119-second audio edit. The renderer will not time-stretch or cut a different version.")
        command += ["-i", str(args.audio)]
    # Gentle camera drift keeps the original square art and its title visible.
    # All animation is visual; there is no invented beat or fake audio waveform.
    graph = (
        "[0:v]scale=1600:1600,"
        "zoompan=z='1.015+0.010*sin(on/270)':"
        "x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1080:fps=30[art];"
        "[1:v][art]overlay=x=0:y=70:shortest=1,"
        "drawbox=x=90:y=1233:w=62:h=4:color=0xf1bf67:t=fill,"
        "ass=lyrics.ass,fade=t=in:st=0:d=0.25,"
        "fade=t=out:st=118.55:d=0.45,format=yuv420p[v]"
    )
    filename = "Queensbro_Lone_Wolf_1m59_Visual_Draft.mp4"
    if args.audio:
        filename = "Queensbro_Lone_Wolf_1m59_Rough_Cut.mp4"
    command += ["-filter_complex", graph, "-map", "[v]"]
    if args.audio:
        command += ["-map", "2:a:0", "-c:a", "aac", "-b:a", "256k",
                    "-af", "apad", "-metadata", "comment=Provisional lyric timing; audio supplied."]
    else:
        command += ["-an", "-metadata", "comment=Silent visual draft. Original song audio missing; lyric timing provisional."]
    command += ["-t", str(args.seconds), "-r", str(FPS), "-c:v", "libx264", "-threads", "4",
                "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", "-metadata", "title=Queensbro - Lone Wolf",
                str(output / filename)]
    subprocess.run(command, cwd=output, check=True)
    info = probe(output / filename)
    video = next(x for x in info["streams"] if x["codec_type"] == "video")
    actual_duration = float(info["format"]["duration"])
    if abs(actual_duration - args.seconds) > 1 / FPS + 0.001:
        raise RuntimeError(f"Unexpected duration: {actual_duration}")
    if (video["width"], video["height"]) != (WIDTH, HEIGHT):
        raise RuntimeError("Unexpected video size.")
    report.update({"filename": filename, "actual_duration_seconds": actual_duration,
                   "frame_count": video.get("nb_frames"), "size_bytes": (output / filename).stat().st_size,
                   "codec": video["codec_name"]})
    (output / "render_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
