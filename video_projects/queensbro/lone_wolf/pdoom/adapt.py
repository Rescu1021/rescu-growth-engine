from pathlib import Path
import json, shutil
import sys
src=Path(__file__).resolve().parent.parent
p=Path(sys.argv[1]).resolve()
t=json.loads((src/'timeline.json').read_text())
lines=[]
for cue in t['cues']:
 words=cue['text'].split(); span=(cue['end']-cue['start'])/len(words)
 lines.append(dict(text=cue['text'],start=cue['start'],end=cue['end'],words=[dict(w=w,start=cue['start']+i*span,end=cue['start']+(i+1)*span) for i,w in enumerate(words)]))
(p/'data/lyrics.json').write_text(json.dumps(dict(timing_status='provisional',lines=lines)))
(p/'data/audio.json').write_text(json.dumps(dict(duration=119,bpm=60,fps=30,beats=[],downbeats=[],sections=[],features={},onsets={},status='no audio; neutral visual clock only')))
shutil.copy(src/'assets/cover.jpg',p/'app/public/lone-wolf.jpg')
f=p/'app/src/engine/gl.ts'; f.write_text(f.read_text().replace('W = 1920','W = 1080').replace('H = 1080','H = 1920'))
(p/'app/src/timeline.ts').write_text("export function makeTimeline(){return [{id:'lonewolf',start:0,end:119,load:()=>import('./scenes/lonewolf')}];}\n")
(p/'app/src/scenes/lonewolf.ts').write_text('''import * as THREE from 'three';
import {Scene,type Frame} from '../engine/scene';
import {Layer2D} from '../engine/gl';
export default class LoneWolf extends Scene {
 world=new THREE.Scene(); camera=new THREE.PerspectiveCamera(48,1080/1920,.1,100);
 layer=new Layer2D(); group=new THREE.Group();
 async init(){
 this.camera.position.z=12; this.world.background=new THREE.Color('#080f1b');
 const tex=await new THREE.TextureLoader().loadAsync('/lone-wolf.jpg');tex.colorSpace=THREE.SRGBColorSpace;
 const art=new THREE.Mesh(new THREE.PlaneGeometry(5.6,5.6),new THREE.MeshBasicMaterial({map:tex}));art.position.y=2;this.world.add(art);
 const mat=new THREE.LineBasicMaterial({color:0xc39859,transparent:true,opacity:.45});
 for(let i=0;i<70;i++){const x=Math.sin(i*24.3)*5,y=Math.cos(i*7.1)*10,z=-2-(i%9);const g=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x,y,z),new THREE.Vector3(x-.025,y+.2,z)]);this.group.add(new THREE.Line(g,mat));}this.world.add(this.group);
 }
 render(f:Frame,out:THREE.WebGLRenderTarget){
 const {renderer,comp,lyrics}=this.ctx;
 this.camera.position.x=.18*Math.sin(f.t*.12);this.camera.lookAt(0,0,0);this.group.position.y=-(f.t*.3%1);
 renderer.setRenderTarget(out);renderer.clear();renderer.render(this.world,this.camera);
 const c=this.layer.ctx;this.layer.clear();c.fillStyle='#080f1b';c.fillRect(0,1250,1080,670);
 const l=lyrics.lineAt(f.t);c.textAlign='center';c.font='bold 62px sans-serif';
 if(l){let rows:string[][]=[[]];for(const word of l.words){let row=rows[rows.length-1]!;if(c.measureText([...row,word.w].join(' ').toUpperCase()).width>850)rows.push([word.w]);else row.push(word.w);}
 let wi=0;rows.forEach((row,ri)=>{let total=c.measureText(row.join(' ').toUpperCase()).width;let x=540-total/2;c.textAlign='left';for(const token of row){const w=l.words[wi++]!;c.fillStyle=f.t>=w.start?'#f1bf67':'#f6efe5';c.fillText(token.toUpperCase(),x,1380+ri*84);x+=c.measureText(token.toUpperCase()+' ').width;}});
 }else{c.textAlign='center';c.fillStyle='#f6efe5';c.fillText('LONE WOLF',540,1430);}
 c.textAlign='center';c.font='24px sans-serif';c.fillStyle='#c39859';c.fillText('QUEENSBRO',540,1760);
 comp.draw(renderer,this.layer.upload(),out);return {bloom:0.1,grain:.025,hud:0};
 }
}
''')
print('Adapted pdoom engine with 68 provisional lyric cues and original 3D scene')

# Keep the original project's song out of this adaptation.
for f in (p/'audio').glob('*.mp3'): f.unlink()
