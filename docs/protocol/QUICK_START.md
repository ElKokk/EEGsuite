# 🧪 Experiment Procedure & Quick Start

This guide provides a step-by-step walkthrough for preparing, running, and analyzing EEG measurements within the **EEGsuite** ecosystem.

---

## 1. Preparation
1.  **Open Workspace**:
    *   VS Code: Open `D:\F2H_code\GH\EEGsuite`
    *   File Explorer: Open data folder `G:\My Drive\SharedData\` (if using cloud sync)

2.  **Hardware Connection**:
    *   Connect the **FreeEEG32** board to the 'EEG Acquisition PC' (LSL StreamOutlet Server).
    *   Connect the **VHP Stimulator** (VBS) to the 'Control PC' (Master: Sweep control, EEG, and event recording).
    *   Set up the **EEG Visualization PC** (Real-time Monitor) to receive and display EEG data for signal quality assessment.
    *   *Note: These roles can be performed by the same PC or separate machines on the same local network.*

3.  **Verify COM Ports**:
    *   Open Windows Device Manager (`devmgmt.msc`) on both the 'EEG Acquisition PC' and the 'Control PC'.
    *   Note the COM port for the EEG board (e.g., `COM3`).
    *   Note the COM port for the VHP Stimulator (e.g., `COM5`).
  
    *   #method for linux:
    *   in terminal: sudo dmesg | tail
    *      

4.  **Configuration**:
    *   Edit `.\config\hardware\freeeeg.yaml`.
    *   Update `Board: Serial` and `VHP: Serial` to match your noted COM ports.

## 2. Start LSL Stream (Acquisition Node)
Run this on the PC connected to the EEG board.

```powershell
python -m src.main server -c .\config\hardware\freeeeg.yaml
```
*   **Verify**: Wait for the message `* LSL stream 'BrainFlowEEG' is now active`.

## 3. Start Real-time Monitor (Visualization Node)
Run this on the 'EEG Visualization PC' to monitor signal quality.

```powershell
python eeg_viewer_main.py
```
*   **Default**: Connects to the "BrainFlowEEG" LSL stream. 
*   **Custom**: To specify a different stream name, use: `python eeg_viewer_main.py --lsl-stream "YourStreamName"`


## 4. Run Experiment (Control Node)
Run this on the PC connected to the VHP Stimulator.

```powershell
python -m src.main sweep -d .\config\hardware\freeeeg.yaml -p .\config\protocols\sweep_default.yaml
```
*   **Procedure**: Follow the on-screen prompts (e.g., "Press SPACEBAR when ready").
*   **Output**: Data is automatically saved to `data/raw/` (or your configured cloud path).

## 5. Analyze Data (Post-Processing)
Generate HTML reports and plots from the recorded CSV files.

```powershell
# Example: Analyze a specific file from start (0s) to 60s
python -m src.main analyze -f "G:\My Drive\SharedData\data\raw\YOUR_FILE_NAME.csv" -s 0 -d 60
```
*   **Result**: Check the `reports/` folder for the generated `.html` analysis file.
*   **Customization**: Edit `config\analysis\default_offline.yaml` to change channel names, montage, or filter frequencies.
*   **Montage Switching**: To change electrode layouts (e.g., from 32-channel to 8-channel), change the `montage_profile` in `config\analysis\default_offline.yaml`.
    *   `kullab`: Standard 32-channel layout.
    *   `freg8`: Sparse 8-channel motor layout.
*   **Channel Picking**: You can manually override which channels appear in the report by editing the `pick_channels` list in `config\analysis\default_offline.yaml`.
    *   If `pick_channels` is defined in the main YAML, it takes priority over the montage profile's defaults.
    *   This affects all plots: Timeseries, Spectrograms, PSD, and ERPs.
