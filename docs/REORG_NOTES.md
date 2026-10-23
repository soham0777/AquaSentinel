# Reorganisation notes

Branch `reorg/organized-structure`, made from `main` at `fd3c3a3` (the pitch-alignment commit). Nothing was deleted, no history was
rewritten, and nothing was pushed. Moves were made with `git mv`, so `git log --follow <new path>` still shows the history.
Firmware and analytics **logic was not changed**.

## 1. Old path → new path

| Old path | New path | Why |
|---|---|---|
| `docs/engineering/claims_register.md` | `engineering/claims_register.md` | `docs/` is the public website folder; working documents do not belong in it |
| `docs/engineering/jury_QA.md` | `engineering/jury_QA.md` | same |
| `docs/engineering/robotics_subsystems_spec.md` | `archive/superseded-docs/robotics_subsystems_spec.md` | v2-era spec, replaced by R3; kept for history |
| `docs/engineering/solidworks_build_guide.md` | `archive/superseded-docs/solidworks_build_guide.md` | v2-era guide, replaced by R3; kept for history |

Everything else stays where it was. Deliberately **not** moved: `docs/presentation/*.pdf` (the website links it), `docs/viewer.html`,
`docs/dashboard/`, `docs/media/`, `docs/assets/` (all referenced by the live site and README), and every file under `mechanical/`,
`firmware/`, `analytics/`, `hardware/`.

References fixed after the moves: the relative links inside the four moved documents, and the claims-register link in `README.md`.
`python tools/check_links.py` checks every Markdown link, HTML `src`/`href`/`srcset`, CSS `url()`, JS asset reference,
backticked path and absolute `github.com/soham0777/AquaSentinel/...` or `soham0777.github.io/AquaSentinel/...` link.

## 2. New files

| Path | Purpose |
|---|---|
| `START_HERE.md` | "I want to…" guide and folder map |
| `README.md` in every folder | what is inside, the file to open first, the exact command |
| `CONTRIBUTING.md` | checks to run, layout rules, Git LFS note (not applied) |
| `tools/check_links.py`, `tools/verify_all.sh`, `tools/parity/` | read-only checkers (links, detector replay, mechanical rebuild, C++ vs Python parity, optional firmware build) |
| `requirements.txt` | the Python packages the design engine and analytics need |
| `.github/workflows/ci.yml` | runs `tools/verify_all.sh --pio`; checks only, deploys nothing, independent of the Pages build |
| `calculations/README.md` | explains that the hand-calculation scripts are not in the repository |

`.gitignore` was hardened (secrets, `.env`, keys, `private/`, virtual environments, build output, logs). No tracked file is affected.

## 3. Claims and numbers (separate commit, text only)

Removed or softened in editable text: "forensic", "NABL", "sealed sample", "legal evidence", "SF 4.4" as a headline, and the schematic
wording for the KiCad file (it is a text description, not a drawn schematic). Firmware changes are **comments and log strings only**.
Cost: the CSV TOTAL row now reads ₹138,000 / USD 1438.39 / scale-100 USD 994.50, which is the verified sum of the line items; three rows
with unquoted commas were quoted so the file parses as 10 columns everywhere.

**Not edited (binary, already submitted):** the FDC deck PDF and the release PPTX still contain the old figures. The list is in `docs/presentation/README.md`.

## 4. To do and decisions for the team (nothing here was guessed)

| # | Item | Where | Why it was left |
|---|---|---|---|
| 1 | Autonomy and energy figures conflict: `power_budget.csv` says 3.39 Wh/day; the bench test sheet uses 4.07 Wh/day; BOM row D-02 says "15.1 days of continuous zero-sun autonomy" (61.4 Wh usable ÷ 4.07); the retracted pitch line was "10+ days". PV rows quote 9.6× and 16.9× surplus | `hardware/power_budget.csv`, `hardware/AquaSentinel_Cost_Estimate_BOM.csv` (D-01, D-02), `hardware/bench_energy_test_procedure.md` | needs a measured sleep current; do not quote one number until then |
| 2 | `calculations/verified_design_calcs.py/.json` are referenced but not in the repository; the 64.0 MPa / SF 2.66 case is not computed by any tracked file | `calculations/README.md` | needs the team's own script |
| 3 | `mechanical/src/parts.py` lines for "tamper-seal hasp" and "(chain of custody)" flow into `BOM_R3.csv`, the STEP part names and the viewer | `mechanical/src/parts.py`, `mechanical/cad/` | editing them means regenerating about 200 files |
| 4 | "AquaRight" project name in firmware headers, "Jal-Deep" beacon name | `firmware/edge_node/include/config.h`, `firmware/edge_node/src/main.cpp` | branding decision |
| 5 | `test_sleep_current.cpp` (the sleep-current diagnostic) is not written | `hardware/bench_energy_test_procedure.md` | new firmware, outside this pass |
| 6 | Findings B-01 and B-07 and the pump timing from the audit | `AUDIT_REPORT.md` (outside the repository) | they change logic |
| 7 | The KiCad file has no real schematic and no PCB | `hardware/kicad/` | needs design work |
| 8 | Cost sheet is the v2 layout; R3 re-costing and supplier quotes are pending | `hardware/` | "to be confirmed" |
| 9 | Videos, STEP files and the Pack and Go zip are about 100 MB in ordinary Git | `CONTRIBUTING.md` | LFS guidance only; history not converted |

## 5. Not merged

The local, unpushed branch `audit/engineering-knowledge-base` was **not** merged into this branch. The git-ignored `private/` folder was not touched, moved or copied.
