# Contributing / working in this repository

## Before you commit
1. `bash tools/verify_all.sh` must end with `ALL CHECKS PASSED` (add `--pio` if you touched `firmware/`).
2. If you rename or move a file, run `python tools/check_links.py` and fix every broken reference it prints.
3. If you change a number that appears in the README, the website or the pitch, update [`engineering/claims_register.md`](engineering/claims_register.md) too.
4. Never commit secrets (`secrets.h`, `.env`, keys, tokens). They are in `.gitignore`; if one ever lands in a commit, rotate it, because deleting the file does not remove it from history.
5. Never commit build output (`.pio/`, `__pycache__/`, virtual environments). The mechanical build rewrites tracked files in `mechanical/checks` and `mechanical/cad`: look at `git diff` before committing those.

## Layout rules
* `docs/` is the GitHub Pages website only. Engineering documents go in `engineering/`, superseded ones in `archive/` (move with `git mv`, never delete).
* Every folder has a `README.md`: what is inside, which file to open first, and the exact command to run it.
* The firmware and the Python reference must make the same decisions: `python tools/parity/compare.py`.
* Wording: "designed", not "built"; "a sample for the lab", not "evidence"; pole safety factor 2.66 (conservative case).

## Large files and Git LFS (note only: history has **not** been converted)
The repository holds about 100 MB of videos, STEP files and a Pack-and-Go zip in ordinary Git (largest: `docs/media/*.mp4`,
`mechanical/solidworks/*.zip`, the STEP assembly). `.gitattributes` only marks them binary; it has no LFS filter. If you want LFS
for **new** large files, run `git lfs install` and `git lfs track "*.mp4"` before adding them (this changes `.gitattributes`
and affects everyone who clones). Do not rewrite existing history to LFS without agreeing it with the whole team first: it changes every commit hash.
Preferred alternative for videos: attach them to a GitHub release, as `v1.0-fdc` already does.
