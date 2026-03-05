#!/usr/bin/env python3
"""Convert VHP oscilloscope CSV captures to time-series PNG visualization.

This module provides functionality to convert comma-separated voltage and current
measurements into publication-quality time-series plots. Supports single-channel,
multi-channel, and legacy CSV formats with automatic format detection.

Typical usage:
    python src/csv_to_png.py data/raw/capture_*.csv
    python src/csv_to_png.py data/raw/capture_260301-182426_f32_v100.csv --output custom_plot.png
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.stats import linregress

RANDOM_SEED: int = 42

# Sampling rate (Hz) - nRF52 PWM interrupt at 46.875 kHz / 8 channels
SAMPLING_RATE_HZ: float = 5859.375
MS_PER_SAMPLE: float = 1000.0 / SAMPLING_RATE_HZ

# Edge detection parameters
EDGE_DETECTION_WINDOW_MS: float = 2.0  # Window size for slope calculation (ms)
EDGE_DETECTION_THRESHOLD_AMP_PER_S: float = 0.1  # Min slope (A/s) to detect rising edge
SMOOTHING_WINDOW_SAMPLES: int = 11  # Savitzky-Golay window (must be odd)
SMOOTHING_POLYORDER: int = 3  # Polynomial order for smoothing

# Plot styling
FIGURE_WIDTH_INCHES: float = 14.0
SUBPLOT_HEIGHT_INCHES: float = 4.0
LINEWIDTH_DATA: float = 0.8
LINEWIDTH_CHANNEL: float = 1.5
GRID_ALPHA: float = 0.7

# Color scheme
COLOR_VOLTAGE: str = "orange"
COLOR_CURRENT: str = "blue"
COLOR_CHANNEL: str = "green"


def filter_time_window(
    df: pd.DataFrame,
    max_time_ms: float,
) -> pd.DataFrame:
    """Filter DataFrame to include only samples within time window.

    Args:
        df: DataFrame with 'SampleIndex' column.
        max_time_ms: Maximum time window in milliseconds.

    Returns:
        Filtered DataFrame containing only samples within the time window.
    """
    if max_time_ms <= 0:
        return df

    # Calculate which sample index corresponds to max_time_ms
    max_sample_index = (max_time_ms / MS_PER_SAMPLE)
    filtered_df = df[df["SampleIndex"] <= max_sample_index].copy()
    
    return filtered_df


def detect_rising_edges_with_slope(
    current_data: np.ndarray,
    sample_indices: np.ndarray,
    min_slope_a_per_s: float = 0.0,
    debug: bool = False,
    channel_id: str = "",
) -> tuple[np.ndarray, np.ndarray]:
    """Detect rising edges and calculate full-edge slope (bottom to top).

    Identifies complete rising edges by detecting where current starts rising
    above baseline and ends when reaching plateau. Calculates average slope
    over the entire rising edge using linear regression.

    Args:
        current_data: Array of current values (A).
        sample_indices: Array of sample indices corresponding to current_data.
        min_slope_a_per_s: Minimum slope magnitude (A/s) to report. Default=0.
        debug: If True, print detailed edge detection info.
        channel_id: Channel identifier for debug output.

    Returns:
        Tuple of (edge_sample_indices, edge_slopes_A_per_s).
    """
    if len(current_data) < SMOOTHING_WINDOW_SAMPLES:
        return np.array([]), np.array([])

    # Smooth current while preserving edge sharpness
    try:
        smooth_current = savgol_filter(
            current_data,
            window_length=SMOOTHING_WINDOW_SAMPLES,
            polyorder=SMOOTHING_POLYORDER,
            mode="nearest",
        )
    except ValueError:
        return np.array([]), np.array([])

    # Calculate derivative (dI/dt) using central differences
    time_seconds = sample_indices / SAMPLING_RATE_HZ
    derivative = np.gradient(smooth_current, time_seconds)  # dI/dt in A/s

    # Detect peaks in derivative (where dI/dt is highest)
    edges = np.where(derivative > EDGE_DETECTION_THRESHOLD_AMP_PER_S)[0]

    if len(edges) == 0:
        return np.array([]), np.array([])

    # Group consecutive derivative peaks to identify distinct edges
    edge_groups = []
    current_group = [edges[0]]
    for edge in edges[1:]:
        if edge - current_group[-1] <= SAMPLING_RATE_HZ * 0.001:  # ~1ms spacing
            current_group.append(edge)
        else:
            edge_groups.append(current_group)
            current_group = [edge]
    edge_groups.append(current_group)

    # For each edge group, find the full edge extent (from start to end)
    edge_centers = []
    full_edge_slopes = []

    for group_idx, group in enumerate(edge_groups):
        # Peak of derivative is center of group
        peak_idx = group[len(group) // 2]

        # Trace backwards from peak to find edge start (where dI/dt becomes positive)
        start_idx = peak_idx
        for i in range(peak_idx - 1, max(0, peak_idx - int(SAMPLING_RATE_HZ * 0.01)), -1):
            if derivative[i] > EDGE_DETECTION_THRESHOLD_AMP_PER_S * 0.5:
                start_idx = i
            else:
                break

        # Trace forwards from peak to find edge end (where dI/dt drops significantly)
        end_idx = peak_idx
        for i in range(peak_idx + 1, min(len(derivative), peak_idx + int(SAMPLING_RATE_HZ * 0.01))):
            if derivative[i] > EDGE_DETECTION_THRESHOLD_AMP_PER_S * 0.5:
                end_idx = i
            else:
                break

        # Ensure we have a valid edge region
        if end_idx <= start_idx:
            end_idx = min(start_idx + int(SAMPLING_RATE_HZ * 0.002), len(smooth_current) - 1)

        # Calculate full-edge slope using linear regression over entire edge
        edge_time = time_seconds[start_idx:end_idx + 1]
        edge_current = smooth_current[start_idx:end_idx + 1]

        if len(edge_time) >= 2:
            slope_result = linregress(edge_time, edge_current)
            full_edge_slopes.append(slope_result.slope)  # ΔI/Δt over full edge
            edge_centers.append(peak_idx)

            if debug:
                time_start_ms = edge_time[0] * 1000
                time_end_ms = edge_time[-1] * 1000
                duration_ms = (edge_time[-1] - edge_time[0]) * 1000
                i_start = edge_current[0]
                i_end = edge_current[-1]
                expected_slope = (i_end - i_start) / (edge_time[-1] - edge_time[0])
                print(f"\n{channel_id} Edge #{group_idx}:")
                print(f"  Time: {time_start_ms:.2f}ms → {time_end_ms:.2f}ms (Δt={duration_ms:.2f}ms)")
                print(f"  Current: {i_start:.6f}A → {i_end:.6f}A (ΔI={i_end-i_start:.6f}A)")
                print(f"  Slope: {slope_result.slope:.4f} A/s (R²={slope_result.rvalue**2:.4f})")
                print(f"  Edge region: idx[{start_idx}:{end_idx}], {len(edge_time)} samples")
        else:
            full_edge_slopes.append(0.0)
            edge_centers.append(peak_idx)

    # Filter by minimum slope magnitude if specified
    edge_centers = np.array(edge_centers)
    full_edge_slopes = np.array(full_edge_slopes)

    if min_slope_a_per_s > 0:
        mask = np.abs(full_edge_slopes) >= min_slope_a_per_s
        edge_centers = edge_centers[mask]
        full_edge_slopes = full_edge_slopes[mask]

    return np.array(edge_centers, dtype=int), np.array(full_edge_slopes)


def filter_time_window(
    df: pd.DataFrame,
    max_time_ms: float,
) -> pd.DataFrame:
    """Filter DataFrame to include only samples within time window.

    Args:
        df: DataFrame with 'SampleIndex' column.
        max_time_ms: Maximum time window in milliseconds.

    Returns:
        Filtered DataFrame containing only samples within the time window.
    """
    if max_time_ms <= 0:
        return df

    # Calculate which sample index corresponds to max_time_ms
    max_sample_index = (max_time_ms / MS_PER_SAMPLE)
    filtered_df = df[df["SampleIndex"] <= max_sample_index].copy()
    
    return filtered_df


def read_csv_file(csv_path: Path) -> tuple[pd.DataFrame, bool]:
    """Read CSV capture file and detect format.

    Automatically detects header row and handles legacy/new formats.

    Args:
        csv_path: Path to CSV file.

    Returns:
        Tuple of (DataFrame, has_active_channel_flag).

    Raises:
        FileNotFoundError: If CSV file does not exist.
        ValueError: If CSV format is unrecognized.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    header_row = None
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if "SampleIndex,Voltage(V),Current(A),ActiveChannel" in line:
                header_row = i
                return pd.read_csv(csv_path, header=header_row, on_bad_lines="skip"), True
            elif "SampleIndex,Voltage(V),Current(A)" in line:
                header_row = i
                return pd.read_csv(csv_path, header=header_row, on_bad_lines="skip"), False
            elif "SampleIndex,Current(A)" in line:
                header_row = i
                return pd.read_csv(csv_path, header=header_row, on_bad_lines="skip"), False

    raise ValueError(f"Unrecognized CSV format in {csv_path}")


