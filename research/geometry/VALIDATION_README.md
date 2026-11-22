# AE4901 — Independent Geometry Simulation Verification & Validation Review

Date: 2026-11-21. **Status: geometry calculations verified; physical sensor performance NOT validated.**

## Original material reviewed
- `/mnt/data/ae4901_sun_geometry_simulation.py`: original calculations, 30,000 Fibonacci sphere directions, noise and threshold sweeps, 12 LDR orientations on six faces.
- `/mnt/data/ae4901_geometry_results/comparison_metrics.csv`: original results and metrics.
- AE4901 embedded systems project manual, November 11, 2026: 12 GL5537-1 LDRs, two development boards, 6–7 week group project; requires 3+ faces, Sun vector, noise threshold, fault tolerance.

## Mathematical verification
- All tested sensor directions are length 1.
- Flat, icosahedral and dual-rotated 12-sensor configurations have `N.T @ N = 4*I` to numerical precision.
- Each ±rotated six-sensor array has mutually orthogonal sensing directions.
- Independent flat coverage computation, 16,390 Sun directions, yields 85.36% against original 85.42%, differing by sphere sampling and added axis directions.
- Independent ideal-noise check with 1% i.i.d. additive noise gives flat p95 angular error 1.01° versus original 1.016°. Close agreement supports basic reconstruction.
- Noiseless ideal cosine model produces essentially zero reconstruction error where the active sensing matrix has full rank.

## Critical methodological findings
1. **Original model lacked cube-body occlusion.** Sensor directions tilted away from a cube face are sometimes in sunlight even when the underlying physical face is back-facing and may block the ray. The revised model conservatively zeroes a sensor when `face_normal dot sun <= 0`, representing flush/near-face placement; standoff-mounted hardware may differ and needs ray tracing or measurement.
2. **Controller failover coverage changes decisively.** Original dual ±30° rotation (24.40° face tilt) has 85.5% one-board full rank without face shading, but around 57.6% with face shading. Original optimized icosahedral A/B split degrades from ~85.5% to ~46.3%; re-optimizing all 64 splits with face shading cannot improve the worst board beyond ~46.3% for this ideal-threshold-rank metric.
3. **Full-rank observability is not equivalent to practical accuracy or valid Sun detection.** Ill-conditioned directions close to physical face normal can cause high p99 error even with full rank. A 1% threshold with 1% additive noise wrongly admits noisy dark channels; p95 errors increased dramatically at some thresholds. The validation recommends using a noise-calibrated threshold and stability/fit residual checks.
4. **The GL5537-1 is a nonlinear CdS photoresistor, not a linear cosine-response photodiode.** The model has no evidence for actual LDR angular sensitivity, lux-to-ADC transfer function, spectral response under lab lamp, divider saturation, per-channel response, crosstalk, reflection, temperature effects or package shadowing. The arbitrary `cos^1.3` model is a sensitivity example, not a measured device characteristic.
5. **Simple inverse-power calibration of noisy readings is not adequate.** Applying `measurement^(1/p)` amplifies low-signal noise and can worsen error if thresholds are not changed accordingly. A calibrated physical sensor-response model and estimator-level treatment of uncertainty are needed.
6. **No simulated 1° accuracy claim can be transferred to the final LDR prototype.** The figures concern a simplified assumed model only.

## Representative results (self-shadowing included, 5% threshold)
- Flat: 85.36% geometric full-rank coverage, 85.36% with one board remaining; under assumed 1% noise p95 ~1.01° for accepted estimates.
- Dual rotated ±10° about spacecraft [1,1,1] diagonal: each face optical axis tilted 8.16°, 99.96% geometric full-rank coverage and ~79.1% with one board remaining; p95 ~1.16° under 1% noise, p99 ~2.02°.
- Dual rotated ±30° about [1,1,1]: each face optical axis tilted 24.40°, 99.96% geometric full-rank coverage and ~57.6% with one board remaining; p95 ~1.27° under 1% noise.
- The ~99.96% is not robust guaranteed sky coverage. Six axis-aligned sun vectors cannot be reconstructed with a full-rank least-squares fit under the conservative face-shadow geometry. Results near boundaries depend on thresholds, noise and device response.
- At 5% uncalibrated channel gain scatter and assumed 1% random output noise, p95 conditional angular error is ~2.6° for flat, ~2.8° for ±10° rotated, and ~4.0° for ±30° rotated. This test uses only two hypothetical gain realizations, not a statistical qualification.

## Proposed mechanical baseline (engineering judgment, not empirical validation)
Freeze **two LDRs per face**, one connected to Arduino A, one to Arduino B, using **two six-axis sets rotated ±10° around the CubeSat [1,1,1] diagonal**. Actual optical-axis tilt is **8.16° per face**, with **16.30° angular separation between the two axes on a face**. Prefer replaceable/removable 3D-printed wedge inserts and keep active faces unobstructed. This is an evidence-backed mechanical baseline, *not* a verified optimum for the physical GL5537-1 devices.

## Required physical acceptance test
Measure one GL5537-1 plus the intended divider/ADC with a fixed lamp at 0, 15, 30, 45, 60 and 75 degrees; measure response over multiple lamp intensities. Check whether the fitted angular response has enough direction sensitivity near the face plane. Then test at least one complete six-face printed assembly, comparing vector estimates to a known angle reference under a randomized hold-out trajectory and failures. Retain the ability to replace wedge inserts based on data. If a single-controller failure must retain quantified full-sphere accuracy, the architecture or estimator needs revision; the existing design does not establish that capability.

## External literature
- HERMES 2023: https://pmc.ncbi.nlm.nih.gov/articles/PMC10007507/ — 12 redundant photodiodes, cosine response, angular calibration.
- Nonplanar orientation optimization 2019: https://pmc.ncbi.nlm.nih.gov/articles/PMC6603595/ — geometry/conditioning and experimental verification.
- NASA 2026 SmallSat GNC overview: https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/ — cosine detector limitations, albedo, thresholds.
- Çinar & Yeniçeri 2025: https://research.itu.edu.tr/en/publications/low-cost-sun-vector-estimation-least-squares-optimization-in-poly/ — icosahedral simulations with different sensing technology.
- Senba GL5537-1 product listing: https://jlcpcb.com/partdetail/Senba_SensingTech-GL55371/C125628 — nonlinear CdS LDR, gamma ~0.6, spectral peak 540 nm.

## Reproduction
- `ae4901_validation_audit.py`: independent checking of original geometry and visibility.
- `ae4901_additional_stress.py`: gain, angular mounting error, nonlinear response scenarios.
- `ae4901_optimize_icosa_split.py`: 64 reassignment checks for icosahedron under face self-shadowing.
- `ae4901_final_checks.py`: icosa optimized split and inverse-response calibration check.
- Numerical data in CSV files and sensitivity figures inside this directory.
