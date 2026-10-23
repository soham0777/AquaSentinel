# docs/assets: images used by the site and the README

| Path | Contents |
|---|---|
| `banner.png`, `ui/` | README and site graphics (buttons, KPI strip, "sense-decide-act", anatomy, architecture, team, timeline) |
| `renders/` | 12 CAD renders (hero river, alert, exploded, gate open, underwater, motion study…) |
| `slide-01.jpg` … `slide-13.jpg`, `deck-overview.jpg` | page images of the Final Design Concept deck |
| `pole-*.jpg`, `bracket-*.jpg` | SOLIDWORKS Simulation plots (stress and displacement) |
| `detector-evaluation.jpg`, `check-sheet.jpg`, `drawing-ga.jpg`, `dashboard.jpg`, `viewer.jpg`, `enovia-gantt.jpg` | evaluation plot, design-check sheet, general-arrangement drawing, screenshots, project plan |
| `*.gif` | assembly sequence and the float riding the pole |

Everything here is referenced by `docs/index.html` or the root `README.md`. If you rename a file, run `python tools/check_links.py`.
