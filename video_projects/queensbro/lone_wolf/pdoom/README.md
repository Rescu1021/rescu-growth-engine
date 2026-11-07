# Lone Wolf on the P(doom) engine

Uses mexicat/pdoom-video, pinned to fa164b74fd0b26a99375715b619c55b4a0fb3d05. Keep its MIT license and font licenses in the checkout.

```sh
git clone https://github.com/mexicat/pdoom-video.git pdoom-lone-wolf
git -C pdoom-lone-wolf checkout fa164b74fd0b26a99375715b619c55b4a0fb3d05
python video_projects/queensbro/lone_wolf/pdoom/adapt.py pdoom-lone-wolf
cd pdoom-lone-wolf/app
npm install
npx vite build
npx vite
```

The adapter installs a new Three.js scene, camera drift, dimensional rain, the Queensbro cover, 1080x1920 logical canvas, a 119-second timeline and provisional word highlights. It uses the actual upstream Engine, Scene, Layer2D and Lyrics classes.

Timing is estimated from the existing phrase cues. No vocals or beat analysis are supplied. The original P(doom) song is removed. Add and align the authorized Lone Wolf recording before final export.

Validation: Vite production build passed locally. Browser validation could not run because the workspace denied Chromium's required socket operation. No new P(doom) MP4 has been rendered. The earlier FFmpeg video remains a separate visual draft.

The upstream offline renderer assumes a landscape 1920x1080 export and macOS Chrome. Its dimensions and Chrome launch configuration must be adapted for this portrait/Linux project before using it for MP4 export. This is an integration in progress, not a final video.
