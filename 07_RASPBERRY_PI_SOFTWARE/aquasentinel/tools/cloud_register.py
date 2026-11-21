"""Creates this station's own Firebase login, on the Pi. Nobody types or sees the password.

  python3 ~/aquasentinel/tools/cloud_register.py

It makes a random password here, creates the user station-<station_id>@aquasentinel.local in Firebase Authentication,
and saves the e-mail and password only in secrets.json (readable only by this user). It prints the user's UID: that UID
must then be set at owners/<station_id> in the Realtime Database (Firebase console > Data), so the station may write.
"""
import json
import os
import secrets as rnd
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aquasentinel import settings     # noqa: E402

SIGNUP = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={key}"


def main():
    cfg = settings.load()
    sec = settings.load_secrets()
    if not sec or not sec.get("api_key") or "PUT_" in sec["api_key"]:
        sys.exit("secrets.json needs the api_key first (it is already filled in the copy from the laptop).")
    sid = cfg["cloud"]["station_id"]
    email = f"station-{sid}@aquasentinel.local"
    password = rnd.token_urlsafe(24)
    body = json.dumps({"email": email, "password": password, "returnSecureToken": True}).encode()
    req = urllib.request.Request(SIGNUP.format(key=sec["api_key"]), data=body, headers={"Content-Type": "application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=20).read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        if "EMAIL_EXISTS" in msg:
            sys.exit(f"{email} already exists in Firebase. If this Pi does not have its password, delete that user in "
                     "Firebase console > Authentication > Users and run this again.")
        sys.exit(f"Firebase refused: {msg[:300]}")
    sec["email"], sec["password"] = email, password
    tmp = settings.SECRETS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(sec, f, indent=2)
    os.replace(tmp, settings.SECRETS_PATH)
    try:
        os.chmod(settings.SECRETS_PATH, 0o600)
    except OSError:
        pass
    print(f"OK  station login created: {email}")
    print("    password: made at random and saved only in secrets.json (not shown)")
    print(f"    UID: {r['localId']}")
    print(f"Next: in Firebase > Realtime Database > Data set  owners/{sid}  to this UID, then run tools/cloud_test.py")


if __name__ == "__main__":
    main()
