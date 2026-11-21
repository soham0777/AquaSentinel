"""Publishes the station to Firebase (Realtime Database), so the dashboard can be seen from anywhere.

Standard library only (no pip install, nothing heavy on the Pi). Works without internet: everything to upload is
first saved in a small SQLite file (logs/cloud_outbox.db) and sent when the network is back, oldest first.

What goes up (under /stations/<station_id>/):
  live            the current state and readings, replaced every few seconds (only the newest matters)
  readings/<ms>   one reading every minute, and one at every change of state
  events/<id>     each event (alert type, reasons, sample, SMS), updated when it clears
The cloud dashboard (cloud/public/index.html) reads these.

Login: the station signs in as its own Firebase user (e-mail + password from secrets.json). The database rules
(cloud/database.rules.json) let only that user write, and anyone read.
"""
import json
import os
import queue
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

SIGNIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={key}"
REFRESH_URL = "https://securetoken.googleapis.com/v1/token?key={key}"
BATCH = 100


def compact_reading(p):
    """Small reading for the cloud history (about 120 bytes)."""
    return {"t": round(p["t"], 1), "s": p.get("state"), "ph": p.get("ph"), "tds": p.get("tds"),
            "turb": p.get("turbid"), "vap": p.get("vapour"), "tw": p.get("t_water"), "ta": p.get("t_air"),
            "rh": p.get("rh")}


class Cloud:
    def __init__(self, cfg, secrets, log):
        self.cfg = cfg
        self.c = cfg.get("cloud", {})
        self.secrets = secrets or {}
        self.log = log
        self.sid = self.c.get("station_id", "station")
        self.db_url = (self.secrets.get("database_url") or "").rstrip("/")
        self.key = self.secrets.get("api_key", "")
        self.inbox = queue.Queue()
        self.live = None
        self.live_sent = 0.0
        self.index_sent = 0.0
        self.last_reading = 0.0
        self.token = None
        self.refresh_token = None
        self.token_until = 0.0
        self.status = "starting"
        self.last_ok = None
        self.queued = 0
        self.sent = 0
        self.backoff = 2

    @property
    def ready(self):
        vals = [self.db_url, self.key, self.secrets.get("email", ""), self.secrets.get("password", "")]
        return all(vals) and not any("PUT_" in v or " " in v for v in vals)     # placeholders not filled in yet

    # ---------- called by the station (any thread, never blocks) ----------
    def set_live(self, snap):
        self.live = snap

    def reading(self, point, force=False):
        now = point["t"]
        if force or now - self.last_reading >= self.c.get("reading_every_s", 60):
            self.last_reading = now
            self.inbox.put((f"readings/{int(now * 1000)}", compact_reading(point)))

    def event(self, ev):
        self.inbox.put((f"events/{ev['id']}", {k: v for k, v in ev.items() if k != "id"}))

    # ---------- HTTP ----------
    def _http(self, method, url, body=None, form=False, timeout=15):
        data = None
        headers = {}
        if body is not None:
            if form:
                data = urllib.parse.urlencode(body).encode(); headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                data = json.dumps(body).encode(); headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"null")

    def _auth(self):
        if self.token and time.time() < self.token_until - 120:
            return self.token
        if self.refresh_token:
            try:
                r = self._http("POST", REFRESH_URL.format(key=self.key),
                               {"grant_type": "refresh_token", "refresh_token": self.refresh_token}, form=True)
                self.token, self.refresh_token = r["id_token"], r["refresh_token"]
                self.token_until = time.time() + int(r.get("expires_in", 3600))
                return self.token
            except Exception:
                self.refresh_token = None
        r = self._http("POST", SIGNIN_URL.format(key=self.key),
                       {"email": self.secrets["email"], "password": self.secrets["password"], "returnSecureToken": True})
        self.token, self.refresh_token = r["idToken"], r["refreshToken"]
        self.token_until = time.time() + int(r.get("expiresIn", 3600))
        self.log("Cloud: signed in to Firebase")
        return self.token

    def _url(self, path):
        return f"{self.db_url}/stations/{self.sid}{path}.json?auth={urllib.parse.quote(self._auth())}"

    # ---------- the upload thread ----------
    def _db(self):
        path = os.path.join(self.cfg["log_dir"], "cloud_outbox.db")
        db = sqlite3.connect(path)
        db.execute("CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, body TEXT)")
        db.commit()
        return db

    def _drain_inbox(self, db):
        rows = []
        while True:
            try:
                rows.append(self.inbox.get_nowait())
            except queue.Empty:
                break
        if rows:
            db.executemany("INSERT INTO outbox (path, body) VALUES (?, ?)", [(p, json.dumps(b)) for p, b in rows])
            cap = self.c.get("max_queue", 50000)
            n = db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]
            if n > cap:                                  # very long offline: keep the newest
                db.execute("DELETE FROM outbox WHERE id IN (SELECT id FROM outbox ORDER BY id LIMIT ?)", (n - cap,))
            db.commit()
        self.queued = db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]

    def _push_once(self, db):
        did = False
        if self.live is not None and time.time() - self.live_sent >= self.c.get("live_every_s", 5):
            body = dict(self.live); body["updated"] = {".sv": "timestamp"}
            self._http("PUT", self._url("/live"), body)
            if time.time() - self.index_sent > 600:          # the station list the cloud dashboard reads
                self._http("PUT", f"{self.db_url}/index/{self.sid}.json?auth={urllib.parse.quote(self._auth())}",
                           {"site": body.get("site"), "updated": {".sv": "timestamp"}})
                self.index_sent = time.time()
            self.live_sent = time.time(); did = True
        rows = db.execute("SELECT id, path, body FROM outbox ORDER BY id LIMIT ?", (BATCH,)).fetchall()
        if rows:
            patch = {path: json.loads(body) for _, path, body in rows}
            self._http("PATCH", self._url(""), patch)       # one request writes the whole batch
            db.execute("DELETE FROM outbox WHERE id <= ?", (rows[-1][0],)); db.commit()
            self.sent += len(rows); did = True
        return did

    def run(self):
        if not self.ready:
            self.status = "not set up (secrets.json)"
            self.log("Cloud: enabled in config.json but secrets.json is missing or incomplete; staying local")
            return
        db = self._db()
        while True:
            try:
                self._drain_inbox(db)
                if self._push_once(db):
                    self.status, self.last_ok, self.backoff = "online", time.strftime("%H:%M:%S"), 2
                    self._drain_inbox(db)
                time.sleep(0.5 if self.queued else 1)
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    self.token = None
                    self.status = "login refused: check secrets.json and the database rules"
                else:
                    self.status = f"server error {e.code}"
                self._wait()
            except Exception as e:
                self.status = "offline (saving to send later)"
                if self.backoff == 2:
                    self.log(f"Cloud: offline ({str(e)[:60]}); readings are kept and sent later")
                self._wait()

    def _wait(self):
        end = time.time() + self.backoff
        while time.time() < end:
            time.sleep(1)
        self.backoff = min(60, self.backoff * 2)

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def info(self):
        return {"enabled": True, "status": self.status, "queued": self.queued, "sent": self.sent,
                "last_ok": self.last_ok, "station": self.sid}
