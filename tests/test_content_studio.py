"""Offline tests for campaign batching: no paid services or network."""
from __future__ import annotations
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from rescu_growth.content_studio import produce

def campaign(slug="trilift-review"):
    return {"slug":slug,"title":"What to ask about TriLift","hook":"Questions before a demo?",
            "service":"TriLift", "intro":"Discuss goals and suitability with the team.",
            "cta_label":"Book a conversation","cta_url":"https://rescu.life/book",
            "facts":[{"text":"Rescu offers TriLift.",
                      "source_url":"https://rescu.life/trilift"}]}

class ContentStudioTests(unittest.TestCase):
    def test_batch_no_images(self):
        with TemporaryDirectory() as directory:
            output=Path(directory)/"output"
            report=produce({"campaigns":[campaign(),campaign("hbot-review")]},output,pngs=False)
            self.assertEqual(report["campaigns"],2)
            self.assertTrue((output/"campaigns"/"trilift-review"/"landing.html").exists())
            self.assertTrue((output/"campaigns"/"hbot-review"/"instagram.txt").exists())
            self.assertIn("NOT APPROVED", (output/"campaigns"/"trilift-review"/"review.json").read_text())
            with (output/"content-calendar.csv").open(newline="") as file:
                rows=list(csv.DictReader(file))
            self.assertEqual(len(rows),2)
            self.assertTrue(all(r["status"]=="DRAFT_REQUIRES_REVIEW" for r in rows))
            self.assertFalse((output/"index.html").exists())
            self.assertIn("utm_medium=reel", (output/"campaign-links.csv").read_text())

    def test_duplicate_slugs_rejected_before_writes(self):
        with TemporaryDirectory() as directory:
            output=Path(directory)/"out"
            with self.assertRaises(ValueError):
                produce({"campaigns":[campaign(),campaign()]},output,pngs=False)
            self.assertFalse(output.exists())

    def test_traversal_slug_rejected(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                produce({"campaigns":[campaign("../steal")]},Path(directory)/"out",pngs=False)

    def test_missing_fact_source_rejected(self):
        item=campaign();item["facts"]=[{"text":"Bad unsupported claim"}]
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                produce({"campaigns":[item]},Path(directory)/"out",pngs=False)

    def test_image_dashboard_optional_pillow(self):
        try:
            import PIL
        except ImportError:
            self.skipTest("Pillow optional for image rendering")
        from PIL import Image
        with TemporaryDirectory() as directory:
            output=Path(directory)/"out"
            produce({"campaigns":[campaign()]},output,pngs=True)
            self.assertIn("PRIVATE DRAFTS", (output/"index.html").read_text())
            post=output/"campaigns"/"trilift-review"/"cover-post.png"
            story=output/"campaigns"/"trilift-review"/"cover-story.png"
            with Image.open(post) as im: self.assertEqual(im.size,(1080,1350))
            with Image.open(story) as im: self.assertEqual(im.size,(1080,1920))

if __name__=="__main__":
    unittest.main()
