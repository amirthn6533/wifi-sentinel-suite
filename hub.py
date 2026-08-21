"""
Wi-Fi Cyber Suite | Master Command Center (English Edition)
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
        self.geometry("780x520")
        self.resizable(False, False)
        self.configure(bg="#050811")

        self.c_bg = "#050811"
        self.c_panel = "#0b1220"
        self.c_border = "#1a2a47"
        self.c_neon_cyan = "#00f0ff"
        self.c_neon_green = "#00ff9d"
        self.c_neon_red = "#ff0055"
        self.c_neon_amber = "#ffb703"
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        self.build_hub_ui()

    def build_hub_ui(self):
        # Header
        header = tk.Frame(self, bg=self.c_panel, height=80, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(header, text="⚡ WI-FI CYBER SUITE", font=('Segoe UI', 16, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(pady=(12, 2))
        tk.Label(header, text="Realtek RTL8811AU (TP-Link High-Gain Antenna) | Cyber Defense & RF Sensing",
                 font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_muted).pack()

        # Body
        body = tk.Frame(self, bg=self.c_bg)
        body.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # Card 1: Motion Detector
        card1 = tk.Frame(body, bg=self.c_panel, width=350, highlightthickness=1, highlightbackground=self.c_border, padx=18, pady=18)
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        tk.Label(card1, text="🚨 Wi-Fi Motion Sentinel", font=('Segoe UI', 13, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_red).pack(anchor='w', pady=(0, 6))
        
        desc1 = "Detect human movement & room entry without cameras!\n\nFeatures ultra-precise RF Seismograph waveform rendering, 5s quiescent noise calibration, and an armed security siren."
        tk.Label(card1, text=desc1, font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_text,
                 justify=tk.LEFT, wraplength=310).pack(anchor='w', pady=(0, 15))

        btn_launch1 = tk.Button(card1, text="🚀 Launch Motion Sentinel",
                                bg=self.c_neon_red, fg="#ffffff", font=('Segoe UI', 10, 'bold'),
                                relief=tk.FLAT, pady=10, cursor='hand2',
                                activebackground="#be123c", activeforeground="#ffffff",
                                command=self.launch_motion)
        btn_launch1.pack(fill=tk.X, side=tk.BOTTOM)

        # Card 2: Radar & Analyzer
        card2 = tk.Frame(body, bg=self.c_panel, width=350, highlightthickness=1, highlightbackground=self.c_border, padx=18, pady=18)
        card2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

        tk.Label(card2, text="📡 Wi-Fi Radar & Security Audit", font=('Segoe UI', 13, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(anchor='w', pady=(0, 6))
        
        desc2 = "360° dynamic radar, 2.4G & 5G frequency spectrum analyzer, Evil Twin / Rogue AP detection, hardware OUI vendor lookup, and Geiger signal tracker."
        tk.Label(card2, text=desc2, font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_text,
                 justify=tk.LEFT, wraplength=310).pack(anchor='w', pady=(0, 15))

        btn_launch2 = tk.Button(card2, text="🚀 Launch Wi-Fi Radar",
                                bg=self.c_neon_cyan, fg="#050811", font=('Segoe UI', 10, 'bold'),
                                relief=tk.FLAT, pady=10, cursor='hand2',
                                activebackground="#0284c7", activeforeground="#ffffff",
                                command=self.launch_radar)
        btn_launch2.pack(fill=tk.X, side=tk.BOTTOM)

        # Bottom Bar
        footer = tk.Frame(self, bg=self.c_panel, height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        tk.Label(footer, text="Antigravity Cyber Suite • High-Performance RF Sensing Engine",
                 font=('Consolas', 8), bg=self.c_panel, fg=self.c_muted).pack(pady=8)

    def launch_motion(self):
        script = os.path.join(os.path.dirname(__file__), "wifi_motion_sensor.py")
        subprocess.Popen([sys.executable, script])

    def launch_radar(self):
        script = os.path.join(os.path.dirname(__file__), "wifi_radar.py")
        subprocess.Popen([sys.executable, script])


if __name__ == '__main__':
    app = CyberSuiteHub()
    app.mainloop()
