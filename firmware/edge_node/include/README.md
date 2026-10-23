# include

Headers for the modules in [`../src`](../src).

* `config.h`: **pin map, intervals, hard limits**. Start here when wiring the board.
* `exported_anomaly_weights.h`: output of `analytics/train_proxy_anomaly_engine.py`. **Not included by the firmware** (the decision logic uses statistics, not these weights); kept for reference.
* `secrets.h`: *you create this locally* for credentials; it is git-ignored and must never be committed.
