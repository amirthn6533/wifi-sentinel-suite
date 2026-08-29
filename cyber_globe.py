"""
=============================================================================
🌐 3D CYBER ATTACK GLOBAL THREAT MAP (Warfare Globe Edition)
=============================================================================
Author: Antigravity Pair Programmer
Architecture: Mathematical 3D Vector Sphere, Ballistic Bézier Missiles & HUD
Standard: Hollywood Cyber War Command Center (60 FPS Interactive Engine)
=============================================================================
"""

import sys
import os
import time
import math
import random
import threading
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox

# Audio Engine for Radar & Cyber Missile SFX
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# =====================================================================
# Real Geographic Coordinates (Lat, Lon) for 35+ Major Global Hubs
# =====================================================================
CITIES_DB = {
    "US-East (New York)": {"lat": 40.71, "lon": -74.00, "country": "United States", "region": "NA"},
    "US-West (Silicon Valley)": {"lat": 37.38, "lon": -122.08, "country": "United States", "region": "NA"},
    "US-Central (Chicago)": {"lat": 41.87, "lon": -87.62, "country": "United States", "region": "NA"},
    "UK (London)": {"lat": 51.50, "lon": -0.12, "country": "United Kingdom", "region": "EU"},
    "Germany (Frankfurt)": {"lat": 50.11, "lon": 8.68, "country": "Germany", "region": "EU"},
    "France (Paris)": {"lat": 48.85, "lon": 2.35, "country": "France", "region": "EU"},
    "Netherlands (Amsterdam)": {"lat": 52.36, "lon": 4.90, "country": "Netherlands", "region": "EU"},
    "Russia (Moscow)": {"lat": 55.75, "lon": 37.61, "country": "Russia", "region": "EU/ASIA"},
    "Russia (St. Petersburg)": {"lat": 59.93, "lon": 30.33, "country": "Russia", "region": "EU"},
    "Iran (Tehran)": {"lat": 35.68, "lon": 51.38, "country": "Iran", "region": "ME"},
    "Iran (Isfahan)": {"lat": 32.65, "lon": 51.66, "country": "Iran", "region": "ME"},
    "UAE (Dubai)": {"lat": 25.20, "lon": 55.27, "country": "UAE", "region": "ME"},
    "Saudi Arabia (Riyadh)": {"lat": 24.71, "lon": 46.67, "country": "Saudi Arabia", "region": "ME"},
    "China (Beijing)": {"lat": 39.90, "lon": 116.40, "country": "China", "region": "ASIA"},
    "China (Shanghai)": {"lat": 31.23, "lon": 121.47, "country": "China", "region": "ASIA"},
    "China (Shenzhen)": {"lat": 22.54, "lon": 114.05, "country": "China", "region": "ASIA"},
    "Japan (Tokyo)": {"lat": 35.67, "lon": 139.65, "country": "Japan", "region": "ASIA"},
    "South Korea (Seoul)": {"lat": 37.56, "lon": 126.97, "country": "South Korea", "region": "ASIA"},
    "Singapore": {"lat": 1.35, "lon": 103.81, "country": "Singapore", "region": "ASIA"},
    "India (Mumbai)": {"lat": 19.07, "lon": 72.87, "country": "India", "region": "ASIA"},
    "India (Bangalore)": {"lat": 12.97, "lon": 77.59, "country": "India", "region": "ASIA"},
    "Australia (Sydney)": {"lat": -33.86, "lon": 151.20, "country": "Australia", "region": "OC"},
    "Australia (Melbourne)": {"lat": -37.81, "lon": 144.96, "country": "Australia", "region": "OC"},
    "Brazil (São Paulo)": {"lat": -23.55, "lon": -46.63, "country": "Brazil", "region": "SA"},
    "South Africa (Johannesburg)": {"lat": -26.20, "lon": 28.04, "country": "South Africa", "region": "AF"},
    "Canada (Toronto)": {"lat": 43.65, "lon": -79.38, "country": "Canada", "region": "NA"},
    "Israel (Tel Aviv)": {"lat": 32.08, "lon": 34.78, "country": "Israel", "region": "ME"},
    "Turkey (Istanbul)": {"lat": 41.00, "lon": 28.97, "country": "Turkey", "region": "ME/EU"},
    "Ukraine (Kyiv)": {"lat": 50.45, "lon": 30.52, "country": "Ukraine", "region": "EU"},
    "Taiwan (Taipei)": {"lat": 25.03, "lon": 121.56, "country": "Taiwan", "region": "ASIA"},
}

