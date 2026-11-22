# AE4901: 12-LDR Sun Sensor — Simulation, Optical Mask Study & Prototype Kit

**Version:** 2026-11-21  
**Status:** Computational study completed; actual GL5537-1 calibration, hardware integration and printed-mask performance NOT yet measured.

## Executive result

With the chosen 6-face / 12-LDR / 2-Arduino architecture (sensor arrays rotated +/-10 degrees about CubeSat [1,1,1], optical tilt 8.1615 degrees), a broad computational study found **no robust improvement from adding 3D-printed circular or offset apertures**. A bare LDR was best under the principal simulated full-sphere conditions. Since the actual LDR angular response is unknown, this is a recommendation **not to replace the bare design without a small physical A/B test**, not a proof that passive optics cannot help.

| Test (all results SIMULATED) | Bare | Shallow 0.6-mm recess, aperture radius 3.6 mm |
|---|---:|---:|
| Ideal calibrated electrical/optical model, 80-lux source: p95 error | 0.868 deg | 1.566 deg |
| Ideal model, 80 lux: directions <= 5 deg error | 100.00% | 99.56% |
| Optical/angular/mounting mismatch, 80 lux: p95 error | 3.039 deg | 4.427 deg |
| Optical mismatch, 20 lux: p95 error | 5.089 deg | 6.563 deg |
| Ideal model, 80 lux, only Arduino A: p95 error | 2.678 deg | 9.220 deg |
| Directional stray source at 10% of primary: p95 error | 5.525 deg | 6.210 deg |
| Directional stray source at 30% of primary: p95 error | 20.852 deg | 23.612 deg |

The fault coverage and angular accuracy definition here **differs from the older full-rank least-squares simulation**. A normalized-pattern lookup uses the zero/nonzero pattern and does not require three above-threshold channels; it gives no real-world accuracy guarantee.

## What's in this package

- `optics_study.py`: reproducible mask sweep + held-out test with assumed optical and electrical response.
- `stray_light_tests.py`: directional interfering source test.
- `hybrid_tests.py`: six bare + six masked channels comparison.
- `electronics_sweep.py`: 10-bit voltage-divider sensitivity; warns about bright-light saturation.
- `results/`: numeric CSVs, plots, chosen mask configurations, reproducibility logs.
- `cad/ldr_mask_parametric.scad`: parametric printed cap and bare holder.
- `cad/tilted_mount_parametric.scad`: tilted socket (8.1615-degree axis) to fit on each CubeSat face.
- `cad/*.stl`: printable candidates; all STL meshes passed automated watertight tests. FDM clearance is NOT physically verified.
- `cad/mount_orientation_table.csv`: full six-face x two-controller optical axes, and mount rotation azimuths.
- `firmware/AE4901_dual_sun_sensor.ino`: Arduino Uno-class six-sensor starter sketch; change `BOARD_ID` and flash the two boards separately. Not hardware compiled here.
- `firmware/host_monitor.py`: dual-Arduino telemetry and vector-visualization prototype. Tested in `--demo --headless` mode.
- `calibration/`: empty CSV templates and scripts to analyze real measured sensor response, then evaluate paired physical prototypes.
- `AE4901_optics_research_report.pdf`: decision-oriented technical report.

## Reproduce

With Python 3.10+, `numpy`, `scipy`, `pandas`, and `matplotlib`:

```bash
python optics_study.py --out results
python stray_light_tests.py
python hybrid_tests.py
python electronics_sweep.py
python firmware/host_monitor.py --demo --headless --seconds 5 --log results/example_telemetry.csv
```

Real serial monitoring additionally requires `pyserial`:

```bash
pip install pyserial
python firmware/host_monitor.py --port-a /dev/cu.usbmodemXXXX --port-b /dev/cu.usbmodemYYYY
```

**The host's nominal 25-kOhm / gamma 0.6 calibration and power-law optical model are placeholders.** Do not present live angular errors as established accuracy until fitted calibration constants have been installed, the geometry checked and a separate held-out test performed.

## The electrical baseline

**For each of twelve independent channels:** +5 V -> nominal 30 kOhm fixed resistor -> ADC pin -> GL5537-1 -> ground. Use A0-A5 for each Uno-class Arduino, and assign exactly one sensor per CubeSat face to each controller. Connect both boards to independent USB ports for the bench, but note they are NOT electrically independent if their power sources are common.

The firmware uses a median of five double ADC reads per channel and reports 10-Hz telemetry. Arduino A and B independently return approximate coarse Sun vectors (axis differences, rotated to the body frame); the host reconstructs a provisional combined vector from all active channels using a normalized-response lookup. Fixed ADC thresholds and rail flags are **diagnostics, not proof of fault isolation**. Reliable fault detection requires per-sensor residuals and measured noise distributions.

