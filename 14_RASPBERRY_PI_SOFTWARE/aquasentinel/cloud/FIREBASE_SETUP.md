# AquaSentinel cloud on Firebase: setup

This puts every station's live state, history and events online. Anyone with the link can view them; only the station itself can write.

The Pi keeps working without internet. Readings wait in `logs/cloud_outbox.db` and go up when the network is back.

**What you need**
- a Google account for the team;
- the Firebase free plan (Spark), which needs no card;
- a laptop for step 8.

The setup takes about 20 minutes.

## 1. Create the project

1. Open https://console.firebase.google.com and click **Add project**.
2. Name it, for example `aquasentinel-live`.
3. Google Analytics is not needed.

## 2. Create the database

1. Go to **Build → Realtime Database → Create database**.
2. Choose the location **Singapore (asia-southeast1)**, which is closest to India.
3. Start in **locked mode**.
4. Copy the database URL shown at the top. It looks like `https://aquasentinel-live-default-rtdb.asia-southeast1.firebasedatabase.app`.

## 3. Create one user per station

1. Go to **Build → Authentication → Get started → Email/Password** and switch it on.
2. Open **Users → Add user**. Use an e-mail such as `station-kopargaon@<your-team-domain>` and a long password. The address does not need to receive mail.
3. Copy the **User UID** shown in the list.

## 4. Let that user write for its station

1. Open **Realtime Database → Data**.
2. Click **+** on the root and add a key `owners`.
3. Inside `owners`, add the key `kopargaon-1to5`. Its value is the UID you copied, in quotes.

The key must match `"station_id"` in `config.json`, under `"cloud"`.

## 5. Rules

1. Open **Realtime Database → Rules**.
2. Replace the text with the contents of `cloud/database.rules.json`.
3. Click **Publish**.

With these rules:
- anyone can read `index` and `stations`;
- only the station's own user can write to them;
- nobody can read or change `owners`, except you in the console.

If the data should be private, change `".read": true` to `".read": "auth != null"`.

## 6. Web keys

1. Open **Project settings (gear) → General**.
2. Copy the **Web API key**.
3. Under **Your apps**, click the web icon `</>` and register an app, for example `dashboard`.
4. Copy the `firebaseConfig` values into `cloud/public/firebase-config.js`.

These values only name the project; they are not passwords. The rules decide who may write.

## 7. On the Pi

```
cd ~/aquasentinel
cp secrets.example.json secrets.json
nano secrets.json
```

Fill in four values:
- the Web API key;
- the database URL;
- the station e-mail;
- the station password.

Save with Ctrl+O and Enter, then leave with Ctrl+X. Then run:

```
bash install.sh
```

The installer switches the cloud on, makes `secrets.json` readable only by your user, and tests the login and a write.

To test again later:

```
python3 tools/cloud_test.py
```

The dashboard footer on the Pi shows `cloud: online`, or how many readings are waiting to be sent.

**Never share `secrets.json`, and never put it in git.** The project's `.gitignore` already excludes it.

## 8. Publish the cloud dashboard (from a laptop, once)

```
npm install -g firebase-tools
firebase login
cd 14_RASPBERRY_PI_SOFTWARE/aquasentinel/cloud
firebase use --add            (pick your project)
firebase deploy --only hosting,database
```

The dashboard is then at `https://<project>.web.app`. Every station appears in its list.

## What goes up, and how much

| Path | What | How often |
|---|---|---|
| `index/<station>` | station name, for the list | every 10 min |
| `stations/<station>/live` | state, readings, beacon, power, SMS status | every 5 s |
| `stations/<station>/readings/<ms>` | pH, TDS, turbidity, vapour, temperatures, humidity | every 60 s, and at every change of state |
| `stations/<station>/events/<id>` | alert type, reasons, sample bottled, cleared time | when an event opens and when it clears |

One station adds about 60 MB of history a year. The free plan allows 1 GB stored and 10 GB downloaded a month.

Delete old `readings` in the console when needed.

To change how often data is sent, edit `"cloud"` in `config.json`:
- `live_every_s`: how often the live state is sent;
- `reading_every_s`: how often a reading is saved to the history.
