# Design decisions and open questions

## Agreed baseline

| ID | Decision | State |
|---|---|---|
| D01 | Six CubeSat faces | User selected |
| D02 | All 12 supplied GL5537-1 LDRs | User selected |
| D03 | 3D-printed structure | User selected |
| D04 | Two microcontrollers | User selected |
| D05 | Quantitative characterization | User selected |
| D06 | 3D vector + system status | User selected |
| D07–D09 | Compare flat and angled layouts computationally | User selected research comparison; ~8.16° geometry is proposed baseline, not measured optimum |

## Current implementation choices

- Six inputs per controller, with local coarse vector and SUN4 telemetry.
- PC-side calibrated nonlinear fitting is a **candidate**, not a verified flight implementation.
- Fixed resistor value uses **30 kΩ placeholder**; actual supplied values are unknown.
- Ratiometric ADC configuration in the compact firmware; no unsafe automatic reference switching.
- Software warnings for high residuals/temporal jumps; no hard claim to solve coherent reflected-light ambiguity.
- No physical ND filter, IMU, magnetometer, temperature sensor, or new electronics presumed available.

## Explicitly not adopted

- Deep or shallow optical masks as baseline: previous idealized tests found no convincing overall improvement.
- Aggressive static brightness gates: may reject valid sunlight with calibration/brightness shifts.
- Online rewriting of sensor calibration from LDR-only observations: ambiguous with changing illumination.
- Gyro/magnetometer fusion: additional hardware unconfirmed.

## To decide with the group

1. Exact Arduino model/pinout and fixed resistor values.
2. Final printed mount geometry after dry-fit.
3. Whether the full calibrated Sun-vector estimator must execute **onboard** or may be demonstrated on the PC. The existing host solution should not be represented as onboard computation.
4. Required UI environment and allowable PC dependencies.
5. Calibration illumination and accuracy acceptance thresholds.