The **GL5537-1 manufacturer** specifies resistance at 10 lux of 20-30 kOhm, gamma ~0.6 determined between 10 and 100 lux, and an approximately 5 mm package. This is not a linear photodiode. An illustrative extrapolation with a 30k divider gives ~3 ADC counts at 100,000 lux, so **do not assume the circuit works for direct outdoor sunlight**. Select the intended test illumination before freezing Rfixed. See `results/divider_dynamic_range.png`.

## Masks and physical build

We generated:

- Bare reference holder (same 5-mm LDR mechanical seat).
- Shallow round cap: 0.6 mm optical recess and 3.6 mm aperture radius.
- Shallow round alternative: 0.6 mm recess, 3.2 mm radius.
- Deep cap: 3.5 mm recess, 2.4 mm radius (negative control; strongly worsened simulated coverage).
- Offset cap: 1.8 mm recess, 3.2 mm radius with 0.6 mm lateral offset (experimental asymmetric variant).
- Common socket wedge tilted 8.1615 degrees.

**CAUTION:** 3D printing does not establish optical blackness, alignment accuracy, surface reflectance, dimensional tolerances, LED beam collimation or real photosensitive area. STL meshes are watertight only. Measure actual LDR body diameter, adjust `case_radius_mm`, print black opaque material, check fit, and measure alignment against reference angles. Roof may need reorientation/support settings in slicer. A baffle can reflect light internally if printed in glossy plastic.

## Essential physical measurements still required

1. Select source illumination range: laboratory LED/lamp and/or outdoor sunlight. Measure lux; do not rely on datasheet response extrapolation.
2. Assemble **one unmasked** channel with the real resistor and Arduino. Record 0 degrees / 10-100 lux / 5 repeats for R10-gamma curve. Repeat at incidence 0, 10, 20, 30, 40, 50, 60, 70, 80 degrees. Include azimuth 0, 90, 180, 270 degrees if testing offset masks.
3. Test at least three separate GL5537-1 devices for specimen-to-specimen variability. Measure dark ADC readings and spontaneous noise.
4. With unchanged sensor, lamp, mounting and divider, compare the bare holder with shallow and one deeper cap, randomizing order. Measure usable field of view and sensor response rather than only subjective brightness.
5. Calibrate all twelve channels and verify the final geometry. Use a physically measured reference 3D Sun vector and record at least 100 paired independent test poses per geometry; include varying intensity and both-controller/one-controller test cases.
6. Use templates in `calibration/` and `evaluate_physical_tests.py` for angular errors, paired differences and bootstrap uncertainty. **Hold out test orientations that were not used for calibration or design tuning.**

### Critical bench geometry caveat

A point lamp 2 m from a 10 cm mock CubeSat can cause around **1.4 degrees** ray-direction difference between its center and a sensor displaced 5 cm toward a side face; a lamp with a broad emitting surface adds further angular spread. If your accuracy target is around one degree, either use a genuinely more distant/collimated source or explicitly model each sensor's position and the lamp position. Align the rotation center with the cube center. Use a light-tight enclosure or quantify reflections.

### Pre-registered decision gate

Adopt the mask for the final design **only if** the independent physical data show all three:

- at least **20% lower held-out p95 angular error** compared with the bare reference under the same source conditions, with a confidence interval supporting improvement;
- no more than **2 percentage point** loss in the fraction of full-sphere directions with error <=5 degrees;
- no unacceptable drop in one-controller performance or low-light performance.

Otherwise retain bare holders as final hardware and present the optical-mask investigation as a negative result with physics-based explanation.

## Priorities

1. Measure real ADC transfer, mechanical axes, ambient response and LDR angular response.
2. Calibrate/fit inverse measurement model, then validate on independent orientations.
3. Implement reliable failover, status/quality flags and fault-injection tests; formal fault isolation not yet completed.
4. Print only a small mask comparison set, and test them objectively. Do not print all twelve masks before seeing data.

## Sources and provenance

- TU Delft AE4901 *Assignment Specifications and General Instructions* (2026-11-11), Assignment 3, pp. 7-8.
- Senba GL5537-1 manufacturer specifications: https://www.nysenba.com/cds/5mm.html
- HERMES 12-photodiode calibration / redundancy: https://pmc.ncbi.nlm.nih.gov/articles/PMC10007507/
- UPMSat-2 experimental response fitting: https://pmc.ncbi.nlm.nih.gov/articles/PMC8309943/
- NASA Small Spacecraft GNC, cosine vs coded/differential sensors and albedo: https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/
- Trapezoidal aperture sensor bench method: https://pmc.ncbi.nlm.nih.gov/articles/PMC13259439/

**This study is deliberately transparent about the boundary between simulation and experimental proof. No hardware was operated, no real Sun-vector validation was performed, and no actual printed cap was tested.**
