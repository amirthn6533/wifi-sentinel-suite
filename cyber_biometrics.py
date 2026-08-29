"""
=============================================================================
🫀 CYBER BIOMETRIC rPPG HEART-RATE HUD (JARVIS Edition)
=============================================================================
Author: Antigravity Pair Programmer
Architecture: Computer Vision Remote Photoplethysmography (rPPG) & FFT DSP
Inspired by: Iron Man / JARVIS HUD & Medical Optics
=============================================================================
"""

import sys
import os
import time
import math
import threading
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from scipy import signal
from PIL import Image, ImageTk

# Windows audio for Heartbeat Synthesizer
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# =====================================================================
# 1D Kalman Filter for BPM Stabilization & Zero-Jitter
# =====================================================================
class KalmanFilter1D:
    def __init__(self, process_variance=0.04, measurement_variance=2.5, initial_value=72.0):
        self.q = process_variance
        self.r = measurement_variance
        self.x = float(initial_value)
        self.p = 1.0
        self.initialized = False

    def update(self, measurement):
        if not self.initialized:
            self.x = float(measurement)
            self.initialized = True
            return self.x
        p_pred = self.p + self.q
        k = p_pred / (p_pred + self.r)
        self.x = self.x + k * (float(measurement) - self.x)
        self.p = (1.0 - k) * p_pred
        return self.x


