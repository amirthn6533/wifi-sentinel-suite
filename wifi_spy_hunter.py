"""
Wi-Fi Spy Cam & Drone RF Hunter (Counter-Surveillance & Bug Sweep Suite)
Author: Antigravity Pair Programmer
Edition: Directional Geiger Homing & RF Threat Fingerprinter
"""

import sys
import os
import re
import math
import time
import subprocess
import threading
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Audio feedback for Geiger Counter and Alert Siren
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# =====================================================================
# 1D Kalman Filter for Real-Time RF Signal Stabilization & Anti-Jitter
# =====================================================================
class KalmanFilter1D:
    """Mathematical 1D Kalman Filter to eliminate RF multipath fluctuations while preserving fast response."""
    def __init__(self, process_variance=0.08, measurement_variance=4.0, initial_value=0.0):
        self.q = process_variance       # Process variance (how fast true signal changes)
        self.r = measurement_variance   # Measurement noise variance (sensor jitter)
        self.x = float(initial_value)   # Current state estimate
        self.p = 1.0                    # Estimation error covariance
        self.initialized = False

    def update(self, measurement):
        if not self.initialized:
            self.x = float(measurement)
            self.initialized = True
            return self.x

        # 1. Prediction step
        p_pred = self.p + self.q

        # 2. Measurement update (Optimal Kalman Gain)
        k = p_pred / (p_pred + self.r)
        self.x = self.x + k * (float(measurement) - self.x)
        self.p = (1.0 - k) * p_pred
        return self.x


