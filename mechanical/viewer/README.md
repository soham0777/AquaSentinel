# mechanical/viewer

`template.html` is the source of the interactive 3D viewer. `python mechanical/src/publish.py viewer` embeds the model into it and
writes `mechanical/AquaSentinel_R3_Viewer.html` (not tracked); `docs/viewer.html` is the published copy of that file (copied by hand; never edit it directly). It loads three.js and mp4-muxer from a CDN, so it needs
internet. To preview and capture renders: `python mechanical/tools/serve.py`, then open `viewer/template.html?capture=1`.