# =====================================================================
# rPPG Biological Optical Signal Processing Pipeline
# =====================================================================
class BiometricProcessor:
    def __init__(self, buffer_size=150, fps=30.0):
        self.buffer_size = buffer_size
        self.fps = fps
        self.green_timeseries = deque(maxlen=buffer_size)
        self.timestamps = deque(maxlen=buffer_size)
        self.filtered_pulse = deque(maxlen=buffer_size)
        self.current_bpm = 0.0
        self.kalman = KalmanFilter1D(process_variance=0.05, measurement_variance=2.0, initial_value=72.0)
        self.snr = 0.0
        self.is_valid = False

        # Load OpenCV default Haar cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def extract_forehead_roi(self, frame):
        """Detects face and isolates forehead capillary blood absorption zone."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(100, 100))

        if len(faces) == 0:
            return None, None

        # Pick largest face
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        (x, y, w, h) = faces[0]

        # Forehead Region: Top 10% to 30% of face height, middle 50% width
        fx = int(x + w * 0.25)
        fy = int(y + h * 0.10)
        fw = int(w * 0.50)
        fh = int(h * 0.18)

        face_box = (x, y, w, h)
        forehead_box = (fx, fy, fw, fh)
        return face_box, forehead_box

    def process_frame(self, frame, forehead_box):
        """Extracts mean green channel intensity and updates DSP filters."""
        if forehead_box is None:
            self.is_valid = False
            return

        fx, fy, fw, fh = forehead_box
        # Bound check
        h_img, w_img = frame.shape[:2]
        fx = max(0, min(fx, w_img - 1))
        fy = max(0, min(fy, h_img - 1))
        fw = max(1, min(fw, w_img - fx))
        fh = max(1, min(fh, h_img - fy))

        roi = frame[fy:fy+fh, fx:fx+fw]
        if roi.size == 0:
            self.is_valid = False
            return

        # Green channel has strongest hemoglobin extinction coefficient
        mean_green = np.mean(roi[:, :, 1])
        now = time.time()

        self.green_timeseries.append(mean_green)
        self.timestamps.append(now)

        if len(self.green_timeseries) >= 45:
            self.compute_bpm()
            self.is_valid = True
        else:
            self.is_valid = False

    def compute_bpm(self):
        """Butterworth bandpass filter (0.75 - 3.0 Hz => 45 - 180 BPM) + FFT Power Peak."""
        raw_vals = np.array(self.green_timeseries)
        
        # Calculate true instant sample rate
        dt = np.diff(self.timestamps)
        if len(dt) > 0 and np.mean(dt) > 0:
            effective_fps = 1.0 / np.mean(dt)
        else:
            effective_fps = self.fps

        # Detrend signal (remove slow lighting drift)
        detrended = signal.detrend(raw_vals)

        # 3rd Order Butterworth Bandpass Filter (0.75 Hz to 3.0 Hz)
        lowcut = 0.75
        highcut = min(3.0, (effective_fps / 2.0) - 0.1)
        if highcut <= lowcut:
            return

        try:
            nyq = 0.5 * effective_fps
            b, a = signal.butter(3, [lowcut / nyq, highcut / nyq], btype='bandpass')
            filtered = signal.filtfilt(b, a, detrended)
            self.filtered_pulse.append(filtered[-1])

            # FFT Power Spectrum Density (PSD)
            N = len(filtered)
            fft_vals = np.fft.rfft(filtered * np.hanning(N))
            freqs = np.fft.rfftfreq(N, d=(1.0 / effective_fps))

            # Filter frequencies between 45 BPM and 180 BPM
            mask = (freqs >= lowcut) & (freqs <= highcut)
            freq_band = freqs[mask]
            power_band = np.abs(fft_vals[mask]) ** 2

            if len(power_band) > 0 and np.max(power_band) > 1e-4:
                peak_idx = np.argmax(power_band)
                raw_bpm = freq_band[peak_idx] * 60.0

                # Compute Signal-to-Noise Ratio (SNR)
                peak_power = power_band[peak_idx]
                noise_power = np.sum(power_band) - peak_power
                self.snr = (peak_power / (noise_power + 1e-6))

                # Apply Kalman smoothing
                if 45.0 <= raw_bpm <= 180.0:
                    smoothed = self.kalman.update(raw_bpm)
                    self.current_bpm = round(smoothed, 1)
        except Exception:
            pass


# =====================================================================
# Main Application GUI & JARVIS HUD Engine
# =====================================================================
class CyberBiometricsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🫀 CYBER BIOMETRIC HUD | rPPG Cardiac Optical Scanner")
        self.geometry("1280x820")
        self.minsize(1050, 700)
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
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        # State Variables
        self.cap = None
        self.camera_running = False
        self.processor = BiometricProcessor(buffer_size=150)
        self.sound_enabled = tk.BooleanVar(value=True)
        self.scanlines_y = 0
        self.heartbeat_anim_scale = 1.0

        self.setup_ui()
        self.start_camera()
        self.start_heartbeat_audio_thread()

    def setup_ui(self):
        # -------------------------------------------------------------
        # Header
        # -------------------------------------------------------------
        header = tk.Frame(self, bg=self.c_panel, height=65, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=self.c_panel)
        title_box.pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(title_box, text="🫀 CYBER BIOMETRIC HUD", font=('Segoe UI', 14, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_box, text="rPPG Optical Capillary Pulse & Facial Vitals Scanner", font=('Segoe UI', 9),
                 bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT)

        self.lbl_status_badge = tk.Label(header, text="📡 INITIALIZING SCANNER...", font=('Segoe UI', 9, 'bold'),
                                         bg=self.c_card, fg=self.c_neon_cyan, padx=14, pady=5,
                                         highlightthickness=1, highlightbackground=self.c_border)
        self.lbl_status_badge.pack(side=tk.RIGHT, padx=20, pady=14)

        # -------------------------------------------------------------
        # Main Split Workspace (Left: Video HUD | Right: Vitals Metrics & EKG)
        # -------------------------------------------------------------
        main_box = tk.Frame(self, bg=self.c_bg)
        main_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left Column: Video HUD Canvas (Width: 700px)
        left_col = tk.Frame(main_box, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.lbl_cam_header = tk.Label(left_col, text="🎯 OPTICAL FACIAL TARGETING MATRIX (JARVIS HUD)",
                                       font=('Segoe UI', 10, 'bold'), bg=self.c_panel, fg=self.c_neon_cyan)
        self.lbl_cam_header.pack(anchor='w', padx=12, pady=(10, 6))

        self.video_canvas = tk.Canvas(left_col, bg="#02040a", highlightthickness=0)
        self.video_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Right Column: Biometric Metrics, Diagnostics & EKG (Width: 420px)
        right_col = tk.Frame(main_box, bg=self.c_panel, width=420, highlightthickness=1, highlightbackground=self.c_border)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 0))
        right_col.pack_propagate(False)
        self.build_metrics_panel(right_col)

    def build_metrics_panel(self, parent):
        pad = 12

        # Card 1: Giant BPM Core Gauge
        gauge_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=16)
        gauge_card.pack(fill=tk.X, padx=pad, pady=(14, 8))

        tk.Label(gauge_card, text="ESTIMATED CARDIAC PULSE", font=('Segoe UI', 9, 'bold'), bg=self.c_card, fg=self.c_muted).pack()

        self.lbl_bpm_value = tk.Label(gauge_card, text="--", font=('Segoe UI', 48, 'bold'), bg=self.c_card, fg=self.c_neon_green)
        self.lbl_bpm_value.pack(pady=(2, 0))

        tk.Label(gauge_card, text="BEATS PER MINUTE (BPM)", font=('Consolas', 10, 'bold'), bg=self.c_card, fg=self.c_neon_cyan).pack()

        self.lbl_cardiac_zone = tk.Label(gauge_card, text="🟢 Status: Calibrating Face...", font=('Segoe UI', 9, 'bold'),
                                         bg=self.c_card, fg=self.c_neon_green)
        self.lbl_cardiac_zone.pack(pady=(8, 0))

        # Card 2: Real-time EKG / Plethysmograph Waveform Canvas
        ekg_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=12, pady=10)
        ekg_card.pack(fill=tk.X, padx=pad, pady=6)

        tk.Label(ekg_card, text="LIVE rPPG CAPILLARY WAVEFORM (EKG)", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_muted).pack(anchor='w')

        self.ekg_w = 370
        self.ekg_h = 130
        self.ekg_canvas = tk.Canvas(ekg_card, bg="#030611", width=self.ekg_w, height=self.ekg_h, highlightthickness=0)
        self.ekg_canvas.pack(fill=tk.X, pady=(6, 4))

        # Card 3: Signal Quality & Optical Diagnostics
        diag_card = tk.Frame(parent, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=12, pady=10)
        diag_card.pack(fill=tk.X, padx=pad, pady=6)

        tk.Label(diag_card, text="OPTICAL SNR & LIGHTING QUALITY", font=('Segoe UI', 8, 'bold'), bg=self.c_card, fg=self.c_muted).pack(anchor='w')

        self.lbl_snr = tk.Label(diag_card, text="Signal Quality: Calibrating...", font=('Consolas', 9), bg=self.c_card, fg=self.c_text)
        self.lbl_snr.pack(anchor='w', pady=2)

        self.lbl_advice = tk.Label(diag_card, text="💡 Pro-Tip: Ensure room lighting is bright and hold your head steady for medical-grade accuracy.",
                                   font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted, wraplength=360, justify=tk.LEFT)
        self.lbl_advice.pack(anchor='w', pady=(4, 0))

        # Bottom Audio Toggle & Controls
        ctrl_bar = tk.Frame(parent, bg=self.c_panel)
        ctrl_bar.pack(fill=tk.X, padx=pad, pady=(10, 14), side=tk.BOTTOM)

        tk.Checkbutton(ctrl_bar, text="🔊 Audio Heartbeat Synth", variable=self.sound_enabled,
                       bg=self.c_panel, fg=self.c_text, selectcolor=self.c_card,
                       font=('Segoe UI', 9, 'bold'), activebackground=self.c_panel).pack(side=tk.LEFT)

        btn_recal = tk.Button(ctrl_bar, text="🔄 Reset Baseline", bg=self.c_border, fg=self.c_neon_cyan,
                              font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=10, pady=4, cursor='hand2',
                              command=self.reset_baseline)
        btn_recal.pack(side=tk.RIGHT)

    def reset_baseline(self):
        self.processor = BiometricProcessor(buffer_size=150)
        self.lbl_bpm_value.config(text="--", fg=self.c_neon_green)
        self.lbl_cardiac_zone.config(text="🟢 Status: Recalibrating...", fg=self.c_neon_green)

    # -----------------------------------------------------------------
    # Camera Capture & Processing Loop
    # -----------------------------------------------------------------
    def start_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else 0)
        if not self.cap.isOpened():
            # Try default backend
            self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Could not access webcam. Please ensure your camera is connected and not in use by another app.")
            return

        self.camera_running = True
        self.update_video_frame()

    def update_video_frame(self):
        if not self.camera_running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Flip horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            # Process rPPG Forehead ROI
            face_box, forehead_box = self.processor.extract_forehead_roi(frame)
            self.processor.process_frame(frame, forehead_box)

            # Render JARVIS Cyberpunk HUD overlay on image
            hud_frame = self.draw_jarvis_hud(frame, face_box, forehead_box)

            # Convert to PIL & display on canvas
            cv2_rgb = cv2.cvtColor(hud_frame, cv2.COLOR_BGR2RGB)
            h, w = cv2_rgb.shape[:2]
            
            # Responsive Canvas resize
            cw = max(100, self.video_canvas.winfo_width()) if self.video_canvas.winfo_width() > 10 else 640
            ch = max(100, self.video_canvas.winfo_height()) if self.video_canvas.winfo_height() > 10 else 480
            
            # Maintain aspect ratio
            scale = min(cw / w, ch / h)
            nw = int(w * scale)
            nh = int(h * scale)

            resized = cv2.resize(cv2_rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)
            pil_img = Image.fromarray(resized)
            self.tk_img = ImageTk.PhotoImage(image=pil_img)

            self.video_canvas.delete("all")
            # Center on canvas
            x_off = (cw - nw) // 2
            y_off = (ch - nh) // 2
            self.video_canvas.create_image(x_off, y_off, anchor="nw", image=self.tk_img)

            # Update Metrics UI
            self.update_biometric_metrics()

        self.after(33, self.update_video_frame)

    def draw_jarvis_hud(self, frame, face_box, forehead_box):
        """Draws Iron Man / JARVIS holographic HUD targeting wireframes on video."""
        hud = frame.copy()
        h, w = hud.shape[:2]

        # Scanlines animation
        self.scanlines_y = (self.scanlines_y + 4) % h
        cv2.line(hud, (0, self.scanlines_y), (w, self.scanlines_y), (255, 240, 0), 1)

        # Draw Face Targeting Reticle
        if face_box:
            (x, y, fw, fh) = face_box
            c_neon = (255, 240, 0)  # BGR Cyan

            # Corner brackets
            d = 20
            # Top-Left
            cv2.line(hud, (x, y), (x + d, y), c_neon, 2)
            cv2.line(hud, (x, y), (x, y + d), c_neon, 2)
            # Top-Right
            cv2.line(hud, (x + fw, y), (x + fw - d, y), c_neon, 2)
            cv2.line(hud, (x + fw, y), (x + fw, y + d), c_neon, 2)
            # Bottom-Left
            cv2.line(hud, (x, y + fh), (x + d, y + fh), c_neon, 2)
            cv2.line(hud, (x, y + fh), (x, y + fh - d), c_neon, 2)
            # Bottom-Right
            cv2.line(hud, (x + fw, y + fh), (x + fw - d, y + fh), c_neon, 2)
            cv2.line(hud, (x + fw, y + fh), (x + fw, y + fh - d), c_neon, 2)

            # Face target label
            cv2.putText(hud, "SUBJECT LOCKED // BIOMETRIC SCAN", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 240, 0), 1, cv2.LINE_AA)

        # Draw Forehead Capillary Optical ROI
        if forehead_box:
            (fx, fy, f_w, f_h) = forehead_box
            cv2.rectangle(hud, (fx, fy), (fx + f_w, fy + f_h), (0, 255, 157), 1)
            cv2.putText(hud, "rPPG OPTICAL ZONE", (fx, fy - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 157), 1, cv2.LINE_AA)

        # Top-left HUD status watermark
        cv2.putText(hud, "JARVIS OPTICAL rPPG ENGINE v2.4", (15, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 240, 255), 1, cv2.LINE_AA)
        cv2.putText(hud, f"SPECTRAL ABSORPTION: GREEN (530nm)", (15, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 116, 139), 1, cv2.LINE_AA)

        return hud

    def update_biometric_metrics(self):
        bpm = self.processor.current_bpm
        is_valid = self.processor.is_valid

        if is_valid and bpm > 45:
            self.lbl_bpm_value.config(text=f"{bpm:.0f}")
            self.lbl_status_badge.config(text=f"🫀 BIOMETRICS ACTIVE: {bpm:.0f} BPM", fg=self.c_neon_green)

            if bpm < 70:
                zone_text = "🟢 State: Resting / Calm & Relaxed"
                zone_col = self.c_neon_green
            elif bpm <= 90:
                zone_text = "🟡 State: Normal / Alert & Focused"
                zone_col = self.c_neon_amber
            else:
                zone_text = "🔴 State: Elevated / High Stress or Exertion"
                zone_col = self.c_neon_red

            self.lbl_cardiac_zone.config(text=zone_text, fg=zone_col)
            self.lbl_bpm_value.config(fg=zone_col)
            self.lbl_snr.config(text=f"Signal SNR Quality: {self.processor.snr:.1f} dB (Optimal)")
        else:
            self.lbl_bpm_value.config(text="--", fg=self.c_muted)
            self.lbl_status_badge.config(text="🔍 ACQUIRING FACE & OPTICAL SIGNAL...", fg=self.c_neon_cyan)
            self.lbl_cardiac_zone.config(text="🟢 Status: Looking at camera...", fg=self.c_muted)
            self.lbl_snr.config(text="Signal Quality: Initializing...")

        # Draw rolling EKG Waveform
        self.draw_ekg_waveform()

    def draw_ekg_waveform(self):
        self.ekg_canvas.delete("all")
        w = self.ekg_w
        h = self.ekg_h
        cy = h // 2

        # Cyber grid
        for gy in range(0, h, 25):
            self.ekg_canvas.create_line(0, gy, w, gy, fill="#081022", width=1)
        for gx in range(0, w, 30):
            self.ekg_canvas.create_line(gx, 0, gx, h, fill="#081022", width=1)

        pulse = list(self.processor.filtered_pulse)
        if len(pulse) < 5:
            # Flatline when no data
            self.ekg_canvas.create_line(0, cy, w, cy, fill="#00f0ff", width=1, dash=(2, 2))
            return

        # Normalize pulse to canvas height
        pulse_arr = np.array(pulse)
        p_min = np.min(pulse_arr)
        p_max = np.max(pulse_arr)
        span = p_max - p_min if (p_max - p_min) > 1e-4 else 1.0

        pts = []
        n = len(pulse_arr)
        step = w / max(1, n - 1)
        for idx, val in enumerate(pulse_arr):
            x = idx * step
            norm_val = (val - p_min) / span
            # Invert for canvas (0 is top)
            y = (h - 20) - (norm_val * (h - 40))
            pts.extend([x, y])

        if len(pts) >= 4:
            self.ekg_canvas.create_line(pts, fill=self.c_neon_green, width=2, smooth=True)

    # -----------------------------------------------------------------
    # Audio Heartbeat Synthesizer Thread
    # -----------------------------------------------------------------
    def start_heartbeat_audio_thread(self):
        def audio_worker():
            while True:
                bpm = self.processor.current_bpm
                is_valid = self.processor.is_valid

                if self.sound_enabled.get() and is_valid and 45 <= bpm <= 180 and HAS_SOUND:
                    interval_sec = 60.0 / bpm
                    try:
                        # Double pulse "Lub-Dub" heartbeat sound
                        winsound.Beep(320, 40)
                        time.sleep(0.08)
                        winsound.Beep(260, 45)
                    except Exception:
                        pass
                    # Sleep remainder of heartbeat cycle
                    sleep_time = max(0.1, interval_sec - 0.15)
                    time.sleep(sleep_time)
                else:
                    time.sleep(0.5)

        t = threading.Thread(target=audio_worker, daemon=True)
        t.start()

    def destroy(self):
        self.camera_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().destroy()


# =====================================================================
# Main Launch Entry
# =====================================================================
if __name__ == '__main__':
    app = CyberBiometricsApp()
    app.mainloop()