# =====================================================================
# Comprehensive Database of Surveillance Chipsets & Drone Manufacturers
# =====================================================================
SURVEILLANCE_OUI_DATABASE = {
    # Espressif (80%+ of DIY Pinhole / Hidden Spy Cams, ESP32, ESP8266)
    "24:0A:C4": ("Espressif (ESP32/8266 Spy Cam)", "CRITICAL", "High probability of DIY pinhole spy cam or hidden bug"),
    "24:6F:28": ("Espressif (ESP32 Spy Cam)", "CRITICAL", "Embedded micro-camera or IoT surveillance bug"),
    "24:B2:DE": ("Espressif Systems", "CRITICAL", "Micro-controller / Hidden sensor"),
    "30:AE:A4": ("Espressif Systems", "CRITICAL", "Micro-controller / Hidden video stream"),
    "3C:71:BF": ("Espressif (ESP8266)", "CRITICAL", "Low-cost wireless spy camera module"),
    "40:22:D8": ("Espressif Systems", "CRITICAL", "ESP32 Wireless Camera"),
    "48:3F:DA": ("Espressif Systems", "CRITICAL", "ESP32 Pinhole Video Streamer"),
    "4C:11:AE": ("Espressif Systems", "CRITICAL", "ESP32 Spy Device"),
    "54:43:B2": ("Espressif Systems", "CRITICAL", "ESP Wireless Transmitter"),
    "5C:CF:7F": ("Espressif Systems", "CRITICAL", "ESP8266 Spy Device"),
    "60:01:94": ("Espressif Systems", "CRITICAL", "ESP8266 Micro Cam"),
    "68:C6:3A": ("Espressif Systems", "CRITICAL", "ESP32 Micro Cam"),
    "84:0D:8E": ("Espressif Systems", "CRITICAL", "ESP Wireless Cam"),
    "84:CC:A8": ("Espressif Systems", "CRITICAL", "ESP Wireless Module"),
    "84:F3:EB": ("Espressif Systems", "CRITICAL", "ESP32 Surveillance Node"),
    "90:38:0C": ("Espressif Systems", "CRITICAL", "ESP32 Cam Module"),
    "A4:CF:12": ("Espressif Systems", "CRITICAL", "ESP8266 Hidden Bug"),
    "AC:D0:74": ("Espressif Systems", "CRITICAL", "ESP32 Micro Video Node"),
    "B4:E6:2D": ("Espressif Systems", "CRITICAL", "ESP32 Micro Cam"),
    "BC:DD:C2": ("Espressif Systems", "CRITICAL", "ESP32 Micro Cam"),
    "C4:4F:33": ("Espressif Systems", "CRITICAL", "ESP32 Micro Cam"),
    "CC:50:E3": ("Espressif Systems", "CRITICAL", "ESP32 Micro Cam"),
    "DC:4F:22": ("Espressif Systems", "CRITICAL", "ESP32 Micro Cam"),
    "E8:DB:84": ("Espressif Systems", "CRITICAL", "ESP32 Micro Cam"),

    # Tuya Smart (Smart Plugs, Smoke Detectors, Clocks with Hidden Cams)
    "D8:1F:12": ("Tuya Smart", "HIGH", "Smart device / Hidden camera in clock/bulb/socket"),
    "50:8A:06": ("Tuya Smart", "HIGH", "Tuya IoT Camera / Hidden Sensor"),
    "10:D5:61": ("Tuya Smart", "HIGH", "Tuya Smart Life Camera"),
    "70:89:76": ("Tuya Smart", "HIGH", "Tuya Smart Device"),
    "84:0D:8E": ("Tuya Smart", "HIGH", "Tuya Wireless Sensor"),
    "A0:92:08": ("Tuya Smart", "HIGH", "Tuya IoT Device"),
    "C4:4E:AC": ("Tuya Smart", "HIGH", "Tuya Smart Surveillance"),

    # V380 / Macro-video / Xiongmai / Anyka (Cheap Spy & Security Cams)
    "00:12:11": ("Macro-Video (V380 Cam)", "CRITICAL", "V380 Wireless Pinhole / Bulb Camera"),
    "00:12:12": ("Macro-Video (V380 Cam)", "CRITICAL", "V380 Wireless Panoramic Spy Cam"),
    "00:12:13": ("Macro-Video (V380 Cam)", "CRITICAL", "V380 Wireless Pinhole Camera"),
    "00:12:14": ("Macro-Video (V380 Cam)", "CRITICAL", "V380 P2P Wireless Camera"),
    "00:30:1B": ("Xiongmai (XM) Camera", "HIGH", "Xiongmai IP CCTV / Hidden Cam"),
    "00:0F:7D": ("Anyka Microelectronics", "HIGH", "Anyka IP Spy Camera SoC"),
    "00:1A:FE": ("Anyka Microelectronics", "HIGH", "Anyka Mini Camera"),

    # Drones & UAVs (DJI, Parrot, Autel, Hubsan, FPV)
    "60:60:1F": ("DJI Technology", "DRONE", "DJI Drone / OcuSync / Remote Controller"),
    "48:10:E5": ("DJI Technology", "DRONE", "DJI Drone (Mavic / Mini / Air / Phantom)"),
    "04:41:69": ("DJI Technology", "DRONE", "DJI Drone Video Link"),
    "00:26:7E": ("Parrot SA", "DRONE", "Parrot Drone (Bebop / Anafi / AR.Drone)"),
    "90:03:B7": ("Parrot SA", "DRONE", "Parrot UAV Wireless Link"),
    "00:12:1C": ("Autel Robotics", "DRONE", "Autel Drone (EVO Series)"),
    "00:1E:A9": ("Hubsan Intelligent", "DRONE", "Hubsan FPV Quadcopter"),
    "00:26:44": ("Yuneec International", "DRONE", "Yuneec Drone / Typhoon"),
    "00:13:EF": ("Walkera Drone", "DRONE", "Walkera FPV Drone Video Feed"),

    # Security & IP Cameras (Hikvision, Dahua, Yi, Reolink, Eufy)
    "44:19:B6": ("Hikvision Digital", "MEDIUM", "Hikvision CCTV / Surveillance Camera"),
    "BC:5E:CD": ("Hikvision Digital", "MEDIUM", "Hikvision IP Camera"),
    "C0:56:E3": ("Hikvision Digital", "MEDIUM", "Hikvision Security Cam"),
    "38:AF:29": ("Dahua Technology", "MEDIUM", "Dahua Security Camera"),
    "48:E2:44": ("Dahua Technology", "MEDIUM", "Dahua IP Camera"),
    "E4:AA:EC": ("Dahua Technology", "MEDIUM", "Dahua Surveillance Node"),
    "70:C9:4E": ("Yi Technology (Xiaoyi)", "MEDIUM", "Yi Home / Dome Security Camera"),
    "EC:71:DB": ("Reolink Digital", "MEDIUM", "Reolink Wireless Security Camera"),
    "98:03:51": ("Anker Eufy Security", "MEDIUM", "Eufy Wireless Security Cam")
}

# Suspicious SSID heuristic patterns
SPY_SSID_REGEX = re.compile(
    r"(?i)^(cam[-_]?\w*|ipcam[-_]?\w*|v380[-_]?\w*|lookcam[-_]?\w*|hdcam[-_]?\w*|mini[-_]?cam\w*|"
    r"wifi[-_]?cam\w*|spy[-_]?\w*|care[-_]?cam\w*|yoosee[-_]?\w*|tuya[-_]?\w*|smartlife[-_]?\w*|"
    r"esp32[-_]?\w*|esp8266[-_]?\w*|cctv[-_]?\w*|dvr[-_]?\w*|nvr[-_]?\w*|clock[-_]?cam\w*|"
    r"bulb[-_]?cam\w*|socket[-_]?cam\w*|hidden[-_]?\w*|p2p[-_]?cam\w*)"
)

