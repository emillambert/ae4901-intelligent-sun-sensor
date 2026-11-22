# Sensor hardware and wiring reference

The assignment supplies 12 GL5537-1 LDRs, 12 resistors **specified only as a range of 30 kΩ–3 MΩ**, and two Arduino-equivalent development boards. It does not guarantee a complete set of 30 kΩ resistors or an Uno pinout. Identify the actual components before wiring.

## Candidate divider polarity

```text
 Arduino Vcc ── R_fixed ──┬── ADC input (A0…A5, if supported)
                          │
                         LDR
                          │
                         GND
```

The prototype source assumes `R_LDR = R_fixed × ADC / (1023 − ADC)` **only when the ADC reference is the same as the divider supply**, and when the ADC provides a 10-bit 0–1023 reading. Different Arduino boards may require a different ADC resolution/reference setting or source changes.

## Channel assignment, each board

| Analog input | CubeSat face |
|---|---|
| A0 | +X |
| A1 | −X |
| A2 | +Y |
| A3 | −Y |
| A4 | +Z |
| A5 | −Z |

Each board gets its *own* LDR per face. This is a proposed wiring contract, not a verified physical wiring diagram.

## Safety and design limits

- Don't exceed the input-voltage rating of the actual development board; verify its analog reference, pin impedance, and supply rail.
- 30 kΩ, nominal R10=25 kΩ and gamma=0.6 are **starting assumptions**, not calibration.
- 10–100 lux is the nominal manufacturer's gamma-characterization regime; don't extrapolate to direct Sun and claim calibrated measurements.
- OD3 optical attenuation is a computationally investigated option; don't install a filter for an indoor demo without confirming transmission and calibration.
- The existing Python host is not a second flight-worthy processor. Watchdog and CRC are software fault-management steps, not environmental qualification.
