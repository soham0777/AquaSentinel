# docs: the project website (GitHub Pages)

This folder **is** the website <https://soham0777.github.io/AquaSentinel/>: GitHub Pages serves everything in `docs/`.
Keep it to site files only; engineering documents live in [`../engineering`](../engineering).

| Path | What it is |
|---|---|
| [`index.html`](index.html) | the home page (single file; open it in a browser) |
| [`viewer.html`](viewer.html) | interactive 3D model. **Generated**: the template [`../mechanical/viewer/template.html`](../mechanical/viewer/template.html) with the model (`mechanical/cad/assembly/AquaSentinel_R3.glb`) embedded. `python mechanical/src/publish.py viewer` writes `mechanical/AquaSentinel_R3_Viewer.html`; copy it over this file to publish. Edit the template, not this file. Needs internet (three.js is loaded from a CDN) |
| [`dashboard/`](dashboard) | the three-language command-dashboard demo (see its README) |
| [`assets/`](assets) | images, GIFs and slide pictures used by the site and the main README |
| [`media/`](media) | the three videos and the hero loop, with poster images |
| [`presentation/`](presentation) | the Final Design Concept deck PDF, as submitted |
| [`REORG_NOTES.md`](REORG_NOTES.md) | what the 23 Oct reorganisation moved, and the open to-do list |

Preview locally: `cd docs && python -m http.server 8000`, then open <http://localhost:8000/>.
Check every link and image: `python tools/check_links.py` (from the repository root).
