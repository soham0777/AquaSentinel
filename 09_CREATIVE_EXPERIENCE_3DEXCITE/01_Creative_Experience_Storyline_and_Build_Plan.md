# AquaSentinel × Creative Experience: storyline and build plan

Written 13 Nov 2026 for the India Geo Finale (booth 19 Nov, pitch 20 Nov, Pune).
Sources: the three 3DEXCITE webinar recordings the organisers shared (AIC 2025 Webinars 7, 9, 10),
our 7 Nov plan (`00_Virtual_Storyteller_Plan.md`), the finale deck, and the project folders.

---

## 1. What the organisers expect

These points come from the three recordings, in the organisers' own framing.

| What they said | What it means for us |
|---|---|
| Storytelling means showing **how the product fits into real life**: the problem, who uses it, and how it makes their life better. Data alone is not enough. | Our story starts with the river and the people downstream, not with the CAD. |
| **Staging:** put the product in its real context, for example "a car on a road". Control the background, the scale and the angle. | Show the float on its pole at a bridge pier, at dusk, with water, a pier and a person for scale. |
| **Materials matter most.** Use 3DS PBR materials with clear names, and put them on every visible part. | Hulls, pole, carriage, pod, beacon lens and water each get a named material, applied before anything else. |
| "Good lighting brings your design to life." Use a rectangle light for the whole scene and a spotlight for one feature. "The camera tells the story." | One camera per act, named, with a spotlight on the part that matters in that act. |
| **Behaviours** (explode, rotate, motion, open/close) plus **natural-language scenarios** ("Each time Explode is clicked, R3 explodes") plus **2D buttons**. No coding needed. | Each act of our story is one button. The judges click through it themselves. |
| **Humans** can be added, posed and scaled. | A technician on the bridge for the service act. This is also the scale reference. |
| **Renders and video.** Scoring is on "your design and your creative experience". Video earns more marks than still images. The 2025 teams screen-recorded their experiences. | Make 4 hero renders plus a 60–90 s screen recording of the experience, with no music. |
| **AR:** export a glTF (Publish → Play optimization → model for play), put it on a web page, and the jury scans a QR code to see the product life-size. | A QR card at the booth puts the full-size AquaSentinel on the table in front of the judges. |

The finale setup changes how we deliver it:
- **Personal laptops are not allowed at the booth.** The organisers supply one display, driven by their own office laptop.
- So the interactive experience runs on **our** PC only while we build it.
- At the booth it reaches the judges as:
  - (a) a video playing on the booth display;
  - (b) hero renders;
  - (c) the AR QR code on the judges' own phones;
  - (d) if it works on the organisers' laptop, the 3DPlay web link.

---

## 2. The story: "A night on the Godavari"

One sentence: **a float that lives in the river, sees a night-time spill, raises the alarm and keeps the proof.**
The acts follow the finale deck, so the booth, the video and the pitch tell the same story.

| Act | Title on screen | What the judge sees | Behaviour / scenario (natural language) | Camera | Claim we can defend |
|---|---|---|---|---|---|
| 0 | **AquaSentinel** · "Click Start" | Logo image over a dusk river | `Each time Act0 is active, CamTitle becomes current.` `Each time Start is clicked, Act1 becomes active.` | wide, slow orbit | - |
| 1 | **Dusk at the bridge** | R3 float on its pole at a pier; beacon **green**; calm water | `Rotate` off; the beacon lens uses the green emissive material | CamWide | "Reads the water every 15 minutes" |
| 2 | **The river rises** | The float slides up the pole (2 m) and back down | `Motion` / path on the float group, along +Z, about 4 s each way | CamSide (sees the pole) | "No anchors, no motor: the river lifts it" (deck slide 8) |
| 3 | **02:00, a spill** | Water material swaps to brown; beacon lens swaps to **red**; an SMS card (2D image) appears | `Each time Spill is clicked, Water becomes WaterBrown, Lens becomes LensRed, SMS becomes visible.` | CamBeacon (close on the beacon) | "Red within two readings (about 30 min), SMS goes out"; the water colour is labelled **illustration** |
| 4 | **It keeps the evidence** | Spotlight on the autosampler; the lid opens; one bottle highlighted | `Open/Close` behaviour on the sampler lid | CamSampler | "Bottles the water at the moment of the spill" |
| 5 | **Service from the bridge** | A technician (Human) on the bridge deck; the carriage gate opens; the sensor cartridge lifts out | `Open/Close` on the gate; `Motion` (+Z) on the cartridge group | CamService | "Installed and serviced from the bridge" |
| 6 | **Inside the sentinel** | Exploded view; buttons **Explode / Assemble**; 6 callouts (2D images) | `Explode` behaviour: distance factor 2, 3 s, one direction | CamExplode | "66-part R3, assembled and simulated in SOLIDWORKS" |
| 7 | **Proof on the table** | The 1:5 LIVE model on a turntable, next to text: "Printed. Real sensors. See it live at our booth." | `Rotate` (Y), with Start / Stop buttons | CamModel | Only what is true on 19 Nov (see section 5) |
| 8 | **See it life-size** | QR image + "Scan to place AquaSentinel on your table" | - | CamTitle | AR link (section 4) |

