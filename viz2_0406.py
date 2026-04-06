#!/usr/bin/env python3
import argparse
from pathlib import Path

import mne
import numpy as np
import pandas as pd
import yaml

MARKER_MAP: dict[float, str] = {
    # New condition-aware markers
    100.0: "FOT_Rest [100]",
    101.0: "FOT_Stim_ON [101]",
    111.0: "FOT_Stim_OFF [111]",
    200.0: "IFNFN_Rest [200]",
    201.0: "IFNFN_Stim_ON [201]",
    211.0: "IFNFN_Stim_OFF [211]",
    # Legacy markers (single-condition recordings)
    0.0: "Stimulation READY [0]",
    1.0: "Stimulation ON [1]",
    11.0: "Stimulation OFF [11]",
    3.0: "Baseline_VHP_OFF [3]",
    33.0: "Baseline_VHP_ON [33]",
    31.0: "Baseline_NoContact [31]",
    333.0: "Baseline_PreSweep [333]",
}


def read_yaml_config(args):
    """Read YAML and return as config object"""
    if args.verbose:
        print(f"* Reading config from {args.config}")

    with open(args.config, encoding="utf8") as file:
        config = yaml.safe_load(file)
    return config


def parse_args():
    """Parse cmdline, read config and return as args,config objects"""
    parser = argparse.ArgumentParser(
        description="Convert 06-04 measurements to MNE RAW"
    )

    parser.add_argument("-f", "--file", type=str, required=True, help="Input file path")
    parser.add_argument(
        "-c", "--config", type=str, required=True, help="Configuration file path"
    )
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="output directory"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    config = read_yaml_config(args)

    return args, config


def mne_from_brainflow(args, config):
    """Read Brainflow CSV and return as MNE Raw object"""
    if args.verbose:
        print(f"* Reading Brainflow CSV from {args.file}")

    csv_file = args.file
    data_in = pd.read_csv(csv_file, header=None).values.T

    # Convert from brainflow (V) to MNE (uV)
    timestamps = data_in[0]

    data = data_in[1 : len(config["channels"]) + 1] * 1e-6
    markers = data_in[len(config["channels"]) + 1]

    ch_types = ["eeg"] * len(config["channels"])  # Assuming all are EEG channels
    sfreq = 512
    info = mne.create_info(
        ch_names=config["channels"],
        sfreq=sfreq,
        ch_types=ch_types,
        verbose=args.verbose,
    )

    raw = mne.io.RawArray(data, info, verbose=args.verbose)

    raw.set_montage(config["montage"], on_missing="ignore", verbose=args.verbose)
    raw.pick(config["pick_channels"])

    # Build annotations from marker column
    valid_mask = pd.to_numeric(pd.Series(markers), errors="coerce").notna()
    marker_vals = pd.to_numeric(pd.Series(markers), errors="coerce").values

    if np.any(valid_mask):
        idxs = np.where(valid_mask)[0]
        onsets = timestamps[idxs] - timestamps[0]
        descriptions = [
            MARKER_MAP.get(float(marker_vals[i]), f"Event_{int(marker_vals[i])}")
            for i in idxs
        ]
        annots = mne.Annotations(
            onset=onsets,
            duration=[0.01] * len(onsets),
            description=descriptions,
        )
        raw.set_annotations(annots)
        print(f"loaded {len(annots)} annotations")
    else:
        print("No markers found!!!")

    return raw


def write_raw(args, raw):
    filename = Path(args.file).stem + "_eeg.fif.gz"
    output_path = Path(args.output) / filename

    raw.save(output_path)


def main():
    """Main actions"""

    args, config = parse_args()

    raw = mne_from_brainflow(args, config)
    write_raw(args, raw)


if __name__ == "__main__":
    main()