def create_time_series_plot(
    df: pd.DataFrame,
    has_active_channel: bool,
    output_path: Path,
    min_slope_a_per_s: float = 0.0,
    debug_edges: bool = False,
) -> None:
    """Create and save sequential time-series visualization.

    For multi-channel data: Creates separate voltage+current panels for each channel,
    stacked vertically (sequential visualization).

    For single-channel data: Creates 2-panel plot (Voltage, Current).

    Args:
        df: DataFrame with 'SampleIndex', 'Voltage(V)', 'Current(A)', and optionally 'ActiveChannel'.
        has_active_channel: Whether DataFrame includes ActiveChannel column.
        output_path: Path to save PNG output.
        min_slope_a_per_s: Minimum slope magnitude (A/s) to display. Default=0 (show all).
        debug_edges: If True, print detailed edge detection info.

    Raises:
        ValueError: If required columns are missing.
    """
    # Validate required columns
    required_cols = ["SampleIndex", "Voltage(V)", "Current(A)"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Missing required columns. Found: {list(df.columns)}")

    # Filter to numeric data
    df = df[pd.to_numeric(df["SampleIndex"], errors="coerce").notnull()].copy()
    df["SampleIndex"] = df["SampleIndex"].astype(int)

    # Add time column (milliseconds)
    df["Time(ms)"] = df["SampleIndex"] * MS_PER_SAMPLE

    # Multi-channel sequential layout
    if has_active_channel and "ActiveChannel" in df.columns:
        channels = sorted(df["ActiveChannel"].unique())
        n_channels = len(channels)
        n_plots = n_channels * 2  # 2 subplots per channel (voltage + current)

        fig = plt.figure(figsize=(FIGURE_WIDTH_INCHES, SUBPLOT_HEIGHT_INCHES * n_channels))

        for idx, channel in enumerate(channels):
            ch_data = df[df["ActiveChannel"] == channel].copy()

            # Re-index time relative to channel start
            ch_data["Time_Relative(ms)"] = (
                ch_data["SampleIndex"].values - ch_data["SampleIndex"].min()
            ) * MS_PER_SAMPLE

            # Voltage subplot
            ax_v = plt.subplot(n_channels, 2, idx * 2 + 1)
            ax_v.plot(
                ch_data["Time_Relative(ms)"],
                ch_data["Voltage(V)"],
                label=f"Ch {channel} Voltage",
                color=COLOR_VOLTAGE,
                linewidth=LINEWIDTH_DATA,
            )
            ax_v.set_ylabel("Voltage (V)")
            ax_v.set_title(f"Channel {channel}: Voltage")
            ax_v.grid(True, which="both", linestyle="--", alpha=GRID_ALPHA)
            ax_v.legend(loc="upper right")

            # Current subplot
            ax_i = plt.subplot(n_channels, 2, idx * 2 + 2)
            ax_i.plot(
                ch_data["Time_Relative(ms)"],
                ch_data["Current(A)"],
                label=f"Ch {channel} Current",
                color=COLOR_CURRENT,
                linewidth=LINEWIDTH_DATA,
            )
            
            # Detect rising edges and annotate slopes
            try:
                current_array = ch_data["Current(A)"].values
                sample_indices = ch_data["SampleIndex"].values - ch_data["SampleIndex"].min()
                edge_indices, slopes = detect_rising_edges_with_slope(
                    current_array, sample_indices, min_slope_a_per_s,
                    debug=debug_edges, channel_id=f"CH_WEBUI_{channel}"
                )
                
                if len(edge_indices) > 0:
                    edge_times_ms = edge_indices * MS_PER_SAMPLE
                    edge_currents = current_array[edge_indices]
                    
                    # Plot edge markers and annotate slopes
                    ax_i.scatter(
                        edge_times_ms,
                        edge_currents,
                        color="red",
                        s=50,
                        zorder=5,
                        label="Rising Edges",
                    )
                    
                    # Annotate each edge with its slope
                    for time_ms, current, slope in zip(edge_times_ms, edge_currents, slopes):
                        slope_str = f"{slope:.2f} A/s"
                        ax_i.annotate(
                            slope_str,
                            xy=(time_ms, current),
                            xytext=(5, 5),
                            textcoords="offset points",
                            fontsize=8,
                            color="red",
                            bbox=dict(
                                boxstyle="round,pad=0.3",
                                facecolor="yellow",
                                alpha=0.7,
                            ),
                        )
            except Exception as e:
                print(f"  Warning: Could not detect edges for channel {channel}: {e}")
            
            ax_i.set_ylabel("Current (Amps)")
            ax_i.set_title(f"Channel {channel}: Current")
            ax_i.grid(True, which="both", linestyle="--", alpha=GRID_ALPHA)
            ax_i.legend(loc="upper right")

            # Add X-label only to bottom row
            if idx == n_channels - 1:
                ax_v.set_xlabel("Time (ms)")
                ax_i.set_xlabel("Time (ms)")

    # Single-channel layout
    else:
        n_plots = 2
        fig = plt.figure(figsize=(FIGURE_WIDTH_INCHES, SUBPLOT_HEIGHT_INCHES * n_plots))

        # Voltage subplot
        ax_voltage = plt.subplot(2, 1, 1)
        ax_voltage.plot(
            df["Time(ms)"],
            df["Voltage(V)"],
            label="Voltage (V)",
            color=COLOR_VOLTAGE,
            linewidth=LINEWIDTH_DATA,
        )
        ax_voltage.set_title("VHP Oscilloscope: Voltage Time Series")
        ax_voltage.set_ylabel("Voltage (V)")
        ax_voltage.grid(True, which="both", linestyle="--", alpha=GRID_ALPHA)
        ax_voltage.legend()

        # Add secondary X-axis (Sample Index)
        ax_voltage_top = ax_voltage.secondary_xaxis(
            "top",
            functions=(
                lambda x: x / MS_PER_SAMPLE,
                lambda x: x * MS_PER_SAMPLE,
            ),
        )
        ax_voltage_top.set_xlabel("Sample Index")

        # Current subplot
        ax_current = plt.subplot(2, 1, 2, sharex=ax_voltage)
        ax_current.plot(
            df["Time(ms)"],
            df["Current(A)"],
            label="Current (A)",
            color=COLOR_CURRENT,
            linewidth=LINEWIDTH_DATA,
        )
        
        # Detect rising edges and annotate slopes
        try:
            current_array = df["Current(A)"].values
            sample_indices = df["SampleIndex"].values
            edge_indices, slopes = detect_rising_edges_with_slope(
                current_array, sample_indices, min_slope_a_per_s,
                debug=debug_edges, channel_id="Single-Channel"
            )
            
            if len(edge_indices) > 0:
                edge_times_ms = df["Time(ms)"].values[edge_indices]
                edge_currents = current_array[edge_indices]
                
                # Plot edge markers and annotate slopes
                ax_current.scatter(
                    edge_times_ms,
                    edge_currents,
                    color="red",
                    s=50,
                    zorder=5,
                    label="Rising Edges",
                )
                
                # Annotate each edge with its slope
                for time_ms, current, slope in zip(edge_times_ms, edge_currents, slopes):
                    slope_str = f"{slope:.2f} A/s"
                    ax_current.annotate(
                        slope_str,
                        xy=(time_ms, current),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=8,
                        color="red",
                        bbox=dict(
                            boxstyle="round,pad=0.3",
                            facecolor="yellow",
                            alpha=0.7,
                        ),
                    )
        except Exception as e:
            print(f"  Warning: Could not detect edges: {e}")
        
        ax_current.set_title("VHP Oscilloscope: Current Time Series")
        ax_current.set_ylabel("Current (Amps)")
        ax_current.set_xlabel("Time (ms)")
        ax_current.grid(True, which="both", linestyle="--", alpha=GRID_ALPHA)
        ax_current.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"✓ Plot saved: {output_path}")


