# Calibration and validation data

Store physical calibration measurements here after acquisition. `raw/` and `processed/` are ignored by Git until the group decides which datasets should be version-controlled.

The calibration tool requires `sensor_id,lux,angle_deg,temp_c,adc,vref_v,vcc_v,rfixed_ohm,split` columns. Never relabel generated/synthetic examples as experimental results. Keep distinct training and held-out test angles.
