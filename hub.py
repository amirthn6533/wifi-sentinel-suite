"""
Wi-Fi Cyber Suite | Master Command Center (4-Tool Ultimate Cyber Grid)
Author: Antigravity Pair Programmer
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

class CyberSuiteHub(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚡ WI-FI CYBER SUITE | Master Command Center")
        self.geometry("1160x650")
        self.minsize(1050, 600)
        self.configure(bg="#050811")

        self.c_bg = "#050811"
        self.c_panel = "#0b1220"
        self.c_card = "#111c30"
        self.c_border = "#1a2a47"
        self.c_neon_cyan = "#00f0ff"
        self.c_neon_green = "#00ff9d"
        self.c_neon_red = "#ff0055"
        self.c_neon_amber = "#ffb703"
        self.c_neon_purple = "#a855f7"
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        self.build_hub_ui()

    def build_hub_ui(self):
        # Header
        header = tk.Frame(self, bg=self.c_panel, height=80, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(header, text="⚡ WI-FI CYBER SUITE", font=('Segoe UI', 16, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(pady=(10, 2))
        tk.Label(header, text="Realtek RTL8811AU & USB Adapters | RF Motion • Radar • 3D Heatmap • Spy Bug Hunter",
                 font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_muted).pack()

        # Body 2x2 Grid Container
        body = tk.Frame(self, bg=self.c_bg)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        # -------------------------------------------------------------
        # Card 1: Motion Detector (Top-Left)
        # -------------------------------------------------------------
        c1 = tk.Frame(body, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=12)
        c1.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        tk.Label(c1, text="🚨 Wi-Fi Motion Sentinel", font=('Segoe UI', 12, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_red).pack(anchor='w')
        
        desc1 = "Camera-less room motion & intruder detector via live RF wave seismograph, 5s baseline calibration & security siren."
        tk.Label(c1, text=desc1, font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_text,
                 justify=tk.LEFT, wraplength=480).pack(anchor='w', pady=(4, 8), fill=tk.BOTH, expand=True)

        tk.Button(c1, text="🚀 Launch Motion Sentinel", bg=self.c_neon_red, fg="#ffffff",
                  font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                  activebackground="#be123c", activeforeground="#ffffff",
                  command=self.launch_motion).pack(fill=tk.X, side=tk.BOTTOM)

        # -------------------------------------------------------------
        # Card 2: Radar & Analyzer (Top-Right)
        # -------------------------------------------------------------
        c2 = tk.Frame(body, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=12)
        c2.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        tk.Label(c2, text="📡 Wi-Fi Radar & Security Audit", font=('Segoe UI', 12, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(anchor='w')
        
        desc2 = "360° dynamic radar, 2.4G & 5G dual-band spectrum analyzer, Evil Twin / Rogue AP detection, and OUI vendor lookup."
        tk.Label(c2, text=desc2, font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_text,
                 justify=tk.LEFT, wraplength=480).pack(anchor='w', pady=(4, 8), fill=tk.BOTH, expand=True)

        tk.Button(c2, text="🚀 Launch Wi-Fi Radar", bg=self.c_neon_cyan, fg="#050811",
                  font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                  activebackground="#0284c7", activeforeground="#ffffff",
                  command=self.launch_radar).pack(fill=tk.X, side=tk.BOTTOM)

        # -------------------------------------------------------------
        # Card 3: 2D/3D Heatmap (Bottom-Left)
        # -------------------------------------------------------------
        c3 = tk.Frame(body, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=12)
        c3.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        tk.Label(c3, text="🗺️ 2D/3D RF Heatmap & Raytracer", font=('Segoe UI', 12, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_purple).pack(anchor='w')
        
        desc3 = "Interactive floorplan design, multi-material wall loss physics, AI router placement optimizer, and 3D terrain mesh."
        tk.Label(c3, text=desc3, font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_text,
                 justify=tk.LEFT, wraplength=480).pack(anchor='w', pady=(4, 8), fill=tk.BOTH, expand=True)

        tk.Button(c3, text="🚀 Launch Heatmap Studio", bg=self.c_neon_purple, fg="#ffffff",
                  font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                  activebackground="#7e22ce", activeforeground="#ffffff",
                  command=self.launch_heatmap).pack(fill=tk.X, side=tk.BOTTOM)

        # -------------------------------------------------------------
        # Card 4: Spy Cam & Drone Hunter (Bottom-Right)
        # -------------------------------------------------------------
        c4 = tk.Frame(body, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=12)
        c4.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)

        tk.Label(c4, text="🕵️‍♂️ Spy Cam & Drone RF Hunter", font=('Segoe UI', 12, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_amber).pack(anchor='w')
        
        desc4 = "Identify hidden pinhole cameras, IoT spy bugs, DJI / FPV drones, and pinpoint exact physical location with audio Geiger ticker."
        tk.Label(c4, text=desc4, font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_text,
                 justify=tk.LEFT, wraplength=480).pack(anchor='w', pady=(4, 8), fill=tk.BOTH, expand=True)

        tk.Button(c4, text="🚀 Launch Spy & Drone Hunter", bg=self.c_neon_amber, fg="#050811",
                  font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                  activebackground="#d97706", activeforeground="#ffffff",
                  command=self.launch_spy_hunter).pack(fill=tk.X, side=tk.BOTTOM)

        # Bottom Bar
        footer = tk.Frame(self, bg=self.c_panel, height=44, highlightthickness=1, highlightbackground=self.c_border)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        tk.Label(footer, text="Antigravity Cyber Suite • 8-Tool Cyber Warfare, 3D Globe & Biometrics Studio",
                 font=('Consolas', 8), bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT, padx=10, pady=12)

        btn_globe = tk.Button(footer, text="🌐 3D Cyber Globe", bg="#1e3a8a", fg=self.c_neon_cyan,
                              font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=7, pady=3, cursor='hand2',
                              activebackground="#2563eb", activeforeground="#ffffff",
                              command=self.launch_globe)
        btn_globe.pack(side=tk.RIGHT, padx=(2, 10), pady=6)

        btn_bio = tk.Button(footer, text="🫀 Biometrics HUD", bg="#064e3b", fg=self.c_neon_green,
                            font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=7, pady=3, cursor='hand2',
                            activebackground="#047857", activeforeground="#ffffff",
                            command=self.launch_biometrics)
        btn_bio.pack(side=tk.RIGHT, padx=2, pady=6)

        btn_fsociety = tk.Button(footer, text="💀 fsociety Simulator", bg="#450a0a", fg=self.c_neon_red,
                                 font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=7, pady=3, cursor='hand2',
                                 activebackground="#7f1d1d", activeforeground="#ffffff",
                                 command=self.launch_fsociety)
        btn_fsociety.pack(side=tk.RIGHT, padx=2, pady=6)

        btn_osint = tk.Button(footer, text="🔍 OSINT Recon", bg="#27272a", fg=self.c_text,
                              font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=7, pady=3, cursor='hand2',
                              activebackground="#3f3f46", activeforeground="#ffffff",
                              command=self.launch_osint)
        btn_osint.pack(side=tk.RIGHT, padx=2, pady=6)

    def launch_motion(self):
        script = os.path.join(os.path.dirname(__file__), "wifi_motion_sensor.py")
        subprocess.Popen([sys.executable, script])

    def launch_radar(self):
        script = os.path.join(os.path.dirname(__file__), "wifi_radar.py")
        subprocess.Popen([sys.executable, script])

    def launch_heatmap(self):
        script = os.path.join(os.path.dirname(__file__), "wifi_heatmap.py")
        subprocess.Popen([sys.executable, script])

    def launch_spy_hunter(self):
        script = os.path.join(os.path.dirname(__file__), "wifi_spy_hunter.py")
        subprocess.Popen([sys.executable, script])

    def launch_osint(self):
        if os.name == 'nt':
            os.system(f'start cmd /k "chcp 65001 > nul && title 💀 Elliot OSINT Recon && python \\"{os.path.join(os.path.dirname(__file__), "elliot_recon.py")}\\""')
        else:
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "elliot_recon.py")])

    def launch_fsociety(self):
        if os.name == 'nt':
            os.system(f'start cmd /k "chcp 65001 > nul && title 💀 fsociety Terminal Game && python \\"{os.path.join(os.path.dirname(__file__), "fsociety_terminal.py")}\\""')
        else:
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "fsociety_terminal.py")])

    def launch_biometrics(self):
        script = os.path.join(os.path.dirname(__file__), "cyber_biometrics.py")
        subprocess.Popen([sys.executable, script])

    def launch_globe(self):
        script = os.path.join(os.path.dirname(__file__), "cyber_globe.py")
        subprocess.Popen([sys.executable, script])


if __name__ == '__main__':
    app = CyberSuiteHub()
    app.mainloop()