def main(argv: list[str] | None = None) -> int:
    """Main entry point for CSV to PNG conversion.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 = success, 1 = error).
    """
    parser = argparse.ArgumentParser(
        description="Convert VHP CSV captures to time-series PNG plots."
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        type=Path,
        help="CSV file(s) to convert (supports wildcards).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output PNG path (default: input_file.png).",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        default=100.0,
        help="Maximum time window in milliseconds (default: 100 ms).",
    )
    parser.add_argument(
        "--min-slope",
        type=float,
        default=0.0,
        help="Minimum slope magnitude (A/s) to display (default: 0.0, show all edges).",
    )
    parser.add_argument(
        "--debug-edges",
        action="store_true",
        help="Print detailed edge detection info for debugging.",
    )

    args = parser.parse_args(argv)

    # Handle file expansion
    csv_files = []
    for pattern in args.csv_files:
        if "*" in str(pattern):
            expanded = list(Path(".").glob(str(pattern)))
            csv_files.extend(expanded)
        else:
            csv_files.append(pattern)

    if not csv_files:
        print("Error: No CSV files found.", file=sys.stderr)
        return 1

    try:
        for csv_path in csv_files:
            # Determine output path
            if args.output and len(csv_files) == 1:
                output_path = args.output
            else:
                output_path = csv_path.with_suffix(".png")

            # Read and validate
            print(f"Processing: {csv_path}")
            df, has_active_channel = read_csv_file(csv_path)
            
            # Filter to time window
            df = filter_time_window(df, args.max_time)
            print(f"  Time window: 0 - {args.max_time} ms")
            print(f"  Min slope filter: {args.min_slope} A/s")

            # Print summary
            print(f"  Samples: {len(df)}")
            print(
                f"  Duration: {(df['SampleIndex'].max() * MS_PER_SAMPLE) / 1000:.3f} sec"
            )
            print(f"  Channels: {df['ActiveChannel'].nunique() if has_active_channel else 1}")
            print(f"  Mean voltage: {df['Voltage(V)'].mean():.4f} V")
            print(f"  Mean current: {df['Current(A)'].mean():.6f} A")

            # Generate plot
            create_time_series_plot(df, has_active_channel, output_path, args.min_slope, args.debug_edges)

        return 0

    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
