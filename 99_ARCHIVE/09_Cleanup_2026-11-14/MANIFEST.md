# 99_ARCHIVE / 09_Cleanup_2026-11-14 — MANIFEST

Project-manager cleanup of the AquaSentinel folder, 14 Nov 2026.
**Moves only — nothing was permanently deleted.** Every item below can be restored by moving it back to its original path.

| Moved from (original) | Moved to (here) | Why |
|---|---|---|
| `03_ELECTRONICS_RASPBERRY_PI` | `03_ELECTRONICS_RASPBERRY_PI_old_ADS1115_design` | Old Pi-direct ADS1115-era design (Oct). Current electronics: Arduino Nano + Sensor Hub PCB v1.2 (`12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1`) + Raspberry Pi 3B+ software (`14_RASPBERRY_PI_SOFTWARE`). FDC post updated 13 Nov already describes the new build. |
| `04_SENSOR_HOUSING` | `04_SENSOR_HOUSING_preLD` | Pre-LD simple housing. Current housing: LD parts in `02_LIVE_MODEL_1to5` + live cage in `12_ELECTRONICS_MANUAL_1to5`. |
| `10_VIRTUAL_STORYTELLER` | `10_VIRTUAL_STORYTELLER_superseded_by_13` | Superseded by `13_CREATIVE_EXPERIENCE_STORYTELLING` (13 Nov). Heavy media (video frames) preserved here. |
| `11_LINKEDIN_POST_8Nov` | `11_LINKEDIN_POST_8Nov_done` | One-off task; post published 8 Nov. |
| `12_ELECTRONICS_MANUAL_1to5/BOOTH_LITE_v3` | `12_BOOTH_LITE_v3_superseded` | Earlier booth software (Pi reads sensors directly). Superseded by Sensor Hub build + `14_RASPBERRY_PI_SOFTWARE`. |
| `12_ELECTRONICS_MANUAL_1to5/_work` | `12_manual__work_scratch` | Build scratch for the manual; manual PDF stays in `12_ELECTRONICS_MANUAL_1to5`. |
| `08_VIDEOS/AquaSentinel_Pitch_Video_1080p.mp4` | `08_videos_superseded_versions/` | Superseded by the 7 Nov voice-over takes. |
| `08_VIDEOS/AquaSentinel_Pitch_Video_Clean_Water_Now_FINAL.mp4` | `08_videos_superseded_versions/` | Earlier take (v1). Latest is `…_FINAL_v3.mp4`. |
| `08_VIDEOS/AquaSentinel_Pitch_Video_Clean_Water_Now_FINAL_v2.mp4` | `08_videos_superseded_versions/` | Earlier take (v2). Latest is `…_FINAL_v3.mp4`. |
| `12_MAKER_FEST_VADODARA_2027` | → `09_SUBMISSIONS_AND_CERTIFICATES/07_Maker_Fest_Vadodara_2027` | Numbering fix: it is a registration form record, now filed with the other submissions. |

## Safety records

- Git tag **and** branch `backup/pre-reorg-2026-11-14` mark the pre-cleanup commit (fd3c3a3).
- This manifest + the updated `README.md` / `00_START_HERE.md` are committed to `main` on 14 Nov 2026.

## To restore anything

Move the folder/file back from `99_ARCHIVE/09_Cleanup_2026-11-14/` to the path in the "Moved from" column. That's it.
