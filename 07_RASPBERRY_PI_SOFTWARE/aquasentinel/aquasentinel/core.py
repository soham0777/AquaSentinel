"""Glues the parts together: reading in -> decide -> act -> log -> publish to the dashboard."""
import csv
import json
import os
import threading
import time
from collections import deque

from .brain import Brain, CLASS_INFO
from .sensors import Conditioner, derive
from .sysmon import SysMon
from . import settings

BEACON = {"LEARNING": "B", "NORMAL": "G", "SENSOR FAULT": "F"}   # any spill class -> "R"


class Station:
    def __init__(self, cfg, simulate=False):
        self.cfg = cfg
        self.brain = Brain(cfg)
        self.cond = Conditioner(cfg)
        self.sysmon = SysMon(self.log)
        self.lock = threading.Lock()
        self.history = deque(maxlen=3600)          # one hour of 1-second readings
        self.events = deque(maxlen=50)
        self.logs = deque(maxlen=200)
        self.latest = None
        self.listeners = []
        self.started = time.time()
        self.beacon_colour = "B"
        self.busy_until = 0.0                      # beacon test running
        self.samples_taken = 0
        self.simulate = simulate
        if simulate:
            from .simulator import FakeNano
            self.nano = FakeNano(cfg, self.on_reading, self.log)
        else:
            from .nano import NanoLink
            self.nano = NanoLink(cfg, self.on_reading, self.log)
        from .sms import Modem
        self.modem = Modem(cfg, self.log) if not simulate else Modem({**cfg, "sim_enabled": False}, self.log)
        self._csv_day = None
        self._csv = None
        self.cloud = None
        if cfg.get("cloud", {}).get("enabled"):
            from .cloud import Cloud
            self.cloud = Cloud(cfg, settings.load_secrets(), self.log)

    # ---------- logging ----------
    def log(self, text):
        line = time.strftime("%H:%M:%S ") + text
        print(line, flush=True)
        self.logs.appendleft(line)

    def _csv_row(self, r, state):
        day = time.strftime("%Y-%m-%d")
        if day != self._csv_day:
            path = os.path.join(self.cfg["log_dir"], f"readings_{day}.csv")
            new = not os.path.exists(path)
            self._csv = open(path, "a", newline="", encoding="utf-8")
            self._csvw = csv.writer(self._csv)
            if new:
                self._csvw.writerow(["time", "state", "ph", "ph_v", "tds_ppm", "tds_v", "turbid", "turb_v",
                                     "vapour", "mq3_v", "t_water", "t_air", "rh", "dark", "pump"])
            self._csv_day = day
        self._csvw.writerow([time.strftime("%H:%M:%S"), state, r["ph"], r["ph_v"], r["tds"], r["tds_v"], r["turbid"],
                             r["turb_v"], r["vapour"], r["mq3_v"], r["t_water"], r["t_air"], r["rh"], r["dark"], r["pump"]])
        self._csv.flush()

    # ---------- the heart ----------
    def on_reading(self, raw):
        r = derive(self.cond.clean(raw), self.cfg)
        state, changed, reasons = self.brain.step(r)
        now = time.time()
        if changed:
            self._on_change(state, reasons, r)
        if now > self.busy_until:
            want = BEACON.get(state, "R")
            if want != self.beacon_colour:
                self.nano.beacon(want); self.beacon_colour = want
        point = {"t": round(now, 1), **r, "state": state}
        with self.lock:
            self.latest = point
            self.history.append(point)
        try:
            self._csv_row(r, state)
        except Exception as e:
            self.log(f"log write failed: {e}")
        self.publish()
        if self.cloud:
            self.cloud.reading(point, force=changed)
            self.cloud.set_live(self.cloud_live(point))

    def cloud_live(self, p):
        b = self.brain
        return {"site": self.cfg["site_name"], "team": self.cfg.get("team", ""), "state": b.state,
                "title": CLASS_INFO[b.state][0], "reasons": b.last_reasons, "since": round(b.state_since),
                "reading": {k: p.get(k) for k in ("ph", "tds", "turbid", "turb_pct", "vapour", "t_water", "t_air", "rh", "dark")},
                "beacon": self.beacon_colour, "samples": self.samples_taken, "nano": self.nano.connected,
                "sim": self.modem.status, "power_ok": self.sysmon.info.get("power_ok"),
                "cpu_temp": self.sysmon.info.get("cpu_temp"), "uptime": int(time.time() - self.started)}

    def _on_change(self, state, reasons, r):
        title, text = CLASS_INFO[state]
        self.log(f"STATE -> {state}: {', '.join(reasons) or text}")
        if state in ("NORMAL", "LEARNING"):
            if self.events and self.events[0].get("open"):
                self.events[0]["open"] = False
                self.events[0]["cleared"] = time.strftime("%H:%M:%S")
                if self.cloud:
                    self.cloud.event(self.events[0])
            return
        if self.events and self.events[0].get("open"):          # one event turns into another: close the first
            self.events[0]["open"] = False
            self.events[0]["cleared"] = time.strftime("%H:%M:%S")
            if self.cloud:
                self.cloud.event(self.events[0])
        ev = {"id": int(time.time() * 1000), "time": time.strftime("%H:%M:%S"), "date": time.strftime("%d %b"), "cls": state, "title": title,
              "reasons": reasons or [text], "open": True, "sample": False, "sms": ""}
        if state != "SENSOR FAULT" and self.cfg.get("auto_sample", True):
            secs = self.cfg.get("sample_pump_seconds", 5)
            self.nano.pump(secs); self.samples_taken += 1
            ev["sample"] = True
            self.log(f"Sample: pump on for {secs} s")
        sms = (f"AquaSentinel ALERT: {title.upper()} at {self.cfg['site_name']}, "
               f"{time.strftime('%d %b %H:%M')}. pH {r['ph'] if r['ph'] is not None else '-'}, "
               f"TDS {int(r['tds']) if r['tds'] is not None else '-'} ppm. "
               + ("Sample bottled." if ev["sample"] else "Check the sensors."))
        ev["sms"] = self.modem.send_all(sms)
        self.events.appendleft(ev)
        if self.cloud:
            self.cloud.event(ev)

    # ---------- dashboard data ----------
    def snapshot(self, history_seconds=600):
        with self.lock:
            hist = [p for p in self.history if p["t"] >= time.time() - history_seconds]
            latest = self.latest
        b = self.brain
        title, text = CLASS_INFO[b.state]
        return {
            "now": time.time(),
            "site": self.cfg["site_name"], "team": self.cfg.get("team", ""),
            "state": b.state, "title": title, "text": text, "reasons": b.last_reasons,
            "since": b.state_since, "baseline": b.baseline,
            "learn_left": max(0, int(self.cfg.get("learn_seconds", 20) - (time.time() - b.started))),
            "latest": latest, "history": hist,
            "events": list(self.events), "logs": list(self.logs)[:30],
            "beacon": self.beacon_colour, "samples": self.samples_taken,
            "ph_calibrated": self.cfg["ph_calibration"].get("calibrated", False),
            "link": {"nano": self.nano.connected, "port": self.nano.port,
                     "age": round(time.time() - self.nano.last_rx, 1) if self.nano.last_rx else None,
                     "sim": self.modem.status, "signal": self.modem.signal, "operator": self.modem.operator,
                     "numbers": len([n for n in self.cfg.get("sms_numbers", []) if n.strip()]),
                     "simulate": self.simulate, "stats": getattr(self.nano, "stats", {})},
            "system": self.sysmon.info,
            "cloud": self.cloud.info() if self.cloud else {"enabled": False},
            "sms": self.modem.sent[:5],
            "uptime": int(time.time() - self.started),
        }

    def publish(self):
        if not self.latest:
            return
        snap = self.snapshot(history_seconds=0)
        snap["history"] = [self.latest]
        data = json.dumps(snap)
        for q in list(self.listeners):
            try:
                q.put_nowait(data)
            except Exception:
                pass

    # ---------- commands from the dashboard ----------
    def command(self, action, arg=None):
        if action == "beacon_test":
            self.busy_until = time.time() + 13
            def seq():
                for c in "RGBW":
                    self.nano.beacon(c); time.sleep(3)
                self.busy_until = 0; self.beacon_colour = "?"
            threading.Thread(target=seq, daemon=True).start()
            return "beacon test running"
        if action == "sample":
            secs = int(arg or self.cfg.get("sample_pump_seconds", 5))
            self.nano.pump(secs); self.samples_taken += 1
            self.log(f"Manual sample: pump {secs} s")
            return f"pump on for {secs} s"
        if action == "sms_test":
            return self.modem.send_all(f"AquaSentinel test message from {self.cfg['site_name']}. "
                                       f"System working, {time.strftime('%d %b %H:%M')}.", force=True)
        if action == "reload_config":
            new = settings.load()
            for k in ("ph_calibration", "calibration", "limits", "sms_numbers", "hold_seconds", "digital_outputs"):
                self.cfg[k] = new[k]
            self.cond.reset()
            self.log("Settings and calibration reloaded")
            return "reloaded"
        if action == "relearn":
            self.brain.relearn(); self.log("Baseline reset: learning the water again")
            return "learning again"
        return "unknown command"

    def start(self):
        threading.Thread(target=self.nano.run, daemon=True).start()
        threading.Thread(target=self.modem.run, daemon=True).start()
        self.sysmon.start()
        if self.cloud:
            self.cloud.start()
        def watchdog():
            while True:
                time.sleep(2)
                silent = (time.time() - self.nano.last_rx > 10) if self.nano.last_rx else (time.time() - self.started > 20)
                if silent and self.brain.state != "SENSOR FAULT":
                    self.brain._set("SENSOR FAULT"); self.brain.last_reasons = ["sensor hub (Arduino Nano) not answering"]
                    self.log("STATE -> SENSOR FAULT: sensor hub not answering")
                    self.publish()
        threading.Thread(target=watchdog, daemon=True).start()
