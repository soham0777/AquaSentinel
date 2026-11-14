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

**Tracked (345 files at 14 Nov):**

- `README.md`, `LICENSE`, `.gitignore`, `.gitattributes`
- the old October tree: `mechanical/`, `docs/`, `analytics/`, `firmware/`, `hardware/`, `project-management/`
  (these files were moved off the visible workspace during the numbered-folder reorganisation, so `git status` lists them as deleted)
- `14_RASPBERRY_PI_SOFTWARE/aquasentinel/aquasentinel/brain.py`, `config.json`, `tools/self_test.py`
- `99_ARCHIVE/09_Cleanup_2026-11-14/MANIFEST.md`

**Not tracked, by design or by the local exclude file:**

- everything in `01_`–`07_` (blanket rules in `.git/info/exclude`), including the deck, STLs and R3 CAD;
- `08_`, `09_`, `12_`, `13_` (they are simply untracked);
- `99_ARCHIVE` contents (except its manifest), `*.zip`, `.claude/worktrees/`, `private/`.

This is why the numbered folder tree does not appear in the public repository. It is a deliberate local-only layout,
inherited from before this cleanup. **Do not “fix” it by running `git add .`** — that would try to add gigabytes.

## Why `git status` shows ~336 deleted files

On 14 Nov the project was reorganised into numbered folders, moving or removing the old `mechanical/`, `docs/`,
`analytics/`, `firmware/`, `hardware/` and `project-management/` trees. Those files are still in git history and in the
14 Nov bundle; they were never committed as deletions. The result is a working tree that does not match HEAD.

**Do not click “Discard changes” in a git client.** That would restore the old folder tree on top of the clean layout.

The pre-cleanup state is preserved by:

- tag and branch `backup/pre-reorg-2026-11-14` (commit `fd3c3a3`);
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
