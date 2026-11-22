# AE4901 V6 — Computational Sun Sensor Improvement Audit

**Date:** 21 November 2026  
**Assessment:** **Share with caveats**, for a student design reference—not ready for flight use.  
**Hardware measurements:** None. No validated real GL5537-1 response, solar filter characteristics, radiation/thermal performance, or compiled Arduino code.

## Executive decision

1. **Retain** the six-face, 12-LDR, two-controller V5 geometry and safety architecture.
2. **Adopt the offline known-angle angular calibration procedure** for individual LDRs and any installed optical filter. This is a plausible meaningful improvement for the student prototype, but it requires actual reference-angle measurements.
3. **For a genuine sunlight-level demonstration only, trial an optically characterized neutral-density attenuator**: optical density approximately 3, near 0.1% transmission, in a removable printed holder. With only the supplied 30 kΩ resistor, the unattenuated bright-Sun regime is outside the datasheet's 10–100 lux gamma calibration. A filter is *additional hardware*, not part of the supplied kit. Do **not** install ND filters for a dim indoor lamp without checking signal strength.
4. **Keep brightness-excess detection as a warning by default.** Strict glint rejection is only an optional mode after photometric reference stability and response have been demonstrated. A strong reflection can be physically indistinguishable from a different direct Sun direction with this hardware.
5. **Do not adopt** oversampling, a hypothetical 1 kΩ resistor swap, a rolling brightness threshold, or temporal angular-jump veto as general glint solutions. They did not provide a robust system-level improvement in the tested conditions. Polarizer-pair coding deserves a small optional physical feasibility experiment, but it does not distinguish unpolarized reflections.

## Reproducible synthetic results

| Scenario | V5 / stale / unfiltered | New candidate | Interpretation |
|---|---:|---:|---|
| Angular-response drift; p95 | 4.67° | **1.83°**, known-angle recalibration | 60.7% lower error with an independent lab reference |
| 80,000 lux extrapolated direct Sun; p95 | 10.15° | **1.69°**, OD3 filter | 83.4% lower error in assumed model; not a flight prediction |
| Severe glint; WRONG accepted | 93.49% | **1.56%**, strict 8% excess light gate | Rejects nearly everything under glint; does **not** recover correct Sun |
| Legitimate +12% solar-signal gain; CORRECT accepted | 99.72% | **8.33%** | Unacceptable availability regression |
| ND filter with modeled 5% channel transmission scatter and 0.1 angular exponent scatter; p95 | 2.85° | 0.35° after known-angle joint gain/exponent recalibration | Shows value of individually calibrating the installed filter; especially optimistic forward-model overlap |
| Typical held-out direct Sun: correct within 5° | 99.74% | No justified gain from further glint rules | Retain V5 normal estimator |

**Glint test populations differ across rows**: the V5 holdout uses four unseen seeds × four sequences × 24 frames; the +12% photometric stress uses three different seeds × four sequences × 30 frames. Never interpret those rows as a single pooled risk rate. All fractions are conditional synthetic scenario metrics, not probabilities per orbit.

### Some additional experiments

- **Oversampling:** 16, 64 or 256 nominally independent ADC conversions did not materially reduce the extrapolated bright-sun p95 error. This is consistent with systematic resistance/response-calibration error dominating, not just quantization. Averaging cannot correct an invalid sensor response model.
- **Changing to 1 kΩ:** did not solve that modeled response mismatch, and a 1 kΩ resistor is outside the specified supplied set.
- **ND filter tolerance:** independent 5% per-filter transmission and 0.10 optical-exponent perturbations increased p95 to approximately 2.85° without new calibration. Offline fitting reduced it to 0.35° in the matched synthetic model; this result should not be used to justify sub-degree accuracy on hardware.
- **Polarization:** an idealized pairwise polarizer arrangement with a 90% polarized glint reduced wrong accepted directions from approximately 73.6% to 41.1%, but failed to solve the problem and adds optics and calibration burdens. If the glint is unpolarized, the method has no discrimination advantage. This is an exploratory model only.
- **Temporal glint veto:** often misses sustained glints entirely and can confuse rapid spacecraft rotation with an optical glitch. Keep advisory only unless an independent gyro/rate constraint is available.

