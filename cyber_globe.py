"""
=============================================================================
🌐 CYBER THREAT COMMAND CENTER | 3D Globe & 2D World War Map (Ultra HD)
=============================================================================
Author: Antigravity Pair Programmer
Architecture: Real 180-Country Vector Topography + Dual 3D/2D War Room Matrix
Features: 3D Spherical & 2D Flat Mercator Views + Real-Time Ballistic Missiles
=============================================================================
"""

import sys
import os
import time
import math
import json
import random
import threading
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

# Audio Engine for Radar & Missile SFX
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# =====================================================================
# Load Real 180-Country Vector Topography Database
# =====================================================================
DATA_PATH = os.path.join(os.path.dirname(__file__), "world_map_data.json")
WORLD_COUNTRIES = []

if os.path.exists(DATA_PATH):
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            WORLD_COUNTRIES = json.load(f)
    except Exception as e:
        print("Error loading world_map_data.json:", e)

# 35 Major Strategic Hubs (Capitals & Cloud DCs)
CITIES_DB = {
    "USA (Washington D.C.)": {"lat": 38.90, "lon": -77.03, "flag": "🇺🇸"},
    "USA (Silicon Valley)": {"lat": 37.38, "lon": -122.08, "flag": "🇺🇸"},
    "USA (New York Cloud)": {"lat": 40.71, "lon": -74.00, "flag": "🇺🇸"},
    "Iran (Tehran)": {"lat": 35.68, "lon": 51.38, "flag": "🇮🇷"},
    "Iran (Isfahan Grid)": {"lat": 32.65, "lon": 51.66, "flag": "🇮🇷"},
    "Russia (Moscow)": {"lat": 55.75, "lon": 37.61, "flag": "🇷🇺"},
    "Russia (St. Petersburg)": {"lat": 59.93, "lon": 30.33, "flag": "🇷🇺"},
    "China (Beijing Center)": {"lat": 39.90, "lon": 116.40, "flag": "🇨🇳"},
    "China (Shanghai Financial)": {"lat": 31.23, "lon": 121.47, "flag": "🇨🇳"},
    "China (Shenzhen Tech)": {"lat": 22.54, "lon": 114.05, "flag": "🇨🇳"},
    "Germany (Frankfurt AWS)": {"lat": 50.11, "lon": 8.68, "flag": "🇩🇪"},
    "UK (London Exchange)": {"lat": 51.50, "lon": -0.12, "flag": "🇬🇧"},
    "France (Paris DC)": {"lat": 48.85, "lon": 2.35, "flag": "🇫🇷"},
    "Japan (Tokyo Core)": {"lat": 35.67, "lon": 139.65, "flag": "🇯🇵"},
    "South Korea (Seoul)": {"lat": 37.56, "lon": 126.97, "flag": "🇰🇷"},
    "UAE (Dubai Hub)": {"lat": 25.20, "lon": 55.27, "flag": "🇦🇪"},
    "Saudi Arabia (Riyadh)": {"lat": 24.71, "lon": 46.67, "flag": "🇸🇦"},
    "Israel (Tel Aviv)": {"lat": 32.08, "lon": 34.78, "flag": "🇮🇱"},
    "Singapore Data Hub": {"lat": 1.35, "lon": 103.81, "flag": "🇸🇬"},
    "India (Mumbai)": {"lat": 19.07, "lon": 72.87, "flag": "🇮🇳"},
    "India (Bangalore IT)": {"lat": 12.97, "lon": 77.59, "flag": "🇮🇳"},
    "Australia (Sydney)": {"lat": -33.86, "lon": 151.20, "flag": "🇦🇺"},
    "Brazil (São Paulo)": {"lat": -23.55, "lon": -46.63, "flag": "🇧🇷"},
    "Netherlands (Amsterdam)": {"lat": 52.36, "lon": 4.90, "flag": "🇳🇱"},
    "Turkey (Istanbul)": {"lat": 41.00, "lon": 28.97, "flag": "🇹🇷"},
    "Canada (Toronto)": {"lat": 43.65, "lon": -79.38, "flag": "🇨🇦"},
    "South Africa (Johannesburg)": {"lat": -26.20, "lon": 28.04, "flag": "🇿🇦"},
    "Ukraine (Kyiv)": {"lat": 50.45, "lon": 30.52, "flag": "🇺🇦"},
}

