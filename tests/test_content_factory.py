"""Offline tests for the RESCU Content Factory."""
import json
import unittest
from rescu_growth.content_factory import build

def sample():
    return {"slug": "first-hbot-visit-scarsdale", "service": "HBOT",
            "title": "Your first HBOT visit",
            "intro": "Learn what to ask about an introductory visit at RESCU.",
            "hook": "Questions about hyperbaric oxygen?",
            "cta_label": "Explore booking",
            "cta_url": "https://rescu.life/book?ref=first-dive",
            "facts": [{"text": "RESCU has an HBOT service page.",
                       "source_url": "https://rescu.life/"}]}

class ContentFactoryTests(unittest.TestCase):
    def test_build_pack(self):
        output = build(sample())
        self.assertEqual(set(output), {"landing.html", "instagram.txt", "reel_storyboard.json", "review.json"})
        self.assertIn('rel="canonical"', output["landing.html"])
        self.assertIn("utm_medium=article", output["landing.html"])
        self.assertIn("ref=first-dive", output["landing.html"])
        self.assertIn("Source 1", output["landing.html"])
        self.assertIn("NOT APPROVED", output["review.json"])
        self.assertEqual(len(json.loads(output["reel_storyboard.json"])["slides"]), 4)

    def test_no_patient_data(self):
        item = sample(); item["patient_name"] = "Example"
        with self.assertRaises(ValueError): build(item)

    def test_requires_fact_source(self):
        item = sample(); del item["facts"][0]["source_url"]
        with self.assertRaises(ValueError): build(item)

    def test_cta_must_be_rescu(self):
        item = sample(); item["cta_url"] = "https://other.example/"
        with self.assertRaises(ValueError): build(item)

    def test_html_escaped(self):
        item = sample(); item["title"] = '<script>alert("bad")</script>'
        self.assertNotIn("<script>", build(item)["landing.html"])

    def test_flags_dubious_claim(self):
        item = sample(); item["hook"] = "Guaranteed instant results"
        self.assertTrue(json.loads(build(item)["review.json"])["risky_claim_flags"])

if __name__ == "__main__":
    unittest.main()
