# File audit and lean pass — 14 November 2026

This is the file-by-file validation the project lead asked for after the count
reached 1,034. The complete list of every remaining file is in
`FILE_AUDIT_2026-11-14.csv`; every packed file and its SHA-256 is in
`PACKED_FILES_2026-11-14.csv`.

## 1. The 1,034 were not junk

The count was dominated by CAD and images, not by leftovers:

| Type | Files | Share |
|---|---|---|
| PNG images | 410 | 40 % |
| SOLIDWORKS parts/assemblies/drawings | 268 | 26 % |
| STL (3D print/exchange) | 106 | 10 % |
| STEP (neutral CAD) | 69 | 7 % |
| Markdown, Python, CNC, PDF, SVG, video, office, config and the rest | 181 | 17 % |

By folder, 867 of 1,034 files (84 %) sat in four folders: `05_R3_FULL_SIZE_CAD`
(398), `02_LIVE_MODEL_1to5` (261), `12_ELECTRONICS_MANUAL_1to5` (208) and
`13_CREATIVE_EXPERIENCE_STORYTELLING` (78).

The deep dive found three kinds of removable material:

1. **True duplicates** — an unzipped R3 Pack-and-Go folder byte-identical to its
   own zip and to the working assembly; a duplicate A3 drawing PDF.
2. **Derived render caches** — 172 PNGs in two `views/` folders that were used
   once to lay out the manuals. The finished PDFs and the manual figure sets
   remain.
3. **Superseded or derived CAD exports** — two old PCB layouts and the 66 R3
   part STL exports (the R3 has never been printed, and the STEP files remain).

Nothing current was deleted. The SOLIDWORKS working copies in
`12_ELECTRONICS_MANUAL_1to5/CAD/` were **not** touched: the current `*_v2`
assemblies reference them through external links, so removing them would break
the manual assemblies.

## 2. What was done

| Action | Files | Where they are now |
|---|---|---|
| R3 manual render cache packed | 100 | `05_R3_FULL_SIZE_CAD/03_SOLIDWORKS_2026_assembly_for_manual/views.zip` |
| 1:5 manual render cache packed | 72 | `02_LIVE_MODEL_1to5/05_SOLIDWORKS_ASSEMBLY/views.zip` |
| Old PCB layouts packed | 21 | `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/older_versions.zip` |
| R3 part STL exports packed | 66 | `05_R3_FULL_SIZE_CAD/07_Parts_STEP_STL/R3_parts_STL_exports.zip` |
| Unzipped Pack-and-Go folder removed | 67 | already preserved in `05_R3_FULL_SIZE_CAD/02_SOLIDWORKS_PackAndGo_FDC/AquaSentinel_R3_SOLIDWORKS_PackAndGo.zip` (67/67 entries verified identical) |
| Duplicate A3 drawing PDF removed | 1 | identical to the retained `AquaSentinel_R3_Drawing_Set.pdf` |

Every archive was verified against the originals **before** the originals were
removed: entry count and SHA-256 matched for all 259 newly packed files. The
existing Pack-and-Go zip had already been verified 67/67 against its folder.

## 3. Result

| Measure | After purge | After lean pass |
|---|---|---|
| Files (excluding `.git`) | 1,034 | **711** project files + 3 audit records = **714** |
| Size (excluding `.git`) | 807 MB | **784 MB** |
| Archives kept | 2 | 6 |

The size barely moved because the packed content is mostly already-compressed
PNG. The point of this pass was the file count, and it is down 31 % without
losing a single byte of content.

### What the 711 project files are

