import sys
from pypdf import PdfReader

r = PdfReader(r"C:\Users\dell\OneDrive\Desktop\AquaSentinel\12_ELECTRONICS_MANUAL_1to5\_build_v2\manual_v2.pdf")
print("pages:", len(r.pages))

checks = {
    1:  ["Revision 2.0", "14 November 2026", "Sensor Hub PCB v1.2", "Do not build from old printouts"],
    2:  ["What changed", "no longer true", "ADS1115", "rain sensor", "MX1508", "Hub HAT"],
    3:  ["The system in one picture", "AUX 5 V charger", "step-down"],
    4:  ["Parts you need", "Mini L298N", "The USB cable also powers the Nano"],
    5:  ["Board tour", "J18", "RX (pin 10)", "AUX 5 V in", "never from the Nano"],
    6:  ["power first", "9.0 V", "4.0 V", "it takes 4.0 V", "it takes 9 V"],
    7:  ["the board itself", "TTC-450 Pro", "1000 µF C2"],
    8:  ["Wire the seven sensors", "600 ms", "board is on the header"],
    9:  ["The sensors in 3D", "LED G", "PUMP 3"],
    10: ["SIM800L", "AT+CPIN", "4.7 k/10 k", "pin 10"],
    11: ["Mount everything", "MQ-3 sniffing station", "sensor cage"],
    12: ["Flash the Arduino Nano", "BOARD_PCB 1", "115200", "PING", "38 mV/pH"],
    13: ["Set up the Raspberry Pi", "install.sh", "8080", "sms_numbers", "learn"],
    14: ["Calibration and bench checks", "check_hardware.py", "calibrate_ph.py", "wiring_test.py", "KCl"],
    15: ["six demo waters", "SENSOR FAULT", "Learn new water", "never as normal"],
    16: ["If something is wrong", "Revision history", "TDS always 0 ppm", "do not build from it", "Superseded"],
    17: ["Team", "good luck at the finale", "12–13 Nov 2026"],
}

forbidden = ["ADS1115", "DS3231", "Hub HAT", "MX1508", "GPIO17", "12 V 2 A", "rain board"]

bad = 0
for i, page in enumerate(r.pages, start=1):
    t = (page.extract_text() or "")
    print(f"--- page {i} ({len(t)} chars) ---")
    if i in checks:
        for c in checks[i]:
            ok = c.lower() in t.lower()
            if not ok: bad += 1
            print(("  OK   " if ok else "  MISS ") + c)
    if i >= 3 and i <= 17:
        for f in forbidden:
            if f.lower() in t.lower():
                bad += 1
                print(f"  FORBIDDEN TERM ON BUILD PAGE: {f}")
    try:
        imgs = len(page.images)
        if imgs: print(f"  embedded images: {imgs}")
    except Exception:
        pass

print("TOTAL_MISS_OR_FORBIDDEN:", bad)
