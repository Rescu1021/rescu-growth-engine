"""Offline tests of RESCU original video planning and Content Factory integration."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from rescu_growth.video_planning import build_video_assets
from rescu_growth.content_studio import produce


def sample():
    spec = {
        "slug": "first-hbot-visit", "service": "HBOT",
        "title": "First HBOT appointment", "hook": "First visit?",
        "intro": "Ask your clinical team about screening and chamber selection.",
        "cta_label": "Explore consultation options",
        "cta_url": "https://rescu.life/book",
        "facts": [{"text": "HBOT uses a pressurized chamber.",
                   "source_url": "https://rescu.life/"}],
    }
    return spec


def storyboard(spec):
    return {"reel_storyboard.json": json.dumps({"format": "9:16", "slides": [
        {"seconds": [0, 4], "title": spec["hook"], "visual": "approved facility"},
        {"seconds": [4, 10], "title": spec["intro"], "visual": "equipment"},
        {"seconds": [10, 16], "title": spec["facts"][0]["text"], "visual": "diagram"},
        {"seconds": [16, 20], "title": spec["cta_label"], "visual": "end card"},
    ]})}


class VideoPlanningTests(unittest.TestCase):
    def test_outputs_require_signoff(self):
        spec = sample()
        assets = build_video_assets(spec, storyboard(spec))
        plan = json.loads(assets["video-production.json"])
        review = json.loads(assets["video-quality-review.json"])
        self.assertEqual(plan["total_seconds"], 20.0)
        self.assertEqual(len(plan["shots"]), 4)
        self.assertEqual(plan["shots"][2]["source_url_for_editor_to_verify"], "https://rescu.life/")
        self.assertIn("BLOCKED_PENDING", review["status"])
        self.assertIn("WEBVTT", assets["captions-draft.vtt"])
        self.assertIn("00:00:16.000 --> 00:00:20.000", assets["captions-draft.vtt"])

    def test_overspeed_voiceover_warning(self):
        spec = sample()
        spec["intro"] = "Word " * 60
        assets = build_video_assets(spec, storyboard(spec))
        review = json.loads(assets["video-quality-review.json"])
        self.assertTrue(any("words/sec" in x for x in review["flags"]))

    def test_discontinuous_scenes_fail(self):
        spec = sample()
        data = storyboard(spec)
        s = json.loads(data["reel_storyboard.json"])
        s["slides"][2]["seconds"] = [11, 16]
        data["reel_storyboard.json"] = json.dumps(s)
        with self.assertRaises(ValueError):
            build_video_assets(spec, data)

    def test_insecure_evidence_rejected(self):
        spec = sample()
        spec["facts"][0]["source_url"] = "http://example.com/medical-claim"
        with self.assertRaises(ValueError):
            build_video_assets(spec, storyboard(spec))

    def test_full_studio_writes_unpublished_video_package(self):
        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "review"
            result = produce({"campaigns": [sample()]}, dest, pngs=False)
            folder = dest / "campaigns" / "first-hbot-visit"
            self.assertEqual(result["video_plans_generated"], 1)
            self.assertTrue((folder / "video-production.json").exists())
            self.assertTrue((folder / "voiceover-draft.txt").exists())
            self.assertTrue((folder / "captions-draft.vtt").exists())
            self.assertIn("BLOCKED_PENDING", (folder / "video-quality-review.json").read_text())
            self.assertFalse((dest / "index.html").exists())


    def test_evidence_first_ozone_campaign_joins_existing_video_lineup(self):
        manifest = json.loads(
            (Path(__file__).resolve().parents[1] / "examples" / "2026-rescu-eight-campaigns.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(len(manifest["campaigns"]), 8)
        ozone = next(c for c in manifest["campaigns"] if c["slug"] == "ozone-consult-basics")
        self.assertIn("evidence", ozone["hook"].lower())
        self.assertIn("Lyme", ozone["intro"])
        self.assertIn("POTS", ozone["intro"])
        self.assertTrue(all(f["source_url"].startswith("https://") for f in ozone["facts"]))
        self.assertEqual(ozone["cta_url"], "https://rescu.life/book")
        with TemporaryDirectory() as tmp:
            report = produce({"campaigns": [ozone]}, Path(tmp), pngs=False)
            self.assertEqual(report["video_plans_generated"], 1)
            folder = Path(tmp) / "campaigns" / "ozone-consult-basics"
            review = json.loads((folder / "video-quality-review.json").read_text())
            self.assertIn("BLOCKED_PENDING", review["status"])
            plan = json.loads((folder / "video-production.json").read_text())
            self.assertEqual(plan["total_seconds"], 20)
            self.assertEqual(len(plan["source_register_unverified"]), 4)
            self.assertIn("WEBVTT", (folder / "captions-draft.vtt").read_text())


if __name__ == "__main__":
    unittest.main()
