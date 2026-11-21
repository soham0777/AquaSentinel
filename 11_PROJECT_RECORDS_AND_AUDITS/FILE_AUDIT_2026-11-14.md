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
The 15 Nov CAD pass added 49 further entries (7 removed files + 40 spare parts
+ 2 manifests); all 49 were hashed and the 7 removed files were compared to
their archive copies before deletion.

## 3. Result

| Measure | After purge | After PNG + CAD passes |
|---|---|---|
| Files (excluding `.git`) | 1,034 | **704** project files + 6 audit records = **710** |
| Size (excluding `.git`) | 807 MB | **826.6 MB of file bytes (788 MiB)**; 791 MB on disk |
| Archives kept | 2 | 8 |

The size is **791 MB on disk**, 16 MB below the 807 MB post-purge figure,
because the removed files' cluster overhead was larger than the two new CAD
archives. The point of the pass was the file count, and it is down 32 % (1,034
→ 704 project files) without losing a single byte of current content.

### What the 704 project files are

| Category | Files |
|---|---|
| Images (manual figures, renders, drawings, labels) | 232 |
| Native CAD (198 SLDPRT + 6 SLDASM + 1 Fusion) | 205 |
| STEP neutral CAD | 69 |
| STL (38 print files + dish + reference) | 40 |
| Documentation (Markdown) | 34 |
| Code (Python 23, HTML 6, JS 1, Arduino 1) | 31 |
| PDF documents | 17 |
| SVG diagrams | 12 |
| CNC/G-code | 10 |
| Data/config (JSON 7, CSV 6) | 13 |
| Video | 7 |
| Archives (zip) | 8 |
| Plain text | 5 |
| Decks (pptx) | 5 |
| Office documents (xlsx 3, docx 2) | 5 |
| GLB models | 3 |
| Shell scripts | 3 |
| Other (3 extensionless, 1 CSS, 1 KiCad PCB) | 5 |

Where they sit (710 files including the 6 audit records; 826.6 MB of file bytes,
788 MiB; 791 MB on disk with block overhead):

| Folder | Files | Size |
|---|---|---|
| `01_FINALE_PRESENTATION` | 5 | 90.7 MiB |
| `02_LIVE_MODEL_1to5` | 191 | 81.8 MiB |
| `05_R3_FULL_SIZE_CAD` | 166 | 111.4 MiB |
| `06_SIMULATION` | 9 | 4.2 MiB |
| `07_COST_AND_BUSINESS` | 5 | 0.2 MiB |
| `08_VIDEOS` | 7 | 355.8 MiB |
| `09_SUBMISSIONS_AND_CERTIFICATES` | 21 | 40.9 MiB |
| `12_ELECTRONICS_MANUAL_1to5` | 181 | 61.2 MiB |
| `13_CREATIVE_EXPERIENCE_STORYTELLING` | 77 | 40.3 MiB |
| `14_RASPBERRY_PI_SOFTWARE` | 26 | 0.7 MiB |
| `00_PROJECT_CONTROL` | 14 | 0.2 MiB |
| `99_ARCHIVE` | 2 | 0.8 MiB |
| Root files (map, README, licence, audit, git config) | 6 | 0.0 MiB |
| **Total** | **710** | **788.3 MiB** |

## 4. Post-pack verification

- **All 375 zip entries re-opened and hashed:** 375/375 match the SHA-256 in
  `PACKED_FILES_2026-11-14.csv` (326 from the lean pass + 49 in the two
  archives added by the 15 Nov CAD pass), 0 failures.
- **0 zero-byte files** in the tree.
- **All 704 paths in `FILE_AUDIT_2026-11-14.csv` exist**; the 6 audit records
  themselves are the only files not listed.
- **45 byte-identical groups remain, all intentional:** 40 are the 1:5
  assembly's local part set. They are byte-identical to the `live_copy` set,
  but the assembly stores references to its own copies, so they are not
  interchangeable; a deletion test produced 40 missing references. The other 2
  are repeated manual figure images; the remaining 3 are the R3 GLB shared with
  the storytelling AR scene and the deployed/source copies of two HTML viewers.
  Removing any of them would break an assembly, a manual or a demo.

## 5. PNG pass, 15 November 2026

The 410 PNGs in the 1,034-file state were reduced to 234 by the lean pass:
176 were packed — 172 manual render caches in the two `views.zip` archives and
4 old PCB layout renders in `older_versions.zip`. The remaining **234 were then
inspected one by one**, as contact sheets at 300 px per image plus full-size
views of every ambiguous or low-content file.

Verdicts are recorded per file in `PNG_AUDIT_2026-11-15.csv`:

