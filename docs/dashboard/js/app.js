// AquaSentinel v2.0 — Web Console Logic
// Trilingual Community Portal, Real-time Sensor Monitoring & 1-D River Transport Simulator

document.addEventListener('DOMContentLoaded', () => {

  // --- TRILINGUAL DICTIONARY ---
  const i18n = {
    en: {
      appTitle: "AquaSentinel Early-Warning & Community Protection Console",
      appSub: "Maharashtra Basin — Godavari River Corridor (Kopargaon Bridge to Puntamba Reach)",
      modeOperator: "Command Center",
      modeCommunity: "Community Portal (लोकसहभाग)",
      demoBadge: "DEMO MODE",
      demoBanner: "⚠️ DEMO MODE ACTIVE — Replaying Synthetic Godavari River Pollution Scenario for Evaluation",
      pillNode: "NODE 01: ACTIVE",
      sensorHeader: "In-Situ RS485 Submerged Sensor Array (15-Minute Epoch)",
      sensorBadge: "4 Industrial Probes + Ultrasonic Stage",
      lblPh: "pH Level (Glass Probe)",
      lblTurb: "Turbidity (90° Nephelometric)",
      lblDo: "Dissolved Oxygen (Optical DO)",
      lblEc: "Electrical Conductivity (EC)",
      lblTemp: "Water Temperature",
      lblStage: "River Water Level (Stage)",
      roboticsHeader: "Robotics Closed-Loop Actuation Status",
      btnCoc: "View Chain-of-Custody Card",
      btnWipe: "Trigger Manual Wiper Sweep",
      wiperSub: "Interval: Every 6 Hours | Next Sweep: 3h 42m | Drift Auto-Trigger: Active",
      commTitle: "Godavari River Water Safety Advisory (गोदावरी जलसुरक्षा सूचना)",
      commSub: "Location: Kopargaon Bridge to Puntamba Reach (19.0 km)",
      beaconSafeState: "BEACON STATUS: SAFE (जलदीप: सुरक्षित)",
      beaconSafeHead: "River Water is Safe for Community Use",
      beaconSafeSub: "Water quality is within normal biological baseline. Normal activities permitted.",
      beaconAlertState: "BEACON STATUS: DANGER (जलदीप: धोक्याची सूचना)",
      beaconAlertHead: "CONTAMINATION ALERT — DO NOT USE RIVER WATER",
      beaconAlertSub: "Upstream pollution spike detected. Water intake pumps isolated.",
      guideDrinkTitle: "Drinking Water Supply (पिण्याचे पाणी)",
      guideDrinkSafe: "Municipal piped water from storage reservoirs is safe. Raw river water must be boiled.",
      guideDrinkAlert: "DO NOT DRINK RAW RIVER WATER. Downstream treatment plants have been alerted to isolate intakes.",
      guideBathTitle: "Bathing & Ghat Activities (स्नान व घाट वापर)",
      guideBathSafe: "River ghats at Puntamba and Kopargaon are safe for regular washing and rituals.",
      guideBathAlert: "AVOID DIRECT CONTACT AT GHATS. Toxic / organic plume is advancing downstream.",
      guideFarmTitle: "Agriculture & Cattle (शेती व पशुधन)",
      guideFarmSafe: "Lift irrigation schemes operating normally. Electrical conductivity is within permissible agricultural limits.",
      guideFarmAlert: "SUSPEND LIFT IRRIGATION PUMPS. Protect crops and cattle from chemical shock load.",
      hotlineTitle: "Kopargaon Municipal Emergency Water Cell:",
      btnSms: "Subscribe to Free SMS Alerts",
      transportTitle: "1-D River Plume Transport & Warning Horizon",
      btnLockout: "EMERGENCY INTAKE LOCKOUT (TRIP PUMPS)",
      btnLockoutActive: "LOCKOUT ENGAGED: ALL INTAKES ISOLATED",
      simTitle: "Event Simulation & Demonstration Controls",
      simDesc: "Click below to inject simulated lotic contamination plumes into the live model and observe downstream advance warning countdowns:",
      simBtnAcid: "Simulate Industrial Acid Dump",
      simBtnSewage: "Simulate 9.98 MLD Sewage Spill",
      simBtnReset: "Reset to Clean Baseline"
    },
    mr: {
      appTitle: "अ‍ॅक्वासेंटिनेल नदी जलसुरक्षा व पूर्वसूचना नियंत्रण कक्ष",
      appSub: "महाराष्ट्र खोरे — गोदावरी नदी पट्टा (कोपरगाव पूल ते पुणतांबा परिसर)",
      modeOperator: "तांत्रिक नियंत्रण कक्ष",
      modeCommunity: "लोकसहभाग माहिती पोर्टल",
      demoBadge: "डेमो मोड सक्रिय",
      demoBanner: "⚠️ डेमो मोड सुरू आहे — गोदावरी नदी प्रदूषण परिस्थितीचे थेट सादरीकरण",
      pillNode: "केंद्र ०१: सक्रिय",
      sensorHeader: "स्थानिक RS485 सेन्सर प्रणाली (प्रत्येक १५ मिनिटांची नोंद)",
      sensorBadge: "४ औद्योगिक सेन्सर्स + अल्ट्रासॉनिक जलपातळी",
      lblPh: "सामू / pH पातळी (ग्लास प्रोब)",
      lblTurb: "गढूळपणा (टर्बिडिटी - NTU)",
      lblDo: "विद्राव्य ऑक्सिजन (DO)",
      lblEc: "विद्युत वाहकता (EC)",
      lblTemp: "नदीच्या पाण्याचे तापमान",
      lblStage: "नदीतील पाण्याची पातळी (मीटर)",
      roboticsHeader: "स्वयंचलित नमुना व स्वच्छता यंत्रणा",
      btnCoc: "कायदेशीर पुरावा कार्ड पहा (CoC)",
      btnWipe: "स्वच्छता वायपर सुरू करा",
      wiperSub: "कालावधी: दर ६ तासांनी | पुढील स्वच्छता: ३ तास ४२ मिनिटांनी",
      commTitle: "गोदावरी नदी जलसुरक्षा सूचना (लोकसहभाग)",
      commSub: "स्थान: कोपरगाव पूल ते पुणतांबा घाट (१९.० किमी पट्टा)",
      beaconSafeState: "जलदीप स्थिती: सुरक्षित (हिरवा दिवा)",
      beaconSafeHead: "नदीचे पाणी वापरासाठी सुरक्षित आहे",
      beaconSafeSub: "पाण्याची गुणवत्ता सामान्य मर्यादेत आहे. नेहमीप्रमाणे वापर करता येईल.",
      beaconAlertState: "जलदीप स्थिती: धोकादायक (लाल दिवा)",
      beaconAlertHead: "धोका! नदीचे पाणी तात्काळ वापरणे थांबवा",
      beaconAlertSub: "वरच्या भागात अचानक प्रदूषण आढळले आहे. पाणी उपसा तात्काळ थांबवण्यात आला आहे.",
      guideDrinkTitle: "पिण्याचे पाणी (Drinking Supply)",
      guideDrinkSafe: "साठवण तलावातील नळाचे पाणी सुरक्षित आहे. नदीचे कच्चे पाणी उकळूनच वापरावे.",
      guideDrinkAlert: "नदीचे पाणी अजिबात पिऊ नका! जलशुद्धीकरण केंद्रांना उपसा बंद करण्याचे आदेश दिले आहेत.",
      guideBathTitle: "स्नान व कपडे धुणे (Bathing & Ghats)",
      guideBathSafe: "पुणतांबा व कोपरगाव घाटावर नेहमीप्रमाणे वापर सुरक्षित आहे.",
      guideBathAlert: "घाटावर पाण्याचा संपर्क टाळा! रासायनिक किंवा दूषित पाण्याचा लोट खाली येत आहे.",
      guideFarmTitle: "शेती व पशुधन (Agriculture & Cattle)",
      guideFarmSafe: "उपसा सिंचन योजना चालू ठेवण्यास हरकत नाही. क्षारता सामान्य आहे.",
      guideFarmAlert: "शेतीसाठी पाणी उपसा त्वरित थांबवा! जनावरांना नदीवर पाणी पाजू नका.",
      hotlineTitle: "कोपरगाव नगरपरिषद आपत्कालीन पाणी नियंत्रण कक्ष:",
      btnSms: "मोफत SMS सूचना सुरू करा",
      transportTitle: "नदी प्रवाह व आगाऊ धोक्याचा इशारा (ETA)",
      btnLockout: "आपत्कालीन पंप लॉकआउट (सर्व उपसा बंद करा)",
      btnLockoutActive: "लॉकआउट सक्रिय: सर्व उपसा पंप बंद केले आहेत",
      simTitle: "प्रात्यक्षिक व प्रदूषण चाचणी नियंत्रक",
      simDesc: "गोदावरी नदीत प्रदूषण उद्भवल्यास काय होते हे पाहण्यासाठी खालील बटणे दाबा:",
      simBtnAcid: "कारखान्याचे रासायनिक आम्ल गळती चाचणी",
      simBtnSewage: "९.९८ MLD सांडपाणी गळती चाचणी",
      simBtnReset: "सर्व पूर्ववत सामान्य करा"
    },
    hi: {
      appTitle: "एक्वासेंटिनल नदी जल सुरक्षा एवं पूर्व चेतावनी नियंत्रण कक्ष",
      appSub: "महाराष्ट्र बेसिन — गोदावरी नदी क्षेत्र (कोपरगांव पुल से पुणतांबा तक)",
      modeOperator: "तकनीकी कमांड सेंटर",
      modeCommunity: "जनसंवाद / नागरिक पोर्टल",
      demoBadge: "डेमो मोड",
      demoBanner: "⚠️ डेमो मोड सक्रिय — गोदावरी नदी प्रदूषण सिमुलेशन का प्रदर्शन",
      pillNode: "नोड ०१: सक्रिय",
      sensorHeader: "स्वचालित RS485 सेंसर प्रणाली (प्रत्येक १५ मिनट)",
      sensorBadge: "४ औद्योगिक सेंसर + अल्ट्रासोनिक जल स्तर",
      lblPh: "पीएच स्तर (pH Probe)",
      lblTurb: "गंदलापन (Turbidity - NTU)",
      lblDo: "घुलित ऑक्सीजन (DO - Dissolved Oxygen)",
      lblEc: "विद्युत चालकता (EC)",
      lblTemp: "जल तापमान",
      lblStage: "नदी जल स्तर (मीटर)",
      roboticsHeader: "रोबोटिक सैंपल संग्रह एवं वाइपर स्थिति",
      btnCoc: "विधिक साक्ष्य कार्ड देखें (CoC)",
      btnWipe: "वाइपर सफाई शुरू करें",
      wiperSub: "अंतराल: हर ६ घंटे | अगली सफाई: ३ घंटे ४२ मिनट बाद",
      commTitle: "गोदावरी नदी जल सुरक्षा परामर्श",
      commSub: "स्थान: कोपरगांव पुल से पुणतांबा घाट (१९.० किमी)",
      beaconSafeState: "जलदीप स्थिति: सुरक्षित (हरा संकेत)",
      beaconSafeHead: "नदी का जल उपयोग के लिए सुरक्षित है",
      beaconSafeSub: "पानी की गुणवत्ता सामान्य मानकों के भीतर है।",
      beaconAlertState: "जलदीप स्थिति: चेतावनी / खतरा (लाल संकेत)",
      beaconAlertHead: "चेतावनी! नदी का जल उपयोग तुरंत बंद करें",
      beaconAlertSub: "ऊपरी हिस्से में रासायनिक या सीवेज प्रदूषण दर्ज किया गया है।",
      guideDrinkTitle: "पेयजल आपूर्ति (Drinking Water)",
      guideDrinkSafe: "नगरपालिका का जलापूर्ति सुरक्षित है। नदी का कच्चा पानी उबाल कर पिएं।",
      guideDrinkAlert: "नदी का कच्चा पानी न पिएं! डाउनस्ट्रीम पम्पिंग स्टेशन बंद कर दिए गए हैं।",
      guideBathTitle: "स्नान व घाट उपयोग (Ghats & Bathing)",
      guideBathSafe: "घाटों पर स्नान और सामान्य उपयोग सुरक्षित है।",
      guideBathAlert: "घाटों पर नदी के सीधे संपर्क से बचें! प्रदूषित धारा आगे बढ़ रही है।",
      guideFarmTitle: "कृषि एवं मवेशी (Farming & Cattle)",
      guideFarmSafe: "सिंचाई लिफ्ट योजनाएं सामान्य रूप से चल रही हैं।",
      guideFarmAlert: "खेतों में नदी का पानी खींचना तुरंत बंद करें! मवेशियों को दूर रखें।",
      hotlineTitle: "कोपरगांव नगर परिषद आपातकालीन जल नियंत्रण कक्ष:",
      btnSms: "मुफ्त एसएमएस अलर्ट चालू करें",
      transportTitle: "नदी जल प्रवाह एवं अग्रिम चेतावनी समय (ETA)",
      btnLockout: "आपातकालीन पंप लॉकआउट (पानी खींचना बंद करें)",
      btnLockoutActive: "लॉकआउट सक्रिय: सभी पंप बंद किए गए हैं",
      simTitle: "प्रदूषण सिमुलेशन एवं परीक्षण नियंत्रण",
      simDesc: "प्रदूषण का प्रभाव और अग्रिम चेतावनी समय देखने के लिए नीचे क्लिक करें:",
      simBtnAcid: "औद्योगिक अपशिष्ट / एसिड रिसाव टेस्ट",
      simBtnSewage: "९.९८ MLD सीवेज रिसाव टेस्ट",
      simBtnReset: "सामान्य स्थिति पर रीसेट करें"
    }
  };

  // --- STATE ---
  const state = {
    lang: 'en',
    mode: 'operator', // 'operator' or 'community'
    demoActive: true,
    isAlert: false,
    alertReason: 'NONE',
    sensors: {
      ph: 7.42,
      turb: 8.4,
      do: 7.15,
      ec: 382,
      temp: 24.6,
      stage: 1.35
    },
    plume: {
      active: false,
      posKm: 0.0,
      velocityKmh: 2.7, // 0.75 m/s = 2.7 km/h
      widthKm: 1.2
    },
    lockoutActive: false,
    autosampler: {
      vial1: "SEALED (250mL)",
      vial2: "READY (Sterile)",
      vial3: "READY (Sterile)",
      vial4: "READY (Sterile)"
    }
  };

  // --- DOM CACHE ---
  const dom = {
    // Mode toggles
    btnModeOperator: document.getElementById('btn-mode-operator'),
    btnModeCommunity: document.getElementById('btn-mode-community'),
    viewOperator: document.getElementById('view-operator'),
    viewCommunity: document.getElementById('view-community'),
    
    // Language buttons
    langBtns: document.querySelectorAll('.lang-btn'),
    
    // Demo toggle
    demoToggle: document.getElementById('demo-mode-toggle'),
    demoBanner: document.getElementById('demo-banner'),
    
    // Alert Banner
    alertBanner: document.getElementById('alert-banner'),
    alertTitle: document.getElementById('txt-alert-title-text'),
    alertDesc: document.getElementById('alert-desc'),

    // Sensors
    valPh: document.getElementById('val-ph'),
    barPh: document.getElementById('bar-ph'),
    valTurb: document.getElementById('val-turb'),
    barTurb: document.getElementById('bar-turb'),
    valDo: document.getElementById('val-do'),
    barDo: document.getElementById('bar-do'),
    valEc: document.getElementById('val-ec'),
    barEc: document.getElementById('bar-ec'),
    valTemp: document.getElementById('val-temp'),
    barTemp: document.getElementById('bar-temp'),
    valStage: document.getElementById('val-stage'),
    barStage: document.getElementById('bar-stage'),

    // Beacon & Community
    beaconHalo: document.getElementById('beacon-halo'),
    txtBeaconState: document.getElementById('txt-beacon-state'),
    txtBeaconHeadline: document.getElementById('txt-beacon-headline'),
    txtBeaconSub: document.getElementById('txt-beacon-sub'),
    guideDrinkDesc: document.getElementById('txt-guide-drink-desc'),
    guideBathDesc: document.getElementById('txt-guide-bath-desc'),
    guideFarmDesc: document.getElementById('txt-guide-farm-desc'),
    guideDrinkCard: document.getElementById('guide-drinking'),
    guideBathCard: document.getElementById('guide-bathing'),
    guideFarmCard: document.getElementById('guide-farming'),

    // River plume
    plumeIndicator: document.getElementById('plume-indicator'),
    tagA: document.getElementById('tag-a'),
    timeA: document.getElementById('time-a'),
    descA: document.getElementById('desc-a'),
    tagB: document.getElementById('tag-b'),
    timeB: document.getElementById('time-b'),
    descB: document.getElementById('desc-b'),

    // Buttons
    btnLockout: document.getElementById('btn-lockout-pumps'),
    txtBtnLockout: document.getElementById('txt-btn-lockout'),
    btnSimAcid: document.getElementById('btn-sim-acid'),
    btnSimSewage: document.getElementById('btn-sim-sewage'),
    btnSimReset: document.getElementById('btn-sim-reset'),
    btnManualWipe: document.getElementById('btn-manual-wipe'),
    txtWiperSub: document.getElementById('txt-wiper-sub'),
    btnSubscribeSms: document.getElementById('btn-subscribe-sms'),

    // Modal CoC
    modalCoc: document.getElementById('modal-coc'),
    btnOpenCoc: document.getElementById('btn-open-coc'),
    btnCloseCoc: document.getElementById('btn-close-coc'),
    btnModalDismiss: document.getElementById('btn-modal-dismiss'),
    cocTime: document.getElementById('coc-time'),

    // Vials
    vial1: document.getElementById('vial-1'),
    vial2: document.getElementById('vial-2'),
    vial3: document.getElementById('vial-3'),
    vial4: document.getElementById('vial-4')
  };

  // --- LOCALIZATION UPDATE ---
  function applyLanguage(lang) {
    state.lang = lang;
    const t = i18n[lang];

    // Header & Brand
    document.getElementById('txt-app-title').innerText = t.appTitle;
    document.getElementById('txt-app-sub').innerText = t.appSub;
    document.getElementById('txt-mode-operator').innerText = t.modeOperator;
    document.getElementById('txt-mode-community').innerText = t.modeCommunity;
    document.getElementById('txt-demo-badge').innerText = t.demoBadge;
    document.getElementById('txt-demo-banner-text').innerText = t.demoBanner;
    document.getElementById('txt-pill-node').innerText = t.pillNode;

    // Operator View
    document.getElementById('txt-sensor-header').innerText = t.sensorHeader;
    document.getElementById('txt-sensor-badge').innerText = t.sensorBadge;
    document.getElementById('txt-lbl-ph').innerText = t.lblPh;
    document.getElementById('txt-lbl-turb').innerText = t.lblTurb;
    document.getElementById('txt-lbl-do').innerText = t.lblDo;
    document.getElementById('txt-lbl-ec').innerText = t.lblEc;
    document.getElementById('txt-lbl-temp').innerText = t.lblTemp;
    document.getElementById('txt-lbl-stage').innerText = t.lblStage;
    document.getElementById('txt-robotics-header').innerText = t.roboticsHeader;
    document.getElementById('txt-btn-coc').innerText = t.btnCoc;
    document.getElementById('txt-btn-wipe').innerText = t.btnWipe;

    // Community View
    document.getElementById('txt-comm-title').innerText = t.commTitle;
    document.getElementById('txt-comm-sub').innerText = t.commSub;
    document.getElementById('txt-guide-drink-title').innerText = t.guideDrinkTitle;
    document.getElementById('txt-guide-bath-title').innerText = t.guideBathTitle;
    document.getElementById('txt-guide-farm-title').innerText = t.guideFarmTitle;
    document.getElementById('txt-hotline-title').innerText = t.hotlineTitle;
    document.getElementById('txt-btn-sms').innerText = t.btnSms;

    // Transport Sidebar
    document.getElementById('txt-transport-title').innerText = t.transportTitle;
    dom.txtBtnLockout.innerText = state.lockoutActive ? t.btnLockoutActive : t.btnLockout;
    document.getElementById('txt-sim-title').innerText = t.simTitle;
    document.getElementById('txt-sim-desc').innerText = t.simDesc;
    document.getElementById('txt-sim-btn-acid').innerText = t.simBtnAcid;
    document.getElementById('txt-sim-btn-sewage').innerText = t.simBtnSewage;
    document.getElementById('txt-sim-btn-reset').innerText = t.simBtnReset;

    // Update active button state
    dom.langBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    renderBeacon();
  }

  // --- VIEW TOGGLE ---
  function setViewMode(mode) {
    state.mode = mode;
    if (mode === 'operator') {
      dom.viewOperator.style.display = 'block';
      dom.viewCommunity.style.display = 'none';
      dom.btnModeOperator.classList.add('active');
      dom.btnModeCommunity.classList.remove('active');
    } else {
      dom.viewOperator.style.display = 'none';
      dom.viewCommunity.style.display = 'block';
      dom.btnModeOperator.classList.remove('active');
      dom.btnModeCommunity.classList.add('active');
    }
  }

  // --- RENDER SENSORS ---
  function renderSensors() {
    dom.valPh.innerText = state.sensors.ph.toFixed(2);
    dom.valTurb.innerText = state.sensors.turb.toFixed(1);
    dom.valDo.innerText = state.sensors.do.toFixed(2);
    dom.valEc.innerText = Math.round(state.sensors.ec);
    dom.valTemp.innerText = state.sensors.temp.toFixed(1);
    dom.valStage.innerText = state.sensors.stage.toFixed(2);

    // Progress bar fills
    dom.barPh.style.width = Math.min(100, (state.sensors.ph / 14.0) * 100) + '%';
    dom.barTurb.style.width = Math.min(100, (state.sensors.turb / 200.0) * 100) + '%';
    dom.barDo.style.width = Math.min(100, (state.sensors.do / 12.0) * 100) + '%';
    dom.barEc.style.width = Math.min(100, (state.sensors.ec / 2000.0) * 100) + '%';
    dom.barTemp.style.width = Math.min(100, (state.sensors.temp / 50.0) * 100) + '%';
    dom.barStage.style.width = Math.min(100, (state.sensors.stage / 3.0) * 100) + '%';

    // Color accents for anomalies
    const isPhBad = (state.sensors.ph < 6.5 || state.sensors.ph > 8.5);
    const isDoBad = (state.sensors.do < 4.0);
    const isTurbBad = (state.sensors.turb > 25.0);
    const isEcBad = (state.sensors.ec > 800);

    dom.valPh.style.color = isPhBad ? 'var(--accent-rose)' : 'var(--text-main)';
    dom.barPh.style.backgroundColor = isPhBad ? 'var(--accent-rose)' : 'var(--accent-cyan)';

    dom.valDo.style.color = isDoBad ? 'var(--accent-rose)' : 'var(--text-main)';
    dom.barDo.style.backgroundColor = isDoBad ? 'var(--accent-rose)' : 'var(--accent-green)';

    dom.valTurb.style.color = isTurbBad ? 'var(--accent-rose)' : 'var(--text-main)';
    dom.barTurb.style.backgroundColor = isTurbBad ? 'var(--accent-rose)' : 'var(--accent-amber)';

    dom.valEc.style.color = isEcBad ? 'var(--accent-rose)' : 'var(--text-main)';
    dom.barEc.style.backgroundColor = isEcBad ? 'var(--accent-rose)' : 'var(--accent-blue)';
  }

  // --- RENDER BEACON & COMMUNITY ---
  function renderBeacon() {
    const t = i18n[state.lang];
    if (state.isAlert) {
      dom.beaconHalo.className = "beacon-halo-glow danger";
      dom.txtBeaconState.innerText = t.beaconAlertState;
      dom.txtBeaconHeadline.innerText = t.beaconAlertHead;
      dom.txtBeaconSub.innerText = t.beaconAlertSub;

      dom.guideDrinkCard.className = "guidance-card danger";
      dom.guideBathCard.className = "guidance-card danger";
      dom.guideFarmCard.className = "guidance-card danger";

      dom.guideDrinkDesc.innerText = t.guideDrinkAlert;
      dom.guideBathDesc.innerText = t.guideBathAlert;
      dom.guideFarmDesc.innerText = t.guideFarmAlert;

      dom.alertBanner.style.display = "block";
      dom.alertTitle.innerText = "CRITICAL CONTAMINATION SPIKE FLAGGED: " + state.alertReason;
      dom.alertDesc.innerText = `Upstream plume detected at Kopargaon Bridge Outfall. Downstream community warning horizon activated!`;
    } else {
      dom.beaconHalo.className = "beacon-halo-glow safe";
      dom.txtBeaconState.innerText = t.beaconSafeState;
      dom.txtBeaconHeadline.innerText = t.beaconSafeHead;
      dom.txtBeaconSub.innerText = t.beaconSafeSub;

      dom.guideDrinkCard.className = "guidance-card safe";
      dom.guideBathCard.className = "guidance-card safe";
      dom.guideFarmCard.className = "guidance-card safe";

      dom.guideDrinkDesc.innerText = t.guideDrinkSafe;
      dom.guideBathDesc.innerText = t.guideBathSafe;
      dom.guideFarmDesc.innerText = t.guideFarmSafe;

      dom.alertBanner.style.display = "none";
    }
  }

  // --- RIVER PLUME TRANSPORT LOOP (1-D ADVECTIVE-DISPERSIVE) ---
  setInterval(() => {
    if (state.plume.active) {
      // Advance plume position
      state.plume.posKm += (state.plume.velocityKmh * (1.0 / 60.0)); // per second step
      state.plume.widthKm += 0.035; // dispersion spreading

      const totalReachKm = 21.0;
      const leftPercent = Math.max(0, ((state.plume.posKm - state.plume.widthKm / 2) / totalReachKm) * 100);
      const widthPercent = Math.min(100 - leftPercent, (state.plume.widthKm / totalReachKm) * 100);

      dom.plumeIndicator.style.display = 'block';
      dom.plumeIndicator.style.left = leftPercent + '%';
      dom.plumeIndicator.style.width = widthPercent + '%';

      // ETA 1: Lift Scheme A at 4.5 km
      const remA = 4.5 - state.plume.posKm;
      if (remA <= 0) {
        dom.tagA.className = "eta-tag danger";
        dom.tagA.innerText = "PLUME ARRIVED";
        dom.timeA.innerText = "00:00:00";
        dom.descA.innerText = "🚨 Emergency trip engaged; intake isolated.";
      } else {
        const minsA = Math.round((remA / state.plume.velocityKmh) * 60);
        dom.tagA.className = "eta-tag danger";
        dom.tagA.innerText = "WARNING";
        dom.timeA.innerText = `ETA: ${minsA} mins`;
        dom.descA.innerText = `Plume advancing at 2.7 km/h. Advance notice provided!`;
      }

      // ETA 2: Puntamba Ghats at 19.0 km
      const remB = 19.0 - state.plume.posKm;
      if (remB <= 0) {
        dom.tagB.className = "eta-tag danger";
        dom.tagB.innerText = "PLUME ARRIVED";
        dom.timeB.innerText = "00:00:00";
        dom.descB.innerText = "🚨 Ghat advisories broadcasted; riverbank cleared.";
      } else {
        const hrsB = (remB / state.plume.velocityKmh);
        const minsB = Math.round(hrsB * 60);
        dom.tagB.className = "eta-tag danger";
        dom.tagB.innerText = "WARNING";
        dom.timeB.innerText = minsB < 60 ? `ETA: ${minsB} mins` : `ETA: ${(minsB/60).toFixed(1)} hrs`;
        dom.descB.innerText = `Community Jal-Deep Beacon alert active.`;
      }

      // Reset when plume passes reach
      if (state.plume.posKm > 22.0) {
        state.plume.active = false;
        dom.plumeIndicator.style.display = 'none';
      }
    }
  }, 1000);

  // --- SIMULATION TRIGGERS ---
  dom.btnSimAcid.addEventListener('click', () => {
    state.isAlert = true;
    state.alertReason = "INDUSTRIAL ACID / HEAVY METAL DUMP";
    state.sensors.ph = 4.12;
    state.sensors.ec = 1480;
    state.sensors.turb = 45.0;
    state.sensors.do = 3.80;

    state.plume.active = true;
    state.plume.posKm = 0.5;
    state.plume.widthKm = 1.0;

    // Activate autosampler vial 2
    dom.vial2.className = "vial-slot active";
    dom.vial2.querySelector('.vial-status').innerText = "SEALED (250mL)";

    renderSensors();
    renderBeacon();
  });

  dom.btnSimSewage.addEventListener('click', () => {
    state.isAlert = true;
    state.alertReason = "9.98 MLD RAW MUNICIPAL SEWAGE SHOCK LOAD";
    state.sensors.do = 1.85;
    state.sensors.turb = 185.0;
    state.sensors.ec = 890;
    state.sensors.ph = 6.85;

    state.plume.active = true;
    state.plume.posKm = 0.5;
    state.plume.widthKm = 1.4;

    // Activate autosampler vial 3
    dom.vial3.className = "vial-slot active";
    dom.vial3.querySelector('.vial-status').innerText = "SEALED (250mL)";

    renderSensors();
    renderBeacon();
  });

  dom.btnSimReset.addEventListener('click', () => {
    state.isAlert = false;
    state.alertReason = "NONE";
    state.sensors.ph = 7.42;
    state.sensors.turb = 8.4;
    state.sensors.do = 7.15;
    state.sensors.ec = 382;
    state.sensors.temp = 24.6;
    state.sensors.stage = 1.35;

    state.plume.active = false;
    state.plume.posKm = 0.0;
    dom.plumeIndicator.style.display = 'none';

    dom.tagA.className = "eta-tag safe";
    dom.tagA.innerText = "SAFE";
    dom.timeA.innerText = "NORMAL FLOW";
    dom.descA.innerText = "Intake pumps operating normally";

    dom.tagB.className = "eta-tag safe";
    dom.tagB.innerText = "SAFE";
    dom.timeB.innerText = "NORMAL FLOW";
    dom.descB.innerText = "Riverbank water in clean baseline";

    dom.vial2.className = "vial-slot ready";
    dom.vial2.querySelector('.vial-status').innerText = "READY (Sterile)";
    dom.vial3.className = "vial-slot ready";
    dom.vial3.querySelector('.vial-status').innerText = "READY (Sterile)";

    renderSensors();
    renderBeacon();
  });

  // --- MANUAL WIPER ACTION ---
  dom.btnManualWipe.addEventListener('click', () => {
    dom.txtWiperSub.innerText = "WIPING ACTIVE: 180° bidirectional sweep running... Please wait.";
    dom.btnManualWipe.disabled = true;
    setTimeout(() => {
      dom.txtWiperSub.innerText = "Status: Sweep complete. Parked in hydrodynamic recess. Interval: 6h.";
      dom.btnManualWipe.disabled = false;
    }, 3000);
  });

  // --- EMERGENCY INTAKE LOCKOUT ---
  dom.btnLockout.addEventListener('click', () => {
    state.lockoutActive = !state.lockoutActive;
    const t = i18n[state.lang];
    if (state.lockoutActive) {
      dom.btnLockout.style.backgroundColor = "#059669";
      dom.btnLockout.style.borderColor = "#10b981";
      dom.txtBtnLockout.innerText = t.btnLockoutActive;
      alert("⚠️ EMERGENCY SIGNAL SENT: Remote telemetry trip issued to Rural Lift Irrigation & Municipal Water Intake pumps!");
    } else {
      dom.btnLockout.style.backgroundColor = "#e11d48";
      dom.btnLockout.style.borderColor = "#f43f5e";
      dom.txtBtnLockout.innerText = t.btnLockout;
    }
  });

  // --- CHAIN OF CUSTODY MODAL ---
  dom.btnOpenCoc.addEventListener('click', () => {
    dom.cocTime.innerText = new Date().toUTCString();
    dom.modalCoc.style.display = 'flex';
  });

  dom.btnCloseCoc.addEventListener('click', () => {
    dom.modalCoc.style.display = 'none';
  });

  dom.btnModalDismiss.addEventListener('click', () => {
    dom.modalCoc.style.display = 'none';
  });

  // --- SMS SUBSCRIPTION ---
  dom.btnSubscribeSms.addEventListener('click', () => {
    const mobile = prompt("कृपया आपला १० अंकी मोबाईल नंबर प्रविष्ट करा (Enter your 10-digit mobile number for SMS alerts):");
    if (mobile && mobile.trim().length >= 10) {
      alert("✅ धन्यवाद! आपला नंबर नोंदवला गेला आहे. नदीत कोणतीही अचानक रासायनिक गळती किंवा धोका निर्माण झाल्यास आपल्याला तात्काळ SMS येईल.");
    }
  });

  // --- EVENT LISTENERS FOR CONTROLS ---
  dom.btnModeOperator.addEventListener('click', () => setViewMode('operator'));
  dom.btnModeCommunity.addEventListener('click', () => setViewMode('community'));

  dom.langBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      applyLanguage(e.target.dataset.lang);
    });
  });

  dom.demoToggle.addEventListener('change', (e) => {
    state.demoActive = e.target.checked;
    dom.demoBanner.style.display = state.demoActive ? 'block' : 'none';
  });

  // Initial setup
  renderSensors();
  renderBeacon();
  applyLanguage('en');

});