| Category | Files |
|---|---|
| Images (manual figures, renders, drawings, labels) | 234 |
| Native CAD (202 SLDPRT + 8 SLDASM + 1 SLDDRW + 1 Fusion) | 212 |
| STEP neutral CAD | 69 |
| STL (38 print files + dish + reference) | 40 |
| Documentation (Markdown) | 34 |
| Code (Python 23, HTML 6, JS 1, Arduino 1) | 31 |
| PDF documents | 17 |
| SVG diagrams | 12 |
| CNC/G-code | 10 |
| Data/config (JSON 7, CSV 6) | 13 |
| Video | 7 |
| Archives (zip) | 6 |
| Plain text | 5 |
| Decks (pptx) | 5 |
| Office documents (xlsx 3, docx 2) | 5 |
| GLB models | 3 |
| Shell scripts | 3 |
| Other (3 extensionless, 1 CSS, 1 KiCad PCB) | 5 |

Where they sit (714 files, 781.3 MB of file bytes; 784 MB on disk with block
overhead):

| Folder | Files | Size |
|---|---|---|
| `01_FINALE_PRESENTATION` | 5 | 90.7 MB |
| `02_LIVE_MODEL_1to5` | 190 | 74.2 MB |
| `05_R3_FULL_SIZE_CAD` | 166 | 111.4 MB |
| `06_SIMULATION` | 9 | 4.2 MB |
| `07_COST_AND_BUSINESS` | 5 | 0.2 MB |
| `08_VIDEOS` | 7 | 355.8 MB |
| `09_SUBMISSIONS_AND_CERTIFICATES` | 21 | 40.9 MB |
| `12_ELECTRONICS_MANUAL_1to5` | 188 | 61.4 MB |
| `13_CREATIVE_EXPERIENCE_STORYTELLING` | 78 | 40.7 MB |
| `14_RASPBERRY_PI_SOFTWARE` | 26 | 0.7 MB |
| `00_PROJECT_CONTROL` | 11 | 0.2 MB |
| `99_ARCHIVE` | 2 | 0.8 MB |
| Root files (map, README, licence, audit, git config) | 6 | 0.0 MB |
| **Total** | **714** | **781.3 MB** |

## 4. Post-pack verification

- **All 326 zip entries re-opened and hashed:** 326/326 match the SHA-256 in
  `PACKED_FILES_2026-11-14.csv` (259 newly packed + 67 Pack-and-Go), 0 failures.
- **0 zero-byte files** in the tree.
- **All 711 paths in `FILE_AUDIT_2026-11-14.csv` exist**; the 3 audit records
  themselves are the only files not listed.
- **45 byte-identical groups remain, all intentional:** 40 are the CAD working
  copies in `12_ELECTRONICS_MANUAL_1to5/CAD/` that the current `*_v2`
  assemblies reference by path; 2 are repeated manual figure images; the
  remaining 3 are the R3 GLB shared with the storytelling AR scene and the
  deployed/source copies of two HTML viewers. Removing any of them would break
  an assembly, a manual or a demo.

## 5. Can it go below 711?

Not without deleting current work. The remaining 711 are the build itself:

- **212 native SOLIDWORKS files** — the 1:5 model (40 parts + assembly in
  `05_SOLIDWORKS_ASSEMBLY`), the R3 working assembly (66 parts + assembly),
  the electronics-bay copies used by the current assemblies, the remaining
  PCB/electrical models, plus the drawing.
- **69 STEP + 40 STL** — the portable CAD and the print set.
- **234 images** — the figures the finished manuals and deck are made of.
- **7 videos** — 373 MB of current deliverables, including the 109 MB of raw
  teammate recordings used to cut the pitch video.

Deleting any of these would remove the ability to rebuild a manual, edit an
assembly or re-cut a video. If the project only needs what is shown at the
booth, a separate "booth-only" copy is the right move — not deleting the source.

## 6. How to restore anything

- Extract the relevant `.zip` in place; the entry names are the original file
  names, and `PACKED_FILES_2026-11-14.csv` carries the SHA-256 of every entry.
- For the R3 Pack-and-Go, extract
  `05_R3_FULL_SIZE_CAD/02_SOLIDWORKS_PackAndGo_FDC/AquaSentinel_R3_SOLIDWORKS_PackAndGo.zip`
  and the folder structure returns exactly as submitted.
- `FILE_AUDIT_2026-11-14.csv` lists every file that remains, its size, extension
  and category.
