# 🛡️ Firewall Configuration for Lab Streaming Layer (LSL)

This guide provides the necessary steps to configure the Firewall (Windows 11 or Linux) to allow seamless EEG data streaming via the **Lab Streaming Layer (LSL)** protocol.

---

## 📖 Introduction

LSL relies on **UDP Multicast** for stream discovery and **TCP/UDP** for data transmission. By default, many security policies block these communications.

## 🏗️ Terminology

*   **Acquisition Node (Outlet)**: The computer physically connected to the EEG hardware (e.g., FreeEEG32). It broadcasts the data stream.
*   **Visualization/Analysis Node (Inlet)**: The computer(s) receiving the data for real-time monitoring or recording.

---

## ⚙️ Windows 11 Configuration

### 1. Set Network Profile to "Private"
Windows blocks LSL discovery on "Public" networks. Ensure your connection is set to **Private**.

1.  Open **Settings** > **Network & internet**.
2.  Select your active connection (**Ethernet** or **Wi-Fi**).
3.  Change **Network profile type** to **Private**.

### 2. Configure Firewall Port Exceptions
LSL requires specific ports to be open on **both** the Acquisition and Visualization nodes.

*   **UDP Port 16571**: Required for stream discovery.
*   **TCP & UDP Ports 16572–16604**: Required for data transmission.

#### ⌨️ Automated Setup (Recommended)
Run the following command in an **Administrative PowerShell** terminal to automatically create the necessary firewall rules:

```powershell
# Create inbound rule for LSL Discovery
New-NetFirewallRule -DisplayName "LSL Discovery (UDP-In)" -Direction Inbound -LocalPort 16571 -Protocol UDP -Action Allow

# Create inbound rule for LSL Data
New-NetFirewallRule -DisplayName "LSL Data (TCP/UDP-In)" -Direction Inbound -LocalPort 16572-16604 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "LSL Data (TCP/UDP-In)" -Direction Inbound -LocalPort 16572-16604 -Protocol UDP -Action Allow
```

---

## ⚙️ Linux Configuration (UFW)

If you use `ufw` (Uncomplicated Firewall) on Linux (e.g., Ubuntu), run the following:

```bash
# Allow LSL Discovery
sudo ufw allow 16571/udp

# Allow LSL Data (TCP & UDP)
sudo ufw allow 16572:16604/tcp
sudo ufw allow 16572:16604/udp
```

---

## 🧪 Connection Verification

To verify that the network is correctly configured, use the following diagnostic scripts.

### 1. Acquisition Test (Outlet)
Run this script on the **Acquisition Node** to broadcast a synthetic EEG stream.

```python
import logging
import time
from pylsl import StreamInfo, StreamOutlet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

RANDOM_SEED: int = 42

def broadcast_test_stream() -> None:
    """Broadcasts a synthetic 8-channel EEG stream at 100Hz."""
    info = StreamInfo('TestStream', 'EEG', 8, 100, 'float32', 'diagnostic_uid_123')
    outlet = StreamOutlet(info)

    logger.info("Broadcasting 'TestStream'... Press Ctrl+C to stop.")
    
    try:
        while True:
            # Synthetic 8-channel sample
            sample = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
            outlet.push_sample(sample)
            time.sleep(0.01)
    except KeyboardInterrupt:
        logger.info("Broadcast stopped by user.")

if __name__ == "__main__":
    broadcast_test_stream()
```

### 2. Visualization Test (Inlet)
Run this script on the **Visualization Node**. If it fails to find the stream, the firewall is likely still blocking UDP 16571.

```python
import logging
from pylsl import resolve_stream, StreamInlet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def receive_test_stream() -> None:
    """Attempts to resolve and receive data from an EEG stream."""
    logger.info("Looking for EEG streams on the network...")
    
    streams = resolve_stream('type', 'EEG')
    
    if not streams:
        logger.error("No EEG streams found. Check firewall settings.")
        return

    inlet = StreamInlet(streams[0])
    logger.info("Stream found! Receiving data...")

    try:
        while True:
            sample, timestamp = inlet.pull_sample()
            logger.info("Timestamp: %f, Sample: %s", timestamp, sample)
    except KeyboardInterrupt:
        logger.info("Reception stopped by user.")

if __name__ == "__main__":
    receive_test_stream()
```

---

## 🛠️ Advanced Troubleshooting

### Static IP Resolution (`lsl_api.cfg`)
If the nodes are on different subnets or multicast discovery is unreliable, you can force LSL to look at a specific IP address.

1.  Create a file named `lsl_api.cfg` in your user home folder (e.g., `C:\Users\YourName\lsl_api.cfg`).
2.  Add the following configuration (replace `192.168.1.XX` with the Acquisition PC's IP):

```ini
[multicast]
Addresses={192.168.1.XX}
```