**Buttons, bottom-left:** Start · Rise · Spill · Sample · Service · Inside · Model · Restart. Each button only appears in its own act, using the "becomes visible" trick from Webinar 9.

**Voice and text:** short on-screen lines only, no music. The finale rule is that videos must have no background music.

---

## 3. Build order (who, what, which app)

This PC qualifies: NVIDIA Quadro T2000 and 32 GB RAM. The webinar minimum is 32 GB RAM plus a dedicated GPU. Build everything on this PC and share through our collaborative space.

### Day 1 (13–14 Nov): get in and bring the model in

1. **Sign in and launch from Chrome or Edge, not from the Claude browser pane.** The Claude pane blocks the 3DEXPERIENCE launcher (`127.0.0.1:20250`); we found that on 7 Nov.
   1. In Chrome, open Dashboard → Compass → *Virtual Storyteller for Education* → **Creative Experience**.
   2. The first launch installs the native app. It is several GB, so approve the download and wait.
2. **Create our collaborative space** in 3DSpace:
   - name: `AquaSentinel_AG26-1500$41`;
   - family: Design;
   - visibility: **Private**.
   - Add the teammates as Leader or Author.
   - Never import into the common space, which every team can see.
3. **Model.** Use the STEP we already have: `04_R3_FULL_SIZE_DESIGN/08_Assembly_STEP_GLB/AquaSentinel_R3_Assembly_MidWater.step` (16 MB, 66 parts).
   1. In CXP: **+ → Import → STEP → from disk**.
   2. In the preview, right-click the top node → **Properties** and **copy the PRD name** into our notes. Use that name to find the model again.
   3. Right-click the 3D actor → **Insert existing product** → search for the PRD name.
   4. Fix the orientation in **Properties**: Rotation 90° on X if it lies flat, Position 0,0,0.
   5. Rename the experience `AquaSentinel_Godavari_v1_Soham` and save it (Share arrow → Save).
4. **Check every part arrived** by rotating all round the model. **Hide the parts we no longer claim** (section 5).

### Day 2 (14–15 Nov): materials and staging (most of the time goes here)

1. Open the product's **Properties → Open → Rendering Scene Design**.
2. **Create and apply → covering → 3DS PBR** for each material below. Use clear names; each one appears once per part type, and **Pick & apply** copies it to the rest.

   | Material | Base colour | Metallic | Roughness | Parts |
   |---|---|---|---|---|
   | `HDPE_Hull_Yellow_AS` | amber yellow | 0 | 0.45 | pontoon hulls, bow bumpers |
   | `SS316_Brushed_AS` | light grey | 1 | 0.3 | pole, carriage, brackets, deck plate, rails |
   | `PE_Black_AS` | near-black | 0 | 0.6 | sensor well, cartridge cap, rollers |
   | `Pod_White_IP67_AS` | off-white | 0 | 0.35 | power pod, sampler cassette |
   | `PV_Glass_AS` | dark blue | 0.2 | 0.05 | solar panel |
   | `Lens_Green_Emissive_AS` | green, emission on | 0 | 0.1 | beacon lens (normal) |
   | `Lens_Red_Emissive_AS` | red, emission on | 0 | 0.1 | duplicate of the green lens, used in act 3 |
   | `Water_Clean_AS` / `Water_Brown_AS` | blue-green / muddy brown, glass type | 0 | 0.05 | a large flat **plane primitive** (the river) |
   | `Concrete_Pier_AS` | grey | 0 | 0.9 | a **cube primitive** scaled into a bridge pier and deck |

