# Four-person group workflow (proposal, not an agreed assignment)

The best way to avoid duplication is to divide by technical ownership **with shared interfaces**, rather than give each person one Arduino or one CubeSat face. One feasible grouping:

- Optics + electronics: geometry implementation, LDR dividers, wiring and measured analog performance.
- Embedded acquisition + fault monitoring: both boards, SUN4 format, watchdog and controller health.
- Sun-vector estimation + calibration: response fit, direction algorithm and uncertainty/validity logic.
- Test equipment + verification software: calibration procedure, reference orientations, logging, and live UI.

**These are suggested responsibilities only.** The group should balance effort and agree formally. Everyone joins end-to-end integration and final verification.

## Git workflow

- `main`: passing, demonstrable baseline; do not commit failing prototypes.
- One feature branch per change (`firmware/adc`, `gse/plot`, `estimator/calibration`, etc.).
- Open a PR with a short change explanation and the test used to verify it.
- Merge only after CI, review and local integration when physical hardware is affected.
- Keep raw measurements out of git until everyone agrees on licensing/privacy and file sizes; add documented anonymized examples if useful.
- Commit separate electrical/mechanical/software work as small reviewable changes. Prefer `git status` and `git diff` to bulk overwrites.
