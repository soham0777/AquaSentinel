# FDC post: validation against the AAKRUTI rules (7 Nov 2026)

Post: AAKRUTI_FDC_AG26-1500$41_Sanjivani Hero's Journey (team community). Checked live after a fresh reload: 39 media, none broken.

## Sources checked
- Portal: "Task 6 | Final Design Concept Submission" and the template post "AAKRUTI_FDC_TeamID_TeamName" (AAKRUTI 2026 Community - For Students).
- Organisers' FDC presentation template (09_SUBMISSIONS_AND_CERTIFICATES/FDC_template_from_organisers.pptx).
- WhatsApp group "AAKRUTI INDIA Finalists 2026" (export up to 4 Nov): Shubham Arora, 2 Nov 17:49 and 18:34; organiser, 2 Nov 21:06.
- Gmail kadusoham64: finale email 25 Oct (nothing about the FDC post; no AAKRUTI mail since 31 Oct).
- Earlier rule notes: Art. 7.4 (no third-party copyright), Art. 10 (false statements can disqualify).

## Rule-by-rule
| Rule (source) | Status |
|---|---|
| Update all data in the EXISTING FDC post only (WhatsApp 2 Nov) | OK: same post, same link, nothing new posted elsewhere |
| Last date to submit and lock: 7 Nov (WhatsApp 2 Nov) | OK: published 7 Nov |
| Add all rendered images; hero images for the banner (WhatsApp 2 Nov) | OK: section 8, five hero images at full resolution |
| One post per team, in the private team community only (Task 6) | OK |
| Title AAKRUTI_FDC_TeamID_TeamName (Task 6) | OK, unchanged |
| Template fields: Team & Product Details, Final Presentation, Pitch video, Journey video, CAD zip, Additional Data (template post) | OK: all kept unchanged in section 9 |
| Simulation data from DS tools only (template post) | OK: the 6 simulation files are SOLIDWORKS Simulation |
| Finale videos without background music (WhatsApp 2 Nov) | OK: all 5 new videos are silent |
| No false statements (Art. 10) | FIXED 7 Nov evening, see below |
| No third-party copyright (Art. 7.4) | CHECK: source of the night/river footage in the journey video |
| No confidential grades or personal contact details | OK |

## Corrections published 7 Nov (Art. 10)
Evidence: the 66 Pack-and-Go parts are imported bodies with no feature tree (open `05_R3_FULL_SIZE_CAD/02_SOLIDWORKS_PackAndGo_FDC`), and the mechanical source is in git commit 3b9f501 (drawings and check sheet made with matplotlib; the animation is a three.js web viewer). The 5 Nov handover report cited when this was written was deleted in the 14 Nov purge; the claim can be checked directly in the CAD and in git.
- "Designed in SOLIDWORKS" -> "CAD and simulation", with the true description (imported parts, SOLIDWORKS Simulation, drawings computed from the CAD; the 17 new 1:5 parts are native SOLIDWORKS).
- Video captions no longer say "SOLIDWORKS animation": now "3D animation of our CAD model".
- Night clip marked "illustrative scene from our journey video".
- The drawing set and check sheet added inside the original FDC section are marked "Added 7 Nov 2026".

## Finale deck corrected (7 Nov evening)
Same evidence. 15 text edits made in PowerPoint (videos, autoplay and fonts unchanged); the pre-fix copy was deleted in the 14 Nov purge, and the edits are listed below.
- Slide 1: "R3 · SOLIDWORKS render" -> "R3 · CAD render".
- Slide 8: "SOLIDWORKS animation" -> "3D animation of our CAD"; "checks pass on the SOLIDWORKS model" -> "on the R3 CAD model" (slide and notes).
- Slide 9: title -> "Assembled and simulated in SOLIDWORKS."; label -> "CAD AND SIMULATION"; "17 new parts: designed in SOLIDWORKS for the 1:5 live model"; notes reworded the same way.
- Slide 11: footnote -> "Rendered from our print files; the 17 new parts are native SOLIDWORKS parts."; notes reworded.
- Slide 27 notes and slide 28 caption: "printed from our CAD files", "Assembled in SOLIDWORKS; SOLIDWORKS Simulation, Pack and Go, ENOVIA Project Planner".
- The corrected deck replaced the old one on the FDC post (section 1, media bCpaKzjFQR-vLqjdx-zrAA; SHA-256 starts 9c078cd8). Live post re-checked: 39 media, none broken.
- Kept (true): "66-part assembly in SOLIDWORKS", SOLIDWORKS Simulation studies, "The float in SOLIDWORKS" screenshot.
- Still to confirm by the team: slide 11 / 15 chips "✓ printed" (true only if all 37 parts are printed); source of the night/river footage (Art. 7.4).

## Q&A line if a juror asks "Is the R3 native SOLIDWORKS?"
"Our full-size R3 was generated from a parametric model in code and brought into SOLIDWORKS as an assembly, where we assigned materials, ran SOLIDWORKS Simulation and packaged it. The 17 new parts of our 1:5 live model are native SOLIDWORKS parts with full feature trees. Rebuilding the R3 natively is our next CAD step."

## Post reorganised (7 Nov, night)
Modelled on the 2026 winner's FDC post (media first, very little text).
- Part 1: India Geo Finale, 19 and 20 November 2026: finale presentation, videos, 1:5 live model, electronics, cost, R3 drawings and design checks (added 7 Nov), team, hero images for the banner.
- Part 2: Our FDC submission (5 October 2026): the template sections exactly as evaluated. The drawing set and check sheet were moved out of it into Part 1, so Part 2 is now unchanged.
- Live check after reload: 39 media, none broken, "FDC Submission" tag kept.