3. **Staging:**
   - Viewer → turn the grid, path, point, lights and camera icons off.
   - Ambience: a dusk or outdoor one from the library.
   - **Rectangle light:** cool tone, low intensity, for the whole scene.
   - **Spotlight:** warm, on the beacon.
   - **Scale check:** use the human from act 5. A person is about 1.7 m tall; the float is about 1.5 m long.

### Day 3 (15–16 Nov): story, buttons and cameras

1. **Cameras:** create one camera per act (`CamTitle`, `CamWide`, `CamSide`, `CamBeacon`, `CamSampler`, `CamService`, `CamExplode`, `CamModel`). Frame each view, then right-click the camera → **Apply current view**.
2. **Behaviours (add from the library):**
   - **Explode** on the R3: −X, distance factor 2, 3 s;
   - **Rotate** on the 1:5 model;
   - **Open/Close** on the gate and the sampler lid;
   - **Motion** on the float group and the cartridge.
3. **2D buttons:** make one for each act. Set Name = Label, for example `Spill`, because the names show up in the scenario editor.
4. **Storytelling → Local scenario.** One paragraph per button, in plain English, as in Webinar 9. For example:
   - `Each time Spill is clicked, CamBeacon becomes current, Lens becomes LensRed, Water becomes WaterBrown, SMS becomes visible.`
   - `Each time Inside is clicked, CamExplode becomes current, R3 explodes.`
   - `Each time Restart is clicked, R3 implodes, Lens becomes LensGreen, Water becomes WaterClean, Act1 becomes active.`
5. **Human (act 5):** Assemble → Human → Create, then pick one adult. Scale it to real height. Use **Create posture → Grab an object** on the gate's T-handle.
6. **Exact names to confirm in the app:** the scenario wording for "becomes", "visible" and material swaps depends on what the editor offers. Pick from its drop-downs; it only accepts sentences it can complete.
7. Save with Ctrl+S after every step. The app can crash (it did in the webinar); on restart choose **Restore previous scene**.

### Day 4 (16–17 Nov): outputs for the booth

1. **4 hero renders** (render tab, or a clean screenshot with the UI panels closed):
   - (1) dusk at the bridge, beacon green;
   - (2) spill, beacon red;
   - (3) exploded view with callouts;
   - (4) the technician servicing it from the bridge.
2. **Video, 60–90 s:**
   1. Close every panel, then press Play and screen-record (Windows: Win+Alt+R with Xbox Game Bar, or OBS).
   2. Click through acts 0 → 8 at a calm pace.
   3. **No music.**
   4. Add 1-line captions per act if needed.
   5. Save it as `09_CREATIVE_EXPERIENCE_3DEXCITE/04_story_video/AquaSentinel_Story_A_Night_on_the_Godavari_1080p.mp4`.
3. **AR model:**
   1. Publish → **Play optimization** → Custom → + → **Model for play (glTF)**. The camera is not supported in AR, which is normal.
   2. Choose a local folder and Publish. This takes about 4–5 min.
   3. Check the result in any glTF viewer.
   4. The hosting decision is in section 4.
4. **3DPlay link:** publish the experience and test the link **in a plain browser on another PC**. If it plays there, it can also run on the booth laptop.

### Day 5 (18 Nov): freeze and rehearse

- Put everything on a USB stick (video, renders, AR link, QR PDF). If the venue network fails, the stick still works.
- Do 3 rehearsals of a 60-second booth walk-through, one sentence per act.
- Optionally, make a 3DSwym post in **our private team community**, never the global one.

