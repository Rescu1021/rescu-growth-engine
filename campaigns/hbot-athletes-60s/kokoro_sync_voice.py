#!/usr/bin/env python3
"""Produce a natural-voice HBOT reel narration whose spoken lines match the exact
on-screen captions and their start/end times. Open-source Kokoro ONNX; no paid APIs.

This script is executed on GitHub Actions (internet-enabled runner) because Kokoro's
public model is not bundled in this repository. The resulting voice WAV contains
no patient media, personal data, or Queensbro music.
"""
from __future__ import annotations
import json
import argparse
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

# EXACTLY the main captions in lyrics.ass from the original 60-second master.
# Always speak what is visible; no unrelated narration or off-screen monologue.
CUES = [
    (0.00, 1.90, "Every rep."),
    (1.90, 3.60, "Every sprint."),
    (3.60, 5.40, "Every last second."),
    (5.40, 7.90, "You give the game everything."),
    (7.90, 10.00, "What about recovery?"),
    (10.00, 12.10, "Train hard."),
    (12.10, 14.40, "Recover smart."),
    (14.40, 16.80, "The next session starts now."),
    (16.80, 20.00, "Recovery is part of the work."),
    (20.00, 22.50, "Meet H B O T."),
    (22.50, 25.10, "Oxygen. Under pressure."),
    (25.10, 27.60, "More oxygen in blood plasma."),
    (27.60, 30.00, "Built around your goals."),
    (30.00, 32.00, "One body."),
    (32.00, 34.00, "One life."),
    (34.00, 36.60, "Take recovery seriously."),
    (36.60, 40.00, "Physician led. Athlete focused."),
    (40.00, 42.30, "Run. Lift. Compete."),
    (42.30, 45.20, "Make room to recover."),
    (45.20, 47.60, "Every sport. Every level."),
    (47.60, 50.00, "Let recovery be your routine."),
    (50.00, 52.00, "Your first dive."),
    (52.00, 54.00, "One ninety nine intro visit."),
    (54.00, 56.50, "Book your dive."),
    (56.50, 60.00, "Rescue Scarsdale. Book at rescue dot life."),
]
# The intro price and booking page must be verified before publishing.
VOICE = "am_michael"
SR = 24000

def trim_silence(wave: np.ndarray) -> np.ndarray:
    """Tightly trim synthesizer tails without truncating speech."""
    if len(wave) == 0:
        return wave
    threshold = max(.004, .014 * float(np.max(np.abs(wave))))
    active = np.where(np.abs(wave) >= threshold)[0]
    if len(active) < 2:
        return wave
    a = max(0, int(active[0]) - int(.025 * SR))
    b = min(len(wave), int(active[-1]) + int(.05 * SR))
    return wave[a:b]

def pitch_preserving_fit(wave: np.ndarray, max_len: int) -> np.ndarray:
    """Speed up any overlong clip with FFmpeg atempo while keeping voice pitch."""
    if len(wave) <= max_len:
        return wave
    speed = (len(wave) / max_len) * 1.012
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "in.wav", Path(td) / "out.wav"
        sf.write(src, wave, SR)
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                        "-i",str(src),"-af",f"atempo={speed:.4f}",str(dst)],check=True)
        result, sr = sf.read(dst, dtype="float32")
        assert sr == SR
        return result[:max_len]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="kokoro-v1.0.int8.onnx")
    ap.add_argument("--voices", default="voices-v1.0.bin")
    ap.add_argument("--output", default="rescu_hbot_natural_voice.wav")
    args = ap.parse_args()

    kokoro = Kokoro(args.model, args.voices)
    complete = np.zeros((60 * SR,), dtype=np.float32)
    report = []

    for idx, (start, end, spoken) in enumerate(CUES):
        samples, rate = kokoro.create(spoken, voice=VOICE, speed=1.075, lang="en-us")
        if rate != SR:
            raise RuntimeError(f"Unexpected Kokoro audio sample rate {rate}")
        clip = trim_silence(np.asarray(samples, dtype=np.float32))
        # Reserve 75 ms lead and 80 ms end silence for clean word boundaries.
        allocated = round((end - start - 0.20) * SR)
        original = len(clip)
        clip = pitch_preserving_fit(clip, allocated)
        lead = round((start + .075) * SR)
        final = min(60 * SR, lead + len(clip))
        clip = clip[:final - lead]
        f = min(int(.02 * SR), len(clip) // 3)
        if f:
            clip[:f] *= np.linspace(0, 1, f)
            clip[-f:] *= np.linspace(1, 0, f)
        complete[lead:final] += clip
        report.append({"line":idx+1,"start":start,"end":end,
                       "spoken":spoken,"generated_sec":round(original/SR,2),
                       "fitted_sec":round(len(clip)/SR,2)})
        print(f"{idx+1:02d} {start:05.2f}-{end:05.2f} {spoken} ({original/SR:.2f}s -> {len(clip)/SR:.2f}s)",flush=True)

    max_amp=float(np.max(np.abs(complete)))
    if max_amp>.95:
        complete*=.95/max_amp
    sf.write(args.output,complete,SR,subtype="PCM_16")
    Path("rescu_hbot_narration_alignment.json").write_text(json.dumps(report,indent=2)+"\n")
    print(f"Generated {args.output}, {len(complete)/SR:.2f}s, peak={max_amp:.3f}",flush=True)

if __name__ == "__main__":
    main()