| Group | Files | Verdict |
|---|---:|---|
| 1:5 assembly manual figures | 74 | Keep — every page of the 30-page manual |
| 1:5 CAD preview, part labels, printed dish | 3 | Keep — current variant and booth material |
| R3 drawings, design-check sheet, renders | 22 | Keep — current manual, deck and FDC; the three 5 Oct SOLIDWORKS screenshots are used on R3 manual p25 |
| FEA result plots | 4 | Keep — current simulation evidence |
| Electronics manual figures + PCB renders/guides | 61 | Keep — Rev 2.0 manual and v1.2 board |
| CXP 2-D assets and renders | 65 | Keep — current story/deck overlays |
| SIM800L wiring diagrams | 3 | Keep — current SMS wiring; these were missing from disk and were restored from git during this audit (hashes matched the pre-purge manifest) |
| **Kept** | **232** | |
| Blank manual-build check (`_build_v2/page1_check.png`) | 1 | **Deleted** — one colour, no content, not referenced |
| Contact sheet `00_PREVIEW_all_assets.png` | 1 | **Deleted** — montage of the other 31 assets, no unique content |
| **Deleted** | **2** | |

No current manual figure, render, drawing, overlay or wiring diagram was
removed. The four 640×480 `part_ORIG-F15a…d` files contain two byte-identical
pairs, but each is a separate part entry in the manual's parts list, so they
stay.

## 5b. CAD pass, 15 November 2026

All **212 native CAD files** (198 SLDPRT, 6 SLDASM, 1 Fusion after the pass)
were reviewed. Every current assembly was opened read-only in SOLIDWORKS, its
component tree walked, and every referenced path checked on disk. The per-file
verdicts are in `CAD_AUDIT_2026-11-15.csv` and the reasoning in
`CAD_AUDIT_2026-11-15.md`.

| Assembly | References | Missing |
|---|---:|---:|
| R3 full-size assembly | 66 | 0 |
| 1:5 LIVE assembly | 40 | 0 |
| live_v2 (with electronics) | 62 | 0 |
| Detail_MQ3_station | 4 | 0 |
| Detail_sensor_cage | 10 | 0 |
| bay_v2 | 18 | 0 |

**Kept: 205.** 67 R3 files, 41 for the 1:5 working assembly (40 parts + the
assembly), 18 named parts designed with **Vector** (17 from 31 Oct plus the
13 Nov sample-bottle variant), 76 electronics parts, 2 FEA study parts and the
Fusion 360 source of the printed dish. “Vector” is the AI engineering copilot
that generated the 1:5 model, so those files are the design source, not junk.

**Removed: 7**, all obsolete v1/legacy files, preserved in
`12_ELECTRONICS_MANUAL_1to5/CAD/older_design_2026-11-09.zip` (7/7 hashes
verified): the old 1:5 render assembly, the old bay v1 assembly and drawing,
the legacy E07 third buck and E12 level converter, and the removed E27/E28
rain-sensor parts.

**The 40-part finding.** The 1:5 assembly's stored references point to its own
40 local parts. They are byte-identical to the 40 in `CAD/live_copy/`, but when
I removed the local set as duplicates, a clean re-open reported 40 missing
references; the first read had reused the already-loaded `live_copy` documents
because the filenames and bytes matched. All 40 were restored from
`05_SOLIDWORKS_ASSEMBLY/assembly_parts_copy_2026-11-07.zip` (40/40 hashes match)
and the assembly again resolves 40/40.

`E02_ADS1115_ADC` and `E03_DS3231_RTC` are electrically legacy in the final
build, but they are still inserted in live_v2 and bay_v2, so they stay. `E07`
and `E12` are not in the v2 assemblies and were removed with the old bay v1
assembly.


## 6. Can it go below 704?

Not without deleting current work. The remaining 704 are the build itself:

- **205 native CAD files** — the R3 assembly (66 parts + assembly), the 1:5
  working set (40 parts + assembly), the 18 named Vector design parts, the
  electronics-bay parts and v2 assemblies, the two FEA study parts and the
  printed-dish Fusion source.
- **69 STEP + 40 STL** — the portable CAD and the print set.
- **232 images** — the figures the finished manuals and deck are made of.
- **7 videos** — 373 MB of current deliverables, including the 109 MB of raw
  teammate recordings used to cut the pitch video.

Deleting any of these would remove the ability to rebuild a manual, edit an
assembly or re-cut a video. If the project only needs what is shown at the
booth, a separate "booth-only" copy is the right move — not deleting the source.

## 7. How to restore anything

- Extract the relevant `.zip` in place; the entry names are the original file
  names, and `PACKED_FILES_2026-11-14.csv` carries the SHA-256 of every entry.
- For the 7 obsolete CAD files, extract
  `12_ELECTRONICS_MANUAL_1to5/CAD/older_design_2026-11-09.zip` over
  `12_ELECTRONICS_MANUAL_1to5/CAD/`; `RESTORE.txt` lists the hashes.
- The 40 local parts of the 1:5 assembly are on disk. A spare verified copy is
  `02_LIVE_MODEL_1to5/05_SOLIDWORKS_ASSEMBLY/assembly_parts_copy_2026-11-07.zip`.
- For the R3 Pack-and-Go, extract
  `05_R3_FULL_SIZE_CAD/02_SOLIDWORKS_PackAndGo_FDC/AquaSentinel_R3_SOLIDWORKS_PackAndGo.zip`
  and the folder structure returns exactly as submitted.
- `FILE_AUDIT_2026-11-14.csv` lists every project file that remains, its size,
  extension and category. `CAD_AUDIT_2026-11-15.csv` adds the per-file CAD
  verdict, reference evidence and reason.
