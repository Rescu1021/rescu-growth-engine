"""Offline, original RESCU video preproduction: no generators, voice clones, PHI or posting."""
from __future__ import annotations

import json
from urllib.parse import urlsplit

SHOT_MOTION = (
    ("close-up / approved facility establishing shot", "Slow push-in; reveal question without flashing"),
    ("medium / clinical equipment detail", "Match cut to authentic device footage or a restrained diagram"),
    ("legible information graphic", "One cited claim per screen; verify the supporting source"),
    ("static end card with approved RESCU quadrants logo", "Hold the CTA long enough for legibility"),
)


def _stamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    hour, rem = divmod(ms, 3600000)
    minute, rem = divmod(rem, 60000)
    sec, milli = divmod(rem, 1000)
    return f"{hour:02}:{minute:02}:{sec:02}.{milli:03}"


def build_video_assets(spec: dict, pack: dict[str, str]) -> dict[str, str]:
    """Make blocked drafts from a campaign already validated by content_factory.build."""
    storyboard = json.loads(pack["reel_storyboard.json"])
    slides = storyboard["slides"]
    facts = spec["facts"]
    if len(slides) != 4 or not facts:
        raise ValueError("Video planner requires four storyboard slides and cited facts")
    narration = [spec["hook"], spec["intro"], facts[0]["text"], spec["cta_label"]]
    chapters, shots, warnings = [], [], []
    captions = ["WEBVTT", "", "NOTE Draft scene-timed captions only; align to approved audio before release.", ""]
    previous_end = 0.0
    for i, (slide, spoken) in enumerate(zip(slides, narration)):
        start, end = map(float, slide["seconds"])
        if start != previous_end or end <= start or end - start > 30:
            raise ValueError("Scenes must be consecutive, positive and <=30 seconds")
        previous_end = end
        rate = len(spoken.split()) / (end - start)
        if rate > 2.5:
            warnings.append(f"Scene {i + 1}: {rate:.1f} words/sec; rewrite or retime after recording")
        if len(slide["title"]) > 80:
            warnings.append(f"Scene {i + 1}: long title may be hard to read on mobile")
        source_url = facts[0]["source_url"] if i == 2 else None
        if source_url and urlsplit(source_url).scheme != "https":
            raise ValueError("Evidence URL must be HTTPS")
        chapters.append({"start_seconds": start, "title": ("Hook", "What to know", "Evidence point", "Next step")[i]})
        shots.append({
            "scene": i + 1, "time": [start, end], "chapter": chapters[-1]["title"],
            "title": slide["title"], "voiceover_draft": spoken, "visual": slide["visual"],
            "framing": SHOT_MOTION[i][0], "motion_direction": SHOT_MOTION[i][1],
            "source_url_for_editor_to_verify": source_url,
            "narration_words_per_second": round(rate, 2),
        })
        captions.extend([str(i + 1), f"{_stamp(start)} --> {_stamp(end)}", spoken, ""])

    checks = [
        "Physician checks every claim against the cited source and current evidence",
        "Review indications, screening, uncertainty and medical advertising requirements",
        "Confirm device images represent actual RESCU equipment and services",
        "Obtain appropriate releases and verify image/music/voice licenses and consent",
        "Record approved narration, align captions to its timestamps, check sound levels",
        "Review actual video cut for pacing, transitions, contrast and mobile-safe text",
        "Verify CTA destination and obtain final human approval before publishing",
    ]
    plan = {
        "status": "UNAPPROVED_VIDEO_PREPRODUCTION_DRAFT",
        "campaign": spec["slug"], "service": spec["service"],
        "aspect_ratio": storyboard["format"], "total_seconds": previous_end,
        "source_register_unverified": facts, "chapters": chapters, "shots": shots,
        "brand": {
            "colors": {"plum": "#481B2E", "tangerine": "#E7714D", "fawn": "#F9E3DB"},
            "logo": "Only authorized RESCU quadrants logo; never invent a substitute",
            "tone": "Physician-led, premium, approachable and clinically restrained",
        },
        "delivery": {
            "formats": ["9:16 Reel", "16:9 website explainer (requires a separately edited version)"],
            "audio": "Use approved/consented recordings; do not synthesize doctor or patient voice",
            "captions": "Approximate timings only; synchronize after final recording",
            "website": "Use accessible MP4/poster, checked VTT and crawlable transcript after approval",
        },
        "checks_before_publish": checks,
    }
    review = {
        "status": "BLOCKED_PENDING_CLINICAL_AND_EDITORIAL_APPROVAL",
        "automated_checks": {
            "scenes": len(shots), "continuous_scene_timing": True,
            "caption_timing": "rough_scene_boundaries_only",
            "source_urls_present": all(bool(f.get("source_url")) for f in facts),
            "output_is_unpublished": True,
        },
        "flags": warnings, "required_human_signoff": checks,
    }
    return {
        "video-production.json": json.dumps(plan, indent=2, ensure_ascii=False),
        "voiceover-draft.txt": "\n\n".join(narration) + "\n\nUNAPPROVED DRAFT — verify sources and record approved audio.\n",
        "captions-draft.vtt": "\n".join(captions),
        "video-quality-review.json": json.dumps(review, indent=2, ensure_ascii=False),
    }
