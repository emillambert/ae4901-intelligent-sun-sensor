# System architecture

## Concept

Six CubeSat faces (+X, −X, +Y, −Y, +Z, −Z). Two optical channels per face, twelve total. Each Arduino nominally receives one LDR from each face so it can compute a **coarse independent estimate** in degraded operation. An external host receives raw readings and computes the full calibrated estimate using the measurements that remain usable.

```text
   12 GL5537-1 LDRs + analogue dividers
          /                         \
  Arduino A (6)                  Arduino B (6)
  ADC + local                    ADC + local
  coarse vector                  coarse vector
         \                          /
          SUN4 serial packets (CRC16)
                    |
                PC / GSE host
           per-sensor calibration
          full Sun-vector estimate
         warnings / validity state
```

## Mechanics

Current mechanical *baseline* uses two six-direction arrays rotated +10° and −10° around the CubeSat body diagonal `[1,1,1]` (approximately 8.16° optical tilt per sensor away from the local face normal). This was chosen after idealized geometry simulations; the exact realized mounting axes, LDR angular response, and 3D-printed part tolerances still require measurement.

## Architecture constraints

- The host PC is a **single point of failure** for the 12-channel fused estimate. The board-local vector provides a fallback but is **not yet performance-validated**.
- Current PC-side software requires SciPy and does **not** run on AVR Arduino boards.
- The two sketches are identical except `BOARD_ID`, but both may share USB power/GSE, so physical fault tolerance must be examined.
- SUN4 is a **prototype protocol**, not a spacecraft telemetry standard.
- The LDR optical reading alone cannot universally distinguish coherent glints from a true Sun vector. A simulated external attitude reference is not present in this hardware baseline.
