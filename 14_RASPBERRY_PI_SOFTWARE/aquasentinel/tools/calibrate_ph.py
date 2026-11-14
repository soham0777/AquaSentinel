"""pH calibration with your buffer solutions (pH 4.0, 7.0 and 9.2; two are enough).

  sudo systemctl stop aquasentinel      (frees the Nano's USB port)
  python3 tools/calibrate_ph.py
  sudo systemctl start aquasentinel

For each buffer: rinse the probe in clean water, dip it in the buffer, wait for the reading to settle,
press Enter. The result is saved in config.json and used from the next start.
"""
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import serial                                   # noqa: E402
from aquasentinel import settings              # noqa: E402
from aquasentinel.nano import candidate_ports  # noqa: E402
from aquasentinel.sensors import fit_line      # noqa: E402


def open_nano(cfg):
    for port in candidate_ports(cfg.get("nano_port", "auto")):
        try:
            s = serial.Serial(port, cfg["nano_baud"], timeout=1)
            time.sleep(2.2); s.reset_input_buffer()
            print(f"Nano found on {port}")
            return s
        except Exception as e:
            print(f"{port}: {e}")
    sys.exit("No Nano found. Is the USB cable in, and is the service stopped (sudo systemctl stop aquasentinel)?")


def read_ph_v(s, seconds=12):
    vals, t0 = [], time.time()
    while time.time() - t0 < seconds:
        try:
            j = json.loads(s.readline().decode(errors="replace"))
            if j.get("ph_v") is not None:
                vals.append(j["ph_v"]); print(f"\r  {j['ph_v']:.3f} V   ", end="", flush=True)
        except ValueError:
            pass
    print()
    if len(vals) < 5:
        sys.exit("Too few readings from the Nano.")
    tail = vals[len(vals) // 2:]                       # the settled half
    return statistics.median(tail), statistics.pstdev(tail)


def main():
    cfg = settings.load()
    s = open_nano(cfg)
    points = []
    for ph in (7.0, 4.0, 9.2):
        ans = input(f"\nPut the probe in the pH {ph} buffer and press Enter (or type s to skip this one): ").strip().lower()
        if ans == "s":
            continue
        print("  reading for 12 s, keep the probe still...")
        v, sd = read_ph_v(s)
        print(f"  pH {ph}: {v:.3f} V  (noise {sd * 1000:.1f} mV)")
        points.append((v, ph))
    if len(points) < 2:
        sys.exit("Need at least two buffers. Nothing saved.")
    a, b = fit_line(points)
    print(f"\nResult: pH = {a:.3f} x V + {b:.3f}   ({abs(1 / a) * 1000:.0f} mV per pH unit)")
    for v, ph in points:
        print(f"  check: {v:.3f} V -> pH {a * v + b:.2f}  (buffer {ph})")
    if abs(1 / a) < 0.03:
        print("WARNING: very small change per pH unit. Check the probe and the board's gain trimmer.")
    if input("\nSave this calibration? (y/n): ").strip().lower() == "y":
        settings.save_ph_calibration(points)
        print("Saved in config.json. Start the service again:  sudo systemctl start aquasentinel")


if __name__ == "__main__":
    main()
