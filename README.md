# ⚡ Wi-Fi Cyber Suite | Advanced RF Sensing, Security, Heatmap & Spy Bug Hunter

> **Ever seen a spy movie where an agent sweeps a hotel room with a beeping gadget to find hidden bugs? That’s literally this app.**
> 
> A high-performance Wi-Fi surveillance, security audit, 360° radar, spectrum analyzer, **2D/3D RF Heatmap & Raytracer**, **Spy Cam & Drone Hunter**, and **camera-less human motion detector** optimized for Realtek RTL8811AU (TP-Link High-Gain USB Antenna) and all standard Wi-Fi cards.

---

## 🚀 Quick Launch (Master Command Center):
Double-click **`RUN_WIFI_SUITE.bat`** to open the Master Hub, or run individual tools:

| Executable File | Application | Description |
|---|---|---|
| **`RUN_WIFI_SUITE.bat`** | ⚡ **Master Command Center (`hub.py`)** | Central 4-module cyber dashboard to launch any tool with 1 click |
| **`run_motion_sensor.bat`** | 🚨 **Wi-Fi Motion Sentinel (`wifi_motion_sensor.py`)** | RF wave seismograph, 5s noise calibration, burglar alarm |
| **`run_radar.bat`** | 📡 **Wi-Fi Radar & Security (`wifi_radar.py`)** | 360° radar, spectrum analyzer, Evil Twin detection, vendor OUI |
| **`run_heatmap.bat`** | 🗺️ **Wi-Fi 2D/3D Heatmap (`wifi_heatmap.py`)** | Interactive floorplan, RF Raytracer, AI AP locator, 3D surface |
| **`run_spy_hunter.bat`** | 🕵️‍♂️ **Spy Cam & Drone Hunter (`wifi_spy_hunter.py`)** | Directional Geiger bug sweep, pinhole cam OUI fingerprinting, drone detector |

---

## ✨ Key Modules & Features:

### 1. 🚨 Wi-Fi Motion Sentinel (`wifi_motion_sensor.py`)
- **Real-Time RF Seismograph (40 FPS Custom Canvas):** Plots ultra-smooth RF perturbations caused by human body movement.
- **Segmented LED Energy Gauge (0-100%):** Color-shifting LED bar (Green ➔ Amber ➔ Red) for real-time perturbation intensity.
- **360° Sonar Pulse Radar:** Pulsing sonar sweep with shockwave rings on motion discovery.
- **5s Baseline Noise Calibration:** Profiles the quiescent environment for zero false alarms.
- **Armed Burglar Alarm:** Arm countdown with audio cyber siren alerts (`winsound`).

### 2. 📡 Wi-Fi Radar & Security Audit (`wifi_radar.py`)
- **360° Dynamic Radar:** Visualizes surrounding APs based on distance (signal strength) and Wi-Fi channel.
- **Evil Twin & Rogue AP Detector:** Detects duplicate SSIDs with conflicting encryption schemes (phishing/honeypots) or mismatched hardware vendors.
- **MAC OUI Vendor Lookup:** Automatic manufacturer identification (TP-Link, Huawei, ZTE, Cisco, Apple, Xiaomi, MikroTik, Sagemcom, etc.).
- **Dual-Band Spectrum Analyzer (2.4 GHz & 5 GHz):** Plots channel overlap curves and recommends the cleanest interference-free channel.
- **Signal Direction Finder (Geiger Tracker):** Live RSSI tracking gauge with audible Geiger beeps and 1D Kalman DSP smoothing.

### 3. 🗺️ Wi-Fi 2D/3D Heatmap & RF Raytracer (`wifi_heatmap.py`)
- **Interactive Floorplan Designer:** Draw walls with real physical materials (Concrete 12dB, Brick 7dB, Drywall 3dB, Metal Shield 26dB, Glass 2dB, Wood 4dB).
- **RF Raytracer & Wave Physics Engine:** Simulates Free-Space Path Loss (FSPL) and multi-wall attenuation for 2.4 GHz and 5.0 GHz bands with specular multi-reflection bounce rays.
- **Live Survey Walk-Through Mode:** Sample live Wi-Fi RSSI from your active adapter or TP-Link antenna as you walk across rooms.
- **AI Optimal Router Placement Locator:** Analyzes floorplan geometry and obstacles to pinpoint the ideal coordinates that eliminate dead zones.
- **3D Spatial Elevation Mesh:** Renders interactive 3D topological heightmaps showing RF peaks and dead-zone canyons.

### 4. 🕵️‍♂️ Spy Cam & Drone RF Hunter (`wifi_spy_hunter.py`)
- **Surveillance Chipset Fingerprinter:** Identifies MAC addresses from 60+ known hidden camera vendors (Espressif ESP32/8266, Tuya, V380, Xiongmai, Anyka, Allwinner, Hikvision, Dahua).
- **Drone & UAV Detector:** Identifies telemetry and Wi-Fi FPV streams from DJI (Mavic/Mini/Phantom), Parrot, Autel, Hubsan, and FPV drones.
- **Directional Geiger Homing Compass:** Target-locks suspicious devices and plays real-time audio Geiger clicks that speed up as you point your antenna toward the physical bug.
- **1D Kalman Filter Anti-Jitter:** Mathematical smoothing for rock-solid signal tracking.
- **Proximity Range Alert:** Classifies distance into `< 1m (Search Objects!)`, `1-3m (In This Room)`, and `> 5m (Distant)`.

---

## 👤 Author & Repository
- 🔗 **GitHub Repository:** [amirthn6533/wifi-sentinel-suite](https://github.com/amirthn6533/wifi-sentinel-suite)
- 👤 **Developer:** [@amirthn6533](https://github.com/amirthn6533)
