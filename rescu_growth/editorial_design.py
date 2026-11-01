"""Original RESCU editorial covers using real, externally supplied logo assets.

Requires Pillow and a local 4x2 image contact sheet. No paid API, network,
patient data, automatic publishing, or imitation logos.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

PLUM=(72,27,46);ORANGE=(231,113,77);FAWN=(249,227,219);LAVENDER=(186,165,192);CHALK=(247,247,247)
TITLES={
"first-dive-questions":("THE FIRST","DIVE.","HBOT / FIRST VISIT"),
"trilift-demo-guide":("FACE","WORKOUT.","TRILIFT / DMSt"),
"skin-plan-questions":("SIX WEEKS.","ONE PLAN.","RESCU SKIN PLAN"),
"rescu-reset-first-visit":("THE","RESET.","RED LIGHT + PEMF"),
"emsella-consult-questions":("LET'S TALK","PELVIC FLOOR.","EMSELLA / CONSULT"),
"corporate-wellness-pilot":("WELLNESS","AT WORK.","FOR YOUR TEAM"),
"emsculpt-neo-first-visit":("BEYOND","THE SCALE.","EMSCULPT NEO"),
"ozone-consult-basics":("QUESTIONS","COME FIRST.","OZONE CONSULTATION")}
PHOTO_IDX={s:i for i,s in enumerate(TITLES)}

def font(size,regular=False):
    paths=(["/usr/share/fonts/truetype/lato/Lato-Regular.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"] if regular else
           ["/usr/share/fonts/truetype/lato/Lato-Heavy.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"])
    for path in paths:
        if Path(path).exists():return ImageFont.truetype(path,int(size))
    return ImageFont.load_default(size=int(size))

def crop_to(img,size,fy=.5):
    w,h=size;iw,ih=img.size;r=max(w/iw,h/ih);rw,rh=int(iw*r)+2,int(ih*r)+2
    up=img.resize((rw,rh),Image.Resampling.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1,percent=120,threshold=2))
    return up.crop(((rw-w)//2,int((rh-h)*fy),(rw+w)//2,int((rh-h)*fy)+h))

def logo_from_drive_file(path):
    logo=Image.open(path).convert("RGBA")
    bb=logo.getchannel("A").getbbox()
    if not bb:raise ValueError("Supplied logo is empty")
    logo=logo.crop(bb)
    if not .85 < logo.width/logo.height < 1.2:
        raise ValueError("Expected official circular four-quadrant logo")
    return logo

def collage_tiles(path):
    im=Image.open(path).convert("RGB");w,h=im.size
    return [im.crop((x*w//4+2,y*h//2+2,(x+1)*w//4-2,(y+1)*h//2-2))
            for y in range(2) for x in range(4)]

def fitted_title(d,s,limit,px):
    f=font(px)
    while px>42 and d.textbbox((0,0),s,font=f)[2]>limit:
        px-=2;f=font(px)
    return f

def cover(spec,photo,logo,index,story=False):
    w,h=(1080,1920) if story else (1080,1350)
    ph=int(h*(.60 if story else .635))
    out=Image.new("RGB",(w,h),CHALK)
    pic=crop_to(photo,(w,ph),.44 if index in (1,2) else .5)
    out.paste(ImageEnhance.Contrast(pic).enhance(1.08),(0,0))
    d=ImageDraw.Draw(out);d.rectangle((0,0,17,ph),fill=ORANGE)
    d.rounded_rectangle((60,65,355,122),radius=3,fill=PLUM)
    d.text((80,79),"RESCU  /  JOURNAL",font=font(26),fill=CHALK)
    size=189; x,y=w-277,58
    d.rounded_rectangle((x-15,y-15,x+size+15,y+size+15),radius=20,fill=CHALK)
    badge=logo.resize((size,size),Image.Resampling.LANCZOS)
    out.paste(badge,(x,y),badge);d=ImageDraw.Draw(out)
    py=ph-92
    d.polygon([(0,py+44),(w,py-54),(w,h),(0,h)],fill=FAWN)
    d.line((60,py+145,w-60,py+145),fill=PLUM,width=2)
    d.text((64,py+100),f"{index+1:02}   /   08",font=font(27),fill=PLUM)
    d.text((285,py+100),"SCIENCE  /  SELF  /  WELLNESS",font=font(22,True),fill=PLUM)
    lines=TITLES.get(spec["slug"],("EXPLORE","RESCU.",spec["service"].upper()))
    ty=py+(205 if story else 172)
    for line in lines[:2]:
        face=fitted_title(d,line,w-128,124 if story else 91)
        d.text((65,ty),line,font=face,fill=PLUM)
        ty+=int(face.size*1.02)+6
    d.text((68,ty+(12 if story else 10)),lines[2],font=font(29,True),fill=PLUM)
    bottom=h-(245 if story else 130)
    d.rectangle((65,bottom-28,480,bottom+36),fill=PLUM)
    d.text((82,bottom-18),"EXPLORE AT RESCU.LIFE",font=font(25),fill=CHALK)
    d.ellipse((w-133,bottom-36,w-65,bottom+32),fill=ORANGE)
    d.line([(w-115,bottom+1),(w-85,bottom+1)],fill=PLUM,width=5)
    d.line([(w-97,bottom-11),(w-83,bottom+1),(w-97,bottom+13)],fill=PLUM,width=5)
    d.text((65,h-34),"CONCEPT VISUAL · NOT A RESCU EQUIPMENT OR CLIENT PHOTO",font=font(15,True),fill=PLUM)
    return out

def render(manifest_path,logo_path,photo_sheet_path,output_dir):
    specs=json.loads(Path(manifest_path).read_text(encoding="utf-8"))["campaigns"]
    logo=logo_from_drive_file(logo_path);tiles=collage_tiles(photo_sheet_path)
    output=Path(output_dir);output.mkdir(parents=True,exist_ok=True)
    for i,spec in enumerate(specs):
        slug=spec["slug"];picture=tiles[PHOTO_IDX.get(slug,i%8)]
        dst=output/"campaigns"/slug;dst.mkdir(parents=True,exist_ok=True)
        for is_story,name in [(False,"cover-post.png"),(True,"cover-story.png")]:
            cover(spec,picture,logo,i,story=is_story).save(dst/name,optimize=True)
    return output

def main():
    p=argparse.ArgumentParser(description="RESCU editorial redesign from official, local assets")
    p.add_argument("--manifest",required=True);p.add_argument("--logo",required=True)
    p.add_argument("--photo-sheet",required=True);p.add_argument("--output-dir",required=True)
    a=p.parse_args()
    print(render(a.manifest,a.logo,a.photo_sheet,a.output_dir))

if __name__=="__main__":main()