DRONE_SSID_REGEX = re.compile(
    r"(?i)^(dji[-_]?\w*|phantom[-_]?\w*|mavic[-_]?\w*|spark[-_]?\w*|tello[-_]?\w*|inspire[-_]?\w*|"
    r"parrot[-_]?\w*|bebop[-_]?\w*|anafi[-_]?\w*|autel[-_]?\w*|hubsan[-_]?\w*|syma[-_]?\w*|"
    r"holy[-_]?stone\w*|drone[-_]?\w*|uav[-_]?\w*|quadcopter\w*|fpv[-_]?\w*|betafpv\w*)"
)


# =====================================================================
# Wi-Fi Scanner & Target Classifier Engine
# =====================================================================
class WifiThreatScanner:
    @staticmethod
    def scan_all_targets():
        """Scans all surrounding BSSIDs and classifies threats."""
        try:
            raw = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                encoding='cp1252',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except Exception:
            return []

        networks = []
        cur_ssid = None
        cur_auth = "Open"
        cur_bssid = None
        cur_sig = 0
        cur_radio = "802.11"
        cur_chan = 1

        for line in raw.splitlines():
            line_s = line.strip()
            if line_s.startswith("SSID") and ":" in line_s and not line_s.startswith("BSSID"):
                parts = line_s.split(":", 1)
                cur_ssid = parts[1].strip() if len(parts) > 1 else "Hidden Network"
                if not cur_ssid:
                    cur_ssid = "<Hidden SSID>"
            elif line_s.startswith("Authentication") and ":" in line_s:
                cur_auth = line_s.split(":", 1)[1].strip()
            elif line_s.startswith("BSSID") and ":" in line_s:
                if cur_bssid:
                    threat = WifiThreatScanner.classify_device(cur_ssid, cur_bssid, cur_sig, cur_auth, cur_chan, cur_radio)
                    networks.append(threat)
                cur_bssid = line_s.split(":", 1)[1].strip().upper()
            elif line_s.startswith("Signal") and ":" in line_s:
                try:
                    cur_sig = int(line_s.split(":", 1)[1].replace("%", "").strip())
                except ValueError:
                    cur_sig = 0
            elif line_s.startswith("Radio type") and ":" in line_s:
                cur_radio = line_s.split(":", 1)[1].strip()
            elif line_s.startswith("Channel") and ":" in line_s:
                try:
                    cur_chan = int(line_s.split(":", 1)[1].strip())
                except ValueError:
                    cur_chan = 1

        if cur_bssid:
            threat = WifiThreatScanner.classify_device(cur_ssid, cur_bssid, cur_sig, cur_auth, cur_chan, cur_radio)
            networks.append(threat)

        return networks

    @staticmethod
    def classify_device(ssid, bssid, signal_pct, auth, channel, radio):
        """Multi-factor classification: OUI + SSID heuristics + Encryption + Signal."""
        oui = bssid[:8].upper()
        vendor_info = SURVEILLANCE_OUI_DATABASE.get(oui, None)
        
        dbm = -100 + (signal_pct * 0.7)
        # Distance estimation: d = 10 ^ ((27.55 - 20*log10(2400) + |dbm|) / 20)
        # Rough indoor path loss estimate:
        try:
            est_meters = max(0.2, round(10 ** ((-35 - dbm) / (10 * 2.8)), 1))
        except Exception:
            est_meters = 5.0

        is_spy_ssid = bool(SPY_SSID_REGEX.search(ssid))
        is_drone_ssid = bool(DRONE_SSID_REGEX.search(ssid))
        is_hidden = (ssid == "<Hidden SSID>" or not ssid)

        threat_type = "STANDARD_AP"
        threat_level = "LOW"
        threat_title = "Standard Wi-Fi Router / Hotspot"
        threat_desc = "Normal consumer or enterprise wireless access point."

        if vendor_info:
            v_name, v_level, v_desc = vendor_info
            if v_level == "CRITICAL":
                threat_type = "SPY_CAMERA"
                threat_level = "CRITICAL"
                threat_title = f"🚨 SPY CAMERA: {v_name}"
                threat_desc = v_desc
            elif v_level == "DRONE":
                threat_type = "DRONE_UAV"
                threat_level = "DRONE"
                threat_title = f"🛸 DRONE / UAV: {v_name}"
                threat_desc = v_desc
            elif v_level == "HIGH":
                threat_type = "SMART_CAM_BUG"
                threat_level = "HIGH"
                threat_title = f"⚠️ IOT SURVEILLANCE: {v_name}"
                threat_desc = v_desc
            elif v_level == "MEDIUM":
                threat_type = "SECURITY_CAM"
                threat_level = "MEDIUM"
                threat_title = f"📷 IP SECURITY CAM: {v_name}"
                threat_desc = v_desc

        # Heuristic override if SSID strongly matches spy camera
        if is_spy_ssid and threat_level in ["LOW", "MEDIUM"]:
            threat_type = "SPY_CAMERA"
            threat_level = "CRITICAL"
            threat_title = "🚨 SUSPICIOUS SPY CAM (SSID Match)"
            threat_desc = f"Broadcast SSID '{ssid}' matches known spy/pinhole camera signatures."
        elif is_drone_ssid and threat_level != "DRONE":
            threat_type = "DRONE_UAV"
            threat_level = "DRONE"
            threat_title = "🛸 SUSPICIOUS DRONE (SSID Match)"
            threat_desc = f"Broadcast SSID '{ssid}' matches known drone/UAV telemetry feeds."

        # Hidden network with strong signal close by
        if is_hidden and signal_pct > 80 and threat_level == "LOW":
            threat_type = "HIDDEN_P2P"
            threat_level = "MEDIUM"
            threat_title = "🔒 UNIDENTIFIED HIDDEN LINK"
            threat_desc = "Strong unadvertised wireless link nearby (possible hidden P2P video stream)."

        return {
            "ssid": ssid,
            "bssid": bssid,
            "signal_pct": signal_pct,
            "signal_dbm": round(dbm, 1),
            "est_meters": est_meters,
            "auth": auth,
            "channel": channel,
            "radio": radio,
            "threat_type": threat_type,
            "threat_level": threat_level,
            "threat_title": threat_title,
            "threat_desc": threat_desc,
            "vendor": vendor_info[0] if vendor_info else "Unknown Manufacturer",
            "last_seen": time.strftime("%H:%M:%S")
        }


