# AquaSentinel × Virtual Storyteller (3DEXCITE): plan for the finale

Written 7 Nov 2026. Booth: 19 Nov. Pitch: 20 Nov, Pune.

## Why this role matters

- The organisers asked every finalist to hold this role (WhatsApp, 2 and 4 Nov).
- The booth has **no personal laptops**: only one display, driven by an office laptop. A web-based 3D experience that runs from a link is exactly what that setup can show.
- The jury and booth visitors are from Dassault Systèmes. A team that turns its SOLIDWORKS model into a 3DEXCITE story uses their platform end to end.
- **Rule for us:** say only what we have built. The deck is frozen today, so none of this goes in the deck. It goes on the booth display, a QR card, a 3DSwym post and the Q&A answers.

## What we already have to feed it

- The full R3 assembly as STEP: `04_R3_FULL_SIZE_DESIGN/08_Assembly_STEP_GLB/AquaSentinel_R3_Assembly_MidWater.step`, 66 parts. A GLB of it is in the same folder.
- The SOLIDWORKS Pack and Go.
- The 1:5 live model: 17 SOLIDWORKS parts and 37 STL files.
- The story is already written: the night spill → the river lifts the float → the beacon turns red + SMS → a bottle for the lab → service from the bridge.

## The experience, scene by scene (Creative Experience)

One interactive 3D experience called **"A night on the Godavari"**: 6 scenes, buttons to switch between them, about 2 minutes if played straight through.

| # | Scene | What moves | Click |
|---|---|---|---|
| 1 | **Normal river**, dusk | float on its pole, beacon **green**, water calm | "Start" |
| 2 | **The river rises** | float slides 2 m up the pole; a level gauge counts | "Flood" / "Low water" |
| 3 | **Spill at 02:00** | water tint turns brown, beacon **red**, SMS card appears | "Spill" |
| 4 | **Evidence** | pump runs, one bottle fills (highlight) | "Sample" |
| 5 | **Service from the bridge** | carriage gate opens, cartridge lifts out | "Service" |
| 6 | **Inside** | exploded view; click a part to see its name and material | "Explode" / click a part |

The office laptop plays it from a **3DPlay / share link**: judges click through it themselves. A QR card on the table opens the same link on their phones.

## The apps and what each one does for us

| App (in our role) | Our use | Output |
|---|---|---|
| **Converter for STEP · Experience Models Preparation** | Bring the R3 STEP into the platform; simplify it; group parts (hulls, carriage, cartridge, beacon) | Light model ready for 3DEXCITE |
| **Ambience Studio** | River at dusk and at night: sky, water, lighting, a bridge pier | Reusable environment |
| **Rendering Scene Design · Live Rendering** | Photo-real hero images and a 20-second turntable | 4 renders + 1 video for the booth display loop |
| **Creative Experience** | The 6-scene interactive story above | Shareable experience link |
| **Human Animation Studio** | A technician on the bridge opening the gate and lifting the cartridge | Scene 5, the human-centred service story |
| **Planets Studio** | Kopargaon on the Godavari, then Maharashtra's 54 polluted sites | Opening shot, "where we deploy" |
| **Twin Factory** (optional) | Assembly line for 100 floats | Business-scale answer in Q&A |
| **3DSwym** | Post the experience and renders in our team community | Visibility to organisers and judges |

## Priority, so the booth is safe even if we run short of time

**Tier 1 (must have):**
1. Import the R3 into the platform.
2. Make 4 hero renders and a turntable video in Live Rendering.
3. Build a 3-scene Creative Experience: Normal → Spill → Service.
4. Make the share link and the QR card.

**Tier 2 (strong):**
- Add the river-rise animation and the exploded view (scenes 2 and 6).
- Add the technician (Human Animation Studio).
- Add the Kopargaon opening shot (Planets Studio).

**Tier 3 (if time):**
- Twin Factory line.
- A digital twin of the 1:5 live model, shown next to the physical model.

## Timeline

| Dates | Work | Owner |
|---|---|---|
| 7 Nov | Submit the deck. Open Creative Experience and Live Rendering once, to confirm they run in the browser or need the native app. | Soham + Claude |
| 8–9 Nov | Import the STEP, prepare the model, build the river ambience, make the renders | Prasad (CAD) + Claude |
| 10–12 Nov | Creative Experience scenes 1, 3, 5; share link; QR | Tanmay + Claude |
| 13–14 Nov | Tier 2 scenes; booth display loop (renders + turntable + our 4 videos) | Bhakti / Prasad |
| 15–16 Nov | Freeze. Test the link on another laptop in a plain browser; save an offline video copy on a USB stick | Soham |
| 17–18 Nov | 3DSwym post; rehearse the booth walk-through | Whole team |

## At the booth (19 Nov)

- **Office laptop:** the experience runs on a loop, and visitors can click through it.
- **Table:** the 1:5 live model, and the QR card ("Explore AquaSentinel in 3D").
- **Booth line:** "Designed in SOLIDWORKS, simulated in SOLIDWORKS Simulation, brought to life with 3DEXCITE on 3DEXPERIENCE."
- **Backup:** the turntable and story video on USB, in case the network fails.

## Risks and how we handle them

| Risk | Handling |
|---|---|
| Some 3DEXCITE apps need the native 3DEXPERIENCE app and a good GPU | Check on 7 Nov; use the college lab PC if this laptop struggles |
| The full 66-part model is too heavy | Simplify in Experience Models Preparation; hide fasteners |
| No internet at the venue | Offline video copy on USB, plus the PDF deck |
| Nobody on the team has used these apps | The 3DS edu workshop recordings on 3DSwym ("Virtual Storyteller role" workshop, "Create interactive experiences" webinar); Claude drives the platform step by step |

## Checked on the platform and on this PC (7 Nov, 12:20)

| Finding | Meaning |
|---|---|
| Creative Experience, Ambience Studio, Live Rendering, Rendering Scene Design, Experience Models Preparation, Human Animation Studio, Planets Studio and Twin Factory are **native apps** (no web link in the Compass) | They need the **3DEXPERIENCE native app installed on Windows**. It installs from the Compass the first time an app is opened: a large download, and it needs the user's approval. |
| **3DStory** and **3DPlay** are **web apps** | These open in any browser, which is what the organisers' booth laptop can show. The plan: build with the native apps on our PC, publish, show in 3DPlay or 3DStory at the booth. |
| This PC has **3DEXPERIENCE Exchange for SOLIDWORKS** installed | We can save the R3 straight from SOLIDWORKS to the platform; no STEP conversion is needed. |
| This PC: NVIDIA Quadro T2000 (4 GB), 32 GB RAM | A workstation-class GPU, suitable for the native apps (check the certified-hardware list when installing). |
| The 3DEXPERIENCE native app is **not installed yet** | Step 1 = install it (with the user's OK), then open Creative Experience once to confirm. |

## Install log (7 Nov, 12:30)

- `3DEXPERIENCELauncher.msi` downloaded from the platform. Its digital signature is valid, issued to DASSAULT SYSTEMES SE (DigiCert).
- Installed: **3DEXPERIENCE Launcher 26.10.632**. The service is running and answers on `http://127.0.0.1:20250`.
- **Limitation:** the Claude app's built-in browser pane blocks pages from talking to the launcher (`ERR_BLOCKED_BY_CLIENT`). Native apps must be started from **Edge or Chrome**: open the AAKRUTI dashboard there → Compass → Virtual Storyteller for Education → Creative Experience. The launcher then installs the native apps (several GB).
