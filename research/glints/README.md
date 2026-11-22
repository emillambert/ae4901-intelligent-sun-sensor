# AE4901 Sun Sensor V8 — residual limitations and tested fixes

**Date:** 22 November 2026. **Status:** Computational prototype using the original V7 synthetic forward model; NOT physical validation and NOT flight-qualified. The supplied course components remain 12 GL5537-1 LDRs, 2 Arduino-equivalent microcontrollers and supplied fixed resistors. The assumed 8.16° tilted geometry is unchanged.

## Core results

### 1. Fundamental illumination ambiguity (mathematical counterexample)

For ideal cosine-response detectors, where two sources illuminate the **same active sensor subset**, their combined signal is exactly that of a single virtual source at the normalized intensity-weighted sum direction. This is true with 12 independent directions and 2 redundant Arduinos. The reproducible `identifiability_test.py` finds sources 21.19° apart with second-source intensity 80% of the first, creating an apparent 9.41° direction error with **2.2e-16 maximum deviation from an ideal single-source sensor measurement**.

This is a *counterexample*, not a statement that every real GL5537-1 LDR is indistinguishable. Noncosine responses can reveal certain multi-source signals, but cannot guarantee separation for all relative source directions/intensities. An estimator cannot fix missing information.

### 2. Causal adaptive temporal detector

The `v8_temporal_study.py` tests a **new optional** temporal jump detector with one-step per-frame streaming input, using only previous accepted direction estimates. It rejects sudden changes inconsistent with the recently observed rotation rate and reacquires after three consecutive consistent observations. It never labels a held stale vector as a current valid measurement. It is not gyro-assisted and it does not use truth as an estimator input.

**Independent holdout:** four new synthetic sensor populations × 22 independent 40-frame sequences per scenario (=3,520 frames per scenario). The development set used four separate populations × 22 sequences. A complete comparison is in `temporal_heldout_summary.csv`.

| Case | Previous accepted wrong >10° | With temporal gate | Good and accepted within 5°: previous -> new |
|---|---:|---:|---:|
| Brief 4-frame strong glint | 9.86% | **4.89%** | 89.77% -> 89.77% |
| Sustained strong glint | 67.30% | **61.68%** | 32.47% -> 32.47% |
| Clean slow rotation | 0% | 0% | 99.72% -> 99.69% |
| Fast continuous tumble | 0% | 0% | 99.55% -> 99.55% |
| Real abrupt 38° attitude step | 0% | 0% | **99.74% -> 94.72%** |

**Interpretation:** a useful partial fix for transient glints, with a downside for real abrupt slews and almost no protection against sustained glints. Do not enable the gate unconditionally for unknown-fast-motion spacecraft. This compares the **same calibrated V3 angular estimator with and without one extra temporal gate**—it is *not* a direct comparison between full V7 and V8 pipelines. The synthetic glint is a fixed direction in the spacecraft body frame, with 80% of Sun intensity, appearing briefly or persistently. This is a stress scenario, not a statistical LEO glint model.

### 3. Relative gain self-calibration trial — NOT adopted

`relative_drift_study.py` tries to learn sensor-to-sensor gain drift only from the sensor's own estimates over varying illumination. Held-out p95 angular error **rose** from 5.22° to 5.32° on clean calibration sequences, while valid-within-5° changed 89.67% -> 90.44%. With a persistent 20%-strength interfering source during calibration, held-out p95 changed 5.22° -> 5.12°, too small and inconsistent to claim general improvement. The gain-estimation error remained ~11–12% in these simulated populations.

**Reject automatic on-orbit gain updates** using only LDR data. Use persistent channel residuals to *warn*, never silently rewrite calibration coefficients; obtain independent reference or laboratory ground calibration for corrections.

### 4. Bright-Sun circuit feasibility (calculation only)

A nominal 30 kΩ divider with representative GL5537 R10 = 25 kΩ and gamma = 0.6 has inadequate ADC resolution if the 10–100 lux power-law is **extrapolated** to unfiltered direct sunlight. At 100,000 lux the model gives ~15 counts with the 1.1 V ADC reference. A calibrated OD3 optical filter would attenuate this to ~100 lux and yield ~805 counts on a nominal 1.1 V reference. This is **not validated** for actual sensor response, filter angle/spectrum/aging, nor the exact Arduino reference voltage. Read `brightness_tradeoffs.csv` and `circuit_tradeoffs.py`.

For the indoor course experiment the OD3 filter would excessively reduce incident light; it must be removable and is not part of baseline. Do not choose it for space without optical testing and material qualification.

### 5. Environmental engineering / temperature

V7 temperature compensation helped substantially under an assumed temperature response when the true coefficients and temperature were independently supplied; a wrong-sign coefficient made things much worse. No new measurable thermal hardware performance is claimed by V8. Without a thermistor/thermocouple and real multi-temperature calibration, automatic temperature correction is an unvalidated counterfactual. Thermal gradients between opposite CubeSat faces require separate attention. Radiation, vacuum, UV, outgassing and vibration cannot be corrected or certified by this software study.

## Engineering decision

**KEEP:** 12-LDR geometry, individual calibration workflow, robust estimation, existing eclipse/fault/health validity checks. **ADD as optional software:** adaptive temporal warning/gate only when angular-rate assumptions are credible, with explicit suspect/reacquisition state and no stale-vector substitution. **OPTIONAL EXTRA HARDWARE:** a calibrated removable neutral-density filter for genuinely bright solar use, temperature sensors if needed, and independent attitude/optical sensing if true glint discrimination is required. **REJECT:** automatic LDR-only self-calibration and unconditional strict brightness or temporal rejection. **NOT POSSIBLE FROM CURRENT SENSOR MEASUREMENTS ALONE:** guaranteed correction of a sustained coherent glint.

### Practical proposal for the four-person AE4901 group

1. Calibrate the final assembled sensor (12 channels) at independent angles, intensities and if possible two temperatures; keep held-out test angles.
2. Use the nominal 30 kΩ resistor *only if supplied* and characterize its ADC range for the chosen lab light source. Avoid promising direct-Sun operation with the unchanged circuit.
3. Demonstrate direct Sun acquisition, eclipse/no-light rejection, single failed sensor, controller failover, brief glint warning and true fast-rotation response.
4. Report **accepted-and-within-5°**, **wrong-accepted-over-10°**, **percent accepted**, and **p95 among accepted**, always together; state these are *laboratory* numbers once measured.

## Reproduce

```bash
pip install numpy pandas scipy matplotlib
python identifiability_test.py
python v8_temporal_study.py
python relative_drift_study.py
python circuit_tradeoffs.py
python -m unittest -v test_v8.py
python make_figures.py
```

The `source/AE4901_v7/reference` folder is an unchanged excerpt from the original V7 package, included to make the reproducible results self-contained. All new code files are Python references; no Arduino firmware was compiled, no KiCad or SPICE execution occurred, and no physical readings were available.

## Literature context

- NASA Small Spacecraft GNC, 2026: https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/
- EIVE flight albedo and sensor gating: https://link.springer.com/article/10.1007/s12567-024-00559-7
- UPMSat-2 ground/on-orbit analog Sun sensor calibration and albedo: https://www.mdpi.com/1424-8220/21/14/4905
- Magnetometer-assisted Earth-albedo correction (with additional hardware): https://www.sciencedirect.com/science/article/pii/S0094576521005142
- GL5537-1 product specifications: https://www.senbasensor.com/visible-light-sensor/5mm.html
