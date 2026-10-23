# test

Unity tests, run on a connected board: `pio test -e bench` (from `firmware/edge_node`).

* `test_fail_safe/`: 12 tests (median of reads, a failed or dead probe is a fault and never "clean water", invalid values never enter the baseline or trip a limit)
* `test_state_machine/`: 14 tests (one sample per event, event ending after clean cycles, learning phase, learned state surviving a power cut or deep-sleep wake, sampler lockout)

None of them has run on real hardware yet. The same decision rules are checked on a PC by `python tools/parity/compare.py`.
