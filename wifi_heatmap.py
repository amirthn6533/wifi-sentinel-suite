"""
Wi-Fi 2D/3D Heatmap & RF Raytracer Suite
Author: Antigravity Pair Programmer
Edition: Cyberpunk Neon HUD & Wave Physics Engine
"""

import sys
import os
import math
import time
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from collections import deque
import numpy as np

# Matplotlib integration
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm

# PIL for floorplan image import
try:
    from PIL import Image, ImageTk, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Sound effects
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# =====================================================================
# Wall Materials & Physical RF Attenuation Database (dB at 2.4G & 5G)
# =====================================================================
WALL_MATERIALS = {
    "Concrete Wall": {"color": "#64748b", "width": 6, "loss_2g": 12.0, "loss_5g": 18.0, "desc": "Thick Reinforced Concrete"},
    "Brick Wall":    {"color": "#b45309", "width": 5, "loss_2g": 7.0,  "loss_5g": 11.0, "desc": "Standard Masonry Brick"},
    "Drywall":       {"color": "#94a3b8", "width": 3, "loss_2g": 3.0,  "loss_5g": 4.5,  "desc": "Interior Plasterboard"},
    "Metal / Shield":{"color": "#ef4444", "width": 6, "loss_2g": 26.0, "loss_5g": 32.0, "desc": "Heavy Steel / Metal Door"},
    "Glass Window":  {"color": "#38bdf8", "width": 2, "loss_2g": 2.0,  "loss_5g": 3.0,  "desc": "Standard Window Glass"},
    "Wood Door":     {"color": "#d97706", "width": 4, "loss_2g": 4.0,  "loss_5g": 6.0,  "desc": "Solid / Hollow Wooden Door"}
}


# =====================================================================
# Live Wi-Fi Hardware Scanner Interface
# =====================================================================
class LiveWifiSampler:
    @staticmethod
    def get_live_rssi(adapter_name=None):
        """Fetches active Wi-Fi link signal strength (%) and converts to dBm."""
        try:
            raw = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'interfaces'],
                encoding='cp1252',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            cur_signal = None
            cur_ssid = "Unknown"
            cur_bssid = "N/A"
            for line in raw.splitlines():
                line_s = line.strip()
                if line_s.startswith("SSID") and ":" in line_s and not line_s.startswith("BSSID"):
                    cur_ssid = line_s.split(":", 1)[1].strip()
                elif line_s.startswith("BSSID") and ":" in line_s:
                    cur_bssid = line_s.split(":", 1)[1].strip()
                elif line_s.startswith("Signal") and ":" in line_s:
                    val_str = line_s.split(":", 1)[1].replace("%", "").strip()
                    try:
                        cur_signal = int(val_str)
                    except ValueError:
                        pass
            
            if cur_signal is not None:
                # RSSI conversion: 100% ≈ -30 dBm, 0% ≈ -100 dBm
                dbm = -100 + (cur_signal * 0.7)
                return {
                    "connected": True,
                    "signal_pct": cur_signal,
                    "signal_dbm": round(dbm, 1),
                    "ssid": cur_ssid,
                    "bssid": cur_bssid
                }
        except Exception:
            pass

        return {
            "connected": False,
            "signal_pct": 0,
            "signal_dbm": -100.0,
            "ssid": "Disconnected",
            "bssid": "N/A"
        }


