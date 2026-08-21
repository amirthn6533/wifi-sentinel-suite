# ⚡ Wi-Fi Cyber Suite | Advanced RF Sensing & Security Audit

A high-performance Wi-Fi surveillance, security audit, 360° radar, spectrum analyzer, and **camera-less human motion detector** optimized for Realtek RTL8811AU (TP-Link High-Gain USB Antenna).

---

## 🚀 Quick Launch (Master Command Center):
Double-click **`RUN_WIFI_SUITE.bat`** to open the Master Hub, or run individual tools:

| Executable File | Application | Description |
|---|---|---|
| **`RUN_WIFI_SUITE.bat`** | ⚡ **Master Command Center (`hub.py`)** | Central dashboard to launch either tool with 1 click |
| **`run_motion_sensor.bat`** | 🚨 **Wi-Fi Motion Sentinel (`wifi_motion_sensor.py`)** | RF wave seismograph, 5s noise calibration, burglar alarm |
| **`run_radar.bat`** | 📡 **Wi-Fi Radar & Security (`wifi_radar.py`)** | 360° radar, spectrum analyzer, Evil Twin detection, vendor OUI |

---

## ✨ Key Features:

### 1. 🚨 Wi-Fi Motion Sentinel (`wifi_motion_sensor.py`)
- **Real-Time RF Seismograph (40 FPS Custom Canvas):** Plots ultra-smooth RF perturbations caused by human body movement.
- **Segmented LED Energy Gauge (0-100%):** Color-shifting LED bar (Green ➔ Amber ➔ Red) for real-time perturbation intensity.
- **360° Sonar Pulse Radar:** Pulsing sonar sweep with shockwave rings on motion discovery.
- **5s Baseline Noise Calibration:** Profiles the quiescent environment for zero false alarms.
- **Armed Burglar Alarm:** Arm countdown with audio cyber siren alerts (`winsound`).
- **Antenna Selector:** Easily switch between the high-gain external TP-Link antenna and internal Wi-Fi adapters.

### 2. 📡 Wi-Fi Radar & Security Audit (`wifi_radar.py`)
- **360° Dynamic Radar:** Visualizes surrounding APs based on distance (signal strength) and Wi-Fi channel.
- **Evil Twin & Rogue AP Detector:** Detects duplicate SSIDs with conflicting encryption schemes (phishing/honeypots) or mismatched hardware vendors.
- **MAC OUI Vendor Lookup:** Automatic manufacturer identification (TP-Link, Huawei, ZTE, Cisco, Apple, Xiaomi, MikroTik, Sagemcom, etc.).
- **Dual-Band Spectrum Analyzer (2.4 GHz & 5 GHz):** Plots channel overlap curves and recommends the cleanest interference-free channel.
- **Signal Direction Finder (Geiger Tracker):** Live RSSI tracking gauge with audible Geiger beeps as you aim the antenna toward the signal source.
