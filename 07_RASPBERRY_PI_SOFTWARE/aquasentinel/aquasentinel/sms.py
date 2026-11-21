"""SIM800L on the Pi's serial port (Sensor Hub J18: Pi TX pin 8 -> divider -> SIM RXD, Pi RX pin 10 <- SIM TXD).

Runs in its own thread so a slow or missing modem never blocks the sensors or the dashboard.
"""
import queue
import threading
import time

import serial


class Modem:
    def __init__(self, cfg, log):
        self.cfg = cfg
        self.log = log
        self.enabled = cfg.get("sim_enabled", True)
        self.q = queue.Queue()
        self.ser = None
        self.status = "off" if not self.enabled else "starting"
        self.signal = None            # 0..31 from AT+CSQ, None = unknown
        self.operator = None
        self.sent = []                # [{time, to, text, ok}]
        self.last_alert_sent = 0.0

    # ---------- low level ----------
    def _at(self, cmd, wait=1.0, expect="OK"):
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\r").encode())
        t0, buf = time.time(), ""
        while time.time() - t0 < wait:
            buf += self.ser.read(self.ser.in_waiting or 1).decode(errors="replace")
            if expect in buf or "ERROR" in buf:
                break
        return buf

    def _open(self):
        try:
            self.ser = serial.Serial(self.cfg["sim_port"], self.cfg.get("sim_baud", 9600), timeout=0.2)
        except Exception as e:
            if getattr(e, "errno", None) == 16 or "Errno 16" in str(e):
                self.status = "serial port busy: another program holds " + self.cfg["sim_port"] + " (run tools/doctor.sh)"
            else:
                self.status = "no serial port (" + str(e).split(":")[0] + ")"
            return False
        for _ in range(3):
            if "OK" in self._at("AT", 1.0):
                self._at("ATE0"); self._at("AT+CMGF=1"); self._at('AT+CSCS="GSM"')
                self.status = "ready"
                return True
            time.sleep(1)
        self.status = "no answer from SIM800L"
        self.ser.close(); self.ser = None
        return False

    def _poll_signal(self):
        r = self._at("AT+CSQ", 1.5)
        try:
            self.signal = int(r.split("+CSQ:")[1].split(",")[0])
        except Exception:
            self.signal = None
        r = self._at("AT+COPS?", 2.0)
        if '"' in r:
            self.operator = r.split('"')[1]
        reg = self._at("AT+CREG?", 1.5)
        if ",1" in reg or ",5" in reg:
            self.status = "ready"
        else:
            self.status = "searching network"

    def _send_one(self, number, text):
        r = self._at(f'AT+CMGS="{number}"', 3.0, expect=">")
        if ">" not in r:
            return False
        self.ser.write(text.encode("ascii", "replace") + b"\x1a")
        t0, buf = time.time(), ""
        while time.time() - t0 < 30:
            buf += self.ser.read(self.ser.in_waiting or 1).decode(errors="replace")
            if "+CMGS" in buf or "ERROR" in buf:
                break
        return "+CMGS" in buf

    # ---------- thread ----------
    def run(self):
        if not self.enabled:
            return
        last_poll = 0
        while True:
            if self.ser is None and not self._open():
                time.sleep(15)
                continue
            try:
                job = self.q.get(timeout=1)
            except queue.Empty:
                job = None
            try:
                if job:
                    number, text = job
                    ok = self._send_one(number, text)
                    self.sent.insert(0, {"time": time.strftime("%H:%M:%S"), "to": number, "text": text, "ok": ok})
                    del self.sent[20:]
                    self.log(f"SMS to {number}: {'sent' if ok else 'FAILED'}")
                elif time.time() - last_poll > 20:
                    self._poll_signal(); last_poll = time.time()
            except Exception as e:
                self.log(f"SIM800L error: {e}")
                try:
                    self.ser.close()
                except Exception:
                    pass
                self.ser = None
                self.status = "reconnecting"

    # ---------- public ----------
    def send_all(self, text, force=False):
        nums = [n for n in self.cfg.get("sms_numbers", []) if n.strip()]
        if not self.enabled or not nums:
            return "no numbers set" if self.enabled else "SMS disabled"
        if not force and time.time() - self.last_alert_sent < self.cfg.get("sms_cooldown_minutes", 10) * 60:
            return "cooldown"
        self.last_alert_sent = time.time()
        for n in nums:
            self.q.put((n, text[:160]))
        return "queued"
