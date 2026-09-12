"""Validate and summarize CSV samples emitted by the AVR UART logger."""
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


def summarize(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or "adc" not in rows[0]:
        raise ValueError("expected a CSV file with an adc column")
    samples = [int(row["adc"]) for row in rows]
    if any(not 0 <= sample <= 1023 for sample in samples):
        raise ValueError("ADC samples must be in the 10-bit range 0..1023")
    print(f"samples : {len(samples)}")
    print(f"mean    : {statistics.fmean(samples):.2f}")
    print(f"min/max : {min(samples)} / {max(samples)}")
    print(f"stdev   : {statistics.stdev(samples):.2f}" if len(samples) > 1 else "stdev   : n/a")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    summarize(parser.parse_args().csv_file)
