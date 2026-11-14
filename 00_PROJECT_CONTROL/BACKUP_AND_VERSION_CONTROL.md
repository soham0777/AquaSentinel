# Backup and version control

AquaSentinel is a **local-first** project: the folder on this laptop (synced by
OneDrive) is the source of truth. Git is a history of the text and code, **not**
a backup of the 807 MB of media, CAD, decks and manuals.

## The three layers

| Layer | What it protects | Where |
|---|---|---|
| OneDrive | The whole folder, continuously; recycle bin and previous versions for deleted or changed files (they expire) | `C:\Users\dell\OneDrive\Desktop\AquaSentinel` |
| Git | History of tracked text/code; every branch and tag | `.git` |
| Audit trail | Every move, every deleted folder, and a SHA-256 fingerprint of the pre-purge state | `00_PROJECT_CONTROL/WORKSPACE_REORG_LOG_2026-11-14.csv`, `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md`, `99_ARCHIVE/file_manifest_before_purge_2026-11-14.csv` |

There is **no in-project bundle or second archive any more**. Those were
deleted on 14 Nov 2026 to remove duplication; git itself holds all tracked
history, and

```bash
git bundle create "C:/Users/dell/Desktop/AquaSentinel_backup_$(date +%F).bundle" --all
```

creates a fresh external copy whenever one is wanted (keep it **outside** the
project folder).

## What git actually tracks

**Tracked (89 files at 14 Nov 2026):**

- `README.md`, `LICENSE`, `.gitignore`, `.gitattributes`, `00_START_HERE.md`;
- `00_PROJECT_CONTROL/` — audit, critical path, reorg report, purge report,
  backup policy, move log, and the two 5 Nov deep audits;
- one `README.md` per working folder, the archive purge note and the pre-purge
  manifest;
- the **complete Raspberry Pi application** in `14_RASPBERRY_PI_SOFTWARE/aquasentinel/`
  (code, web UI, tools, scripts) and the three wiring diagrams;
- the **current Sensor Hub PCB v1.2** sources: KiCad board, DRC, design
  scripts, G-code, firmware, guides (the superseded `older_versions/` layouts
  are not tracked).

**Not tracked:**

- the old October tree (`mechanical/`, `docs/`, `analytics/`, `firmware/`,
  `hardware/`, `project-management/`): removed from HEAD in commit `654764d`,
  still present in history and in tag `backup/pre-reorg-2026-11-14`;
- the deck and presentation assets in `01_`; STLs and SOLIDWORKS in `02_`;
  R3 CAD in `05_`; cost and simulation binaries in `06_`/`07_`;
- videos in `08_`, submission packages in `09_`, manual PDF/images/CAD copies
  in `12_`, assets in `13_`;
- `*.zip`, `.claude/`, `private/`, and the deleted old archive contents.

These exclusions come from blanket rules in `.git/info/exclude` (`00_*`–`07_*`)
plus plain untracked status. They are the reason a fresh clone does not contain
the heavy project files. **Do not “fix” it by running `git add .`** — that
would try to add gigabytes of media and CAD.

## What happened on 14 Nov 2026

1. **Reorganisation:** the current deck was separated from the 7 Nov submission
   record, October renders moved out of the live folder, navigation rebuilt.
   Recorded in commit `654764d`, tag `workspace/reorg-2026-11-14`, and
   `00_PROJECT_CONTROL/WORKSPACE_REORG_REPORT_2026-11-14.md`.
2. **Purge (approved by the project lead):** old decks, old video takes, the
   virtual-storyteller build, abandoned electronics, old reports, both git
   bundles and Claude's two worktrees were permanently deleted. Four unique
   documents were rescued first and hash-checked. Recorded in
   `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md`.
3. **Result:** 4,281 → 1,034 working files; 2.25 GB → 807 MB (1.1 GB including
   `.git`). Nothing was pushed.

## Remote

- `main` is at `260aaf5`, **20 commits ahead / 14 behind** `origin/main`.
- The public GitHub repository is an older, divergent version. It is not the
  source of truth.
- Do not push before the finale unless the team has decided how to reconcile
  the two histories. Never force-push.

## Safe routines

**Before any big change**

```bash
git bundle create "C:/Users/dell/Desktop/AquaSentinel_backup_$(date +%F).bundle" --all
```

**Check what would be committed**

```bash
git status --short
git diff --stat
```

**Never**

- `git add .` or `git add -A` (would sweep local-only media);
- `git push --force`;
- delete `.git`, `00_START_HERE.md` or any current folder to “save space”.

## If a file is lost

1. OneDrive recycle bin or version history (time-limited).
2. `git log --all -- <path>` / `git show <tag>:<path>` for tracked files.
3. `00_PROJECT_CONTROL/WORKSPACE_REORG_LOG_2026-11-14.csv` to see where a moved
   file went.
4. `00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md` to confirm whether it was
   deliberately deleted.
