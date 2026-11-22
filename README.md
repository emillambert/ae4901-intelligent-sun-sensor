# AE4901 — Intelligent Sun Sensor

**TU Delft embedded-systems group project** · 12 GL5537-1 LDRs · six CubeSat faces · two Arduino-equivalent controllers

> **Status: prototype software / simulated design, not hardware-validated.**
> The source files here are a consolidated candidate runtime; they are **not** a full deployment of the experimental V2–V8 simulation features. Calibration values are placeholders, the supplied Arduino models and resistor values are not yet confirmed, and the code has not been compiled/uploaded with the Arduino toolchain.

## Repository map

| Directory | What goes here | Active? |
|---|---|---|
| `runtime/firmware/SunNode/` | One sensing sketch flashed on **both** boards (`BOARD_ID=0` or `1`) | **Yes — candidate** |
| `runtime/pc/` | Host serial acquisition, calibrated Sun-vector estimate, status | **Yes — candidate** |
| `tools/` | Laboratory calibration fit and calibration transfer | **Yes — when measurements exist** |
| `tests/` | Python unit tests and mock Arduino compile support | **Yes** |
| `docs/` | Requirements, interface contract, construction, decisions, validation plan | **Yes** |
| `research/` | Curated simulations, representative results, parametric CAD, circuit reference | Reference only |
| `legacy/archives/` | **Original ten study ZIPs**, unchanged; not runtime dependencies | Historical |
| `legacy/v4-results/` | V4 results that previously existed only as loose files | Historical |

## Quick start (no hardware)

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python runtime/pc/host.py --demo
```

The demonstration uses **synthetic observations and placeholder calibration**. `valid_for_control` remains false.

## Using the two actual Arduinos

1. Confirm board model, analogue input pin count, input voltage, supplied fixed resistor values, and whether `A0`–`A5` are available.
2. Inspect the schematic and wiring notes in [`docs/hardware.md`](docs/hardware.md). No board voltage or pin assignments should be assumed from the manual alone.
3. Open `runtime/firmware/SunNode/SunNode.ino` in the Arduino IDE. Build for the **actual** board. Flash once with `BOARD_ID=0`, then with `BOARD_ID=1` (change the macro or provide it as a build option).
4. For each board, assign one LDR per +X, −X, +Y, −Y, +Z, −Z face. Connect six independent divider outputs to A0–A5, if supported.
5. Run the PC estimator with the two identified serial ports:

```bash
python runtime/pc/host.py --port-a PORT_A --port-b PORT_B --config runtime/pc/calibration_PLACEHOLDER.json
```

**Do not mark estimates qualified until physical calibration and independent angular validation are complete.**

## Documents

- [Architecture and interfaces](docs/architecture.md)
- [Course requirements and acceptance matrix](docs/requirements.md)
- [Design decisions](docs/decisions.md)
- [Hardware assumptions and wiring](docs/hardware.md)
- [Serial protocol](docs/protocol.md)
- [Validation / next steps](docs/validation.md)
- [Research archive index](docs/research-index.md)
- [Four-person collaboration guide](docs/collaboration.md)

## Source-of-truth policy

- **Edit current sensor code only in `runtime/`.**
- **Add real calibration datasets only under `data/`,** never replace the clearly labeled placeholder in-place with invented readings.
- **Treat `research/` as analysis and `legacy/` as historical evidence.** Do not import experimental algorithms into the runtime without porting and regression-testing them.
- No actual flight-qualification, accuracy, glint-rejection, power, thermal or radiation claims are established by this repository.

## GitHub

This archive includes a local Git repository and initial commit. It is **not yet uploaded to GitHub**. After creating a private, empty repository named `ae4901-intelligent-sun-sensor` on your account:

```bash
git remote add origin https://github.com/emillambert/ae4901-intelligent-sun-sensor.git
git push -u origin main
```

Only do that after confirming the GitHub account and intended repository visibility. Git author identity can be updated in your local repository configuration.
