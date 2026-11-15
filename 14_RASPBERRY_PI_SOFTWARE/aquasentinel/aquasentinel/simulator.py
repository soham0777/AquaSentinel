"""Pretend Nano for testing without hardware (python3 -m aquasentinel --simulate).

Plays the six booth waters in a loop: clean, salty, vinegar, muddy, sanitiser, unplugged probe.
It produces exactly the same JSON lines as the real Nano, so every other part runs unchanged.
"""
import random
import threading
import time

SCENES = [("clean", 40), ("salty", 25), ("clean", 20), ("vinegar", 25), ("clean", 20),
          ("muddy", 25), ("clean", 20), ("sanitiser", 25), ("clean", 20), ("unplugged", 20)]


class FakeNano:
    def __init__(self, cfg, on_reading, log):
        self.on_reading = on_reading
        self.log = log
        self.port = "simulator"
        self.connected = True
        self.last_rx = time.time()
        self.pump_until = 0.0
        self.colour = "G"
        self.stop = threading.Event()
        self.scene = "clean"

    def run(self):
        up, i, t_end = 0, 0, time.time() + SCENES[0][1]
        tds_v, ph_v = 0.62, 2.16
        while not self.stop.is_set():
            if time.time() > t_end:
                i = (i + 1) % len(SCENES); t_end = time.time() + SCENES[i][1]
            self.scene = SCENES[i][0]
            tgt_tds = 1.9 if self.scene == "salty" else 0.62
            tgt_ph = 1.98 if self.scene == "vinegar" else 2.16
            tds_v += (tgt_tds - tds_v) * 0.35 + random.uniform(-0.01, 0.01)
            ph_v += (tgt_ph - ph_v) * 0.35 + random.uniform(-0.004, 0.004)
            up += 1
            msg = {"vcc": 4.75, "ph_v": round(ph_v, 3), "ph": None, "tds_v": round(tds_v, 3),
                   "turb_v": round(1.2 if self.scene == "muddy" else 1.8 + random.uniform(-.05, .05), 3),
                   "mq3_v": round(2.6 if self.scene == "sanitiser" else 1.6 + random.uniform(-.05, .05), 3),
                   "ldr_do": 0, "ph_do": 0,
                   "turb_do": 0 if self.scene == "muddy" else 1,
                   "mq3_do": 0 if self.scene == "sanitiser" else 1,
                   "t_water": None if self.scene == "unplugged" else round(26.0 + random.uniform(-.1, .1), 2),
                   "t_air": round(28.4 + random.uniform(-.2, .2), 1), "rh": 42,
                   "pump": 1 if time.time() < self.pump_until else 0, "up": up}
            self.last_rx = time.time()
            self.on_reading(msg)
            time.sleep(1)

    def send(self, cmd):
        if cmd.startswith("PUMP"):
            self.pump_until = time.time() + int(cmd.split()[1])
        elif cmd.startswith("LED"):
            self.colour = cmd.split()[1]
        return True

    def beacon(self, colour):
        return self.send("LED " + colour)

    def pump(self, seconds):
        return self.send("PUMP %d" % seconds)
