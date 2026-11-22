# Verification and readiness

## What's verified in this repository

- Eight Python runtime unit tests with synthetic signals.
- Host synthetic demonstration; `valid_for_control` stays false.
- C++ **mock** header syntax checks for `BOARD_ID=0` and `1` (NOT Arduino IDE/CLI builds).
- Historical archive integrity hashes.

## Not verified

- Actual Arduino target, pin mapping, ADC and supplied resistor selection.
- Physical GL5537-1 angular, intensity or temperature calibration.
- The true Sun-vector accuracy of the final electronics and mount.
- Hardware failover with power and communication faults.
- V2–V8 simulation feature equivalence in the consolidated runtime.
- Calibration behavior in direct Sun, under Earth albedo or coherent glints.

## Minimum real acceptance test plan

1. Measure divider voltage/ADC versus known 10, 20, 50, 100 lux using the **actual** hardware and source spectrum.
2. Measure angular response on controlled 0°–75° sweeps and held-out intermediate angles for all LDRs.
3. Fit individual models with `tools/calibrate_ldr.py`, retain raw lab data privately and record true mounting directions.
4. Compare angular error, accepted/invalid fraction and 95th-percentile error across the full intended field of view.
5. Inject open/short/stuck LDR, controller reset/disconnect, serial corruption, ambient light and light loss/reacquisition.
6. Demonstrate live Sun direction and status output without false claims of flight qualification.

## Progress

Current level: **software prototype, not hardware integrated**.

Use a readiness ladder: **modelled → software test → built → calibrated → fault-tested → verified**. Do not treat the first two as evidence for the last three.