ATTACK_TYPES = [
    {"name": "DDoS Volumetric Surge (1.2 Tbps)", "tag": "DDoS-FLOOD", "color": "#ff0055"},
    {"name": "LockBit 3.0 Enterprise Ransomware", "tag": "RANSOMWARE", "color": "#a855f7"},
    {"name": "Pegasus Zero-Day Mobile Infiltration", "tag": "ZERO-DAY", "color": "#ffb703"},
    {"name": "CobaltStrike C2 Beacon Activity", "tag": "C2-BEACON", "color": "#00ff9d"},
    {"name": "SQLi Financial Database Exfiltration", "tag": "DATA-BREACH", "color": "#00f0ff"},
    {"name": "SCADA Industrial Grid Sabotage", "tag": "ICS-ATTACK", "color": "#f97316"},
]


# =====================================================================
# 3D/2D Ballistic Missile & Shockwave Engine
# =====================================================================
class CyberMissile:
    def __init__(self, src_key, dst_key, meta, speed=0.018):
        self.src = src_key
        self.dst = dst_key
        self.meta = meta
        self.progress = 0.0
        self.speed = speed
        self.alive = True
        self.trail_3d = deque(maxlen=16)
        self.trail_2d = deque(maxlen=16)

        # Coordinates
        self.lat1, self.lon1 = CITIES_DB[src_key]["lat"], CITIES_DB[src_key]["lon"]
        self.lat2, self.lon2 = CITIES_DB[dst_key]["lat"], CITIES_DB[dst_key]["lon"]

        # 3D endpoints on unit sphere
        p_s = self.to_cartesian(self.lat1, self.lon1)
        p_d = self.to_cartesian(self.lat2, self.lon2)
        self.p_start = p_s
        self.p_end = p_d

        mid = (p_s + p_d) * 0.5
        norm = np.linalg.norm(mid)
        self.p_mid = (mid / norm) * random.uniform(1.45, 1.70) if norm > 1e-4 else np.array([0, 1.55, 0])

    def to_cartesian(self, lat, lon):
        phi = math.radians(lat)
        theta = math.radians(lon)
        return np.array([math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta)])

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.alive = False

        t = self.progress
        # 3D position
        curr_3d = (1 - t)**2 * self.p_start + 2 * (1 - t) * t * self.p_mid + t**2 * self.p_end
        self.trail_3d.append(curr_3d)

        # 2D flat map position (Interpolated Lat/Lon with parabolic altitude arch)
        curr_lat = (1 - t) * self.lat1 + t * self.lat2
        curr_lon = (1 - t) * self.lon1 + t * self.lon2
        arch_offset = math.sin(t * math.pi) * 35.0  # Arch upward in 2D
        self.trail_2d.append((curr_lat + arch_offset, curr_lon))


class ExplosionShockwave:
    def __init__(self, dst_key, color):
        self.city = dst_key
        self.color = color
        self.radius = 3.0
        self.max_radius = 36.0
        self.alpha = 1.0
        self.alive = True

        lat = CITIES_DB[dst_key]["lat"]
        lon = CITIES_DB[dst_key]["lon"]
        self.lat = lat
        self.lon = lon
        phi = math.radians(lat)
        theta = math.radians(lon)
        self.p3d = np.array([math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta)])

    def update(self):
        self.radius += 2.2
        self.alpha -= 0.05
        if self.alpha <= 0 or self.radius >= self.max_radius:
            self.alive = False


