"""Validate and summarize ``ADC=123`` samples emitted by the AVR logger."""
from __future__ import annotations

import argparse
import statistics
from pathlib import Path


def summarize(path: Path) -> None:
    samples: list[int] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("ADC="):
            continue
        try:
            samples.append(int(line.removeprefix("ADC=")))
        except ValueError as error:
            raise ValueError(f"invalid ADC sample on line {line_number}") from error
    if not samples:
        raise ValueError("expected at least one ADC=123 sample line")
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