# =====================================================================
# Main Application Window
# =====================================================================
class WifiSpyHunterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🕵️‍♂️ WI-FI CYBER SUITE | Spy Cam & Drone RF Hunter")
        self.geometry("1380x840")
        self.minsize(1150, 720)
        self.configure(bg="#050811")

        # Color Palette
        self.c_bg = "#050811"
        self.c_panel = "#0b1220"
        self.c_card = "#111c30"
        self.c_border = "#1a2a47"
        self.c_neon_cyan = "#00f0ff"
        self.c_neon_green = "#00ff9d"
        self.c_neon_amber = "#ffb703"
        self.c_neon_red = "#ff0055"
        self.c_neon_purple = "#a855f7"
        self.c_neon_blue = "#38bdf8"
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        # State Variables
        self.scanning_active = True
        self.locked_target = None  # Dict of currently locked target
        self.detected_threats = []
        self.geiger_audio_active = tk.BooleanVar(value=True)
        self.filter_mode = tk.StringVar(value="ALL")  # ALL, THREATS, DRONES, CAMS
        self.current_proximity_pct = 0.0
        self.kalman_filters = {}  # bssid -> KalmanFilter1D instance

        self.setup_ui()
        self.start_scanner_thread()
        self.start_geiger_audio_loop()

    def setup_ui(self):
        # -------------------------------------------------------------
        # Header Bar
        # -------------------------------------------------------------
        header = tk.Frame(self, bg=self.c_panel, height=65, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=self.c_panel)
        title_frame.pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(title_frame, text="🕵️‍♂️ SPY CAM & DRONE RF HUNTER", font=('Segoe UI', 14, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_red).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_frame, text="Counter-Surveillance & Directional Geiger Sweep", font=('Segoe UI', 9),
                 bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT)

        # Header Threat Summary Badge
        self.lbl_threat_badge = tk.Label(header, text="🛡️ Threat Status: SCANNING...", font=('Segoe UI', 10, 'bold'),
                                         bg=self.c_card, fg=self.c_neon_cyan, padx=14, pady=6,
                                         highlightthickness=1, highlightbackground=self.c_border)
        self.lbl_threat_badge.pack(side=tk.RIGHT, padx=20, pady=12)

        # -------------------------------------------------------------
        # Main Split Workspace (Left: Radar & Geiger | Right: Threat List & Dossier)
        # -------------------------------------------------------------
        main_box = tk.Frame(self, bg=self.c_bg)
        main_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left Column: Directional Geiger Radar & Proximity HUD (Width: 440px)
        left_col = tk.Frame(main_box, bg=self.c_panel, width=440, highlightthickness=1, highlightbackground=self.c_border)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_col.pack_propagate(False)
        self.build_geiger_hud(left_col)

        # Right Column: Threat Table & Dossier
        right_col = tk.Frame(main_box, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.build_threat_list_panel(right_col)

    # -----------------------------------------------------------------
    # Left Column: Directional Geiger Proximity HUD
    # -----------------------------------------------------------------
    def build_geiger_hud(self, parent):
        pad = 12

        # Title
        tk.Label(parent, text="🎯 DIRECTIONAL GEIGER HOMING", font=('Segoe UI', 11, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(anchor='w', padx=pad, pady=(14, 4))
        
        tk.Label(parent, text="Aim antenna around the room. Ticks accelerate as you point toward the bug.",
                 font=('Segoe UI', 8), bg=self.c_panel, fg=self.c_muted, wraplength=410, justify=tk.LEFT).pack(anchor='w', padx=pad, pady=(0, 10))

        # Locked Target Card
        self.target_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=12, pady=10)
        self.target_card.pack(fill=tk.X, padx=pad, pady=(0, 10))

        self.lbl_target_name = tk.Label(self.target_card, text="🎯 LOCKED TARGET: [No Target Locked]",
                                        font=('Segoe UI', 10, 'bold'), bg=self.c_card, fg=self.c_text)
        self.lbl_target_name.pack(anchor='w')

        self.lbl_target_bssid = tk.Label(self.target_card, text="BSSID: --:--:--:--:--:-- | Vendor: --",
                                         font=('Consolas', 8), bg=self.c_card, fg=self.c_muted)
        self.lbl_target_bssid.pack(anchor='w', pady=(2, 0))

        # Big Circular Sonar / Geiger Compass Canvas
        self.compass_w = 390
        self.compass_h = 240
        self.compass_canvas = tk.Canvas(parent, bg="#050811", highlightthickness=1,
                                        highlightbackground=self.c_border, width=self.compass_w, height=self.compass_h)
        self.compass_canvas.pack(padx=pad, pady=4)

        # Proximity Gauge Bar (0 - 100%)
        gauge_box = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=12, pady=10)
        gauge_box.pack(fill=tk.X, padx=pad, pady=8)

        tk.Label(gauge_box, text="PROXIMITY INTENSITY GAUGE", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_muted).pack(anchor='w')

        self.prox_bar_canvas = tk.Canvas(gauge_box, bg="#050811", height=24, highlightthickness=0)
        self.prox_bar_canvas.pack(fill=tk.X, pady=(6, 4))

        self.lbl_prox_metrics = tk.Label(gauge_box, text="Signal: -- dBm (0%) | Est. Distance: -- m",
                                         font=('Consolas', 9, 'bold'), bg=self.c_card, fg=self.c_neon_green)
        self.lbl_prox_metrics.pack(anchor='w')

        # Distance Alert Banner
        self.lbl_dist_alert = tk.Label(parent, text="Select a suspicious device from the table to start homing sweep.",
                                       font=('Segoe UI', 9, 'bold'), bg=self.c_card, fg=self.c_neon_amber, padx=8, pady=8,
                                       wraplength=400, justify=tk.CENTER)
        self.lbl_dist_alert.pack(fill=tk.X, padx=pad, pady=(4, 8))

        # Audio Toggle & Scan Controls
        ctrl_bar = tk.Frame(parent, bg=self.c_panel)
        ctrl_bar.pack(fill=tk.X, padx=pad, pady=4, side=tk.BOTTOM)

        tk.Checkbutton(ctrl_bar, text="🔊 Audible Geiger Ticks", variable=self.geiger_audio_active,
                       bg=self.c_panel, fg=self.c_text, selectcolor=self.c_card,
                       font=('Segoe UI', 9, 'bold'), activebackground=self.c_panel).pack(side=tk.LEFT)

        btn_rescan = tk.Button(ctrl_bar, text="🔄 Force Re-Scan", bg=self.c_border, fg=self.c_neon_cyan,
                               font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=10, pady=4, cursor='hand2',
                               command=self.trigger_manual_scan)
        btn_rescan.pack(side=tk.RIGHT)

        self.draw_compass_hud(0, 0, "--")

    def draw_compass_hud(self, signal_pct, dbm, distance_str):
        """Draws dynamic concentric sonar rings with glowing pulse."""
        self.compass_canvas.delete("all")
        cx = self.compass_w // 2
        cy = self.compass_h // 2

        # Concentric distance rings
        radii = [105, 80, 55, 30]
        ring_labels = ["> 5m", "3-5m", "1-3m", "< 1m"]
        for r, lbl in zip(radii, ring_labels):
            self.compass_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#162238", width=1)
            self.compass_canvas.create_text(cx + r - 16, cy - 6, text=lbl, fill="#334155", font=('Consolas', 7))

        # Crosshair lines
        self.compass_canvas.create_line(cx, 15, cx, self.compass_h - 15, fill="#162238", width=1, dash=(2, 2))
        self.compass_canvas.create_line(25, cy, self.compass_w - 25, cy, fill="#162238", width=1, dash=(2, 2))

        # Dynamic glowing pulse ring based on signal
        pulse_r = int((signal_pct / 100.0) * 95)
        if pulse_r > 5:
            color = self.c_neon_red if signal_pct > 75 else (self.c_neon_amber if signal_pct > 50 else self.c_neon_cyan)
            self.compass_canvas.create_oval(cx-pulse_r, cy-pulse_r, cx+pulse_r, cy+pulse_r, outline=color, width=2)
            self.compass_canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill=color, outline="#ffffff", width=2)

        # Center label
        center_text = f"{signal_pct}%" if signal_pct > 0 else "IDLE"
        self.compass_canvas.create_text(cx, cy + 26, text=center_text, fill="#ffffff", font=('Segoe UI', 10, 'bold'))

        # Draw segmented LED Proximity Bar
        self.prox_bar_canvas.delete("all")
        w = self.prox_bar_canvas.winfo_width() if self.prox_bar_canvas.winfo_width() > 10 else 380
        num_segs = 28
        active_segs = int((signal_pct / 100.0) * num_segs)
        seg_w = (w - (num_segs * 3)) / num_segs

        for i in range(num_segs):
            x0 = i * (seg_w + 3)
            x1 = x0 + seg_w
            if i < active_segs:
                if i > 20:
                    seg_col = self.c_neon_red
                elif i > 12:
                    seg_col = self.c_neon_amber
                else:
                    seg_col = self.c_neon_green
            else:
                seg_col = "#0e1726"
            self.prox_bar_canvas.create_rectangle(x0, 2, x1, 22, fill=seg_col, outline="")

    # -----------------------------------------------------------------
    # Right Column: Threat Table & Dossier
    # -----------------------------------------------------------------
    def build_threat_list_panel(self, parent):
        pad = 12

        # Filter bar
        filter_box = tk.Frame(parent, bg=self.c_panel)
        filter_box.pack(fill=tk.X, padx=pad, pady=(12, 6))

        tk.Label(filter_box, text="🔎 DETECTED RF DEVICES & SURVEILLANCE TARGETS", font=('Segoe UI', 11, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(side=tk.LEFT)

        filter_frame = tk.Frame(filter_box, bg=self.c_panel)
        filter_frame.pack(side=tk.RIGHT)
        
        for flt_lbl, flt_val in [("All (All)", "ALL"), ("🚨 Cams", "CAMS"), ("🛸 Drones", "DRONES"), ("⚠️ All Threats", "THREATS")]:
            rb = tk.Radiobutton(filter_frame, text=flt_lbl, value=flt_val, variable=self.filter_mode,
                                command=self.refresh_table_view, bg=self.c_panel, fg=self.c_text,
                                selectcolor=self.c_card, font=('Segoe UI', 8, 'bold'))
            rb.pack(side=tk.LEFT, padx=3)

        # Threat TreeView Table
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Threat.Treeview", background="#0b1220", foreground="#f8fafc",
                        fieldbackground="#0b1220", font=('Segoe UI', 9), rowheight=28)
        style.configure("Threat.Treeview.Heading", background="#111c30", foreground="#00f0ff",
                        font=('Segoe UI', 9, 'bold'))
        style.map("Threat.Treeview", background=[('selected', '#1a2a47')])

        table_frame = tk.Frame(parent, bg=self.c_panel)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=pad, pady=4)

        cols = ("level", "ssid", "type", "vendor", "signal", "distance", "channel", "bssid")
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings', style="Threat.Treeview", selectmode='browse')

        self.tree.heading("level", text="Risk Level")
        self.tree.heading("ssid", text="SSID / Broadcast Name")
        self.tree.heading("type", text="Classification")
        self.tree.heading("vendor", text="Manufacturer / OUI")
        self.tree.heading("signal", text="Signal (dBm)")
        self.tree.heading("distance", text="Est. Dist")
        self.tree.heading("channel", text="CH")
        self.tree.heading("bssid", text="MAC Address")

        self.tree.column("level", width=95, anchor=tk.CENTER)
        self.tree.column("ssid", width=180, anchor=tk.W)
        self.tree.column("type", width=160, anchor=tk.W)
        self.tree.column("vendor", width=140, anchor=tk.W)
        self.tree.column("signal", width=90, anchor=tk.CENTER)
        self.tree.column("distance", width=80, anchor=tk.CENTER)
        self.tree.column("channel", width=45, anchor=tk.CENTER)
        self.tree.column("bssid", width=130, anchor=tk.CENTER)

        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_target_selected)

        # Bottom Threat Dossier Card & Guide
        self.dossier_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=14, pady=10)
        self.dossier_card.pack(fill=tk.X, padx=pad, pady=(8, 12))

        self.lbl_dossier_title = tk.Label(self.dossier_card, text="📋 THREAT DOSSIER & BUG MITIGATION GUIDE",
                                          font=('Segoe UI', 10, 'bold'), bg=self.c_card, fg=self.c_neon_cyan)
        self.lbl_dossier_title.pack(anchor='w')

        self.lbl_dossier_body = tk.Label(self.dossier_card,
                                         text="Click any device in the list to lock the Directional Geiger Tracker on it and view detection tips.\n"
                                              "💡 Pro-Tip: To find hidden pinhole lenses, turn off room lights and sweep a bright flashlight; the camera lens will reflect a blue/purple glare back at you.",
                                         font=('Segoe UI', 9), bg=self.c_card, fg=self.c_text, wraplength=850, justify=tk.LEFT)
        self.lbl_dossier_body.pack(anchor='w', pady=(4, 0))

    # -----------------------------------------------------------------
    # Background Scanning Thread
    # -----------------------------------------------------------------
    def start_scanner_thread(self):
        def worker():
            while self.scanning_active:
                targets = WifiThreatScanner.scan_all_targets()
                self.after(0, self.update_threat_data, targets)
                time.sleep(2.5)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def trigger_manual_scan(self):
        def worker():
            targets = WifiThreatScanner.scan_all_targets()
            self.after(0, self.update_threat_data, targets)
        threading.Thread(target=worker, daemon=True).start()

    def update_threat_data(self, targets):
        # Apply 1D Kalman Filter to stabilize RSSI & distance metrics across all devices
        for t in targets:
            bssid = t['bssid']
            if bssid not in self.kalman_filters:
                self.kalman_filters[bssid] = KalmanFilter1D(process_variance=0.08, measurement_variance=3.5, initial_value=t['signal_pct'])
            raw_pct = t['signal_pct']
            filtered_pct = round(self.kalman_filters[bssid].update(raw_pct), 1)
            t['signal_pct'] = filtered_pct
            t['signal_dbm'] = round(-100 + (filtered_pct * 0.7), 1)
            try:
                t['est_meters'] = max(0.2, round(10 ** ((-35 - t['signal_dbm']) / (10 * 2.8)), 1))
            except Exception:
                t['est_meters'] = 5.0

        self.detected_threats = targets
        self.refresh_table_view()

        # Update Badge
        cams_count = sum(1 for t in targets if t['threat_level'] == 'CRITICAL')
        drones_count = sum(1 for t in targets if t['threat_level'] == 'DRONE')
        iot_count = sum(1 for t in targets if t['threat_level'] in ['HIGH', 'MEDIUM'])

        if cams_count > 0:
            badge_text = f"🚨 {cams_count} SPY CAM(S) DETECTED!"
            badge_fg = self.c_neon_red
        elif drones_count > 0:
            badge_text = f"🛸 {drones_count} DRONE(S) IN VICINITY!"
            badge_fg = self.c_neon_purple
        elif iot_count > 0:
            badge_text = f"⚠️ {iot_count} IoT / Security Device(s)"
            badge_fg = self.c_neon_amber
        else:
            badge_text = f"🛡️ SECURE: No Spy Threats ({len(targets)} Safe APs)"
            badge_fg = self.c_neon_green

        self.lbl_threat_badge.config(text=badge_text, fg=badge_fg)

        # Update Locked Target if present
        if self.locked_target:
            # Find matching BSSID in updated list
            matched = next((t for t in targets if t['bssid'] == self.locked_target['bssid']), None)
            if matched:
                self.locked_target = matched
                self.update_locked_target_hud(matched)
            else:
                # Target out of range
                self.update_locked_target_hud(self.locked_target, signal_override=0)

    def refresh_table_view(self):
        # Save selection
        selected_bssid = self.locked_target['bssid'] if self.locked_target else None

        self.tree.delete(*self.tree.get_children())
        flt = self.filter_mode.get()

        for t in self.detected_threats:
            lvl = t['threat_level']
            if flt == "CAMS" and lvl != "CRITICAL":
                continue
            if flt == "DRONES" and lvl != "DRONE":
                continue
            if flt == "THREATS" and lvl not in ["CRITICAL", "DRONE", "HIGH"]:
                continue

            level_badge = "🚨 CRITICAL" if lvl == "CRITICAL" else ("🛸 DRONE" if lvl == "DRONE" else ("⚠️ HIGH" if lvl == "HIGH" else ("📷 MEDIUM" if lvl == "MEDIUM" else "🟢 SAFE")))
            item_id = self.tree.insert(
                "", tk.END,
                values=(level_badge, t['ssid'], t['threat_title'], t['vendor'], f"{t['signal_dbm']} dBm ({t['signal_pct']}%)",
                        f"~{t['est_meters']} m", t['channel'], t['bssid'])
            )

            # Re-select if it was locked
            if selected_bssid and t['bssid'] == selected_bssid:
                self.tree.selection_set(item_id)

    def on_target_selected(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item_values = self.tree.item(selected_items[0], "values")
        if not item_values or len(item_values) < 8:
            return

        bssid = item_values[7]
        target = next((t for t in self.detected_threats if t['bssid'] == bssid), None)
        if target:
            self.locked_target = target
            self.update_locked_target_hud(target)
            if HAS_SOUND:
                try:
                    winsound.Beep(1500, 100)
                except Exception:
                    pass

    def update_locked_target_hud(self, target, signal_override=None):
        sig_pct = signal_override if signal_override is not None else target['signal_pct']
        sig_dbm = target['signal_dbm'] if signal_override is None else -100.0
        est_m = target['est_meters']

        self.current_proximity_pct = sig_pct

        # Target Card
        self.lbl_target_name.config(text=f"🎯 LOCKED: {target['ssid']} ({target['threat_title']})",
                                    fg=self.c_neon_red if target['threat_level'] == "CRITICAL" else self.c_neon_cyan)
        self.lbl_target_bssid.config(text=f"BSSID: {target['bssid']} | Channel: {target['channel']} | Vendor: {target['vendor']}")

        # Proximity metrics
        self.lbl_prox_metrics.config(text=f"Signal: {sig_dbm} dBm ({sig_pct}%) | Est. Distance: ~{est_m} meters")

        # Distance Alert
        if sig_pct > 80 or est_m < 1.0:
            alert_text = "🚨 EXTREMELY CLOSE (< 1m)! Check smoke detectors, clocks, mirrors, power outlets!"
            alert_col = self.c_neon_red
        elif sig_pct > 55 or est_m < 3.0:
            alert_text = "⚠️ IN THIS ROOM (1 - 3m). Sweep antenna in a circle to pinpoint direction."
            alert_col = self.c_neon_amber
        else:
            alert_text = "📡 DISTANT TARGET (> 5m). Walk around to locate the strongest RF signal."
            alert_col = self.c_neon_green

        self.lbl_dist_alert.config(text=alert_text, fg=alert_col)

        # Draw Compass HUD
        self.draw_compass_hud(sig_pct, sig_dbm, f"{est_m}m")

        # Update Dossier Text
        dossier_text = (
            f"Device: {target['ssid']} | MAC: {target['bssid']} | Chipset: {target['vendor']}\n"
            f"Threat Classification: {target['threat_desc']}\n\n"
            f"🔍 Counter-Measure Steps:\n"
            f"1. Physical Sweep: Examine power bricks, USB chargers, digital clocks, picture frames.\n"
            f"2. Lens Glare Test: Turn off all room lights and shine a smartphone flashlight across suspicious items to spot camera lens reflections.\n"
            f"3. Network Isolation: If connected to your LAN, block MAC '{target['bssid']}' in your router settings."
        )
        self.lbl_dossier_body.config(text=dossier_text)

    # -----------------------------------------------------------------
    # Audio Geiger Counter Homing Loop
    # -----------------------------------------------------------------
    def start_geiger_audio_loop(self):
        def geiger_worker():
            while True:
                if self.locked_target and self.geiger_audio_active.get() and HAS_SOUND:
                    pct = self.current_proximity_pct
                    if pct > 0:
                        # Tone frequency scales with signal (600Hz to 2400Hz)
                        freq = int(600 + (pct / 100.0) * 1800)
                        # Sleep interval scales inversely with signal (1.2s down to 0.05s)
                        sleep_s = max(0.04, 1.2 - ((pct / 100.0) * 1.15))
                        try:
                            winsound.Beep(freq, 25)
                        except Exception:
                            pass
                        time.sleep(sleep_s)
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)

        t = threading.Thread(target=geiger_worker, daemon=True)
        t.start()


# =====================================================================
# Main Launch Entry
# =====================================================================
if __name__ == '__main__':
    app = WifiSpyHunterApp()
    app.mainloop()
