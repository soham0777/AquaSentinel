"""Tests for the reliability parts, no hardware and no internet needed:
  - damaged lines from the Nano are dropped (checksum)
  - a short sensor drop-out is bridged; a long one becomes a SENSOR FAULT
  - single spikes are removed by the median filter
  - calibration (TDS factor, turbidity, MQ-3, temperature offset) is applied
  - the cloud uploader signs in, uploads, keeps data while "offline" and sends it later (against a fake Firebase)
Run:  python3 tools/test_reliability.py
"""
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aquasentinel import cloud, settings                     # noqa: E402
from aquasentinel.brain import Brain                         # noqa: E402
from aquasentinel.nano import check_line                     # noqa: E402
from aquasentinel.sensors import Conditioner, derive, tds_ppm  # noqa: E402

RESULTS = []


def check(name, cond):
    RESULTS.append(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}")


def with_ck(body):
    return body + ',"ck":%d}' % (sum(body.encode()) & 0xFF)


def test_checksum():
    good = with_ck('{"vcc":4.750,"ph_v":2.150,"t_water":26.00,"seq":5,"led":"G","fw":2')
    check("a good line with a checksum is accepted", check_line(good) is not None)
    check("a line with one wrong digit is dropped", check_line(good.replace("2.150", "2.750")) is None)
    check("a cut-off line is dropped", check_line(good[:-8]) is None)
    check("a firmware v1 line (no checksum) is still accepted", check_line('{"vcc":4.75,"ph_v":2.15}') is not None)


def test_conditioner(cfg):
    c = Conditioner(cfg)
    t = 1000.0
    base = {"vcc": 4.75, "ph_v": 2.16, "tds_v": 0.62, "turb_v": 1.8, "mq3_v": 1.6, "t_water": 26.0, "t_air": 28.0, "rh": 40}
    for i in range(3):
        c.clean(base, t + i)
    out = c.clean({**base, "t_water": None}, t + 4)
    check("water temp missing for 1 s is bridged with the last good value", out["t_water"] == 26.0)
    out = c.clean({**base, "t_water": None}, t + 3 + cfg["hold_seconds"]["t_water"] + 2)
    check("water temp missing longer than the hold time becomes None (fault)", out["t_water"] is None)
    c2 = Conditioner(cfg)
    for i in range(3):
        c2.clean(base, t + i)
    out = c2.clean({**base, "ph_v": 0.01}, t + 4)
    check("a single pH spike is removed by the median filter", abs(out["ph_v"] - 2.16) < 1e-9)
    # brain: with bridging, a 2 s DHT drop-out never becomes SENSOR FAULT
    b = Brain(cfg); b.started = time.time() - 999
    c3 = Conditioner(cfg); state = None
    for i in range(30):
        raw = {**base, "ldr_do": 0, "turb_do": 1, "mq3_do": 1, "up": 200}
        if i % 7 in (3, 4):
            raw["t_air"] = None; raw["rh"] = None
        state, _, _ = b.step(derive(c3.clean(raw, t + i), cfg))
    check("repeated short DHT11 drop-outs never cause a false SENSOR FAULT", state == "NORMAL")


def test_calibration(cfg):
    cfg = json.loads(json.dumps(cfg))
    v = 0.62
    base = tds_ppm(v, 25.0)
    cfg["calibration"].update({"tds_k": 1.2, "t_water_offset": -0.5, "turbidity_clear_v": 3.0, "mq3_clean_v": 1.5})
    r = derive({"vcc": 4.75, "ph_v": 2.16, "tds_v": v, "turb_v": 2.4, "mq3_v": 2.0, "t_water": 25.5, "turb_do": 1, "mq3_do": 1}, cfg)
    check("TDS factor k is applied", abs(r["tds"] - round(base * 1.2)) <= 1)
    check("water temperature offset is applied", r["t_water"] == 25.0)
    check("turbidity judged against clear water (20 % darker = cloudy)", r["turbid"] is True and r["turb_pct"] == 20)
    check("MQ-3 vapour judged against the clean-air baseline", r["vapour"] is True)


class FakeFirebase(BaseHTTPRequestHandler):
    """Just enough of Firebase Auth + Realtime Database REST for the uploader."""
    data, offline, calls = {}, False, []

    def log_message(self, *a):
        pass

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def _send(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _path(self):
        return [p for p in self.path.split("?")[0].replace(".json", "").split("/") if p]

    def _set(self, parts, value):
        d = FakeFirebase.data
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        d[parts[-1]] = value

    def do_POST(self):
        self._body()
        if "signInWithPassword" in self.path:
            return self._send({"idToken": "tok1", "refreshToken": "ref1", "expiresIn": "3600"})
        self._send({}, 404)

    def do_PUT(self):
        if FakeFirebase.offline:
            self.close_connection = True; return
        FakeFirebase.calls.append(("PUT", self.path.split("?")[0]))
        self._set(self._path(), json.loads(self._body())); self._send({})

    def do_PATCH(self):
        if FakeFirebase.offline:
            self.close_connection = True; return
        FakeFirebase.calls.append(("PATCH", self.path.split("?")[0]))
        body = json.loads(self._body())
        for k, v in body.items():
            self._set(self._path() + k.split("/"), v)
        self._send({})


def test_cloud(cfg, tmp):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), FakeFirebase); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    cloud.SIGNIN_URL = f"http://127.0.0.1:{port}/signInWithPassword?key={{key}}"
    ccfg = {**cfg, "log_dir": tmp, "cloud": {**cfg["cloud"], "enabled": True, "station_id": "test", "live_every_s": 0,
                                             "reading_every_s": 0}}
    logs = []
    c = cloud.Cloud(ccfg, {"api_key": "k", "database_url": f"http://127.0.0.1:{port}", "email": "e", "password": "p"},
                    logs.append)
    c.backoff = 1
    c.start()
    now = time.time()
    c.set_live({"state": "NORMAL", "site": "test"})
    c.reading({"t": now, "state": "NORMAL", "ph": 7.1, "tds": 400}, force=True)
    time.sleep(3)
    st = FakeFirebase.data.get("stations", {}).get("test", {})
    check("cloud: live state uploaded", st.get("live", {}).get("state") == "NORMAL")
    check("cloud: reading uploaded", len(st.get("readings", {})) == 1)
    check("cloud: station listed in the index", "test" in FakeFirebase.data.get("index", {}))
    FakeFirebase.offline = True
    for i in range(5):
        c.reading({"t": now + 10 + i, "state": "INDUSTRIAL", "ph": 7.0, "tds": 1800}, force=True)
    c.event({"id": 123, "title": "Industrial discharge", "open": True})
    time.sleep(3)
    check("cloud: while offline, readings wait in the outbox", c.queued >= 6 and len(st.get("readings", {})) == 1)
    FakeFirebase.offline = False
    t0 = time.time()
    while time.time() - t0 < 20 and (c.queued or len(FakeFirebase.data["stations"]["test"].get("readings", {})) < 6):
        time.sleep(0.5)
    st = FakeFirebase.data["stations"]["test"]
    check("cloud: back online, everything is sent (6 readings + 1 event)", len(st.get("readings", {})) == 6 and "123" in st.get("events", {}))
    srv.shutdown()


def run():
    cfg = settings.load()
    test_checksum()
    test_conditioner(cfg)
    test_calibration(cfg)
    import tempfile
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        test_cloud(cfg, tmp)
    ok = all(RESULTS)
    print("\nRELIABILITY: ALL PASS" if ok else "\nRELIABILITY: SOME FAILED")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
