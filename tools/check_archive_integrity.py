"""Verify untouched historical project archives by SHA-256."""
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
entries = list(csv.DictReader((ROOT / 'legacy/ARCHIVE_MANIFEST.csv').open(newline='')))
for entry in entries:
    content = (ROOT / entry['path']).read_bytes()
    assert len(content) == int(entry['bytes']), entry['path']
    assert hashlib.sha256(content).hexdigest() == entry['sha256'], entry['path']
print(f'OK: {len(entries)} preserved archives')
