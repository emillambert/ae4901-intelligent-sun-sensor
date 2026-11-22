# Prototype serial telemetry — SUN4

One ASCII line per Arduino every ~100 ms at 115200 baud.

```text
SUN4,<board_id>,<sequence>,<millis>,<adc0>,<adc1>,<adc2>,<adc3>,<adc4>,<adc5>,<vx10000>,<vy10000>,<vz10000>,<rail_mask>,<ready>*<CRC16_HEX>

```

- `board_id`: `0` or `1`
- `sequence`: increasing integer (resets on reboot)
- `millis`: board-local elapsed milliseconds
- ADC values: 0–1023 in current ten-bit candidate firmware
- `v*10000`: coarse board-local components scaled ×10,000, **not calibrated results**
- `rail_mask`: bit i set when channel i is close to a rail
- `ready`: always `0` with placeholder calibration; only mark true after physical checks
- CRC16: CCITT-FALSE style initialization `0xFFFF`, polynomial `0x1021`, applied to the ASCII payload before `*`.

**Known limitations**: protocol has no explicit version negotiation or payload length; `host.py` accepts reset/out-of-order sequences in a limited way; tests don't cover rollover, partial frames, reconnections and corrupted synchronization under real serial conditions. These need hardware-in-the-loop tests.
