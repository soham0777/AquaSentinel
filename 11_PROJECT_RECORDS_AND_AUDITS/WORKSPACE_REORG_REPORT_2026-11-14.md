# Workspace reorganisation — 14 November 2026, evening

> **Historical document.** This describes the 22:20 state on 14 Nov. Later that night, with the project lead's
> approval, the archive, both safety bundles and Claude's worktrees were permanently deleted. The file counts and
> archive paths below therefore no longer describe the current folder. For the current state read
> `00_START_HERE.md`; for the deletion record read `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md`.

**Scope:** the whole `AquaSentinel` project folder. **Rule at the time:** organise and archive; delete nothing.
**Outcome:** every file that existed before the reorganisation still existed afterwards, with the same SHA-256, at a known path. Verified.

## Before → after

| | Before (21:25) | After (22:20) |
|---|---|---|
| Files (excluding `.git`) | 4,265 | 4,281 (16 new README/index/control files) |
| Size | 2.2 GB | 2.63 GB (includes the new 244 MB safety bundle) |
| Empty folders | 2 | 0 |
| Current deck location | `01_FINALE_PRESENTATION/SUBMIT_7Nov_FINAL/` (named 7 Nov, last edited 14 Nov) | `01_FINALE_PRESENTATION/AquaSentinel_Finale_7min.pptx` |
| 7 Nov submission | mixed with the current deck | isolated in `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/` |
| 31 Oct concept renders | mixed into `04_DESIGN_NOTES` | `99_ARCHIVE/11_LiveModel_superseded_31Oct2026/` |
| Backups | loose bundle in `99_ARCHIVE/` | `99_ARCHIVE/_SAFETY_SNAPSHOTS/` with manifest + restore notes |
| Navigation | one start file, several broken links | `00_START_HERE.md` + `README.md` + one README per folder + archive index |

## What was done

1. **Inventoried everything** — 4,265 files, sizes, dates, duplicate names and sizes, empty folders, largest files,
   archive contents. Full CSV: `C:\Users\dell\.qoder\tmp\aqua_inventory.csv` (outside the project, working data).
2. **Safety snapshot before any move**
   - git bundle of all branches: `99_ARCHIVE/_SAFETY_SNAPSHOTS/2026-11-14_pre_workspace_reorg/AquaSentinel_git_all_branches_2026-11-14.bundle`;
   - SHA-256 manifest of all 4,266 files at that moment (`file_manifest_before_reorg.csv`);
   - every move logged with source, destination, size, SHA-256 and reason (`WORKSPACE_REORG_LOG_2026-11-14.csv`).
3. **Separated current from submitted** in `01_FINALE_PRESENTATION`: the 14 Nov deck is now at the top; the 7 Nov PDF and
   zip are isolated as a submission record.
4. **Archived October material** out of the live-model folder (31 Oct concept renders, original kit guide).
5. **Grouped backups** into `99_ARCHIVE/_SAFETY_SNAPSHOTS/`; grouped the pre-Phase-3 code into `_pre_phase3_snapshot/`.
6. **Removed two empty folders** (`SUBMIT_7Nov_FINAL` after its contents moved; the never-used
   `05_R3_FULL_SIZE_CAD/SOLIDWORKS_2026_manual_assembly`). Both are logged as `RMDIR`.
7. **Rebuilt navigation** — `00_START_HERE.md`, root `README.md`, a README in every working folder, `99_ARCHIVE/00_ARCHIVE_INDEX.md`,
   this control folder, and a backup/version-control policy.
8. **Corrected stale facts in navigation** — live-model manual is 30 pages (not 43), 38 STL files (not 37),
   `03_PRINT_RECORDS` and the manual build scripts do not exist, the pH guide link was dead and was removed,
   the electronics manual is Rev 2.0 (14 Nov).
9. **Added honest status blocks** in the root docs: what is bench-proven, what is not yet verified, what is empty in `config.json`.

## Verification

- 4,266 manifest entries re-checked by SHA-256 after all work.
- **4,255 identical, 0 missing.**
- 11 existing files were intentionally re-written, all text: `.gitignore`, `00_START_HERE.md`, `README.md`, the control report,
  `02_LIVE_MODEL_1to5/README.md`, the design-notes banner, `13_…/00_README_START_HERE.md`, `13_…/00_Virtual_Storyteller_Plan.md`,
  `14_RASPBERRY_PI_SOFTWARE/README.md`, and two path fixes in `01_…/00_TODAY_7Nov…` and `09_…/FDC_post_contents_7Nov2026.md`.
  No data, deck, CAD, video or manual content was altered. The new README/index/control files are additions, not changes.

## What was deliberately not touched

- **The deck, CAD, videos, manuals and cost figures** — content changes belong to the problem-fixing work
  (`PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md`). Only paths and navigation were edited.
- **SOLIDWORKS part/assembly names and locations** — moving individual parts breaks external references.
- **`.claude/worktrees`** — 421 MB of hidden Claude Code checkouts; still useful as old-version reference until after the finale.
- **Git content** — no file content or history was rewritten. The reorganisation itself was recorded in a new local
  commit `654764d` (tag `workspace/reorg-2026-11-14`), which resolves the 336 pre-existing deletions; **nothing was pushed**.
  Read `BACKUP_AND_VERSION_CONTROL.md` before pushing or merging.

## Known remaining documentation warnings (not errors)

- `02_LIVE_MODEL_1to5/04_DESIGN_NOTES/LIVE_model_design_notes.md` still describes the 31 Oct layout (`STL_print/`, `previews/`,
  ADS1115, rain plate). It is kept as a historical rationale; the folder README says so.
- `13_…/01_Creative_Experience_Storyline_and_Build_Plan.md` mentions a future file
  `08_VIDEOS/AquaSentinel_Creative_Experience_Godavari.mp4` that has not been made yet (it is an instruction, not a link).
- `14_RASPBERRY_PI_SOFTWARE/README.md` uses Pi-relative paths such as `tools/calibrate_ph.py`; on the Pi the working folder is `~/aquasentinel`.

## How to undo

Every move is one row in `WORKSPACE_REORG_LOG_2026-11-14.csv`. Move the file/folder back from `dst` to `src`; hashes in the
same row prove it is the same content. The git bundle restores the repository state; the manifest proves the file set.