# =====================================================================
# Main Cyber Threat Command Center
# =====================================================================
class CyberWarfareCommandCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌐 CYBER THREAT COMMAND CENTER | 3D Globe & 2D World War Map")
        self.geometry("1440x900")
        self.minsize(1150, 750)
        self.configure(bg="#02040a")

        # Palette
        self.c_bg = "#02040a"
        self.c_panel = "#070c18"
        self.c_card = "#0c1527"
        self.c_border = "#162744"
        self.c_neon_cyan = "#00f0ff"
        self.c_neon_green = "#00ff9d"
        self.c_neon_amber = "#ffb703"
        self.c_neon_red = "#ff0055"
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        # Modes: '3D' or '2D'
        self.view_mode = '3D'

        # 3D Globe Matrix State
        self.radius_3d = 235
        self.yaw = 0.55
        self.pitch = 0.20
        self.auto_spin = True
        self.spin_speed = 0.007

        # Drag State
        self.mouse_dragging = False
        self.last_mx = 0
        self.last_my = 0

        # Warfare Simulation
        self.missiles = []
        self.shockwaves = []
        self.total_intercepts = 34910
        self.defcon_level = 3  # Active default!
        self.sound_enabled = tk.BooleanVar(value=True)

        # Starfield
        self.stars = [(random.randint(0, 1440), random.randint(0, 900), random.choice([1, 1, 2])) for _ in range(90)]

        self.setup_ui()
        self.populate_initial_logs()
        self.start_render_loop()
        self.start_cyber_warfare_traffic_thread()

    def setup_ui(self):
        # -------------------------------------------------------------
        # Header Bar
        # -------------------------------------------------------------
        header = tk.Frame(self, bg=self.c_panel, height=65, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=self.c_panel)
        title_box.pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(title_box, text="🌐 CYBER THREAT COMMAND CENTER", font=('Segoe UI', 14, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_box, text="180-Country Vector Topography • Real-Time Ballistic Attack Matrix", font=('Segoe UI', 9),
                 bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT)

        # View Mode Toggle & DEFCON Controls
        ctrl_box = tk.Frame(header, bg=self.c_panel)
        ctrl_box.pack(side=tk.RIGHT, padx=20, pady=14)

        # 3D vs 2D Mode Switcher
        self.btn_view_mode = tk.Button(ctrl_box, text="🗺️ SWITCH TO 2D FLAT MAP", bg="#1e3a8a", fg=self.c_neon_cyan,
                                       font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=10, pady=3, cursor='hand2',
                                       activebackground="#2563eb", activeforeground="#ffffff",
                                       command=self.toggle_view_mode)
        self.btn_view_mode.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(ctrl_box, text="DEFCON:", font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT, padx=(0, 6))

        self.btn_d5 = tk.Button(ctrl_box, text="DEFCON 5", bg=self.c_card, fg=self.c_neon_green,
                                font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=7, pady=3, cursor='hand2',
                                command=lambda: self.set_defcon(5))
        self.btn_d5.pack(side=tk.LEFT, padx=2)

        self.btn_d3 = tk.Button(ctrl_box, text="DEFCON 3", bg=self.c_neon_amber, fg="#030611",
                                font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=7, pady=3, cursor='hand2',
                                command=lambda: self.set_defcon(3))
        self.btn_d3.pack(side=tk.LEFT, padx=2)

        self.btn_d1 = tk.Button(ctrl_box, text="DEFCON 1 (WAR)", bg=self.c_card, fg=self.c_neon_red,
                                font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=7, pady=3, cursor='hand2',
                                command=lambda: self.set_defcon(1))
        self.btn_d1.pack(side=tk.LEFT, padx=2)

        # -------------------------------------------------------------
        # Main Split Workspace
        # -------------------------------------------------------------
        main_box = tk.Frame(self, bg=self.c_bg)
        main_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Center Column: 3D/2D Canvas
        canvas_frame = tk.Frame(main_box, bg="#010308", highlightthickness=1, highlightbackground=self.c_border)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(canvas_frame, bg="#010308", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # Right Column: War Room Dashboard (Width: 440px)
        right_col = tk.Frame(main_box, bg=self.c_panel, width=440, highlightthickness=1, highlightbackground=self.c_border)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 0))
        right_col.pack_propagate(False)
        self.build_war_room_panel(right_col)

    def build_war_room_panel(self, parent):
        pad = 12

        # Card 1: Interactive Cyber Strike Launcher
        strike_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=12, pady=10)
        strike_card.pack(fill=tk.X, padx=pad, pady=(12, 6))

        tk.Label(strike_card, text="🚀 MANUAL CYBER MISSILE STRIKE", font=('Segoe UI', 9, 'bold'), bg=self.c_card, fg=self.c_neon_red).pack(anchor='w')

        f_src = tk.Frame(strike_card, bg=self.c_card)
        f_src.pack(fill=tk.X, pady=(6, 2))
        tk.Label(f_src, text="Source:", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted, width=7, anchor='w').pack(side=tk.LEFT)
        self.combo_src = ttk.Combobox(f_src, values=list(CITIES_DB.keys()), state="readonly", font=('Segoe UI', 8))
        self.combo_src.current(0)
        self.combo_src.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        f_dst = tk.Frame(strike_card, bg=self.c_card)
        f_dst.pack(fill=tk.X, pady=2)
        tk.Label(f_dst, text="Target:", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted, width=7, anchor='w').pack(side=tk.LEFT)
        self.combo_dst = ttk.Combobox(f_dst, values=list(CITIES_DB.keys()), state="readonly", font=('Segoe UI', 8))
        self.combo_dst.current(3)  # Iran (Tehran)
        self.combo_dst.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        f_atk = tk.Frame(strike_card, bg=self.c_card)
        f_atk.pack(fill=tk.X, pady=2)
        tk.Label(f_atk, text="Payload:", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted, width=7, anchor='w').pack(side=tk.LEFT)
        self.combo_atk = ttk.Combobox(f_atk, values=[a["name"] for a in ATTACK_TYPES], state="readonly", font=('Segoe UI', 8))
        self.combo_atk.current(0)
        self.combo_atk.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        btn_fire = tk.Button(strike_card, text="⚡ LAUNCH CYBER MISSILE 🚀", bg=self.c_neon_red, fg="#ffffff",
                             font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                             activebackground="#b91c1c", activeforeground="#ffffff",
                             command=self.fire_manual_missile)
        btn_fire.pack(fill=tk.X, pady=(8, 2))

        # Card 2: Attack Velocity Metrics
        stats_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=12, pady=10)
        stats_card.pack(fill=tk.X, padx=pad, pady=6)

        tk.Label(stats_card, text="GLOBAL ATTACK VELOCITY", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_muted).pack(anchor='w')

        self.lbl_attack_count = tk.Label(stats_card, text="34,910", font=('Consolas', 22, 'bold'), bg=self.c_card, fg=self.c_neon_cyan)
        self.lbl_attack_count.pack(anchor='w', pady=(2, 0))

        tk.Label(stats_card, text="🔴 Attacks Intercepted Worldwide | Peak: 2.38 Tbps", font=('Segoe UI', 8, 'bold'),
                 bg=self.c_card, fg=self.c_neon_green).pack(anchor='w')

        # Card 3: Live War Room Telemetry Feed
        feed_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=10, pady=8)
        feed_card.pack(fill=tk.BOTH, expand=True, padx=pad, pady=6)

        tk.Label(feed_card, text="📡 LIVE WAR ROOM TELEMETRY STREAM", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_neon_cyan).pack(anchor='w')

        self.feed_list = tk.Listbox(feed_card, bg="#02050e", fg=self.c_neon_green, font=('Consolas', 8),
                                    highlightthickness=0, selectbackground=self.c_panel, bd=0)
        self.feed_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        # Bottom Bar
        ctrl_bar = tk.Frame(parent, bg=self.c_panel)
        ctrl_bar.pack(fill=tk.X, padx=pad, pady=(6, 12), side=tk.BOTTOM)

        tk.Checkbutton(ctrl_bar, text="🔊 Radar Audio SFX", variable=self.sound_enabled,
                       bg=self.c_panel, fg=self.c_text, selectcolor=self.c_card,
                       font=('Segoe UI', 9, 'bold'), activebackground=self.c_panel).pack(side=tk.LEFT)

        btn_spin = tk.Button(ctrl_bar, text="🔄 Toggle Spin", bg=self.c_border, fg=self.c_neon_cyan,
                             font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=8, pady=3, cursor='hand2',
                             command=self.toggle_spin)
        btn_spin.pack(side=tk.RIGHT)

    def toggle_view_mode(self):
        if self.view_mode == '3D':
            self.view_mode = '2D'
            self.btn_view_mode.config(text="🌐 SWITCH TO 3D GLOBE")
        else:
            self.view_mode = '3D'
            self.btn_view_mode.config(text="🗺️ SWITCH TO 2D FLAT MAP")

    def populate_initial_logs(self):
        sample_cities = list(CITIES_DB.keys())
        for _ in range(12):
            s = random.choice(sample_cities)
            d = random.choice([c for c in sample_cities if c != s])
            m = random.choice(ATTACK_TYPES)
            t_str = time.strftime('%H:%M:%S')
            log_entry = f"[{t_str}] ➔ [{m['tag']}] {s.split('(')[0]} ➔ {d.split('(')[0]}"
            self.feed_list.insert(tk.END, log_entry)

    def toggle_spin(self):
        self.auto_spin = not self.auto_spin

    def set_defcon(self, level):
        self.defcon_level = level
        self.btn_d5.config(bg=self.c_neon_green if level == 5 else self.c_card, fg="#030611" if level == 5 else self.c_neon_green)
        self.btn_d3.config(bg=self.c_neon_amber if level == 3 else self.c_card, fg="#030611" if level == 3 else self.c_neon_amber)
        self.btn_d1.config(bg=self.c_neon_red if level == 1 else self.c_card, fg="#ffffff" if level == 1 else self.c_neon_red)

    def fire_manual_missile(self):
        src = self.combo_src.get()
        dst = self.combo_dst.get()
        atk_name = self.combo_atk.get()

        if src == dst:
            messagebox.showwarning("Target Conflict", "Source and Target cannot be the same location.")
            return

        meta = next((a for a in ATTACK_TYPES if a["name"] == atk_name), ATTACK_TYPES[0])
        missile = CyberMissile(src, dst, meta, speed=0.022)
        self.missiles.append(missile)
        self.log_attack_event(src, dst, meta)

        if self.sound_enabled.get() and HAS_SOUND:
            try:
                winsound.Beep(1900, 30)
            except Exception:
                pass

    def log_attack_event(self, src, dst, meta):
        t_str = time.strftime('%H:%M:%S')
        s_name = src.split('(')[0].strip()
        d_name = dst.split('(')[0].strip()
        log_entry = f"[{t_str}] ➔ [{meta['tag']}] {s_name} ➔ {d_name}"
        self.feed_list.insert(0, log_entry)
        if self.feed_list.size() > 60:
            self.feed_list.delete(60, tk.END)

        self.total_intercepts += random.randint(2, 7)
        self.lbl_attack_count.config(text=f"{self.total_intercepts:,}")

    # -------------------------------------------------------------
    # Mouse Interaction: 3D Drag & Zoom
    # -------------------------------------------------------------
    def on_mouse_down(self, event):
        self.mouse_dragging = True
        self.last_mx = event.x
        self.last_my = event.y

    def on_mouse_drag(self, event):
        if self.mouse_dragging and self.view_mode == '3D':
            dx = event.x - self.last_mx
            dy = event.y - self.last_my
            self.yaw += dx * 0.008
            self.pitch += dy * 0.008
            self.pitch = max(-math.pi * 0.45, min(math.pi * 0.45, self.pitch))
            self.last_mx = event.x
            self.last_my = event.y

    def on_mouse_up(self, event):
        self.mouse_dragging = False

    def on_mouse_wheel(self, event):
        if self.view_mode == '3D':
            if event.delta > 0:
                self.radius_3d = min(360, self.radius_3d + 18)
            else:
                self.radius_3d = max(140, self.radius_3d - 18)

    # -------------------------------------------------------------
    # 3D Matrix Transformation & 2D Projection
    # -------------------------------------------------------------
    def project_3d_point(self, p, cx, cy):
        x, y, z = p

        # 1. Pitch
        cos_p = math.cos(self.pitch)
        sin_p = math.sin(self.pitch)
        y1 = y * cos_p - z * sin_p
        z1 = y * sin_p + z * cos_p

        # 2. Yaw
        cos_y = math.cos(self.yaw)
        sin_y = math.sin(self.yaw)
        x2 = x * cos_y + z1 * sin_y
        z2 = -x * sin_y + z1 * cos_y

        dist = 550.0
        fov = dist / (dist + z2 * self.radius_3d + 20.0)

        sx = cx + x2 * self.radius_3d * fov
        sy = cy + y1 * self.radius_3d * fov

        is_visible = (z2 > -0.15)
        return sx, sy, z2, is_visible

    def project_2d_flat_point(self, lat, lon, w, h):
        """Equirectangular World Projection: map lat/lon linearly to 2D canvas."""
        pad_x = 40
        pad_y = 40
        cw = w - 2 * pad_x
        ch = h - 2 * pad_y

        sx = pad_x + ((lon + 180.0) / 360.0) * cw
        sy = pad_y + ((90.0 - lat) / 180.0) * ch
        return sx, sy

    # -------------------------------------------------------------
    # 60 FPS Render Engine
    # -------------------------------------------------------------
    def start_render_loop(self):
        def loop():
            self.render_frame()
            if self.auto_spin and not self.mouse_dragging and self.view_mode == '3D':
                self.yaw += self.spin_speed
            self.after(20, loop)

        self.after(100, loop)

    def render_frame(self):
        self.canvas.delete("all")
        w = max(100, self.canvas.winfo_width())
        h = max(100, self.canvas.winfo_height())
        cx = w / 2
        cy = h / 2

        # 1. Deep Space Starfield
        for (sx, sy, size) in self.stars:
            self.canvas.create_oval(sx, sy, sx + size, sy + size, fill="#334155", outline="")

        if self.view_mode == '3D':
            # 3D GLOBE MODE
            # Glowing Atmosphere Halo
            r_glow = self.radius_3d + 16
            self.canvas.create_oval(cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow, outline="#0369a1", width=2)
            self.canvas.create_oval(cx - self.radius_3d, cy - self.radius_3d, cx + self.radius_3d, cy + self.radius_3d,
                                    outline="#00f0ff", width=2.5)

            # Draw 180 Real Countries on 3D Globe
            self.draw_3d_real_countries(cx, cy)
            # Draw 3D Cities
            self.draw_3d_cities(cx, cy)
            # Draw 3D Missiles & Shockwaves
            self.draw_3d_missiles(cx, cy)
            self.draw_3d_shockwaves(cx, cy)
        else:
            # 2D FLAT WAR MAP MODE
            self.draw_2d_flat_map(w, h)
            self.draw_2d_missiles(w, h)
            self.draw_2d_shockwaves(w, h)

        # Cyber HUD Overlays
        self.draw_hud_overlays(w, h)

    # -------------------------------------------------------------
    # 3D Render Routines
    # -------------------------------------------------------------
    def draw_3d_real_countries(self, cx, cy):
        """Draws exact 180 real country polygons on 3D globe."""
        for country in WORLD_COUNTRIES:
            for poly in country.get("polys", []):
                pts = []
                for (lat, lon) in poly:
                    phi = math.radians(lat)
                    theta = math.radians(lon)
                    p = (math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta))
                    sx, sy, z, vis = self.project_3d_point(p, cx, cy)
                    if vis and z > -0.05:
                        pts.extend([sx, sy])
                    else:
                        if len(pts) >= 4:
                            self.canvas.create_line(pts, fill="#00f0ff", width=1.4, smooth=True)
                        pts = []
                if len(pts) >= 4:
                    self.canvas.create_line(pts, fill="#00f0ff", width=1.4, smooth=True)

    def draw_3d_cities(self, cx, cy):
        for name, data in CITIES_DB.items():
            phi = math.radians(data["lat"])
            theta = math.radians(data["lon"])
            p = (math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta))
            sx, sy, z, vis = self.project_3d_point(p, cx, cy)

            if vis and z > 0.10:
                self.canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill="#ffffff", outline=self.c_neon_green, width=2)
                if z > 0.30:
                    c_short = name.split("(")[0].strip()
                    self.canvas.create_text(sx + 7, sy - 4, text=f"{data['flag']} {c_short}",
                                            font=('Segoe UI', 8, 'bold'), fill="#f1f5f9", anchor='w')

    def draw_3d_missiles(self, cx, cy):
        active = []
        for m in self.missiles:
            m.update()
            if len(m.trail_3d) >= 2:
                pts = []
                for p3d in m.trail_3d:
                    sx, sy, z, vis = self.project_3d_point(p3d, cx, cy)
                    if vis:
                        pts.extend([sx, sy])

                if len(pts) >= 4:
                    self.canvas.create_line(pts, fill=m.meta["color"], width=4, smooth=True)
                    self.canvas.create_line(pts, fill="#ffffff", width=1.8, smooth=True)
                    hx, hy = pts[-2], pts[-1]
                    self.canvas.create_oval(hx - 5, hy - 5, hx + 5, hy + 5, fill="#ffffff", outline=m.meta["color"], width=2)

            if m.alive:
                active.append(m)
            else:
                self.shockwaves.append(ExplosionShockwave(m.dst, m.meta["color"]))
                if self.sound_enabled.get() and HAS_SOUND and random.random() < 0.30:
                    try:
                        winsound.Beep(320, 35)
                    except Exception:
                        pass

        self.missiles = active

    def draw_3d_shockwaves(self, cx, cy):
        active = []
        for s in self.shockwaves:
            s.update()
            sx, sy, z, vis = self.project_3d_point(s.p3d, cx, cy)
            if vis and z > 0.0:
                r = s.radius
                self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, outline=s.color, width=2.5)
                self.canvas.create_oval(sx - (r*0.6), sy - (r*0.6), sx + (r*0.6), sy + (r*0.6), outline="#ffffff", width=1.5)
            if s.alive:
                active.append(s)
        self.shockwaves = active

    # -------------------------------------------------------------
    # 2D Flat World Map Render Routines
    # -------------------------------------------------------------
    def draw_2d_flat_map(self, w, h):
        """Draws crystal-clear 180 real country polygons on flat Mercator/Equirectangular grid."""
        # 2D Cyber Grid
        for x_g in range(40, w - 40, 60):
            self.canvas.create_line(x_g, 40, x_g, h - 40, fill="#0b172a", width=1)
        for y_g in range(40, h - 40, 50):
            self.canvas.create_line(40, y_g, w - 40, y_g, fill="#0b172a", width=1)

        # Real 180 Countries Outlines
        for country in WORLD_COUNTRIES:
            for poly in country.get("polys", []):
                pts = []
                for (lat, lon) in poly:
                    sx, sy = self.project_2d_flat_point(lat, lon, w, h)
                    pts.extend([sx, sy])
                if len(pts) >= 4:
                    self.canvas.create_polygon(pts, fill="#071a33", outline="#00e5ff", width=1.2, smooth=True)

        # 2D City Nodes
        for name, data in CITIES_DB.items():
            sx, sy = self.project_2d_flat_point(data["lat"], data["lon"], w, h)
            self.canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill="#ffffff", outline=self.c_neon_green, width=2)
            c_short = name.split("(")[0].strip()
            self.canvas.create_text(sx + 6, sy - 6, text=f"{data['flag']} {c_short}",
                                    font=('Segoe UI', 8, 'bold'), fill="#f1f5f9", anchor='w')

    def draw_2d_missiles(self, w, h):
        active = []
        for m in self.missiles:
            m.update()
            if len(m.trail_2d) >= 2:
                pts = []
                for (lat, lon) in m.trail_2d:
                    sx, sy = self.project_2d_flat_point(lat, lon, w, h)
                    pts.extend([sx, sy])

                if len(pts) >= 4:
                    self.canvas.create_line(pts, fill=m.meta["color"], width=3.5, smooth=True)
                    self.canvas.create_line(pts, fill="#ffffff", width=1.5, smooth=True)
                    hx, hy = pts[-2], pts[-1]
                    self.canvas.create_oval(hx - 5, hy - 5, hx + 5, hy + 5, fill="#ffffff", outline=m.meta["color"], width=2)

            if m.alive:
                active.append(m)
            else:
                self.shockwaves.append(ExplosionShockwave(m.dst, m.meta["color"]))
                if self.sound_enabled.get() and HAS_SOUND and random.random() < 0.30:
                    try:
                        winsound.Beep(320, 35)
                    except Exception:
                        pass
        self.missiles = active

    def draw_2d_shockwaves(self, w, h):
        active = []
        for s in self.shockwaves:
            s.update()
            sx, sy = self.project_2d_flat_point(s.lat, s.lon, w, h)
            r = s.radius
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, outline=s.color, width=2.5)
            self.canvas.create_oval(sx - (r*0.6), sy - (r*0.6), sx + (r*0.6), sy + (r*0.6), outline="#ffffff", width=1.5)
            if s.alive:
                active.append(s)
        self.shockwaves = active

    def draw_hud_overlays(self, w, h):
        d = 30
        c_h = "#1e3a8a"
        self.canvas.create_line(20, 20, 20 + d, 20, fill=c_h, width=2)
        self.canvas.create_line(20, 20, 20, 20 + d, fill=c_h, width=2)
        self.canvas.create_line(w - 20, 20, w - 20 - d, 20, fill=c_h, width=2)
        self.canvas.create_line(w - 20, 20, w - 20, 20 + d, fill=c_h, width=2)
        self.canvas.create_line(20, h - 20, 20 + d, h - 20, fill=c_h, width=2)
        self.canvas.create_line(20, h - 20, 20, h - 20 - d, fill=c_h, width=2)
        self.canvas.create_line(w - 20, h - 20, w - 20 - d, h - 20, fill=c_h, width=2)
        self.canvas.create_line(w - 20, h - 20, w - 20, h - 20 - d, fill=c_h, width=2)

        nav_guide = "🖱️ DRAG TO ROTATE 360° • SCROLL TO ZOOM" if self.view_mode == '3D' else "🗺️ 2D GLOBAL CYBER WARFARE MATRIX"
        self.canvas.create_text(25, h - 35, text=f"{nav_guide} • 180 REAL COUNTRIES ACTIVE",
                                font=('Segoe UI', 8, 'bold'), fill=self.c_neon_cyan, anchor='w')

    # -------------------------------------------------------------
    # High-Density Warfare Traffic Thread
    # -------------------------------------------------------------
    def start_cyber_warfare_traffic_thread(self):
        def worker():
            city_keys = list(CITIES_DB.keys())
            while True:
                if self.defcon_level == 5:
                    interval = random.uniform(1.2, 2.0)
                elif self.defcon_level == 3:
                    interval = random.uniform(0.30, 0.70)
                else:  # DEFCON 1 WAR
                    interval = random.uniform(0.08, 0.20)

                time.sleep(interval)

                src = random.choice(city_keys)
                dst = random.choice([k for k in city_keys if k != src])
                meta = random.choice(ATTACK_TYPES)

                missile = CyberMissile(src, dst, meta, speed=random.uniform(0.016, 0.028))
                self.missiles.append(missile)
                self.log_attack_event(src, dst, meta)

        t = threading.Thread(target=worker, daemon=True)
        t.start()


# =====================================================================
# Main Entry Point
# =====================================================================
if __name__ == '__main__':
    app = CyberWarfareCommandCenter()
    app.mainloop()
