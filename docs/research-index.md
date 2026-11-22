# Research provenance and archive map

## Source-of-truth hierarchy

1. `runtime/`: consolidated software candidate. This is what the group should edit and test.
2. `research/`: select source, plots and documents to help interpret previous experiments; may rely on hypothetical sensor models.
3. `legacy/archives/`: ten **unchanged** historical ZIPs, containing the original full studies, tests, result tables, CAD and duplicated dependency copies. Preserve for audit, not production use.

## Research chronology

| Study | Focus | Main outcome | Original ZIP |
|---|---|---|---|
| Geometry comparison | Flat vs angled sensor axes | Candidate dual-rotated six-face arrays | `AE4901_geometry_comparison.zip` |
| Geometry audit | Face shadowing, controller failure | Recommended smaller ~8.16° face tilt | `AE4901_geometry_validation_package.zip` |
| Optical masks | Bare vs recess/shadow masks | No compelling full-sphere improvement in tested model | `AE4901_Optical_Mask_Study_and_Prototype_Kit.zip` |
| V2 | Electrical range, calibration, estimation | Calibration matters more than extra filters | `AE4901_Sun_Sensor_V2_Computational_Redesign.zip` |
| V3 | Refinement/ablation | Improved model under selected synthetic cases | `AE4901_Sun_Sensor_V3_Improvement_Validation.zip` |
| V4 | Robust estimation/faults | Selected recovery policies, with regressions | Raw V4 results under `legacy/v4-results/` |
| V5 | Earth albedo/eclipse checks | Useful eclipse and fault protection; glints remain | `AE4901_V5_Sun_Sensor_Interference_Test_Kit.zip` |
| V6 | Drift, sunlight, polarization | ND filter optional; strict brightness gate brittle | `AE4901_V6_Calibration_Bright_Sun_Glint_Study.zip` |
| V7 | Thermal response and external prior | Calibrated compensation useful; external prior not available on kit | `AE4901_V7_Residual_Risk_and_Calibration_Kit.zip` |
| V8 | Temporal glint filtering | Helps brief glints, not sustained ambiguous glints | `AE4901_V8_Residual_Limitations_and_Glint_Mitigation.zip` |
| Glint fusion | Hypothetical gyro/magnetometer aids | Simulated benefit, but needs unprovided sensors | `AE4901_Sustained_Glint_Mitigation_Study.zip` |

**Warning:** numbers reported across different study versions are NOT controlled before/after performance comparisons. They often use different LDR models, test directions, noise and rejection policies. No historical simulation p95 number is validated real-sensor performance.

`legacy/ARCHIVE_MANIFEST.csv` contains SHA256 checksums; `python tools/check_archive_integrity.py` confirms all bundle bytes are preserved.
