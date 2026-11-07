# Queensbro — Lone Wolf

A 1:59 vertical lyric visual using the original cover and all 458 supplied lyric words.
Built with Python, Pillow text measurement, FFmpeg and libass. No paid generation API.

## Current deliverable

- 1080 × 1920, 30 fps, H.264 MP4, exactly 119 seconds / 3,570 frames.
- Slow movement over the cover, animated lyric cards, ivory and amber typography.
- 68 editable cues, preserved in source order; punctuation/capitalization in the source remains the user's.
- The MP4 is a **silent visual draft**. The original recording was not available.
- `timeline.json` is **provisional text-length timing**, not audio alignment or final karaoke synchronization.
- Adding a recording with `--audio` produces a rough cut. Review and correct every cue against the vocals before describing it as synchronized.

## Render locally

Install Python 3.11+, FFmpeg (with libass), `fonts-dejavu-core`, and Pillow:

```sh
python -m pip install Pillow
python video_projects/queensbro/lone_wolf/render.py --output output/lone-wolf
```

Output: `Queensbro_Lone_Wolf_1m59_Visual_Draft.mp4`, editable `.srt` and `.ass`, a layout report, and a render report.

To add the intended 1:59 recording:

```sh
python video_projects/queensbro/lone_wolf/render.py \
  --audio /absolute/path/Lone_Wolf.mp3 \
  --output output/lone-wolf-with-audio
```

The script rejects audio more than 0.25 seconds away from 119 seconds instead of silently stretching or cutting a different version. Original audio is encoded as AAC at 256 kbps. The optional rough cut still uses the editable provisional timeline until that timeline is corrected.

## Edit timing

Update `start` and `end` in `timeline.json` while preserving cue text and order. The renderer checks chronological bounds and verifies the full lyric text against `lyrics.txt`. Keep `timing_status` as `provisional` until the recording has been reviewed cue by cue. The supplied spelling and wording are retained intentionally; to revise lyrics, change both the source and corresponding cue text.

## GitHub Actions

The **Queensbro — Lone Wolf lyric video** workflow renders the silent preview when this project's pull request is opened or updated, then stores the MP4, subtitles and reports as a downloadable Actions artifact for 30 days. It can also be run manually once the workflow is available on the default branch. The workflow uses read-only repository permissions and standard CPU runners. It does not post to social media or deploy a website.

Song audio is not included or fetched from any external service. Add only an authorized recording when ready. Rendered videos and local audio are ignored by Git; the cover, script, lyrics and timeline are the reproducible source.

## Source

Lyrics supplied by the user in the November 7, 2026 conversation. Cover generated in that conversation for this song and re-encoded as JPEG for repository size. This renderer is original project code; it does not claim to be a fork of a third-party lyric engine.
