"""Create free, silent, RESCU-branded video drafts with Pillow + FFmpeg."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

PLUM=(72,27,46)
ORANGE=(231,113,77)
FAWN=(249,227,219)
WHITE=(255,255,255)

def font(size,bold=False):
    from PIL import ImageFont
    names=["/usr/share/fonts/truetype/msttcorefonts/Montserrat-Bold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for path in names:
        if Path(path).is_file():
            return ImageFont.truetype(path,size)
    return ImageFont.load_default(size=size)

def wrap(draw,title,face,limit):
    lines=[]; current=""
    for word in title.split():
        trial=(current+" "+word).strip()
        if draw.textbbox((0,0),trial,font=face)[2]<=limit:
            current=trial
        else:
            if current: lines.append(current)
            current=word
    if current: lines.append(current)
    return lines

def render_card(slide,index,total,path):
    from PIL import Image, ImageDraw
    w,h=720,1280
    picture=Image.new("RGB",(w,h),PLUM)
    d=ImageDraw.Draw(picture)
    d.ellipse((340,90,930,680),outline=ORANGE,width=3)
    d.ellipse((-360,650,330,1340),outline=FAWN,width=2)
    d.rectangle((48,70,130,80),fill=ORANGE)
    d.text((48,101),"RESCU WELLNESS",font=font(23,True),fill=FAWN)
    d.text((48,150),"SCARSDALE / EDUCATIONAL SERIES",font=font(18),fill=FAWN)
    title=str(slide["title"]).strip()
    size=62
    while True:
        face=font(size,True); lines=wrap(d,title,face,w-110); step=int(size*1.42)
        if len(lines)*step<670 or size<=30: break
        size-=3
    y=max(315,(h-step*len(lines))//2-20)
    for line in lines:
        d.text((52,y),line,font=face,fill=WHITE); y+=step
    d.rectangle((48,h-210,w-48,h-200),fill=(103,56,66))
    d.rectangle((48,h-210,48+int((w-96)*(index+1)/total),h-200),fill=ORANGE)
    d.text((48,h-168),"DRAFT - CLINICAL APPROVAL REQUIRED",font=font(18),fill=FAWN)
    d.text((w-92,h-170),f"{index+1:02}",font=font(18),fill=FAWN)
    picture.save(path)

def render(storyboard,output):
    if not shutil.which("ffmpeg"): raise RuntimeError("Install FFmpeg to render MP4")
    slides=storyboard.get("slides")
    if not isinstance(slides,list) or not slides: raise ValueError("No storyboard slides")
    output=Path(output).resolve(); output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rescu_reel_") as tmp:
        folder=Path(tmp); playlist=[]
        for i,slide in enumerate(slides):
            start,end=slide["seconds"]; seconds=float(end)-float(start)
            if not 0<seconds<=30: raise ValueError("Invalid scene duration")
            img=folder/f"scene-{i:02d}.png"
            render_card(slide,i,len(slides),img)
            playlist.extend([f"file '{img}'",f"duration {seconds}"])
        playlist.append(f"file '{img}'")
        scenes=folder/"scenes.txt"; scenes.write_text("\n".join(playlist)+"\n")
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat",
             "-safe","0","-i",str(scenes),"-vf","fps=24,format=yuv420p",
             "-t",str(slides[-1]["seconds"][1]),"-c:v","libx264",
             "-preset","fast","-crf","25","-movflags","+faststart","-an",str(output)]
        subprocess.run(cmd,check=True)

def main():
    p=argparse.ArgumentParser(description="Render silent RESCU reel drafts offline")
    p.add_argument("--storyboard",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    render(json.loads(a.storyboard.read_text(encoding="utf8")),a.output)
    print("Video draft:",a.output)

if __name__=="__main__": main()
