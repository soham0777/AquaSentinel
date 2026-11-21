# 99_ARCHIVE — purge record

On **14 November 2026**, with the project lead's explicit approval, the old
versions that used to live here were **permanently deleted**. This folder is
no longer a working archive; it holds one file:

| File | What it is |
|---|---|
| `file_manifest_before_purge_2026-11-14.csv` | SHA-256, size and timestamp of all **4,266 files** that existed just before the purge (relative paths, including `.claude/worktrees`). It proves what existed and lets you check any surviving copy for damage. |

## What was deleted

- Old decks: semi-final (Oct), first draft, pre-wording-fix, pre-Phase-2.
- Old videos: pitch v1/v2/FINAL, virtual-storyteller build, LinkedIn reel, old takes.
- Superseded design: ESP32 electronics, ADS1115/Pi-direct electronics, old housing, 31 Oct concept renders, old reports and audits.
- Both git safety bundles (8 Nov GitHub backup and 14 Nov pre-reorg bundle).
- Claude's two worktree checkouts (`aquasentinel-project-90da4a`, `moisture-sensor-solidworks-29a086`).

The full list, sizes and rationale are in
`00_PROJECT_CONTROL/PURGE_REPORT_2026-11-14.md`.

## What is recoverable

- **Tracked text and code:** still in `.git` on every branch, plus tag
  `backup/pre-reorg-2026-11-14` and tag `workspace/reorg-2026-11-14`.
- **Deleted media/CAD/decks:** not in git. OneDrive's recycle bin and version
  history are the only recovery path, and those expire. Treat them as gone.
- **Rescued before deletion:** the two 5 Nov technical audits, the FDC post
  text used on 7 Nov, and the electronics-manual audit. They were verified
  byte-for-byte against this manifest and now live in `00_PROJECT_CONTROL/`,
  `09_SUBMISSIONS_AND_CERTIFICATES/03_FDC_Update_7Nov2026/` and
  `12_ELECTRONICS_MANUAL_1to5/`.

To find where a moved file went (moves, not deletions), read
`00_PROJECT_CONTROL/WORKSPACE_REORG_LOG_2026-11-14.csv`.
