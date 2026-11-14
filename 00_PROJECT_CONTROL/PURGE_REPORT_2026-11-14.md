# Purge report — 14 November 2026

Approved by the project lead on 14 Nov 2026: delete old and unrelated
content so the folder contains only the current project.

## Before and after

| Measure | Before purge (14 Nov, ~22:55) | After purge (14 Nov, ~23:10) | Change |
|---|---|---|---|
| Files (excluding `.git`) | 4,281 | **1,034** | −3,247 (−76 %) |
| Working-folder size | ~2.25 GB | **807 MB** | −1.44 GB (−64 %) |
| Size including `.git` | ~2.5 GB | **1.1 GB** | −1.4 GB |
| Empty folders | 0 | 0 | — |

Every remaining folder is current work: the deck and its 7 Nov submission
record, the 1:5 model, R3 CAD, simulation, cost, videos, submissions,
electronics, storytelling, Pi software, and project control.

## What was deleted

| Item | Size | Files | Why |
|---|---|---|---|
| `.claude/worktrees/` — two Claude Code checkouts | 421 MB | 940 | Duplicate checkouts. Their commits are on local branches `claude/moisture-sensor-solidworks-29a086` and `publish/numbered-layout`. |
| `99_ARCHIVE/01_SemiFinal_Deck_Oct2026` | 36 MB | — | Superseded deck and video. |
| `99_ARCHIVE/02_ESP32_Electronics_superseded` | 268 KB | — | Abandoned ESP32 design. |
| `99_ARCHIVE/03_Old_Reports` | 6.8 MB | — | Superseded reports. |
| `99_ARCHIVE/04_Old_Audit_and_Analytics` | 5.1 MB | — | Superseded analysis. |
| `99_ARCHIVE/05_Finale_Deck_first_draft` | 22 MB | — | First draft of the current deck. |
| `99_ARCHIVE/06_Finale_Deck_before_wording_fix_7Nov` | 46 MB | — | Pre-wording-fix copy; the submitted version is in `01_FINALE_PRESENTATION/_SUBMISSION_RECORD_7Nov2026/`. |
| `99_ARCHIVE/07_Other_coursework` | 4.0 MB | — | Unrelated coursework. |
| `99_ARCHIVE/08_RPi_design_before_name_removal` | 864 KB | — | Superseded Pi design. |
| `99_ARCHIVE/09_Cleanup_2026-11-14` | 682 MB | — | Old ADS1115 electronics (15 MB), superseded videos (231 MB), virtual-storyteller build (349 MB), LinkedIn post, old booth, scratch manual, pre-Phase-3 snapshot, pre-Phase-2 deck. |
| `99_ARCHIVE/11_LiveModel_superseded_31Oct2026` | 7.8 MB | — | 31 Oct concept renders, replaced by the current LIVE model. |
| `99_ARCHIVE/_SAFETY_SNAPSHOTS` | 487 MB | — | Two git bundles (8 Nov and 14 Nov) and the pre-reorg copy of the manifest. Git itself holds all tracked history. |
| Archive logs (`REORGANISATION_LOG` for 6 and 7 Nov) and `00_ARCHIVE_INDEX.md` | < 20 KB | — | Described folders that no longer exist. |
| Python caches (`__pycache__`, `*.pyc`) | < 1 MB | 7 | Regenerated automatically. |
| Empty `08_VIDEOS/00_source_recordings/` | 0 | 0 | Raw recordings were never stored there. |

The old worktree held four untracked folders. Three contained material that
was either rescued or explicitly recorded as superseded in the 5 Nov audit
(`17_R3_PI_HARDWARE_FIT`). The FDC banner images had already been used on the
portal; the post itself is recorded in `09_SUBMISSIONS_AND_CERTIFICATES/03_FDC_Update_7Nov2026/`.

## What was rescued before deletion

All four copies were checked byte-for-byte against the pre-purge manifest:

| Rescued file | New home | SHA-256 prefix |
|---|---|---|
| 5 Nov design audit and roadmap | `00_PROJECT_CONTROL/DEEP_AUDITS_5Nov2026/2026-11-05_Design_Audit_and_Transformation_Roadmap.md` | `71a5c8d614964f97` |
| 5 Nov ground-truth technical audit | `00_PROJECT_CONTROL/DEEP_AUDITS_5Nov2026/2026-11-05_Ground_Truth_Technical_Audit.md` | `e67622ea880ce090` |
| FDC post update text used on 7 Nov | `09_SUBMISSIONS_AND_CERTIFICATES/03_FDC_Update_7Nov2026/FDC_post_update_text_used_7Nov2026.md` | `b5e35886586c0791` |
| Electronics-manual audit (why v1.0 was wrong) | `12_ELECTRONICS_MANUAL_1to5/MANUAL_AUDIT_2026-11-14.md` | `f013eaf31e0acc3c` |

## What was kept

- The current deck, and the complete 7 Nov submission record (PDF + zip).
- All four current videos, including the R3 assembly and pitch v3.
- The 1:5 model (261 files), R3 CAD (398 files), electronics manual and
  Sensor Hub sources (208 files), storytelling (78 files), submissions and
  certificates (21 files), Pi software (26 files).
- `99_ARCHIVE/file_manifest_before_purge_2026-11-14.csv` — SHA-256 of all
  4,266 files as they were before the purge.
- `00_PROJECT_CONTROL/WORKSPACE_REORG_LOG_2026-11-14.csv` — every move made
  during the earlier reorganisation.

## Verification

- **1,008 remaining files matched their pre-purge SHA-256 exactly** — videos, deck,
  CAD, manuals, images and code were not touched.
- **11 text files differ on purpose**, because links to deleted content had to be
  rewritten: `.gitignore`, `00_START_HERE.md`, `README.md`, `02_LIVE_MODEL_1to5/README.md`,
  the 1:5 design notes, both FDC documents, the 13_ storytelling README and plan,
  the older storyteller plan, and the 14_ Pi README.
- **25 paths are new since the manifest**: files moved during the earlier
  reorganisation plus the new navigation, audit, purge and manifest files.
- **0 empty folders, 0 broken Markdown links** in the final folder.

## Recovery

- **Git-tracked text/code:** intact in `.git`; branches, tags
  `backup/pre-reorg-2026-11-14` and `workspace/reorg-2026-11-14` are present.
- **Deleted videos, decks, CAD and images:** not in git. OneDrive's recycle
  bin and version history are the only route, and they expire. Treat the
  deleted copies as permanently gone.
- **Verification:** the manifest lets you confirm that any surviving file is
  the same bytes as before the purge.
