This folder is filled at runtime by the AquaSentinel service.

One CSV per day: `readings_YYYY-MM-DD.csv`. It is empty in the project copy on purpose — the real logs live on the
Raspberry Pi and are not copied back here automatically. To bring them back for the booth or the report:

```
scp pi@<pi-address>:~/aquasentinel/logs/*.csv .
```

Do not delete the folder itself; the service expects it to exist.