# =====================================================================
# Fast Geometric Utilities for Raytracing
# =====================================================================
def segments_intersect(p1, p2, p3, p4):
    """Checks if segment p1-p2 intersects segment p3-p4."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if abs(denom) < 1e-9:
        return False, None

    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom

    if 0.0 <= ua <= 1.0 and 0.0 <= ub <= 1.0:
        ix = x1 + ua * (x2 - x1)
        iy = y1 + ua * (y2 - y1)
        return True, (ix, iy)
    return False, None


def line_intersection_vectorized(p1, p2_grid_x, p2_grid_y, w_x1, w_y1, w_x2, w_y2):
    """Vectorized check for rays from single router point p1=(rx, ry) to all grid points (GX, GY)."""
    rx, ry = p1
    dx = p2_grid_x - rx
    dy = p2_grid_y - ry
    
    wx = w_x2 - w_x1
    wy = w_y2 - w_y1
    
    denom = wy * dx - wx * dy
    # Avoid zero division
    denom[np.abs(denom) < 1e-9] = 1e-9
    
    ua = (wx * (ry - w_y1) - wy * (rx - w_x1)) / denom
    ub = (dx * (ry - w_y1) - dy * (rx - w_x1)) / denom
    
    intersect = (ua >= 0.0) & (ua <= 1.0) & (ub >= 0.0) & (ub <= 1.0)
    return intersect


# =====================================================================
# Main Application Window
# =====================================================================
class WifiHeatmapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🗺️ WI-FI CYBER SUITE | 2D/3D Heatmap & RF Raytracer")
        self.geometry("1420x860")
        self.minsize(1200, 750)
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
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        # State Data
        self.scale_m_per_px = 0.05  # 1 pixel = 5 cm => 1000px = 50m
        self.band_freq = "2.4 GHz"  # or 5.0 GHz
        self.tx_power_dbm = 20.0
        self.antenna_gain_dbi = 5.0
        self.active_tool = tk.StringVar(value="wall")  # wall, router, survey, delete, probe
        self.active_material = tk.StringVar(value="Concrete Wall")
        self.colormap_name = tk.StringVar(value="plasma")
        self.sim_mode = tk.StringVar(value="simulation")  # simulation or survey
        self.show_rays = tk.BooleanVar(value=True)
        self.show_contours = tk.BooleanVar(value=True)
        self.live_scan_active = False

        # Physical objects
        # Walls: list of dicts: {'x1':..., 'y1':..., 'x2':..., 'y2':..., 'mat':..., 'id':...}
        self.walls = []
        # Router: {'x': float, 'y': float} or None
        self.router = {'x': 320, 'y': 280}
        # Survey Points: list of dicts: {'x': float, 'y': float, 'dbm': float, 'ssid': str}
        self.survey_points = []
        
        # Temp drawing state
        self.drawing_wall_start = None
        self.temp_wall_id = None
        self.hover_probe_coord = None
        self.optimal_router_pos = None

        # Cached calculation grids
        self.grid_res = 12  # Step in pixels for simulation grid
        self.sim_heatmap_data = None
        self.grid_X = None
        self.grid_Y = None

        # Background Floorplan Image
        self.bg_image_raw = None
        self.bg_image_tk = None
        self.bg_image_id = None

        self.setup_ui()
        self.load_preset_apartment()
        self.recompute_heatmap()

    # -----------------------------------------------------------------
    # UI Layout Construction
    # -----------------------------------------------------------------
    def setup_ui(self):
        # Top Header Bar
        header = tk.Frame(self, bg=self.c_panel, height=62, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        # Title & Badges
        title_frame = tk.Frame(header, bg=self.c_panel)
        title_frame.pack(side=tk.LEFT, padx=18, pady=10)

        tk.Label(title_frame, text="🗺️ WI-FI HEATMAP & RF RAYTRACER", font=('Segoe UI', 13, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_frame, text="Wave Physics & Spatial Matrix", font=('Segoe UI', 9),
                 bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT)

        # Live Wi-Fi Hardware Status in Header
        self.lbl_hw_status = tk.Label(header, text="📡 Live Wi-Fi: Scanning...", font=('Segoe UI', 9, 'bold'),
                                      bg=self.c_card, fg=self.c_neon_green, padx=12, pady=4,
                                      highlightthickness=1, highlightbackground=self.c_border)
        self.lbl_hw_status.pack(side=tk.RIGHT, padx=18, pady=14)

        # Main Workspace Splitter
        main_box = tk.Frame(self, bg=self.c_bg)
        main_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Control & Tool Panel (Width: 320px)
        ctrl_panel = tk.Frame(main_box, bg=self.c_panel, width=320, highlightthickness=1, highlightbackground=self.c_border)
        ctrl_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        ctrl_panel.pack_propagate(False)
        self.build_control_panel(ctrl_panel)

        # Right Tabbed Viewer (2D Floorplan Canvas & 3D Spatial Surface)
        view_panel = tk.Frame(main_box, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border)
        view_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.build_view_tabs(view_panel)

    def build_control_panel(self, parent):
        # Scrollable container for control panel
        canvas = tk.Canvas(parent, bg=self.c_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.c_panel)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=310)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        pad = 12

        # -------------------------------------------------------------
        # Section 1: Tool Selector
        # -------------------------------------------------------------
        self.create_section_label(scrollable_frame, "🛠️ INTERACTIVE TOOLS")
        tool_frame = tk.Frame(scrollable_frame, bg=self.c_panel)
        tool_frame.pack(fill=tk.X, padx=pad, pady=4)

        tools = [
            ("🧱 Draw Wall", "wall", self.c_neon_cyan),
            ("📡 Move Router", "router", self.c_neon_green),
            ("🚶 Live Survey", "survey", self.c_neon_amber),
            ("🔍 Probe Signal", "probe", "#38bdf8"),
            ("🗑️ Delete Item", "delete", self.c_neon_red),
        ]
        for idx, (label, mode, color) in enumerate(tools):
            btn = tk.Radiobutton(
                tool_frame, text=label, value=mode, variable=self.active_tool,
                indicatoron=0, selectcolor=self.c_card, fg=self.c_text, bg=self.c_panel,
                font=('Segoe UI', 9, 'bold'), activebackground=self.c_card,
                highlightthickness=1, highlightbackground=self.c_border,
                cursor='hand2', padx=8, pady=5, command=self.on_tool_changed
            )
            btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=2, pady=2)
        tool_frame.columnconfigure(0, weight=1)
        tool_frame.columnconfigure(1, weight=1)

        # Material Picker for Walls
        mat_frame = tk.Frame(scrollable_frame, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border)
        mat_frame.pack(fill=tk.X, padx=pad, pady=6)
        tk.Label(mat_frame, text="Wall Material:", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_muted).pack(anchor='w', padx=8, pady=(4, 2))
        
        mat_cb = ttk.Combobox(mat_frame, textvariable=self.active_material, values=list(WALL_MATERIALS.keys()), state="readonly")
        mat_cb.pack(fill=tk.X, padx=8, pady=(0, 6))

        # -------------------------------------------------------------
        # Section 2: RF Physics Parameters
        # -------------------------------------------------------------
        self.create_section_label(scrollable_frame, "⚡ RF PROPAGATION SETTINGS")
        rf_frame = tk.Frame(scrollable_frame, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=10, pady=8)
        rf_frame.pack(fill=tk.X, padx=pad, pady=4)

        # Band Selector
        tk.Label(rf_frame, text="Frequency Band:", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted).pack(anchor='w')
        band_box = tk.Frame(rf_frame, bg=self.c_card)
        band_box.pack(fill=tk.X, pady=(2, 6))
        for b in ["2.4 GHz", "5.0 GHz"]:
            rb = tk.Radiobutton(band_box, text=b, value=b, variable=tk.StringVar(value=self.band_freq),
                                command=lambda val=b: self.set_band(val),
                                bg=self.c_card, fg=self.c_text, selectcolor=self.c_panel,
                                font=('Segoe UI', 8, 'bold'))
            rb.pack(side=tk.LEFT, padx=6)

        # TX Power Slider
        tk.Label(rf_frame, text="Router TX Power (dBm):", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted).pack(anchor='w')
        self.scale_tx = tk.Scale(rf_frame, from_=10, to=30, orient=tk.HORIZONTAL, bg=self.c_card, fg=self.c_neon_cyan,
                                 highlightthickness=0, troughcolor=self.c_panel, command=self.on_param_changed)
        self.scale_tx.set(self.tx_power_dbm)
        self.scale_tx.pack(fill=tk.X, pady=(0, 6))

        # Visual Toggles
        tk.Checkbutton(rf_frame, text="Render Ray Bouncing Beams", variable=self.show_rays,
                       bg=self.c_card, fg=self.c_text, selectcolor=self.c_panel,
                       activebackground=self.c_card, command=self.redraw_canvas).pack(anchor='w')
        tk.Checkbutton(rf_frame, text="Draw Signal Contour Lines", variable=self.show_contours,
                       bg=self.c_card, fg=self.c_text, selectcolor=self.c_panel,
                       activebackground=self.c_card, command=self.redraw_canvas).pack(anchor='w')

        # Colormap Picker
        tk.Label(rf_frame, text="Heat Colormap:", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted).pack(anchor='w', pady=(4, 0))
        cmap_cb = ttk.Combobox(rf_frame, textvariable=self.colormap_name,
                               values=["plasma", "turbo", "inferno", "viridis", "coolwarm", "jet"], state="readonly")
        cmap_cb.pack(fill=tk.X, pady=(2, 4))
        cmap_cb.bind("<<ComboboxSelected>>", lambda e: self.redraw_canvas())

        # -------------------------------------------------------------
        # Section 3: AI Optimal Router Locator
        # -------------------------------------------------------------
        self.create_section_label(scrollable_frame, "🤖 AI ROUTER OPTIMIZER")
        ai_frame = tk.Frame(scrollable_frame, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=10, pady=8)
        ai_frame.pack(fill=tk.X, padx=pad, pady=4)

        tk.Label(ai_frame, text="Find the best spot for your router to eliminate dead zones.",
                 font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted, wraplength=270, justify=tk.LEFT).pack(anchor='w', pady=(0, 6))

        btn_ai_opt = tk.Button(ai_frame, text="⚡ Calculate Optimal AP Spot", bg=self.c_neon_purple, fg="#ffffff",
                               font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                               activebackground="#9333ea", activeforeground="#ffffff",
                               command=self.run_ai_router_optimizer)
        btn_ai_opt.pack(fill=tk.X)

        # -------------------------------------------------------------
        # Section 4: Preset Templates & Floorplans
        # -------------------------------------------------------------
        self.create_section_label(scrollable_frame, "📐 FLOORPLAN TEMPLATES")
        preset_frame = tk.Frame(scrollable_frame, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=10, pady=8)
        preset_frame.pack(fill=tk.X, padx=pad, pady=4)

        presets = [
            ("🏢 2-Bedroom Apartment", self.load_preset_apartment),
            ("🏛️ Multi-Room Office", self.load_preset_office),
            ("🏠 Open-Space Loft", self.load_preset_loft),
            ("🧹 Clear Floorplan", self.clear_floorplan),
        ]
        for name, cmd in presets:
            btn = tk.Button(preset_frame, text=name, bg=self.c_panel, fg=self.c_text,
                            font=('Segoe UI', 8), relief=tk.FLAT, pady=3, cursor='hand2',
                            activebackground=self.c_border, command=cmd)
            btn.pack(fill=tk.X, pady=2)

        btn_import_img = tk.Button(preset_frame, text="🖼️ Import Floorplan Image...", bg=self.c_border, fg=self.c_neon_cyan,
                                   font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, pady=4, cursor='hand2',
                                   command=self.import_floorplan_image)
        btn_import_img.pack(fill=tk.X, pady=(6, 2))

        # -------------------------------------------------------------
        # Section 5: Coverage Metrics & Export
        # -------------------------------------------------------------
        self.create_section_label(scrollable_frame, "📊 COVERAGE DIAGNOSTICS")
        diag_frame = tk.Frame(scrollable_frame, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=10, pady=8)
        diag_frame.pack(fill=tk.X, padx=pad, pady=4)

        self.lbl_metric_good = tk.Label(diag_frame, text="🟢 High Speed Coverage (> -65 dBm): 0%", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_neon_green)
        self.lbl_metric_good.pack(anchor='w', pady=1)

        self.lbl_metric_fair = tk.Label(diag_frame, text="🟡 Acceptable (-65 to -80 dBm): 0%", font=('Segoe UI', 8), bg=self.c_card, fg=self.c_neon_amber)
        self.lbl_metric_fair.pack(anchor='w', pady=1)

        self.lbl_metric_dead = tk.Label(diag_frame, text="🔴 Dead Zone (< -80 dBm): 0%", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_neon_red)
        self.lbl_metric_dead.pack(anchor='w', pady=1)

        btn_export = tk.Button(diag_frame, text="💾 Export Heatmap Image (PNG)", bg=self.c_neon_cyan, fg="#050811",
                               font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                               activebackground="#0284c7", activeforeground="#ffffff",
                               command=self.export_report)
        btn_export.pack(fill=tk.X, pady=(8, 2))

    def create_section_label(self, parent, text):
        lbl = tk.Label(parent, text=text, font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_neon_cyan)
        lbl.pack(anchor='w', padx=12, pady=(12, 4))

    def build_view_tabs(self, parent):
        # Tab Control
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Cyber.TNotebook", background=self.c_panel, borderwidth=0)
        style.configure("Cyber.TNotebook.Tab", background=self.c_card, foreground=self.c_text,
                        font=('Segoe UI', 9, 'bold'), padding=[16, 6])
        style.map("Cyber.TNotebook.Tab",
                  background=[("selected", self.c_panel)],
                  foreground=[("selected", self.c_neon_cyan)])

        self.tabs = ttk.Notebook(parent, style="Cyber.TNotebook")
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Tab 1: 2D Interactive Floorplan & Heatmap
        tab_2d = tk.Frame(self.tabs, bg=self.c_bg)
        self.tabs.add(tab_2d, text="🗺️ 2D Interactive Heatmap")

        # Tab 2: 3D Spatial Topography & Surface Mesh
        tab_3d = tk.Frame(self.tabs, bg=self.c_bg)
        self.tabs.add(tab_3d, text="🌐 3D Spatial Elevation Mesh")

        self.setup_2d_view(tab_2d)
        self.setup_3d_view(tab_3d)

        # Re-render 3D tab when switched
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def setup_2d_view(self, parent):
        # Status & Legend bar atop 2D canvas
        bar = tk.Frame(parent, bg=self.c_panel, height=32, highlightthickness=1, highlightbackground=self.c_border)
        bar.pack(fill=tk.X, side=tk.TOP)
        bar.pack_propagate(False)

        self.lbl_probe = tk.Label(bar, text="Cursor Probe: X: 0m, Y: 0m | Estimated Signal: -- dBm",
                                  font=('Consolas', 9), bg=self.c_panel, fg=self.c_neon_cyan)
        self.lbl_probe.pack(side=tk.LEFT, padx=12)

        legend_text = "Legend: 🟢 Strong (-30 to -60 dBm) | 🟡 Moderate (-60 to -75 dBm) | 🔴 Weak/Dead (< -80 dBm)"
        tk.Label(bar, text=legend_text, font=('Segoe UI', 8), bg=self.c_panel, fg=self.c_muted).pack(side=tk.RIGHT, padx=12)

        # Interactive Canvas
        self.canvas_w = 900
        self.canvas_h = 680
        self.canvas = tk.Canvas(parent, bg="#050811", highlightthickness=0, width=self.canvas_w, height=self.canvas_h)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Canvas Event Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def setup_3d_view(self, parent):
        self.fig_3d = Figure(figsize=(7, 5), dpi=100, facecolor="#050811")
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.ax_3d.set_facecolor("#050811")
        
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, master=parent)
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # -----------------------------------------------------------------
    # Presets & Floorplans
    # -----------------------------------------------------------------
    def clear_floorplan(self):
        self.walls.clear()
        self.survey_points.clear()
        self.optimal_router_pos = None
        self.recompute_heatmap()

    def load_preset_apartment(self):
        """Loads a realistic 2-Bedroom Modern Apartment layout."""
        self.clear_floorplan()
        w, h = 800, 600
        cx, cy = 50, 40

        # Outer walls (Heavy Concrete)
        mat_c = "Concrete Wall"
        self.add_wall_line(cx, cy, cx + 700, cy, mat_c)
        self.add_wall_line(cx + 700, cy, cx + 700, cy + 500, mat_c)
        self.add_wall_line(cx + 700, cy + 500, cx, cy + 500, mat_c)
        self.add_wall_line(cx, cy + 500, cx, cy, mat_c)

        # Interior Walls (Brick & Drywall)
        mat_b = "Brick Wall"
        mat_d = "Drywall"
        mat_g = "Glass Window"
        mat_m = "Metal / Shield"

        # Master Bedroom
        self.add_wall_line(cx, cy + 260, cx + 280, cy + 260, mat_b)
        self.add_wall_line(cx + 280, cy, cx + 280, cy + 260, mat_b)

        # Balcony Glass Window
        self.add_wall_line(cx + 60, cy, cx + 220, cy, mat_g)

        # Second Bedroom
        self.add_wall_line(cx + 420, cy, cx + 420, cy + 240, mat_d)
        self.add_wall_line(cx + 420, cy + 240, cx + 700, cy + 240, mat_d)

        # Bathroom (Dense concrete & pipes)
        self.add_wall_line(cx, cy + 380, cx + 180, cy + 380, mat_c)
        self.add_wall_line(cx + 180, cy + 380, cx + 180, cy + 500, mat_c)

        # Kitchen Area & Metal Appliance Wall
        self.add_wall_line(cx + 480, cy + 360, cx + 700, cy + 360, mat_d)
        self.add_wall_line(cx + 480, cy + 360, cx + 480, cy + 500, mat_m)

        # Place Router in Living Room
        self.router = {'x': cx + 340, 'y': cy + 320}
        self.recompute_heatmap()

    def load_preset_office(self):
        """Loads a multi-room corporate office with server room and meeting hall."""
        self.clear_floorplan()
        w, h = 800, 600
        cx, cy = 50, 40

        mat_c = "Concrete Wall"
        mat_d = "Drywall"
        mat_g = "Glass Window"
        mat_m = "Metal / Shield"

        # Outer Frame
        self.add_wall_line(cx, cy, cx + 700, cy, mat_c)
        self.add_wall_line(cx + 700, cy, cx + 700, cy + 500, mat_c)
        self.add_wall_line(cx + 700, cy + 500, cx, cy + 500, mat_c)
        self.add_wall_line(cx, cy + 500, cx, cy, mat_c)

        # Server Room (Shielded Cage)
        self.add_wall_line(cx + 20, cy + 20, cx + 180, cy + 20, mat_m)
        self.add_wall_line(cx + 180, cy + 20, cx + 180, cy + 180, mat_m)
        self.add_wall_line(cx + 180, cy + 180, cx + 20, cy + 180, mat_m)

        # Conference Room with Glass partitions
        self.add_wall_line(cx + 400, cy, cx + 400, cy + 250, mat_g)
        self.add_wall_line(cx + 400, cy + 250, cx + 700, cy + 250, mat_g)

        # Cubicle partition row
        self.add_wall_line(cx + 150, cy + 340, cx + 550, cy + 340, mat_d)

        self.router = {'x': cx + 300, 'y': cy + 220}
        self.recompute_heatmap()

    def load_preset_loft(self):
        """Open space loft with minimal interior obstacles."""
        self.clear_floorplan()
        cx, cy = 50, 40
        mat_c = "Concrete Wall"
        mat_g = "Glass Window"
        mat_w = "Wood Door"

        self.add_wall_line(cx, cy, cx + 700, cy, mat_c)
        self.add_wall_line(cx + 700, cy, cx + 700, cy + 500, mat_c)
        self.add_wall_line(cx + 700, cy + 500, cx, cy + 500, mat_c)
        self.add_wall_line(cx, cy + 500, cx, cy, mat_c)

        # Big Glass facade
        self.add_wall_line(cx + 150, cy + 500, cx + 550, cy + 500, mat_g)
        # Small partition
        self.add_wall_line(cx + 500, cy, cx + 500, cy + 180, mat_w)

        self.router = {'x': cx + 350, 'y': cy + 250}
        self.recompute_heatmap()

    def add_wall_line(self, x1, y1, x2, y2, material):
        self.walls.append({
            'x1': float(x1),
            'y1': float(y1),
            'x2': float(x2),
            'y2': float(y2),
            'mat': material
        })

    def import_floorplan_image(self):
        if not HAS_PIL:
            messagebox.showwarning("Pillow Missing", "Pillow (PIL) is required to import floorplan images.")
            return
        path = filedialog.askopenfilename(
            title="Select Floorplan Blueprint (PNG / JPG)",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if path:
            try:
                img = Image.open(path).convert("RGBA")
                img.thumbnail((self.canvas_w, self.canvas_h), Image.Resampling.LANCZOS)
                self.bg_image_raw = img
                self.redraw_canvas()
                messagebox.showinfo("Image Loaded", "Floorplan image loaded as background layer. You can now trace walls on top of it!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {e}")

    # -----------------------------------------------------------------
    # Simulation & Physics Computation Engine
    # -----------------------------------------------------------------
    def set_band(self, band):
        self.band_freq = band
        self.recompute_heatmap()

    def on_param_changed(self, val=None):
        self.tx_power_dbm = float(self.scale_tx.get())
        self.recompute_heatmap()

    def on_tool_changed(self):
        mode = self.active_tool.get()
        if mode == "survey":
            self.start_live_hw_monitor()
        else:
            self.stop_live_hw_monitor()

    def recompute_heatmap(self):
        """Core RF Wave Simulation using ITU-R P.1238 multi-wall path loss and FSPL."""
        w = max(100, self.canvas.winfo_width()) if self.canvas.winfo_width() > 10 else self.canvas_w
        h = max(100, self.canvas.winfo_height()) if self.canvas.winfo_height() > 10 else self.canvas_h

        step = self.grid_res
        xs = np.arange(0, w, step)
        ys = np.arange(0, h, step)
        GX, GY = np.meshgrid(xs, ys)

        if not self.router:
            self.sim_heatmap_data = np.full(GX.shape, -100.0)
            self.grid_X = GX
            self.grid_Y = GY
            self.redraw_canvas()
            return

        rx = self.router['x']
        ry = self.router['y']

        # Distance in meters
        dist_px = np.sqrt((GX - rx)**2 + (GY - ry)**2)
        dist_px[dist_px < 2.0] = 2.0  # Near-field cutoff
        dist_m = dist_px * self.scale_m_per_px

        # Free-Space Path Loss (FSPL)
        freq_mhz = 2400.0 if "2.4" in self.band_freq else 5000.0
        # FSPL(dB) = 20*log10(d_m) + 20*log10(f_MHz) - 27.55
        fspl = 20.0 * np.log10(dist_m) + 20.0 * np.log10(freq_mhz) - 27.55

        # Wall Attenuation Accumulator
        wall_loss_grid = np.zeros_like(GX, dtype=np.float32)
        loss_key = "loss_2g" if "2.4" in self.band_freq else "loss_5g"

        p_router = (rx, ry)
        for wall in self.walls:
            w_mat = WALL_MATERIALS.get(wall['mat'], WALL_MATERIALS["Concrete Wall"])
            w_atten = w_mat[loss_key]
            
            intersect_mask = line_intersection_vectorized(
                p_router, GX, GY,
                wall['x1'], wall['y1'], wall['x2'], wall['y2']
            )
            wall_loss_grid[intersect_mask] += w_atten

        # Final Signal Strength (dBm) = TX_Power + Antenna_Gain - FSPL - Wall_Loss
        rssi_grid = (self.tx_power_dbm + self.antenna_gain_dbi) - fspl - wall_loss_grid
        rssi_grid = np.clip(rssi_grid, -105.0, -25.0)

        self.sim_heatmap_data = rssi_grid
        self.grid_X = GX
        self.grid_Y = GY

        self.update_diagnostics()
        self.redraw_canvas()

    def update_diagnostics(self):
        if self.sim_heatmap_data is None:
            return
        data = self.sim_heatmap_data
        total_pts = data.size
        good_pts = np.count_nonzero(data >= -65.0)
        fair_pts = np.count_nonzero((data >= -80.0) & (data < -65.0))
        dead_pts = np.count_nonzero(data < -80.0)

        pct_good = (good_pts / total_pts) * 100.0
        pct_fair = (fair_pts / total_pts) * 100.0
        pct_dead = (dead_pts / total_pts) * 100.0

        self.lbl_metric_good.config(text=f"🟢 High Speed Coverage (> -65 dBm): {pct_good:.1f}%")
        self.lbl_metric_fair.config(text=f"🟡 Acceptable (-65 to -80 dBm): {pct_fair:.1f}%")
        self.lbl_metric_dead.config(text=f"🔴 Dead Zone (< -80 dBm): {pct_dead:.1f}%")

    # -----------------------------------------------------------------
    # AI Router Placement Optimizer
    # -----------------------------------------------------------------
    def run_ai_router_optimizer(self):
        """Scans the floorplan to find the optimal router location maximizing > -65 dBm coverage."""
        if not self.walls:
            messagebox.showinfo("Optimizer", "Please draw some walls or load a preset first.")
            return

        def opt_worker():
            if HAS_SOUND:
                try:
                    winsound.Beep(1200, 80)
                except Exception:
                    pass

            w = self.canvas.winfo_width() if self.canvas.winfo_width() > 10 else self.canvas_w
            h = self.canvas.winfo_height() if self.canvas.winfo_height() > 10 else self.canvas_h

            # Scan sample candidate spots
            step_cand = 40
            cand_xs = np.arange(80, w - 80, step_cand)
            cand_ys = np.arange(60, h - 60, step_cand)

            best_score = -1e9
            best_pos = None

            # Coarse evaluation grid
            eval_step = 24
            e_xs = np.arange(0, w, eval_step)
            e_ys = np.arange(0, h, eval_step)
            EGX, EGY = np.meshgrid(e_xs, e_ys)
            freq_mhz = 2400.0 if "2.4" in self.band_freq else 5000.0
            loss_key = "loss_2g" if "2.4" in self.band_freq else "loss_5g"

            for cx in cand_xs:
                for cy in cand_ys:
                    p_cand = (cx, cy)
                    dist_px = np.sqrt((EGX - cx)**2 + (EGY - cy)**2)
                    dist_px[dist_px < 2.0] = 2.0
                    dist_m = dist_px * self.scale_m_per_px
                    fspl = 20.0 * np.log10(dist_m) + 20.0 * np.log10(freq_mhz) - 27.55

                    wall_loss = np.zeros_like(EGX, dtype=np.float32)
                    for wall in self.walls:
                        w_mat = WALL_MATERIALS.get(wall['mat'], WALL_MATERIALS["Concrete Wall"])
                        mask = line_intersection_vectorized(p_cand, EGX, EGY, wall['x1'], wall['y1'], wall['x2'], wall['y2'])
                        wall_loss[mask] += w_mat[loss_key]

                    cand_rssi = (self.tx_power_dbm + self.antenna_gain_dbi) - fspl - wall_loss
                    # Score: high coverage > -65 dBm, strong penalty for dead zones < -80 dBm
                    good_cnt = np.count_nonzero(cand_rssi >= -65.0)
                    dead_cnt = np.count_nonzero(cand_rssi < -80.0)
                    score = good_cnt * 2.0 - dead_cnt * 5.0

                    if score > best_score:
                        best_score = score
                        best_pos = (cx, cy)

            if best_pos:
                self.optimal_router_pos = best_pos
                self.after(0, self.on_optimizer_finished, best_pos)

        threading.Thread(target=opt_worker, daemon=True).start()

    def on_optimizer_finished(self, best_pos):
        if HAS_SOUND:
            try:
                winsound.Beep(1800, 150)
                winsound.Beep(2400, 200)
            except Exception:
                pass
        self.router = {'x': best_pos[0], 'y': best_pos[1]}
        self.recompute_heatmap()
        messagebox.showinfo("AI Optimizer Complete",
                            f"✨ Optimal Router Location Calculated!\n\nCoordinates: X={best_pos[0]}px, Y={best_pos[1]}px\n"
                            "Router has been repositioned for peak performance.")

    # -----------------------------------------------------------------
    # Live Wi-Fi Hardware Polling
    # -----------------------------------------------------------------
    def start_live_hw_monitor(self):
        self.live_scan_active = True
        self.poll_live_hw()

    def stop_live_hw_monitor(self):
        self.live_scan_active = False

    def poll_live_hw(self):
        if not self.live_scan_active:
            return
        
        def worker():
            status = LiveWifiSampler.get_live_rssi()
            self.after(0, self.update_hw_badge, status)

        threading.Thread(target=worker, daemon=True).start()
        self.after(1500, self.poll_live_hw)

    def update_hw_badge(self, status):
        if status["connected"]:
            text = f"📡 Active SSID: {status['ssid']} | Live RSSI: {status['signal_dbm']} dBm ({status['signal_pct']}%)"
            fg = self.c_neon_green if status['signal_dbm'] >= -65 else (self.c_neon_amber if status['signal_dbm'] >= -80 else self.c_neon_red)
        else:
            text = "📡 Wi-Fi Adapter Disconnected"
            fg = self.c_muted

        self.lbl_hw_status.config(text=text, fg=fg)

    # -----------------------------------------------------------------
    # Canvas Rendering & Drawing
    # -----------------------------------------------------------------
    def redraw_canvas(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() if self.canvas.winfo_width() > 10 else self.canvas_w
        h = self.canvas.winfo_height() if self.canvas.winfo_height() > 10 else self.canvas_h

        # 1. Background Grid & Image
        if self.bg_image_raw and HAS_PIL:
            self.bg_image_tk = ImageTk.PhotoImage(self.bg_image_raw)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image_tk)
        else:
            # Draw subtle cyber grid
            for gx in range(0, w, 40):
                self.canvas.create_line(gx, 0, gx, h, fill="#0a1222", width=1)
            for gy in range(0, h, 40):
                self.canvas.create_line(0, gy, w, gy, fill="#0a1222", width=1)

        # 2. Render Heatmap Image from NumPy Array
        if self.sim_heatmap_data is not None and HAS_PIL:
            cmap = cm.get_cmap(self.colormap_name.get())
            # Normalize dBm from -95 to -35 for vibrant contrast
            norm_data = np.clip((self.sim_heatmap_data + 95.0) / 60.0, 0.0, 1.0)
            rgba_img = (cmap(norm_data) * 255).astype(np.uint8)
            # Make heatmap semi-transparent (alpha = 180)
            rgba_img[:, :, 3] = 175

            heat_pil = Image.fromarray(rgba_img, 'RGBA')
            heat_pil = heat_pil.resize((w, h), Image.Resampling.BILINEAR)
            self.heat_tk = ImageTk.PhotoImage(heat_pil)
            self.canvas.create_image(0, 0, anchor="nw", image=self.heat_tk)

        # 3. Draw Ray Bouncing Beams (Multi-path Raytracer Visualization)
        if self.show_rays.get() and self.router:
            self.draw_raytracer_beams()

        # 4. Draw Walls
        for wall in self.walls:
            w_mat = WALL_MATERIALS.get(wall['mat'], WALL_MATERIALS["Concrete Wall"])
            self.canvas.create_line(
                wall['x1'], wall['y1'], wall['x2'], wall['y2'],
                fill=w_mat['color'], width=w_mat['width'], capstyle=tk.ROUND
            )
            # Add material label at wall midpoint
            mx = (wall['x1'] + wall['x2']) / 2
            my = (wall['y1'] + wall['y2']) / 2
            self.canvas.create_text(mx, my - 8, text=wall['mat'].split()[0], fill=w_mat['color'], font=('Consolas', 7))

        # 5. Draw Survey Points (if any)
        for idx, pt in enumerate(self.survey_points):
            color = self.c_neon_green if pt['dbm'] >= -65 else (self.c_neon_amber if pt['dbm'] >= -80 else self.c_neon_red)
            self.canvas.create_oval(pt['x']-8, pt['y']-8, pt['x']+8, pt['y']+8, fill=color, outline="#ffffff", width=2)
            self.canvas.create_text(pt['x'], pt['y']-14, text=f"#{idx+1}: {pt['dbm']} dBm", fill="#ffffff", font=('Segoe UI', 8, 'bold'))

        # 6. Draw Router AP Icon & Pulsing Halo
        if self.router:
            rx, ry = self.router['x'], self.router['y']
            # Glowing Halos
            self.canvas.create_oval(rx-26, ry-26, rx+26, ry+26, outline=self.c_neon_cyan, width=1)
            self.canvas.create_oval(rx-18, ry-18, rx+18, ry+18, outline=self.c_neon_cyan, width=2)
            self.canvas.create_oval(rx-10, ry-10, rx+10, ry+10, fill=self.c_neon_cyan, outline="#ffffff", width=2)
            self.canvas.create_text(rx, ry + 22, text="📡 WI-FI ROUTER (AP)", fill=self.c_neon_cyan, font=('Segoe UI', 9, 'bold'))

        # 7. Draw Optimal AI Target Marker (if calculated)
        if self.optimal_router_pos:
            ox, oy = self.optimal_router_pos
            self.canvas.create_oval(ox-22, oy-22, ox+22, oy+22, outline=self.c_neon_green, width=2, dash=(4, 4))
            self.canvas.create_text(ox, oy-28, text="✨ AI OPTIMAL POSITION", fill=self.c_neon_green, font=('Segoe UI', 8, 'bold'))

    def draw_raytracer_beams(self):
        """Draws 360-degree specular multi-path reflection rays emitted from router."""
        rx, ry = self.router['x'], self.router['y']
        num_rays = 64
        max_dist = 600

        for i in range(num_rays):
            angle = (2 * math.pi * i) / num_rays
            dx = math.cos(angle)
            dy = math.sin(angle)
            p1 = (rx, ry)
            p2 = (rx + dx * max_dist, ry + dy * max_dist)

            # Find closest wall intersection
            closest_pt = None
            closest_dist = max_dist
            hit_wall = None

            for wall in self.walls:
                intersect, ip = segments_intersect(p1, p2, (wall['x1'], wall['y1']), (wall['x2'], wall['y2']))
                if intersect:
                    d = math.hypot(ip[0] - rx, ip[1] - ry)
                    if d < closest_dist:
                        closest_dist = d
                        closest_pt = ip
                        hit_wall = wall

            end_pt = closest_pt if closest_pt else p2
            # Draw Primary Ray
            self.canvas.create_line(rx, ry, end_pt[0], end_pt[1], fill="#00f0ff", width=1, dash=(3, 3))

            # If hit wall, calculate specular bounce ray
            if closest_pt and hit_wall:
                wx = hit_wall['x2'] - hit_wall['x1']
                wy = hit_wall['y2'] - hit_wall['y1']
                # Normal vector
                nx, ny = -wy, wx
                n_len = math.hypot(nx, ny)
                if n_len > 1e-6:
                    nx, ny = nx / n_len, ny / n_len
                    # Reflection formula: r = d - 2*(d.n)*n
                    dot = dx * nx + dy * ny
                    rdx = dx - 2 * dot * nx
                    rdy = dy - 2 * dot * ny
                    bounce_p2 = (closest_pt[0] + rdx * 120, closest_pt[1] + rdy * 120)
                    self.canvas.create_line(closest_pt[0], closest_pt[1], bounce_p2[0], bounce_p2[1], fill="#a855f7", width=1)

    # -----------------------------------------------------------------
    # Canvas Mouse Events (Drawing, Moving Router, Surveying)
    # -----------------------------------------------------------------
    def on_canvas_click(self, event):
        tool = self.active_tool.get()
        x, y = event.x, event.y

        if tool == "wall":
            self.drawing_wall_start = (x, y)
        elif tool == "router":
            self.router = {'x': x, 'y': y}
            self.recompute_heatmap()
            if HAS_SOUND:
                try:
                    winsound.Beep(900, 60)
                except Exception:
                    pass
        elif tool == "survey":
            # Sample live Wi-Fi RSSI at this coordinate
            status = LiveWifiSampler.get_live_rssi()
            self.survey_points.append({
                'x': float(x),
                'y': float(y),
                'dbm': status['signal_dbm'],
                'ssid': status['ssid']
            })
            if HAS_SOUND:
                try:
                    winsound.Beep(1400, 100)
                except Exception:
                    pass
            self.redraw_canvas()
        elif tool == "delete":
            # Find and remove closest wall or survey point
            to_remove_wall = None
            for wall in self.walls:
                mx = (wall['x1'] + wall['x2']) / 2
                my = (wall['y1'] + wall['y2']) / 2
                if math.hypot(mx - x, my - y) < 25:
                    to_remove_wall = wall
                    break
            if to_remove_wall:
                self.walls.remove(to_remove_wall)
                self.recompute_heatmap()

    def on_canvas_drag(self, event):
        tool = self.active_tool.get()
        if tool == "wall" and self.drawing_wall_start:
            x0, y0 = self.drawing_wall_start
            x1, y1 = event.x, event.y
            if self.temp_wall_id:
                self.canvas.delete(self.temp_wall_id)
            mat_info = WALL_MATERIALS.get(self.active_material.get(), WALL_MATERIALS["Concrete Wall"])
            self.temp_wall_id = self.canvas.create_line(x0, y0, x1, y1, fill=mat_info['color'], width=mat_info['width'], dash=(2, 2))
        elif tool == "router":
            self.router = {'x': event.x, 'y': event.y}
            self.recompute_heatmap()

    def on_canvas_release(self, event):
        tool = self.active_tool.get()
        if tool == "wall" and self.drawing_wall_start:
            x0, y0 = self.drawing_wall_start
            x1, y1 = event.x, event.y
            if math.hypot(x1 - x0, y1 - y0) > 10:
                self.add_wall_line(x0, y0, x1, y1, self.active_material.get())
                self.recompute_heatmap()
            self.drawing_wall_start = None
            if self.temp_wall_id:
                self.canvas.delete(self.temp_wall_id)
                self.temp_wall_id = None

    def on_canvas_motion(self, event):
        x, y = event.x, event.y
        xm = x * self.scale_m_per_px
        ym = y * self.scale_m_per_px

        # Read signal from heatmap array
        est_dbm = "--"
        if self.sim_heatmap_data is not None and self.grid_X is not None:
            gx_idx = int(np.clip(x // self.grid_res, 0, self.sim_heatmap_data.shape[1] - 1))
            gy_idx = int(np.clip(y // self.grid_res, 0, self.sim_heatmap_data.shape[0] - 1))
            val = self.sim_heatmap_data[gy_idx, gx_idx]
            est_dbm = f"{val:.1f}"

        self.lbl_probe.config(
            text=f"Cursor Probe: X: {xm:.1f}m, Y: {ym:.1f}m | Estimated Signal: {est_dbm} dBm"
        )

    def on_canvas_resize(self, event):
        self.canvas_w = event.width
        self.canvas_h = event.height
        self.recompute_heatmap()

    # -----------------------------------------------------------------
    # 3D Spatial Elevation View
    # -----------------------------------------------------------------
    def on_tab_changed(self, event):
        selected_tab = self.tabs.tab(self.tabs.select(), "text")
        if "3D" in selected_tab:
            self.render_3d_surface()

    def render_3d_surface(self):
        """Renders 3D topological heightmap in the Matplotlib 3D axes."""
        if self.sim_heatmap_data is None or self.grid_X is None:
            return

        self.ax_3d.clear()
        self.ax_3d.set_facecolor("#050811")
        self.fig_3d.patch.set_facecolor("#050811")

        # Downsample for smooth 3D rendering
        stride = 2
        X = self.grid_X[::stride, ::stride] * self.scale_m_per_px
        Y = self.grid_Y[::stride, ::stride] * self.scale_m_per_px
        Z = self.sim_heatmap_data[::stride, ::stride]

        cmap = cm.get_cmap(self.colormap_name.get())
        surf = self.ax_3d.plot_surface(
            X, Y, Z, cmap=cmap, linewidth=0.2, antialiased=True,
            edgecolor="#1a2a47", alpha=0.9
        )

        # Draw contour projection at bottom
        self.ax_3d.contour(X, Y, Z, zdir='z', offset=-105, cmap=cmap, alpha=0.5)

        self.ax_3d.set_zlim(-105, -25)
        self.ax_3d.set_title("3D RF Spatial Topography (Signal Height)", color=self.c_neon_cyan, fontsize=11, fontweight='bold')
        self.ax_3d.set_xlabel("X (Meters)", color=self.c_muted, fontsize=8)
        self.ax_3d.set_ylabel("Y (Meters)", color=self.c_muted, fontsize=8)
        self.ax_3d.set_zlabel("RSSI (dBm)", color=self.c_muted, fontsize=8)

        self.ax_3d.tick_params(colors=self.c_muted, labelsize=7)
        self.canvas_3d.draw()

    # -----------------------------------------------------------------
    # Export Report
    # -----------------------------------------------------------------
    def export_report(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            title="Save Wi-Fi Heatmap Image"
        )
        if not path:
            return

        try:
            # Capture canvas to image
            w = self.canvas_w
            h = self.canvas_h
            if HAS_PIL and self.sim_heatmap_data is not None:
                cmap = cm.get_cmap(self.colormap_name.get())
                norm_data = np.clip((self.sim_heatmap_data + 95.0) / 60.0, 0.0, 1.0)
                rgba_img = (cmap(norm_data) * 255).astype(np.uint8)
                export_img = Image.fromarray(rgba_img, 'RGBA').resize((w, h), Image.Resampling.LANCZOS)
                draw = ImageDraw.Draw(export_img)

                # Draw walls on export image
                for wall in self.walls:
                    draw.line([(wall['x1'], wall['y1']), (wall['x2'], wall['y2'])], fill="#ffffff", width=4)

                # Draw router
                if self.router:
                    rx, ry = self.router['x'], self.router['y']
                    draw.ellipse([rx-12, ry-12, rx+12, ry+12], fill="#00f0ff", outline="#ffffff", width=2)

                export_img.save(path)
                messagebox.showinfo("Export Successful", f"Heatmap successfully exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save image: {e}")


# =====================================================================
# Main Launch Entry
# =====================================================================
if __name__ == '__main__':
    app = WifiHeatmapApp()
    app.mainloop()
