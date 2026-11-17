"""Health of the Raspberry Pi itself, checked every 30 s: power supply, temperature, memory, disk, USB devices.

A weak power supply is the most common hidden cause of a Pi that feels slow AND of USB devices (the Nano) that drop out:
the Pi lowers its speed and the USB ports can lose power for a moment. We read the firmware's own flags for this.
"""
import os
import shutil
import subprocess
import threading
import time

THROTTLE_BITS = {0: "under-voltage now", 1: "speed capped now", 2: "slowed down now", 3: "temperature limit now",
                 16: "under-voltage since boot", 17: "speed capped since boot", 18: "slowed down since boot",
                 19: "temperature limit since boot"}


def throttled():
    """Return the firmware's throttle flags as a number, or None when not on a Pi."""
    for path in ("/sys/devices/platform/soc/soc:firmware/get_throttled",):
        try:
            with open(path) as f:
                return int(f.read().strip(), 16)
        except Exception:
            pass
    try:
        out = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=3).stdout
        return int(out.strip().split("=")[1], 16)
    except Exception:
        return None


def explain_throttle(v):
    if v is None:
        return []
    return [text for bit, text in THROTTLE_BITS.items() if v & (1 << bit)]


def cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read()) / 1000.0, 1)
    except Exception:
        return None


def mem_free_mb():
    try:
        with open("/proc/meminfo") as f:
            info = dict(l.split(":", 1) for l in f)
        return int(info["MemAvailable"].split()[0]) // 1024
    except Exception:
        return None


def usb_devices():
    """Names of the USB devices plugged in (not the hubs)."""
    out = []
    base = "/sys/bus/usb/devices"
    if not os.path.isdir(base):
        return None
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        try:
            with open(os.path.join(p, "bDeviceClass")) as f:
                if f.read().strip() == "09":            # a hub
                    continue
            name = ""
            for k in ("product", "manufacturer"):
                fp = os.path.join(p, k)
                if os.path.exists(fp):
                    with open(fp) as f:
                        name = f.read().strip(); break
            out.append(f"{d} {name}".strip())
        except Exception:
            continue
    return out


class SysMon:
    def __init__(self, log, every=30):
        self.log = log
        self.every = every
        self.info = {}
        self._warned = set()

    def check(self):
        thr = throttled()
        problems = explain_throttle(thr)
        load = os.getloadavg()[0] if hasattr(os, "getloadavg") else None
        disk = shutil.disk_usage("/" if os.name != "nt" else "C:\\")
        self.info = {
            "throttled": None if thr is None else hex(thr),
            "power_ok": None if thr is None else not (thr & 0x1 or thr & 0x10000),
            "problems": problems,
            "cpu_temp": cpu_temp(),
            "load": None if load is None else round(load, 2),
            "mem_free_mb": mem_free_mb(),
            "disk_free_gb": round(disk.free / 1e9, 1),
            "usb": usb_devices(),
            "checked": time.strftime("%H:%M:%S"),
        }
        for p in problems:
            if p not in self._warned:
                self._warned.add(p)
                hint = " Use the official 5.1 V 2.5 A supply and a short, thick cable." if "voltage" in p else ""
                self.log(f"Pi health: {p}.{hint}")
        if self.info["disk_free_gb"] < 1 and "disk" not in self._warned:
            self._warned.add("disk"); self.log("Pi health: less than 1 GB free on the SD card")
        return self.info

    def run(self):
        while True:
            try:
                self.check()
            except Exception as e:
                self.info = {"error": str(e)}
            time.sleep(self.every)

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()
