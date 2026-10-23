# docs/dashboard: command-dashboard demo

A **static demo** of the screen the water-works and the pollution board would use, in English, मराठी and हिंदी.
Open [`index.html`](index.html) in a browser (no server, no build). Live: <https://soham0777.github.io/AquaSentinel/dashboard/>.

| File | Job |
|---|---|
| `index.html` | the page and its translations |
| `css/styles.css` | styles |
| `js/app.js` | the demo logic: **all values are hard-coded** (pH 7.42, EC 382 …), no network calls, no `innerHTML`; a DEMO banner is always shown |

It is **not connected** to the float or to any server. The plume animation runs as a time-lapse (about 60×) while the ETA
text uses real minutes. The firmware's telemetry upload is not written yet, so there is nothing to connect to.