## Root cause: limits of scalar photometry

Under ideal linear response, the weighted sum of two sources can be equivalent to one differently oriented source for the detector's measurements, particularly when the active sensors share an unobstructed hemisphere. With no independent Earth vector, attitude reference, spectral/polarimetric discrimination or well-characterized glint geometry, a perfectly reliable software-only identity test is not identifiable in general. A brightness-amplitude bound helps detect a subset of glints when real Sun brightness and sensor gain are sufficiently stable. It cannot label all possible reflections.

## What the group can build

- **Core prototype:** V5 baseline, six-face sensor axes, calibrated per-channel angular response, conservative fault handling and explicit SUN_VALID / SUSPECT / NO_SUN telemetry.
- **Ground calibration:** rotary angle stage + known source intensity, two physically separate datasets for fit and validation. Repeat with and without any optical film. Calibration drift in flight is not automatically corrected by this test; online drift detection requires new independent information.
- **Optional solar-flux experiment:** removable neutral-density film of measured OD/transmittance in a printed clip. The parametric OpenSCAD holder is conceptual and must be dimension-checked against actual GL5537 package geometry. Use suitable material and verify spectral/angular transmission and heating.
- **Optional source-rejection experiment:** crossed polarizer film pairs, checking glare polarization effects and degraded per-board performance. Not ready for adoption.
- **For future flight operation:** avoid reflective components in each LDR's field of view; consider spacecraft-level baffles localized to known glint paths, independently estimated nadir/sun ephemeris, and sensor technologies with explicit albedo rejection. Do not claim the mock-up is flight-qualified.

## Known model limitations and critical checks

- Actual LDR response in sunlight (~30,000–120,000 lux in the artificial test) is **extrapolated far beyond the manufacturer's 10–100 lux gamma specification**. The bare high-light error figures are conditional only and not physically validated.
- ND filter transmission and attenuation are nominal; directional, spectral and temperature dependencies are hypothetical.
- The ambient/albedo model is a Lambertian simplified Earth-disk simulation, not a validated on-orbit sensor calibration.
- The glint scenarios use synthetic source geometry and assumed amplitude; actual spacecraft reflections are material- and attitude-dependent.
- Strict brightness gating must tolerate legitimate gain, solar-distance changes and calibration uncertainty; the +12% perturbation test demonstrates a major failure case.
- No additional data source was silently substituted: known ground angles are used only for **offline** recalibration, not for estimating test directions.
- `quality_layer.py` produces **display-only candidate** states, never autonomous-control authorization, by default.

## Reproduce

Requires Python 3.10+, `numpy scipy pandas matplotlib`. A self-contained subset of the original V5 computational model is included under `reference_v5/`; the V5 baseline remains unchanged.

```sh
python -m unittest discover -p 'test_v6.py' -v
python run_v6.py --part gates --dev
python run_v6.py --part gates
python run_v6.py --part drift
python run_v6.py --part solar
python run_v6.py --glint-stress
python oversampling_experiment.py
python nd_tolerance.py
python polarization_experiment.py
python make_report.py
```

## Evidence from published systems (context, not validation)

- NASA Small Spacecraft Technology State of the Art, GNC: https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/
- EIVE CubeSat on-orbit false Sun detection and threshold correction (2024): https://link.springer.com/article/10.1007/s12567-024-00559-7
- UPMSat-2 coarse Sun sensor, orbital albedo correction: https://www.mdpi.com/1424-8220/21/14/4905
- Senba GL5537-1 specification: https://www.nysenba.com/cds/5mm.html
