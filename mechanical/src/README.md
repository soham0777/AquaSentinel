# mechanical/src: the parametric design engine

Edit dimensions in `params.py`, rebuild, and everything downstream updates (needs `pip install -r ../../requirements.txt`):

```bash
cd mechanical
python src/build.py          # geometry, 14 design checks, STEP/STL/GLB exports, BOM (about 15 s)
python src/drawings.py       # the 6-sheet A3 drawing set
python src/check_sheet.py    # the design-check sheet image
```

| File | Job |
|---|---|
| `params.py` | every dimension, material and assumption (single source of truth) |
| `geom.py` | small polygon-mesh modelling kernel used to build the parts |
| `parts.py` | the 66 parts and the assembly tree |
| `analysis.py` | mass, hydrostatics, stability, drag, pole and carriage checks, clearances |
| `export.py` | binary STL, GLB and STEP AP214 writers |
| `build.py` | runs everything and writes `checks/`, `cad/` |
| `drawings.py`, `drafting.py`, `check_sheet.py` | drawing sheets and the check sheet |
| `publish.py` | final packaging: motion-study composite, assembly GIF, standalone viewer (`python src/publish.py viewer` writes `mechanical/AquaSentinel_R3_Viewer.html`) |

`build.py` writes into `mechanical/checks` and `mechanical/cad`, i.e. into tracked files: run `git diff` afterwards, or use
`bash tools/verify_all.sh`, which runs it on a temporary copy.
