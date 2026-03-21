# EEG LSL Viewer User Manual

## Overview
The **EEG LSL Viewer** is a real-time visualization tool for EEG data. It supports streaming from LSL (Lab Streaming Layer), direct serial port connection to FreeEEG32 hardware, and CSV playback. The application provides dynamic channel mapping through YAML montage files and features integrated signal processing filters.

---

## 1. Getting Started

### Prerequisites
- Python 3.8+
- Required libraries: `brainflow`, `PyQt5`, `pyqtgraph`, `numpy`, `scipy`, `PyYAML`

### Installation
Install dependencies via pip:
```powershell
pip install brainflow PyQt5 pyqtgraph numpy scipy PyYAML
```

---

## 2. Running the Application

There are two main entry points for the viewer:

### A. Montage config.YAML-Based Viewer (Recommended)
Uses YAML montage files (e.g.,`freg9.yaml`) for flexible channel mapping and virtual channel calculations.

```powershell
python src\analysis\realtime\EEGlslviewer\src\eeg_viewer_main_yaml.py --config config\montages\freg9.yaml [options]
```
### B. Standard Viewer (Legacy/Fixed Config) [obsolete]
Uses `src/modules/config_channels.py` for channel mapping.
```powershell
python src\analysis\realtime\EEGlslviewer\src\eeg_viewer_main.py
```

### Command Line Options
| Option | Description | Example |
| :--- | :--- | :--- |
| `--lsl-stream` | Connect to a specific LSL stream name or ID. | `--lsl-stream BrainFlowEEG` |
| `--serial-port` | Connect to hardware via COM port. | `--serial-port COM3` |
| `--board-id` | BrainFlow board ID (Default: 17 for FreeEEG32). | `--board-id 17` |
| `--playback-file`| Play back a recorded CSV file. | `--playback-file data.csv` |
| `--config` | (YAML version only) Path to the montage YAML. | `--config src/modules/freg9.yaml` |

---

## 3. User Interface Guide

### Visualization Panels
1.  **Time-Series Plot (Left)**: Displays raw or filtered EEG signals in real-time. Each channel includes detailed metrics and status indicators (see *Signal Quality* section below).
2.  **Power Spectral Density (PSD) (Right Top)**: Shows the frequency distribution (1–300 Hz) in log scale.
3.  **Band Power (Right Bottom)**: Bar chart showing relative power in standard EEG bands.

---

## 3. Signal Quality & Diagnostics – In Detail

Each EEG channel displays two lines of live metrics to help you assess signal integrity.

### 🟦 Line 1: Signal Statistics

| Metric | Description | Good Range (Typical) | Interpretation |
|--------|-------------|----------------------|----------------|
| **PTP (Peak-to-Peak)** | Max - Min value over the window. Reflects amplitude. | **10–1000 μV** | Too low → flat or disconnected; too high → motion/noise artifacts. |
| **RMS (Root Mean Square)** | Power of the signal. Related to signal intensity. | **10–100 μV** | Too high → muscle noise; too low → weak contact or bad channel. |
| **DC (Offset)** | Mean signal level. | ~**0 μV** (± few μV) | High offset might suggest drift or poor connection. |
| **Flat** | % of samples with tiny variation (Δ < 3μV). | **< 0.95 (i.e., <95%)** | High flatness = flatlined channel (disconnected/shorted). |
| **Kurtosis** | Measures "spikiness" — extreme outliers. | **< 10** | High kurtosis → spike artifacts (e.g., eye blinks, muscle spikes). |
| **Skewness** | Asymmetry of the waveform. | **-2 to +2** | Very high/low → unusual or non-biological patterns. |

#### Status Tag Examples
- **OK**: All metrics in acceptable range.
- **FLAT**: Flatness > 0.95 or PTP < 10.
- **NOISY**: PTP > 1000.
- **SPIKY**: Kurtosis > 10.
- **HIGH RMS**: RMS > 100.

### 🟥 Line 2: Frequency & Spectral Quality

| Metric | Description | Good Range (Typical) | Interpretation |
|--------|-------------|----------------------|----------------|
| **LNR (Line Noise Ratio)** | Power at 50 Hz / total power. | **< 0.2** (Europe) | Higher → power line interference (electrical noise). |
| **MR (Muscle Ratio)** | Gamma / (Alpha+Beta). | **< 1.0** | Higher → excessive gamma = EMG artifact. |
| **Entropy** | Spectral entropy (flatness of spectrum). | **2.5 – 4.8** | Low = structured (e.g., EEG); high = noise/random. |

