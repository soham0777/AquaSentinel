"""Link to the Arduino Nano: finds the port, reads JSON lines, sends commands, reconnects by itself."""
import glob
import json
import sys
import threading
import time

import serial

try:
    from serial.tools import list_ports
except Exception:  # pragma: no cover
    list_ports = None


def candidate_ports(preferred):
    if preferred and preferred != "auto":
        return [preferred]
    ports = []
    if sys.platform.startswith("linux"):
        ports = sorted(glob.glob("/dev/ttyUSB*")) + sorted(glob.glob("/dev/ttyACM*"))
    elif list_ports:
        ports = [p.device for p in list_ports.comports() if "CH340" in (p.description or "") or "USB" in (p.description or "")]
    return ports


class NanoLink:
    def __init__(self, cfg, on_reading, log):
        self.cfg = cfg
        self.on_reading = on_reading
        self.log = log
        self.ser = None
        self.port = None
        self.connected = False
        self.last_rx = 0.0
        self.lock = threading.Lock()
        self.stop = threading.Event()

    # ---------- connection ----------
    def _try_open(self, port):
        try:
            s = serial.Serial(port, self.cfg["nano_baud"], timeout=1)
        except Exception as e:
            self.log(f"Nano: cannot open {port}: {e}")
            return None
        time.sleep(2.2)                      # the Nano resets when the port opens
        s.reset_input_buffer()
        t0 = time.time()
        while time.time() - t0 < 6:
            line = s.readline().decode(errors="replace").strip()
            if line.startswith("{") and '"vcc"' in line:
                return s
        s.close()
        self.log(f"Nano: no sensor data on {port}")
        return None

    def _connect(self):
        for port in candidate_ports(self.cfg.get("nano_port", "auto")):
            s = self._try_open(port)
            if s:
                self.ser, self.port, self.connected = s, port, True
                self.log(f"Nano connected on {port}")
                return True
        return False

    # ---------- main loop ----------
    def run(self):
        while not self.stop.is_set():
            if not self.connected and not self._connect():
                time.sleep(3)
                continue
            try:
                line = self.ser.readline().decode(errors="replace").strip()
            except Exception as e:
                self._drop(f"read error: {e}")
                continue
            if not line:
                if time.time() - self.last_rx > 8:
                    self._drop("no data for 8 s")
                continue
            if not line.startswith("{"):
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            self.last_rx = time.time()
            if "vcc" in msg:
                self.on_reading(msg)

    def _drop(self, why):
        self.log(f"Nano link lost ({why}); reconnecting")
        self.connected = False
        try:
            self.ser.close()
        except Exception:
            pass
        self.ser = None
        time.sleep(1)

    # ---------- commands ----------
    def send(self, cmd):
        """LED G|R|B|Y|W|F|O, PUMP n, PING"""
        with self.lock:
            if not self.connected:
                return False
            try:
                self.ser.write((cmd + "\n").encode())
                return True
            except Exception as e:
                self.log(f"Nano: send failed: {e}")
                return False

    def beacon(self, colour):
        return self.send("LED " + colour)

    def pump(self, seconds):
        return self.send("PUMP %d" % max(0, min(30, int(seconds))))
