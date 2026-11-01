"""Tests using synthetic, private test fixtures. Real output requires the Drive logo."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

class EditorialDesignTests(unittest.TestCase):
    def test_synthetic_fixture_render_dimensions(self):
        try:
            from PIL import Image, ImageDraw
            from rescu_growth.editorial_design import render
        except ImportError:
            self.skipTest("Optional Pillow dependency absent")
        with TemporaryDirectory() as tmp:
            folder=Path(tmp)
            # Test fixture is not a RESCU mark and is never published.
            mark=Image.new("RGBA",(220,220),(0,0,0,0))
            draw=ImageDraw.Draw(mark)
            draw.ellipse((10,10,210,210),fill=(255,110,30,255))
            mark.save(folder/"fixture.png")
            sheet=Image.new("RGB",(1200,600),"#633647")
            sheet.save(folder/"photos.png")
            spec={"slug":"first-dive-questions","service":"HBOT"}
            (folder/"manifest.json").write_text(json.dumps({"campaigns":[spec]}))
            render(folder/"manifest.json",folder/"fixture.png",folder/"photos.png",folder/"out")
            output=folder/"out"/"campaigns"/"first-dive-questions"
            with Image.open(output/"cover-post.png") as im:
                self.assertEqual(im.size,(1080,1350))
            with Image.open(output/"cover-story.png") as im:
                self.assertEqual(im.size,(1080,1920))

    def test_missing_real_logo_fails_closed(self):
        try:
            from rescu_growth.editorial_design import logo_from_drive_file
        except ImportError:
            self.skipTest("Optional Pillow dependency absent")
        with self.assertRaises(FileNotFoundError):
            logo_from_drive_file("/path/that/does/not/exist.png")
if __name__=="__main__":
    unittest.main()
