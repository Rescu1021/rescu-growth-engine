#!/usr/bin/env python3
"""Re-renderable vertical HBOT athlete lyric reel. Original beats and vector art."""
import json, math, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "creative.json").read_text())
W, H, FPS = 720, 1280, 24
CORAL = (255, 101, 59)
PALE = (247, 246, 241)
BG = (12, 12, 23)
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]
def font(size):
    for path in FONT_PATHS:
        try: return ImageFont.truetype(path, size)
        except OSError: pass
    return ImageFont.load_default()

def original_art(n):
    """Draw ten-second sport / oxygen / physician / booking backdrops."""
    im = Image.new("RGB", (W, H), BG).convert("RGBA")
    glow = Image.new("RGBA", (W, H))
    g = ImageDraw.Draw(glow)
    g.ellipse((-140, 220, 600, 960), fill=(*CORAL, 65))
    glow = glow.filter(ImageFilter.GaussianBlur(200))
    im = Image.alpha_composite(im, glow)
    overlay = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(overlay)
    for k in range(12):
        x = k * 111 - 220 + n * 19
        d.line((x, 0, x + 580, H), fill=(195, 168, 195, 32), width=3)
    for r in (180, 260, 345):
        d.ellipse((360-r, 610-r, 360+r, 610+r), outline=(*CORAL, 85), width=5)
    if n in (0, 1, 4):
        # Abstract original athletic sprinter / jumper icon, not a specific person.
        d.ellipse((300, 375, 385, 460), fill=(*PALE, 235))
        pts = [(345,460,345,660),(345,515,260,590),(260,590,150,585),
               (345,525,450,480),(450,480,530,520),
               (345,660,240,790),(240,790,145,905),
               (345,660,460,750),(460,750,570,745)]
        for j in range(0, len(pts)-1, 2):
            d.line((*pts[j], *pts[j+1]), fill=(*PALE, 235), width=19, joint="curve")
    elif n == 2:
        d.rounded_rectangle((80, 450, 640, 870), radius=170,
                            fill=(110, 90, 126, 175), outline=(*PALE, 210), width=14)
        d.ellipse((185, 522, 535, 800), outline=(*CORAL, 230), width=15)
        d.ellipse((238, 572, 482, 758), fill=(12, 17, 32, 255),
                  outline=(*PALE, 140), width=4)
    elif n == 3:
        for i in range(32):
            angle = i * 2.39996
            rad = 65 + 10*i
            x = int(360 + math.cos(angle)*rad)
            y = int(650 + math.sin(angle)*rad)
            d.ellipse((x-7,y-7,x+7,y+7), fill=(*PALE, 160))
    elif n == 5:
        for k in range(-250, 920, 130):
            d.line((k, 450, k+400, -50), fill=(*CORAL, 55), width=15)
    d.rectangle((38, 87, 682, 91), fill=(*CORAL, 240))
    d.text((40, 111), "RESCU PERFORMANCE / ATHLETE RECOVERY",
           font=font(22), fill=PALE)
    d.rectangle((38, 1175, 682, 1179), fill=(*CORAL, 240))
    d.text((40, 1200), "ONE BODY. ONE LIFE.  •  SCARSDALE, NY",
           font=font(20), fill=PALE)
    im = Image.alpha_composite(im, overlay)
    logo = HERE / "rescu-logo.png"
    if logo.exists():
        lg = Image.open(logo).convert("RGBA")
        lg.thumbnail((145, 145))
        badge = Image.new("RGBA", (165,165), (251,251,249,248))
        badge.alpha_composite(lg, ((165-lg.width)//2, (165-lg.height)//2))
        im.alpha_composite(badge, (512, 975))
    return im.convert("RGB")

def stamp(sec):
    c = int(round(sec*100)); h,c=divmod(c,360000)
    m,c=divmod(c,6000); s,cs=divmod(c,100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
def make_ass():
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,DejaVu Sans,53,&H00F7F6F1,&H00F7F6F1,&H00100C13,&H00000000,-1,0,0,0,100,100,0,0,1,3,4,5,50,50,0,1
Style: Lower,DejaVu Sans,22,&H00F7F6F1,&H00F7F6F1,&H00100C13,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,30,30,80,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events=[]
    for scene in CFG["scenes"]:
        lines=scene["lines"]
        step=(scene["end"]-scene["start"])/len(lines)
        for i,phrase in enumerate(lines):
            a=scene["start"]+i*step; b=a+step
            color="&H003B65FF" if i%2==0 else "&H00F7F6F1"
            safe=phrase.replace(" ", " ")
            if len(safe)>24: safe=safe.replace(" ", r"\N",1)
            y=690
            if scene["start"]==50: y=650
            effects = rf"{{\c{color}\fad(200,150)\fscx92\fscy92\t(0,220,\fscx100\fscy100)\pos(360,{y})}}"
            events.append(f"Dialogue: 1,{stamp(a)},{stamp(b)},Main,,0,0,0,,{effects}{safe}")
    events += [
      f"Dialogue: 2,{stamp(50)},{stamp(60)},Lower,,0,0,0,,"
      r"{\pos(360,850)}111 BROOK STREET · SUITE 106",
      f"Dialogue: 2,{stamp(50)},{stamp(60)},Lower,,0,0,0,,"
      r"{\pos(360,891)}SCARSDALE, NY",
      f"Dialogue: 2,{stamp(50)},{stamp(60)},Lower,,0,0,0,,"
      r"{\pos(360,936)}RESCU.LIFE/BOOK · 914-401-8552",
      f"Dialogue: 3,{stamp(0)},{stamp(60)},Lower,,0,0,0,,"
      r"{\fs16\pos(360,1102)}HBOT: wellness support · screening required · results vary"
    ]
    (HERE/"lyrics.ass").write_text(header+"\n".join(events)+"\n")

def make_original_beat():
    """Create original non-sampled kick/snare/bass/synth score."""
    sr, duration, bpm = 22050, 60, 112
    n=sr*duration; y=np.zeros(n,dtype=np.float32)
    rng=np.random.default_rng(2026); step=60/bpm
    def add(start,v,gain):
        i=int(start*sr)
        if i<0 or i>=n: return
        z=min(n,i+len(v));y[i:z]+=v[:z-i]*gain
    for beat in range(math.ceil(duration/step)):
        t=beat*step
        u=np.arange(int(.36*sr))/sr
        f=48+110*np.exp(-u*24)
        add(t,np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-u*18),.48)
        if beat%4 in (1,3):
            u=np.arange(int(.16*sr))/sr
            s=(rng.standard_normal(len(u))*.7 + .3*np.sin(2*np.pi*170*u))*np.exp(-u*28)
            add(t,s,.20)
        for h in range(2):
            u=np.arange(int(.07*sr))/sr
            noise=rng.standard_normal(len(u))
            add(t+h*step/2,np.tanh(np.diff(noise,prepend=0))*np.exp(-u*55),.05)
        if beat%2==0:
            root=[43.65,38.89,34.65,32.70][(beat//8)%4]
            u=np.arange(int(.46*sr))/sr
            add(t,(np.sin(2*np.pi*root*u)+.24*np.sin(4*np.pi*root*u))
                *np.exp(-u*4),.18)
    edge=np.minimum(1,np.arange(n)/(sr*.3))*np.minimum(1,(n-np.arange(n))/(sr*.8))
    y=np.tanh(y*edge*1.7); y/=max(float(np.max(np.abs(y))),1e-6)
    with wave.open(str(HERE/"original_beat.wav"),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((y*26000).astype("<i2").tobytes())

def main():
    for i in range(6): original_art(i).save(HERE/f"shot_{i}.png")
    make_ass(); make_original_beat()
    args=["ffmpeg","-hide_banner","-loglevel","error","-y"]
    for i in range(6):
        args += ["-loop","1","-framerate","24","-i",str(HERE/f"shot_{i}.png")]
    args+=["-i",str(HERE/"original_beat.wav")]
    filters=[]
    for i in range(6):
        filters.append(f"[{i}:v]zoompan=z='min(zoom+0.00019,1.05)':d=240:"
                       f"s=720x1280:fps=24,trim=duration=10,setpts=PTS-STARTPTS[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(6))+
                   "concat=n=6:v=1:a=0[concat]")
    filters.append(f"[concat]ass={HERE/'lyrics.ass'}[out]")
    args += ["-filter_complex",";".join(filters),"-map","[out]","-map","6:a",
             "-t","60","-c:v","libx264","-crf","23","-preset","veryfast",
             "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
             "-movflags","+faststart",str(HERE/"rescu_hbot_athletes.mp4")]
    subprocess.run(args,check=True)
    print("Rendered",HERE/"rescu_hbot_athletes.mp4")
if __name__=="__main__": main()
