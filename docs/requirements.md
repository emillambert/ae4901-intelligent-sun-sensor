# AE4901 requirements and acceptance matrix

Derived from the supplied **AE4901 Embedded Systems Practical Manual (11 November 2026), Assignment 3**. The PDF is retained in `docs/reference/` for exact wording.

| Assignment requirement | Implementation plan | Evidence needed | Current status |
|---|---|---|---|
| Incidence angles on at least 3 cuboid faces | 12 LDRs on six faces | Physical angular-response tests at known directions | Designed, not verified |
| Determine Sun vector in local reference frame | Calibrated host estimator; local coarse MCU vector | Measured true-direction versus estimated-direction tests | Synthetic test only |
| Visualize Sun vector on UI | Current host prints vector/status JSON | Live 3D UI demo with both Arduinos | 3D UI not integrated |
| Distinguish noise with a threshold | Threshold, rail checks, fit residuals | Dark, low-light, and false-valid tests | Python reference only |
| Failure-tolerant design | Two six-sensor controllers, CRC, watchdog, stale board detection | Disconnect/short LDR, kill controller, corrupt packets, report recovery | Partial simulation/mock tests |

**Targets proposed by the group, not official manual requirements:** aim for ≤5° p95 angular error under nominal illumination; report accuracy and acceptance rate together; controller degraded behavior and false-valid rates measured separately. These are provisional until agreed by the group.

The manual assesses requirements 20%, engineering approach 20%, usability 20%, creativity 15%, presentation 15%, project management 10%. A working, measured prototype matters more than accumulating unvalidated algorithms.