---

## 4. Decisions that need your OK

1. **Where to host the AR model.**
   - Webinar 10 put the glTF in a **public GitHub repository** with GitHub Pages.
   - That publishes our 3D model to the internet, permanently and visible to anyone.
   - Options:
     - (a) a public repository with **only the simplified exterior model** (hulls, pole, pod, beacon; no internals);
     - (b) skip AR and rely on the video and renders.
   - I won't publish anything without your yes.
2. **Which R3 version is shown.** The R3 CAD still contains parts our Pi-based product has dropped. We hide them (section 5), so the experience matches the deck.
3. **Who builds.** It has to be one person on this PC, with me guiding step by step. I cannot click inside the native 3DEXPERIENCE app myself. I can drive the platform pages in Chrome and check every result from screenshots.

---

## 5. Honesty rules (AAKRUTI Art. 10: a false statement can disqualify)

- **Hide or leave unlabelled** the R3 parts we dropped when the product moved to the Raspberry Pi on 6 Nov:
  - `AS3-423` ID band for the optical DO probe (dissolved oxygen is dropped);
  - `AS3-415` optical wiper arm: hide it (the wiper is dropped). Keep `AS3-413` visible because it is the cartridge's spine, but never call it a wiper shaft;
  - `AS3-712` ultrasonic stage sensor (the river-level sensor is dropped);
  - `AS3-603` bottle carousel. Show **one** sample bottle, not 4;
  - `AS3-711` antenna: keep it, but call it the "GSM / SMS antenna", never "LTE";
  - `AS3-515` controller board: don't label it; it is inside the pod.
- **Wording:**
  - say "3D animation of our CAD" and "assembled and simulated in SOLIDWORKS";
  - never say "designed in SOLIDWORKS" for the R3: its geometry started in our Python generator and was rebuilt as native SOLIDWORKS features;
  - the 17 LIVE-model parts *were* designed natively in SOLIDWORKS, so that phrase is fine for them.
- **Spill colour:** the brown water is an **illustration**. Put that word on screen in act 3.
- **The 1:5 model, act 7:** claim only what is true on 19 Nov.
  - As of 12–13 Nov every sensor and output was proven through our own Sensor Hub PCB on the bench: DHT11, LDR, turbidity, MQ-3, RGB beacon, pump, TDS, DS18B20, pH (voltage; calibration pending).
  - The SIM800L and the Raspberry Pi link are **not tested yet**.
  - Don't show an SMS from the model until it has really sent one.
- The SMS card in act 3 is part of the **R3 story**. It is drawn as "what the officer receives", not as a screenshot of a real message.

---

## 6. Assets already in the project

| Need | File |
|---|---|
| R3 model (66 parts) | `04_R3_FULL_SIZE_DESIGN/08_Assembly_STEP_GLB/AquaSentinel_R3_Assembly_MidWater.step` (+ `.glb`, 1.4 MB, handy as the AR fallback) |
| R3 in SOLIDWORKS 2026 | `04_R3_FULL_SIZE_DESIGN/03b_SOLIDWORKS_2026_NATIVE/AquaSentinel_R3_Assembly_NATIVE.SLDASM` (native features; also CXP-importable) |
| 1:5 LIVE model | `05_LIVE_MODEL_1to5/05_SOLIDWORKS_ASSEMBLY/AquaSentinel_LIVE_1to5_Assembly.SLDASM` |
| Electronics bay in SOLIDWORKS | `03_ELECTRONICS_RASPBERRY_PI/SOLIDWORKS_Electronics_Bay/AquaSentinel_Electronics_Bay_1to5.SLDASM` |
| Reference renders (for the look) | `04_R3_FULL_SIZE_DESIGN/06_Renders/` (hero river, exploded, gate open, cartridge pulled up) |
| Story text, numbers | finale deck slides 1–15 (2 m rise, 15-minute cycle, ₹48,000, 296 / 54 sites) |
| Existing videos (muted ones are OK for the booth loop) | `02_FILMS/` |
