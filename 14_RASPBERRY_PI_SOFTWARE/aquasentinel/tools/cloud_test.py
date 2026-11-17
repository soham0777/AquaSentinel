"""Checks the Firebase set-up from the Pi: signs in with secrets.json, writes a test value, reads it back.

  python3 ~/aquasentinel/tools/cloud_test.py
"""
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aquasentinel import settings          # noqa: E402
from aquasentinel.cloud import Cloud       # noqa: E402


def main():
    cfg = settings.load()
    sec = settings.load_secrets()
    if not sec:
        print("No secrets.json. Copy secrets.example.json to secrets.json and fill it in (cloud/FIREBASE_SETUP.md).")
        return 1
    c = Cloud(cfg, sec, print)
    if not c.ready:
        print("secrets.json is not filled in yet: replace every PUT_... value (email and password of the station user)."); return 1
    try:
        c._auth()
        print("OK  signed in as", sec["email"])
    except Exception as e:
        print("FAIL sign-in:", e, "\n     Check the e-mail/password user in Firebase Authentication and the api_key."); return 1
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        c._http("PUT", c._url("/selftest"), {"at": stamp})
        back = c._http("GET", c._url("/selftest"))
        print("OK  wrote and read back", json.dumps(back))
        c._http("DELETE", c._url("/selftest"))
    except Exception as e:
        print("FAIL write:", e, f"\n     In the database, set owners/{c.sid} to this user's UID (cloud/FIREBASE_SETUP.md step 4).")
        return 1
    print(f"Cloud ready for station '{c.sid}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
