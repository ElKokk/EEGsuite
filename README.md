# F2H VBS EEG Software Suite
Modular VBS EEG platform for high-portability research.

## 🛠 Software Parts
1. **Generate & Record**: Hardware interface and data persistence.
2. **Stream LSL**: Network-based data distribution.
3. **VBS WebUI**: Control and monitor the Vibrotactile Haptics Platform (located in `vbs/webui/`). 
    - **3a (v2.3)**: [https://test.heal2.day/webui23/f2heal_webui.html](https://test.heal2.day/webui23/f2heal_webui.html)
    - **3b (v2.4)**: [https://test.heal2.day/webui24/f2heal_webui.html](https://test.heal2.day/webui24/f2heal_webui.html)
4. **VBS Firmware**: Firmware data for the stimulation device (located in `vbs/firmware/`).
5. **Analysis**:
    - **Real-Time**: High-speed LSL inlet processing.
    - **Off-Line**: Advanced post-hoc analysis on saved `.edf`/`.csv` files.

## 🚀 Setup
1. Mount Google Drive Shared Drive.
2. Set `EEG_CLOUD_ROOT` environment variable.
3. `pip install -r requirements.txt`

## 📖 Documentation
For detailed usage, configuration, and command-line arguments, see the [User Manual](docs/USER_MANUAL.md).
