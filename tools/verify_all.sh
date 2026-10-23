#!/usr/bin/env bash
# One-command health check for AquaSentinel. Read-only for the repository: every build runs on a temporary COPY,
# so nothing is written into your working tree.
#
#   bash tools/verify_all.sh            # links + detector replay + mechanical rebuild + C++/Python parity
#   bash tools/verify_all.sh --pio      # ... and also compile the firmware (needs PlatformIO: pip install platformio)
#
# Needs Python 3 with numpy, matplotlib, Pillow (pip install -r requirements.txt) and, for the parity step, a C++17 compiler.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || PY=python
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAIL=0
step() { printf '\n== %s\n' "$1"; }

step "1/5 link and asset check"
"$PY" "$ROOT/tools/check_links.py" "$ROOT" || FAIL=1

step "2/5 detector replay (analytics/evaluate.py on the synthetic dataset)"
cp -r "$ROOT/analytics" "$TMP/analytics"
( cd "$TMP/analytics" && MPLBACKEND=Agg "$PY" evaluate.py ) > "$TMP/eval.txt" 2>&1
grep -E "Events detected|Outside the events" "$TMP/eval.txt"
grep -q "Events detected: 4 of 4" "$TMP/eval.txt" && grep -q "Outside the events: 0 EVENT cycles" "$TMP/eval.txt" \
  && echo "DETECTOR: PASS (4 of 4 events, 0 EVENT cycles outside)" || { echo "DETECTOR: FAIL"; FAIL=1; }

step "3/5 mechanical rebuild (mechanical/src/build.py, 14 design checks)"
mkdir -p "$TMP/mech" && cp -r "$ROOT/mechanical/src" "$ROOT/mechanical/checks" "$ROOT/mechanical/cad" "$TMP/mech/"
( cd "$TMP/mech" && MPLBACKEND=Agg "$PY" src/build.py ) > "$TMP/mech.txt" 2>&1
echo "build.py reported: $(grep -c '\[PASS\]' "$TMP/mech.txt") PASS, $(grep -c '\[FAIL\]' "$TMP/mech.txt") FAIL"
N=$("$PY" - "$TMP/mech/checks/design_checks.json" <<'PYEOF'
import json, sys
c = json.load(open(sys.argv[1], encoding="utf-8"))["checks"]
print(f"{sum(bool(v) for v in c.values())}/{len(c)}")
PYEOF
)
echo "design_checks.json pass count: $N"
[ "$N" = "14/14" ] || { echo "MECHANICAL: FAIL (expected 14/14 checks)"; FAIL=1; }
if cmp -s <(tr -d '\r' < "$TMP/mech/checks/design_checks.json") <(tr -d '\r' < "$ROOT/mechanical/checks/design_checks.json") \
   && cmp -s <(tr -d '\r' < "$TMP/mech/cad/BOM_R3.csv") <(tr -d '\r' < "$ROOT/mechanical/cad/BOM_R3.csv"); then
  echo "MECHANICAL: PASS (regenerated design_checks.json and BOM_R3.csv match the committed files)"
else
  echo "MECHANICAL: FAIL (regenerated output differs from the committed files)"; FAIL=1
fi

step "4/5 firmware decision engine (C++) vs Python reference"
"$PY" "$ROOT/tools/parity/compare.py" "$ROOT" || { rc=$?; [ $rc -eq 2 ] && echo "(skipped: no compiler)" || FAIL=1; }

step "5/5 firmware compile (PlatformIO)"
if [ "${1:-}" = "--pio" ]; then
  cp -r "$ROOT/firmware/edge_node" "$TMP/edge_node"
  ( cd "$TMP/edge_node" && PLATFORMIO_CORE_DIR="${PLATFORMIO_CORE_DIR:-$HOME/.platformio}" pio run -e esp32dev -e bench ) > "$TMP/pio.txt" 2>&1
  grep -E "SUCCESS|FAILED|RAM:|Flash:" "$TMP/pio.txt"
  grep -q "FAILED" "$TMP/pio.txt" && { echo "FIRMWARE BUILD: FAIL"; FAIL=1; } || echo "FIRMWARE BUILD: PASS"
else
  echo "skipped (add --pio to compile the firmware)"
fi

printf '\n'
[ "$FAIL" -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED (see above)"
exit "$FAIL"