# Simplified Continental Coastlines (lat, lon polylines)
CONTINENTS = [
    # North America
    [(70, -160), (70, -90), (60, -60), (45, -60), (30, -80), (20, -90), (15, -95), (20, -105), (32, -117), (48, -125), (60, -140), (70, -160)],
    # South America
    [(12, -75), (5, -50), (-10, -35), (-25, -45), (-55, -65), (-50, -75), (-20, -70), (0, -80), (12, -75)],
    # Europe
    [(70, 25), (60, 30), (55, 20), (45, 15), (36, -5), (43, -9), (50, -5), (58, 5), (70, 25)],
    # Africa
    [(35, -5), (37, 10), (30, 32), (12, 43), (-10, 40), (-35, 20), (-20, 12), (5, 0), (15, -17), (30, -10), (35, -5)],
    # Asia & Middle East
    [(35, 35), (40, 50), (25, 60), (25, 80), (10, 80), (15, 100), (1, 104), (20, 110), (40, 125), (60, 140), (70, 170), (70, 80), (50, 60), (35, 35)],
    # Australia
    [(-12, 130), (-15, 145), (-28, 153), (-38, 145), (-35, 115), (-20, 115), (-12, 130)]
]

ATTACK_TYPES = [
    {"name": "DDoS Volumetric Flood (1.2 Tbps)", "color": "#ff0055", "tag": "DDoS", "severity": "CRITICAL"},
    {"name": "LockBit 3.0 Ransomware Worm", "color": "#a855f7", "tag": "RANSOMWARE", "severity": "HIGH"},
    {"name": "Zero-Day Remote Code Execution (RCE)", "color": "#ffb703", "tag": "ZERO-DAY", "severity": "CRITICAL"},
    {"name": "SQL Injection & Database Exfiltration", "color": "#00f0ff", "tag": "EXFILTRATION", "severity": "MEDIUM"},
    {"name": "Mirai Botnet SSH Brute-Force", "color": "#00ff9d", "tag": "BOTNET", "severity": "HIGH"},
    {"name": "SCADA / Industrial PLC Override", "color": "#f97316", "tag": "INFRASTRUCTURE", "severity": "EXTREME"},
]


# =====================================================================
# 3D Cyber Missile & Particle Physics
# =====================================================================
class CyberMissile:
    def __init__(self, src_city, dst_city, attack_meta, speed=0.015):
        self.src = src_city
        self.dst = dst_city
        self.meta = attack_meta
        self.progress = 0.0
        self.speed = speed
        self.alive = True
        self.trail = deque(maxlen=10)

        # 3D endpoints on unit sphere
        self.p_start = self.lat_lon_to_cartesian(CITIES_DB[src_city]["lat"], CITIES_DB[src_city]["lon"])
        self.p_end = self.lat_lon_to_cartesian(CITIES_DB[dst_city]["lat"], CITIES_DB[dst_city]["lon"])

        # Midpoint arched into orbit (altitude multiplier)
        mid = (self.p_start + self.p_end) * 0.5
        norm = np.linalg.norm(mid)
        if norm > 1e-4:
            self.p_mid = (mid / norm) * 1.55
        else:
            self.p_mid = np.array([0, 1.55, 0])

    def lat_lon_to_cartesian(self, lat, lon):
        phi = math.radians(lat)
        theta = math.radians(lon)
        x = math.cos(phi) * math.sin(theta)
        y = -math.sin(phi)
        z = math.cos(phi) * math.cos(theta)
        return np.array([x, y, z])

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.alive = False

        # Quadratic 3D Bézier curve
        t = self.progress
        current_pos = (1 - t)**2 * self.p_start + 2 * (1 - t) * t * self.p_mid + t**2 * self.p_end
        self.trail.append(current_pos)


class ExplosionShockwave:
    def __init__(self, city_name, color):
        self.city = city_name
        self.color = color
        self.radius = 2.0
        self.max_radius = 28.0
        self.alpha = 1.0
        self.alive = True
        
        # 3D position
        lat = CITIES_DB[city_name]["lat"]
        lon = CITIES_DB[city_name]["lon"]
        phi = math.radians(lat)
        theta = math.radians(lon)
        self.p3d = np.array([math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta)])

    def update(self):
        self.radius += 1.8
        self.alpha -= 0.06
        if self.alpha <= 0 or self.radius >= self.max_radius:
            self.alive = False


