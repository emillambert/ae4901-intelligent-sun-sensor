# AE4901 | Intelligent Sun Sensor — Design discussion sheet
**22 November 2026 · Reference concept, not an approved group design · Based on repository `51a9798`**

> **Purpose.** Give the four-person team a starting point to challenge and improve. The simulations below are hypotheses to test, not instructions to copy or measured claims.

## Assignment in one line
With the supplied **two Arduino-equivalent boards, 12 GL5537-1 LDRs and 12 resistors (30 kΩ–3 MΩ)**, build a fault-tolerant CubeSat mock-up that measures Sun incidence on **at least 3 faces**, reconstructs and displays a **body-frame Sun vector**, and **rejects noise using a threshold**. *Source: AE4901 Practical Manual, Assignment 3, §4.*

## Current reference architecture
```text
12 LDRs / 6 CubeSat faces  (+X, −X, +Y, −Y, +Z, −Z)
                  | paired sensors on each face |
          Arduino A (6 ADC)     Arduino B (6 ADC)
           local coarse         local coarse
          direction + CRC       direction + CRC
                   \            /
           PC / ground support estimator
        calibration • 12-channel fit • health/status
                3D Sun vector + UI
```
**Provisional mechanical geometry:** one LDR per controller per face; rotate the two six-sensor arrays by **+10° / −10° about body diagonal [1,1,1]** (~8.2° off each face normal). Previous idealized geometry comparisons favored this over flat mounting, but it is **not physically validated**. A changeable printed insert would allow an A/B test.

## Why these choices? (what the iterations suggested)
| Area | Current working preference | Evidence / limitation |
|---|---|---|
| Coverage | 12 LDRs on all 6 faces; one six-face set per board | Geometry simulations suggested robust directional coverage and a degraded one-board mode. |
| Estimation | Calibrate each LDR; combine readings with a nonlinear fit on PC | Synthetic accuracy improved with calibration. Current Arduino code only computes a **coarse fallback vector**; PC fit is **not embedded**. |
| Reliability | ADC-rail checks, darkness threshold, CRC packets, stale-board detection and status | Software tests pass; actual controller and LDR fault tolerance still need physical tests. |
| Reflected light | Warn about poor fit and sudden direction changes; do not claim to correct persistent glints | Brief-glint warning helps in simulations; strong sustained reflections can be **indistinguishable** from direct sunlight using only LDR intensities. |
| Optics / extras | Bare LDR baseline; no masks, ND filter, gyro, magnetometer or automatic self-recalibration | Extra parts are not assumed available; earlier experimental additions had mixed or conditional results. |

## Decisions the group should make together
1. **Compute where?** Is the final calibrated vector required to run on Arduino, or is a PC/GSE acceptable for the demonstration? The present proposal assumes PC for the accurate fit.
2. **Mounting?** Adopt the ~8.2° angled arrays, use flat sensors, or build interchangeable inserts to test both?
3. **Electronics?** Confirm actual board model, ADC reference/range, pin availability, resistor values and laboratory lighting before finalizing dividers.
4. **Evidence?** Set an accuracy target (suggested starting point: **p95 ≤5° in nominal lab illumination**) *and* report valid-reading coverage and false-valid cases.
5. **Failure behavior?** Agree which faults must be survived (one LDR, one Arduino, darkness, corrupted packets) and what the UI displays when confidence is low.

## Minimum build-and-test sequence
**Inventory components → breadboard two independent 6-channel chains → 3D-print testable mounts → record per-LDR lux/angle calibration → validate on held-out Sun directions → inject faults and glints → show live 3D vector + status.**

**Evidence boundary:** Design/synthetic software only. No actual board compile/upload, measured angular accuracy, environmental qualification, or full V2–V8 feature integration yet. Repository: `github.com/emillambert/ae4901-intelligent-sun-sensor` (private); see `docs/decisions.md`, `docs/validation.md`, `research/`, `legacy/`.

### Record measured results here (not simulated values)
| Metric | Measured result |
|---|---|
| Held-out angular error, p95 | — ° |
| Valid-reading coverage | — % |
| False-valid rate (darkness / glint / faults) | — % |
| Single-board fallback performance | — |