### 🧠 Band Power Levels

The bar chart visualizes relative power in these frequency ranges:

| Band | Range (Hz) | What it indicates |
|------|------------|-------------------|
| **δ (Delta)** | 1–4 Hz | Deep sleep or brain injury. |
| **θ (Theta)** | 4–8 Hz | Drowsiness, meditation. |
| **α (Alpha)** | 8–13 Hz | Relaxed wakefulness, closed eyes. |
| **β (Beta)** | 13–20 Hz | Alertness, problem-solving. |
| **h-β (High Beta)** | 20–30 Hz | Stress, tension. |
| **γ (Gamma)** | 30–60 Hz | High-level cognition, sensory binding. |
| **h-γ (High Gamma)** | 60–100 Hz | Possible EMG artifact or high attention load. |

### 🧠 Common Artifacts

| Artifact Type    | Indicators |
|------------------|-----------|
| **Loose electrode** | Flat signal (Flat > 0.95, low PTP/RMS) |
| **Muscle noise (EMG)** | High RMS, high gamma/h-gamma, high MR |
| **Power line noise** | High LNR at 50/60 Hz |
| **Eye blink / movement** | High kurtosis and skewness, transient spikes |
| **Disconnected sensor** | Flat + PTP near 0 μV |

---

### Control Panel
-   **Y Range**: Manually set the µV range or enable "Auto" scaling.
-   **PSD Y Range**: Adjust the vertical scale for the PSD plot.
-   **Channels ON/OFF**: Toggle individual channels to focus on specific signals.

---

## 4. Signal Processing & Filters

The application includes a real-time filter engine accessible via checkboxes:
-   **Detrend**: Removes linear trends from the signal (highly recommended).
-   **RTHP 1Hz**: Real-time high-pass filter to remove slow drifts.
-   **Bandpass (3–333 Hz)**: Zero-phase Butterworth filter for a clean frequency window.
-   **Notch 50+H Hz**: Removes 50Hz line noise and its harmonics (100, 150, 200, 250 Hz).
-   **Notch rt 50 Hz**: Real-time recursive notch filter for lower latency.

---

## 5. Configuration & Montages

### YAML Montage (freg9.yaml)
The YAML system allows you to define:
-   **Physical Channels**: Mapping hardware inputs to 10-20 names.
-   **Virtual Channels**: Creating new signals via weighted sums (e.g., Weighted Laplacians for S1 focus).
-   **Pick Channels**: Select which channels to display in the UI.

Example Virtual Channel Definition:
```yaml
virtual_channels:
  S1_left:
    base: C3
    weights: {FC3: 2, CP3: 2, Cz: 1, T7: 1}
    divisor: 6
```

---

## 6. Legacy Channel Configuration (config_channels.py)

If using the standard viewer (`eeg_viewer_main.py`), settings are managed in `src/modules/config_channels.py`:

1.  **Hardware Channel Selection (`EXG_CHANNELS`)**: Defines which hardware indices the application reads.
2.  **Channel Naming (`CHANNEL_MAPPING`)**: Maps hardware indices to human-readable labels (e.g., `1: "T7"`).
3.  **Virtual Differential Channel**: A single virtual channel (e.g., `"C3–C4"`) is automatically appended.

---

## 7. Troubleshooting

### Signal Issues
-   **No data appearing**: Ensure the LSL stream is active or the correct COM port is selected.
-   **"FLAT" Status**: Check electrode connectivity or impedance.
-   **"NOISY" Status**: Ensure the ground electrode is properly attached and check for nearby electronics interference.

### Application Issues
| Issue | Solution |
|-------|----------|
| GUI flashes and disappears | Ensure `app.exec_()` is called properly in main loop. |
| Blank window | Avoid overwriting the main widget inside `PlotManager`. |
| Filters don’t apply | Check if the checkbox is ticked and values are valid. |
| Axis range not updating | Click the **Apply** button after entering values. |

---

## 8. Developer Notes

- **Core Modules**:
  - `controller.py`: Initializes GUI and handles board data.
  - `lsl_board.py`: Custom wrapper for LSL streaming (bypasses BrainFlow networking limitations).
  - `plot_manager.py`: Handles plotting, PSD calculation, and real-time updates.
  - `filters.py`: Contains real-time and batch filters.
  - `ui.py`: Builds control panels.
- **Sampling Rate**: Automatically detected from LSL metadata or hardware handshake.
- **Rendering**: Updates every 250ms using `QTimer`.

