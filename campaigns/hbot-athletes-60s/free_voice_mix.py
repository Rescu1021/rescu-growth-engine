#!/usr/bin/env python3
"""Free/offline RESCU athlete narration with Queensbro song ducking.

Uses the open-source eSpeak / eSpeak NG speech engine and FFmpeg.
Python deps: numpy soundfile scipy. No paid TTS services or APIs.

Run:
  python free_voice_mix.py --video face_blurred.mp4 --music "Locked In.mp3" --output narrated.mp4

Employee face blur belongs in source --video; this script preserves source frames.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

CUES = [
    (1.6, "Every rep. Every sprint. Every last second. You put in the work."),
    (9.0, "Now make room for recovery."),
    (14.1, "At Rescu Performance in Scarsdale, our physician-led team offers hyperbaric oxygen therapy."),
    (26.0, "Also called H B O T. Oxygen, delivered in a pressurized chamber."),
    (36.6, "Athletes exploring recovery options start with a medical conversation. Individual results vary."),
    (47.5, "Train hard. Recover smart. One body. One life."),
    (54.4, "Book your First Dive at Rescu dot life, Scarsdale."),
]
SR = 48000
DURATION = 60

def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)

def read_stereo_wav(path):
    data, rate = sf.read(path, always_2d=True, dtype="float32")
    if rate != SR or data.shape[1] != 2:
        raise ValueError("Expected 48 kHz stereo WAV: " + str(path))
    return data

def convert_to_wav(source, destination, seconds=None):
    cmd = ["ffmpeg", "-y", "-i", str(source)]
    if seconds:
        cmd += ["-t", str(seconds)]
    run(*cmd, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(destination))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--music", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tts = shutil.which("espeak-ng") or shutil.which("espeak")
    if not tts:
        raise SystemExit("Install open-source eSpeak NG: https://github.com/espeak-ng/espeak-ng")
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        convert_to_wav(args.music, temp / "music.wav", DURATION)
        music = read_stereo_wav(temp / "music.wav")
        n = DURATION * SR
        if len(music) < n:
            music = np.pad(music, ((0, n - len(music)), (0, 0)))
        music = music[:n]
        voice = np.zeros((n, 2), dtype=np.float32)
        gain = np.full(n, 10 ** (-11 / 20), dtype=np.float32)
        voice_gain = 10 ** (-23 / 20)
        music_gain = 10 ** (-11 / 20)
        filter_sos = butter(2, 120, fs=SR, btype="highpass", output="sos")

        for index, (start, words) in enumerate(CUES):
            raw = temp / f"voice_{index:02d}.wav"
            wav = temp / f"voice_{index:02d}_48k.wav"
            run(tts, "-v", "en-us+m3", "-s", "168", "-p", "37",
                "-a", "175", "-w", str(raw), words)
            convert_to_wav(raw, wav)
            speech = read_stereo_wav(wav)
            speech = sosfiltfilt(filter_sos, speech, axis=0).astype(np.float32)
            next_start = CUES[index + 1][0] if index + 1 < len(CUES) else 59.7
            speech = speech[:max(0, int((next_start - start - .3) * SR))]
            start_sample = int(start * SR)
            end_sample = min(n, start_sample + len(speech))
            speech = speech[:end_sample - start_sample]
            fade = min(int(.065 * SR), len(speech) // 2)
            if fade:
                speech[:fade] *= np.linspace(0, 1, fade)[:, None]
                speech[-fade:] *= np.linspace(1, 0, fade)[:, None]
            voice[start_sample:end_sample] += speech
            attack = max(0, start_sample - int(.18 * SR))
            release = min(n, end_sample + int(.4 * SR))
            if start_sample > attack:
                gain[attack:start_sample] = np.minimum(
                    gain[attack:start_sample],
                    np.linspace(music_gain, voice_gain, start_sample - attack))
            gain[start_sample:end_sample] = np.minimum(gain[start_sample:end_sample], voice_gain)
            if release > end_sample:
                gain[end_sample:release] = np.minimum(
                    gain[end_sample:release],
                    np.linspace(voice_gain, music_gain, release - end_sample))
        mix = music * gain[:, None] + voice * .90
        peak = np.max(np.abs(mix))
        if peak > .93:
            mix *= .93 / peak
        mixed_audio = temp / "ducked_mix.wav"
        sf.write(mixed_audio, mix, SR, subtype="PCM_16")
        run("ffmpeg", "-y", "-i", str(args.video), "-i", str(mixed_audio),
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
            "-t", str(DURATION), "-movflags", "+faststart", str(args.output))
    print(f"Completed {args.output}")

if __name__ == "__main__":
    main()
