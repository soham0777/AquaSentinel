# Backup and version control

AquaSentinel is a **local-first** project: the folder on this laptop (synced by OneDrive) is the source of truth.
Git is a history of the text and code, **not** a backup of the 2.2 GB of media, CAD and manuals.

## The three layers

| Layer | What it protects | Where |
|---|---|---|
| OneDrive | The whole folder, continuously; also keeps older versions of most files | `C:\Users\dell\OneDrive\Desktop\AquaSentinel` |
| Archive + move log | Every superseded version, every moved file, reversibly | `99_ARCHIVE/` + `00_PROJECT_CONTROL/WORKSPACE_REORG_LOG_2026-11-14.csv` |
| Git | History of tracked text/code; branches and tags | `.git` + snapshots in `99_ARCHIVE/_SAFETY_SNAPSHOTS/` |

## What git actually tracks

**Tracked (79 files at 14 Nov 2026):**

- `README.md`, `LICENSE`, `.gitignore`, `.gitattributes`, `00_START_HERE.md`;
- `00_PROJECT_CONTROL/` (audit, backup policy, reorg report, move log);
- one `README.md` per working folder, plus `99_ARCHIVE/00_ARCHIVE_INDEX.md` and the archive manifest;
- the **complete Raspberry Pi application** in `14_RASPBERRY_PI_SOFTWARE/aquasentinel/` (code, web UI, tools, scripts)
  and the three wiring diagrams;
- the **current Sensor Hub PCB v1.2** sources: KiCad board, DRC, design scripts, G-code, firmware, guides
  (the superseded `older_versions/` layouts are not tracked).

**Not tracked:**

- the old October tree (`mechanical/`, `docs/`, `analytics/`, `firmware/`, `hardware/`, `project-management/`):
  it was removed from HEAD in commit `654764d` and remains in history and in the pre-reorg tag/bundle;
- the deck and presentation assets in `01_`; STLs and SOLIDWORKS in `02_`; R3 CAD in `05_`; cost and simulation binaries in `06_`/`07_`;
- videos in `08_`, submission packages in `09_`, manual PDF/images/CAD copies in `12_`, assets in `13_`;
- `99_ARCHIVE` contents (except its index and manifest), `*.zip`, `_SAFETY_SNAPSHOTS/`, `.claude/`, `private/`.

These exclusions come from blanket rules in `.git/info/exclude` (`00_*`–`07_*`) plus plain untracked status. They are the
reason a fresh clone does not contain the heavy project files. **Do not “fix” it by running `git add .`** — that would try
to add gigabytes of media and CAD.

## Why `git status` used to show ~336 deleted files — now fixed

On 14 Nov the project was reorganised into numbered folders, moving or removing the old `mechanical/`, `docs/`,
`analytics/`, `firmware/`, `hardware/` and `project-management/` trees. Those moves were uncommitted, so git reported
336 files as deleted. **That state was recorded on 14 Nov 2026 in local commit `654764d`**
(tag `workspace/reorg-2026-11-14`) and `git status` is clean of deletions. Nothing was pushed.

The pre-cleanup state is preserved by:

- tag and branch `backup/pre-reorg-2026-11-14` (commit `fd3c3a3`) and tag `workspace/reorg-2026-11-14` (commit `654764d`);
- bundle `99_ARCHIVE/_SAFETY_SNAPSHOTS/2026-11-14_pre_workspace_reorg/AquaSentinel_git_all_branches_2026-11-14.bundle`;
- older bundle `99_ARCHIVE/_SAFETY_SNAPSHOTS/2026-11-08_GitHub_bundle/`.

## Safe routines

**Before any big change**

```bash
git bundle create "99_ARCHIVE/_SAFETY_SNAPSHOTS/$(date +%F)_before_change.bundle" --all
```

**Check what would be committed**

```bash
git status --short
git diff --stat
```

**Never**

- `git add .` or `git add -A` (would sweep local-only media);
- `git push --force` (the remote is 14 commits behind and 14 ahead; it needs a considered merge, not a force);
- delete `99_ARCHIVE` or `.claude` to “save space” before the finale.

## `.claude/` — 421 MB of hidden copies

`.claude/worktrees/` holds two older full checkouts created by Claude Code (`aquasentinel-project-90da4a` at `e44b7fa`,
`moisture-sensor-solidworks-29a086` at `3b9f501`). They are not project deliverables and are hidden in Explorer.
They are useful as an extra old-version reference until the finale. After that they can be removed with
`git worktree remove <path>` (the branches and commits stay in git).

## Remote

- `main` is at `2a92c7c`, **ahead 14 / behind 14** relative to `origin/main`.
- The public GitHub repository is an older, divergent version. It is not the source of truth.
- Do not push before the finale unless the team has decided how to reconcile the two histories.