# =====================================================================
# Main 3D Cyber Threat Globe Application
# =====================================================================
class CyberGlobeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌐 3D CYBER ATTACK THREAT GLOBE | Global Warfare Command Center")
        self.geometry("1400x860")
        self.minsize(1150, 750)
        self.configure(bg="#030611")

        # Cyber Colors
        self.c_bg = "#030611"
        self.c_panel = "#080e1e"
        self.c_card = "#0e1830"
        self.c_border = "#1a2a47"
        self.c_neon_cyan = "#00f0ff"
        self.c_neon_green = "#00ff9d"
        self.c_neon_amber = "#ffb703"
        self.c_neon_red = "#ff0055"
        self.c_neon_purple = "#a855f7"
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        # 3D Globe Parameters
        self.radius_3d = 210
        self.yaw = 0.45    # Rotation around Y axis (longitude)
        self.pitch = 0.25  # Rotation around X axis (latitude)
        self.auto_spin = True
        self.spin_speed = 0.006

        # Interactive Drag State
        self.mouse_dragging = False
        self.last_mx = 0
        self.last_my = 0

        # Simulation Objects
        self.missiles = []
        self.shockwaves = []
        self.total_attacks = 14380
        self.defcon_level = 3  # 5: Low, 3: Medium, 1: Global War
        self.sound_enabled = tk.BooleanVar(value=True)

        # Starfield Particles
        self.stars = [(random.randint(0, 1400), random.randint(0, 860), random.choice([1, 2])) for _ in range(75)]

        self.setup_ui()
        self.start_render_loop()
        self.start_attack_generator_thread()

    def setup_ui(self):
        # -------------------------------------------------------------
        # Header
        # -------------------------------------------------------------
        header = tk.Frame(self, bg=self.c_panel, height=65, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=self.c_panel)
        title_box.pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(title_box, text="🌐 3D CYBER THREAT GLOBE", font=('Segoe UI', 14, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_box, text="Global Vector Telemetry & Ballistic Cyber Warfare Simulator", font=('Segoe UI', 9),
                 bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT)

        # DEFCON Threat Selector
        defcon_box = tk.Frame(header, bg=self.c_panel)
        defcon_box.pack(side=tk.RIGHT, padx=20, pady=14)

        tk.Label(defcon_box, text="DEFCON LEVEL:", font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT, padx=(0, 8))

        self.btn_d5 = tk.Button(defcon_box, text="DEFCON 5", bg=self.c_card, fg=self.c_neon_green,
                                font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=8, pady=3, cursor='hand2',
                                command=lambda: self.set_defcon(5))
        self.btn_d5.pack(side=tk.LEFT, padx=2)

        self.btn_d3 = tk.Button(defcon_box, text="DEFCON 3", bg=self.c_neon_amber, fg="#030611",
                                font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=8, pady=3, cursor='hand2',
                                command=lambda: self.set_defcon(3))
        self.btn_d3.pack(side=tk.LEFT, padx=2)

        self.btn_d1 = tk.Button(defcon_box, text="DEFCON 1 (WAR)", bg=self.c_card, fg=self.c_neon_red,
                                font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=8, pady=3, cursor='hand2',
                                command=lambda: self.set_defcon(1))
        self.btn_d1.pack(side=tk.LEFT, padx=2)

        # -------------------------------------------------------------
        # Main Split Workspace (Center: 3D Canvas | Right: War Room & Controls)
        # -------------------------------------------------------------
        main_box = tk.Frame(self, bg=self.c_bg)
        main_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Center Column: 3D Globe Canvas
        globe_frame = tk.Frame(main_box, bg="#02040b", highlightthickness=1, highlightbackground=self.c_border)
        globe_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(globe_frame, bg="#02040b", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Canvas Mouse Bindings for 3D Drag & Zoom
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # Right Column: Cyber Warfare Command Center & Telemetry (Width: 430px)
        right_col = tk.Frame(main_box, bg=self.c_panel, width=430, highlightthickness=1, highlightbackground=self.c_border)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 0))
        right_col.pack_propagate(False)
        self.build_war_room_panel(right_col)

    def build_war_room_panel(self, parent):
        pad = 12

        # Card 1: Interactive Manual Strike Launcher
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
        self.combo_dst.current(9)  # Iran (Tehran)
        self.combo_dst.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        f_atk = tk.Frame(strike_card, bg=self.c_card)
        f_atk.pack(fill=tk.X, pady=2)
        tk.Label(f_atk, text="Payload:", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted, width=7, anchor='w').pack(side=tk.LEFT)
        self.combo_atk = ttk.Combobox(f_atk, values=[a["name"] for a in ATTACK_TYPES], state="readonly", font=('Segoe UI', 8))
        self.combo_atk.current(0)
        self.combo_atk.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        btn_fire = tk.Button(strike_card, text="⚡ LAUNCH CYBER MISSILE", bg=self.c_neon_red, fg="#ffffff",
                             font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=5, cursor='hand2',
                             activebackground="#b91c1c", activeforeground="#ffffff",
                             command=self.fire_manual_missile)
        btn_fire.pack(fill=tk.X, pady=(8, 2))

        # Card 2: Live Attack Metrics
        stats_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=12, pady=10)
        stats_card.pack(fill=tk.X, padx=pad, pady=6)

        tk.Label(stats_card, text="GLOBAL ATTACK VELOCITY", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_muted).pack(anchor='w')

        self.lbl_attack_count = tk.Label(stats_card, text="14,380", font=('Consolas', 22, 'bold'), bg=self.c_card, fg=self.c_neon_cyan)
        self.lbl_attack_count.pack(anchor='w', pady=(2, 0))

        tk.Label(stats_card, text="Attacks Intercepted Worldwide | Peak Bandwidth: 1.84 Tbps", font=('Segoe UI', 8),
                 bg=self.c_card, fg=self.c_neon_green).pack(anchor='w')

        # Card 3: Real-Time Cyber War Telemetry Feed
        feed_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=10, pady=8)
        feed_card.pack(fill=tk.BOTH, expand=True, padx=pad, pady=6)

        tk.Label(feed_card, text="📡 LIVE WAR ROOM TELEMETRY STREAM", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_neon_cyan).pack(anchor='w')

        self.feed_list = tk.Listbox(feed_card, bg="#030611", fg=self.c_text, font=('Consolas', 8),
                                    highlightthickness=0, selectbackground=self.c_panel, bd=0)
        self.feed_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        # Bottom Bar: Controls & Sound Toggle
        ctrl_bar = tk.Frame(parent, bg=self.c_panel)
        ctrl_bar.pack(fill=tk.X, padx=pad, pady=(6, 12), side=tk.BOTTOM)

        tk.Checkbutton(ctrl_bar, text="🔊 Radar Audio SFX", variable=self.sound_enabled,
                       bg=self.c_panel, fg=self.c_text, selectcolor=self.c_card,
                       font=('Segoe UI', 9, 'bold'), activebackground=self.c_panel).pack(side=tk.LEFT)

        btn_spin = tk.Button(ctrl_bar, text="🔄 Toggle Auto-Spin", bg=self.c_border, fg=self.c_neon_cyan,
                             font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=8, pady=3, cursor='hand2',
                             command=self.toggle_spin)
        btn_spin.pack(side=tk.RIGHT)

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
        missile = CyberMissile(src, dst, meta, speed=0.02)
        self.missiles.append(missile)
        self.log_attack_event(src, dst, meta)

        if self.sound_enabled.get() and HAS_SOUND:
            try:
                winsound.Beep(1800, 30)
            except Exception:
                pass

    def log_attack_event(self, src, dst, meta):
        t_str = time.strftime('%H:%M:%S')
        log_entry = f"[{t_str}] ➔ [{meta['tag']}] {src} ➔ {dst}"
        self.feed_list.insert(0, log_entry)
        if self.feed_list.size() > 50:
            self.feed_list.delete(50, tk.END)

        self.total_attacks += random.randint(1, 5)
        self.lbl_attack_count.config(text=f"{self.total_attacks:,}")

    # -------------------------------------------------------------
    # Mouse Interaction: 3D Globe Drag & Zoom
    # -------------------------------------------------------------
    def on_mouse_down(self, event):
        self.mouse_dragging = True
        self.last_mx = event.x
        self.last_my = event.y

    def on_mouse_drag(self, event):
        if self.mouse_dragging:
            dx = event.x - self.last_mx
            dy = event.y - self.last_my
            self.yaw += dx * 0.008
            self.pitch += dy * 0.008
            # Clamp pitch to avoid gimbal flipping
            self.pitch = max(-math.pi * 0.45, min(math.pi * 0.45, self.pitch))
            self.last_mx = event.x
            self.last_my = event.y

    def on_mouse_up(self, event):
        self.mouse_dragging = False

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.radius_3d = min(320, self.radius_3d + 15)
        else:
            self.radius_3d = max(130, self.radius_3d - 15)

    # -------------------------------------------------------------
    # 3D Matrix Transformation & Perspective Projection
    # -------------------------------------------------------------
    def project_3d_point(self, p, cx, cy):
        """Applies 3D Euler rotation (Pitch & Yaw) and perspective projection."""
        x, y, z = p

        # 1. Rotation around X axis (Pitch)
        cos_p = math.cos(self.pitch)
        sin_p = math.sin(self.pitch)
        y1 = y * cos_p - z * sin_p
        z1 = y * sin_p + z * cos_p

        # 2. Rotation around Y axis (Yaw)
        cos_y = math.cos(self.yaw)
        sin_y = math.sin(self.yaw)
        x2 = x * cos_y + z1 * sin_y
        z2 = -x * sin_y + z1 * cos_y

        # Perspective factor
        dist = 500.0
        fov = dist / (dist + z2 * self.radius_3d + 20.0)

        sx = cx + x2 * self.radius_3d * fov
        sy = cy + y1 * self.radius_3d * fov

        # z2 > 0 means visible on front hemisphere
        is_visible = (z2 > -0.15)
        return sx, sy, z2, is_visible

    # -------------------------------------------------------------
    # 60 FPS Render Loop
    # -------------------------------------------------------------
    def start_render_loop(self):
        def loop():
            self.render_frame()
            if self.auto_spin and not self.mouse_dragging:
                self.yaw += self.spin_speed
            self.after(20, loop)

        self.after(100, loop)

    def render_frame(self):
        self.canvas.delete("all")
        w = max(100, self.canvas.winfo_width())
        h = max(100, self.canvas.winfo_height())
        cx = w / 2
        cy = h / 2

        # 1. Draw Starfield Background
        for (sx, sy, size) in self.stars:
            self.canvas.create_oval(sx, sy, sx + size, sy + size, fill="#1e293b", outline="")

        # 2. Draw 3D Holographic Sphere Aura Ring
        r_aura = self.radius_3d + 12
        self.canvas.create_oval(cx - r_aura, cy - r_aura, cx + r_aura, cy + r_aura,
                                outline="#0f2b48", width=1.5)
        self.canvas.create_oval(cx - self.radius_3d, cy - self.radius_3d, cx + self.radius_3d, cy + self.radius_3d,
                                outline="#00f0ff", width=2)

        # 3. Draw 3D Latitude & Longitude Wireframe Grid
        self.draw_grid_mesh(cx, cy)

        # 4. Draw Continents & Landmass Coastlines
        self.draw_continents(cx, cy)

        # 5. Draw City Nodes
        self.draw_cities(cx, cy)

        # 6. Update and Draw 3D Laser Ballistic Missiles
        self.draw_missiles(cx, cy)

        # 7. Update and Draw Shockwaves
        self.draw_shockwaves(cx, cy)

        # 8. Draw HUD Crosshairs and Scanlines
        self.draw_hud_overlays(cx, cy, w, h)

    def draw_grid_mesh(self, cx, cy):
        # Latitudes
        for lat in range(-60, 70, 30):
            pts = []
            phi = math.radians(lat)
            for lon in range(0, 370, 15):
                theta = math.radians(lon)
                p = np.array([math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta)])
                sx, sy, z, vis = self.project_3d_point(p, cx, cy)
                if vis:
                    pts.extend([sx, sy])
                else:
                    if len(pts) >= 4:
                        self.canvas.create_line(pts, fill="#0c1e38", width=1, smooth=True)
                    pts = []
            if len(pts) >= 4:
                self.canvas.create_line(pts, fill="#0c1e38", width=1, smooth=True)

    def draw_continents(self, cx, cy):
        for poly in CONTINENTS:
            pts = []
            for (lat, lon) in poly:
                phi = math.radians(lat)
                theta = math.radians(lon)
                p = np.array([math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta)])
                sx, sy, z, vis = self.project_3d_point(p, cx, cy)
                if vis:
                    pts.extend([sx, sy])
                else:
                    if len(pts) >= 4:
                        self.canvas.create_line(pts, fill="#143152", width=1.5, smooth=True)
                    pts = []
            if len(pts) >= 4:
                self.canvas.create_line(pts, fill="#143152", width=1.5, smooth=True)

    def draw_cities(self, cx, cy):
        for name, data in CITIES_DB.items():
            phi = math.radians(data["lat"])
            theta = math.radians(data["lon"])
            p = np.array([math.cos(phi) * math.sin(theta), -math.sin(phi), math.cos(phi) * math.cos(theta)])
            sx, sy, z, vis = self.project_3d_point(p, cx, cy)

            if vis and z > 0.05:
                # Glowing node
                self.canvas.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill=self.c_neon_cyan, outline="#ffffff")
                if z > 0.35:
                    c_short = name.split("(")[0].strip()
                    self.canvas.create_text(sx + 6, sy - 4, text=c_short, font=('Consolas', 7, 'bold'),
                                            fill="#67e8f9", anchor='w')

    def draw_missiles(self, cx, cy):
        active = []
        for m in self.missiles:
            m.update()
            if len(m.trail) >= 2:
                pts = []
                for p3d in m.trail:
                    sx, sy, z, vis = self.project_3d_point(p3d, cx, cy)
                    if vis:
                        pts.extend([sx, sy])

                if len(pts) >= 4:
                    self.canvas.create_line(pts, fill=m.meta["color"], width=2, smooth=True)
                    # Glowing missile head
                    hx, hy = pts[-2], pts[-1]
                    self.canvas.create_oval(hx - 4, hy - 4, hx + 4, hy + 4, fill="#ffffff", outline=m.meta["color"], width=2)

            if m.alive:
                active.append(m)
            else:
                # Impact explosion!
                self.shockwaves.append(ExplosionShockwave(m.dst, m.meta["color"]))
                if self.sound_enabled.get() and HAS_SOUND and random.random() < 0.35:
                    try:
                        winsound.Beep(350, 40)
                    except Exception:
                        pass

        self.missiles = active

    def draw_shockwaves(self, cx, cy):
        active = []
        for s in self.shockwaves:
            s.update()
            sx, sy, z, vis = self.project_3d_point(s.p3d, cx, cy)
            if vis and z > 0.0:
                r = s.radius
                self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, outline=s.color, width=2)
            if s.alive:
                active.append(s)
        self.shockwaves = active

    def draw_hud_overlays(self, cx, cy, w, h):
        # Corner HUD brackets
        d = 30
        c_h = "#1a365d"
        # Top-Left
        self.canvas.create_line(20, 20, 20 + d, 20, fill=c_h, width=2)
        self.canvas.create_line(20, 20, 20, 20 + d, fill=c_h, width=2)
        # Top-Right
        self.canvas.create_line(w - 20, 20, w - 20 - d, 20, fill=c_h, width=2)
        self.canvas.create_line(w - 20, 20, w - 20, 20 + d, fill=c_h, width=2)
        # Bottom-Left
        self.canvas.create_line(20, h - 20, 20 + d, h - 20, fill=c_h, width=2)
        self.canvas.create_line(20, h - 20, 20, h - 20 - d, fill=c_h, width=2)
        # Bottom-Right
        self.canvas.create_line(w - 20, h - 20, w - 20 - d, h - 20, fill=c_h, width=2)
        self.canvas.create_line(w - 20, h - 20, w - 20, h - 20 - d, fill=c_h, width=2)

        # Bottom-left instructions
        self.canvas.create_text(25, h - 35, text="🖱️ DRAG TO ROTATE 360° • SCROLL TO ZOOM",
                                font=('Segoe UI', 8, 'bold'), fill=self.c_muted, anchor='w')

    # -------------------------------------------------------------
    # Automated Simulated Warfare Traffic Generator Thread
    # -------------------------------------------------------------
    def start_attack_generator_thread(self):
        def worker():
            city_keys = list(CITIES_DB.keys())
            while True:
                if self.defcon_level == 5:
                    interval = random.uniform(1.8, 3.2)
                elif self.defcon_level == 3:
                    interval = random.uniform(0.5, 1.1)
                else:  # DEFCON 1
                    interval = random.uniform(0.12, 0.28)

                time.sleep(interval)

                src = random.choice(city_keys)
                dst = random.choice([k for k in city_keys if k != src])
                meta = random.choice(ATTACK_TYPES)

                missile = CyberMissile(src, dst, meta, speed=random.uniform(0.012, 0.022))
                self.missiles.append(missile)
                self.log_attack_event(src, dst, meta)

        t = threading.Thread(target=worker, daemon=True)
        t.start()


# =====================================================================
# Main Launch Entry
# =====================================================================
if __name__ == '__main__':
    app = CyberGlobeApp()
    app.mainloop()
