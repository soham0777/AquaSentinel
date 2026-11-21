"""Link to the Arduino Nano: finds the port, reads JSON lines, sends commands, reconnects by itself.

Made for reliability (17 Nov 2026):
  - a damaged line is dropped: it must parse as JSON and, with firmware v2, match its checksum "ck"
  - lost lines are counted from the line counter "seq"
  - commands go through a sender thread and are re-sent (up to 3 times) until the Nano answers {"ok":...}
  - the beacon colour the Nano reports ("led") is compared with the one we want; a lost command is re-sent
  - the port is found by its fixed name /dev/aquasentinel-nano (udev rule from install.sh) when it exists
"""
import glob
import json
import os
import queue
import sys
import threading
import time

import serial

try:
    from serial.tools import list_ports
except Exception:  # pragma: no cover
    list_ports = None

FIXED_NAME = "/dev/aquasentinel-nano"


def candidate_ports(preferred):
    if preferred and preferred != "auto":
        return [preferred]
    ports = []
    if sys.platform.startswith("linux"):
        if os.path.exists(FIXED_NAME):
            ports.append(FIXED_NAME)
        ports += sorted(glob.glob("/dev/serial/by-id/*"))
        ports += sorted(glob.glob("/dev/ttyUSB*")) + sorted(glob.glob("/dev/ttyACM*"))
        seen, uniq = set(), []
        for p in ports:                                  # the same device can appear under several names
            real = os.path.realpath(p)
            if real not in seen:
                seen.add(real); uniq.append(p)
        ports = uniq
    elif list_ports:
        ports = [p.device for p in list_ports.comports() if "CH340" in (p.description or "") or "USB" in (p.description or "")]
    return ports


def check_line(line):
    """Return the parsed message, or None if the line is damaged. Lines without "ck" (firmware v1) are accepted."""
    if not line.startswith("{") or not line.endswith("}"):
        return None
    i = line.rfind(',"ck":')
    if i > 0:
        try:
            ck = int(line[i + 6:-1])
        except ValueError:
            return None
        if sum(line[:i].encode("ascii", "replace")) & 0xFF != ck:
            return None
    try:
        return json.loads(line)
    except ValueError:
        return None


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
        self.cmdq = queue.Queue()
        self.acks = {"led": threading.Event(), "pump": threading.Event()}
        self.want_led = None
        self.last_led_sent = 0.0
        self.last_seq = None
        self.stats = {"lines": 0, "bad": 0, "lost": 0, "reconnects": 0, "resent": 0, "fw": None,
                      "e_dht": 0, "e_ds": 0, "last_problem": ""}

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
                self.last_seq = None
                self.log(f"Nano connected on {port}")
                if self.want_led:
                    self.cmdq.put(("LED " + self.want_led, "led"))   # the Nano restarted: restore the beacon
                return True
        return False

    # ---------- main loop ----------
    def run(self):
        threading.Thread(target=self._sender, daemon=True).start()
        while not self.stop.is_set():
            if not self.connected and not self._connect():
                time.sleep(3)
                continue
            try:
                line = self.ser.readline().decode("ascii", errors="replace").strip()
            except Exception as e:
                self._drop(f"read error: {e}")
                continue
            if not line:
                if time.time() - self.last_rx > 8:
                    self._drop("no data for 8 s")
                continue
            if not line.startswith("{"):
                continue
            msg = check_line(line)
            if msg is None:
                self.stats["bad"] += 1
                self.stats["last_problem"] = time.strftime("%H:%M:%S ") + "damaged line dropped"
                continue
            self.last_rx = time.time()
            if "ok" in msg:
                ev = self.acks.get(msg["ok"])
                if ev:
                    ev.set()
                continue
            if "vcc" not in msg:
                continue
            self._bookkeeping(msg)
            self.on_reading(msg)

    def _bookkeeping(self, msg):
        st = self.stats
        st["lines"] += 1
        st["fw"] = msg.get("fw", 1)
        st["e_dht"], st["e_ds"] = msg.get("e_dht", 0), msg.get("e_ds", 0)
        seq = msg.get("seq")
        if seq is not None:
            if self.last_seq is not None and seq > self.last_seq + 1:
                st["lost"] += seq - self.last_seq - 1
            self.last_seq = seq
        led = msg.get("led")
        if led and self.want_led and led != self.want_led and time.time() - self.last_led_sent > 3:
            st["resent"] += 1
            self.cmdq.put(("LED " + self.want_led, "led"))

    def _drop(self, why):
        self.log(f"Nano link lost ({why}); reconnecting")
        self.stats["reconnects"] += 1
        self.stats["last_problem"] = time.strftime("%H:%M:%S ") + why
        self.connected = False
        try:
            self.ser.close()
        except Exception:
            pass
        self.ser = None
        time.sleep(1)

    # ---------- commands ----------
    def _write(self, cmd):
        with self.lock:
            if not self.connected or self.ser is None:
                return False
            try:
                self.ser.write((cmd + "\n").encode())
                return True
            except Exception as e:
                self.log(f"Nano: send failed: {e}")
                return False

    def _sender(self):
        """Sends queued commands one by one and waits for the Nano's answer; re-sends a lost command."""
        while not self.stop.is_set():
            cmd, tag = self.cmdq.get()
            ev = self.acks.get(tag)
            for attempt in range(3):
                if ev:
                    ev.clear()
                if tag == "led":
                    self.last_led_sent = time.time()
                if not self._write(cmd):
                    break
                if ev is None or ev.wait(1.5):
                    break
                if attempt < 2:
                    self.stats["resent"] += 1
            else:
                self.stats["last_problem"] = time.strftime("%H:%M:%S ") + f"no answer to {cmd}"

    def send(self, cmd):
        """LED G|R|B|Y|W|F|O, PUMP n, PING. Returns at once; the sender thread delivers it."""
        tag = "led" if cmd.startswith("LED") else "pump" if cmd.startswith("PUMP") else None
        if tag == "led":
            self.want_led = cmd.split()[1]
        self.cmdq.put((cmd, tag))
        return self.connected

    def beacon(self, colour):
        return self.send("LED " + colour)

    def pump(self, seconds):
        return self.send("PUMP %d" % max(0, min(30, int(seconds))))
