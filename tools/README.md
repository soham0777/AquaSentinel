# tools: checks you can run any time (all read-only)

| Command | What it does |
|---|---|
| `bash tools/verify_all.sh` | Runs everything below in one go and ends with `ALL CHECKS PASSED` or `SOME CHECKS FAILED`. Builds run on temporary copies, so your working tree is never touched. Add `--pio` to also compile the ESP32 firmware (needs `pip install platformio`). |
| `python tools/check_links.py` | Finds broken relative links, images, scripts and backtick-quoted file paths in every tracked file, and absolute links to this repo or its GitHub Pages site. Exit code 1 if anything is broken. |
| `python tools/parity/compare.py` | Compiles the real firmware decision engine for your PC and checks it makes the same decisions as `analytics/detector.py` on all 2,880 synthetic rows. See [`parity/README.md`](parity/README.md). |

Set-up once: `pip install -r requirements.txt` (numpy, matplotlib, Pillow) and have a C++17 compiler (or `pip install ziglang`).

The project's own build scripts are not here: the mechanical design engine lives in [`../mechanical/src`](../mechanical/src) and
the 1:5 model generator in [`../mechanical/scale_model_1to5`](../mechanical/scale_model_1to5).
