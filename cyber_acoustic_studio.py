"""
=============================================================================
🔊 CYBER ACOUSTIC & SPECTROGRAM STUDIO (Ultrasonic Air-Gap & Audio Stego)
=============================================================================
Author: Antigravity Pair Programmer
Architecture: FSK Ultrasonic Acoustic Modem (18-20 kHz) + Spectrogram Art Synthesizer
=============================================================================
"""

import sys
import os
import time
import math
import wave
import struct
import random
import threading
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk

# PyAudio & Audio Engine
try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


# =====================================================================
# Ultrasonic FSK Acoustic Protocol Constants
# =====================================================================
SAMPLE_RATE = 44100
FREQ_SYNC = 17800   # Sync Preamble Tone
FREQ_BIT0 = 18600   # Binary 0 Tone
FREQ_BIT1 = 19400   # Binary 1 Tone
BIT_DURATION = 0.040  # 40ms per bit (25 bps robust transfer)


# =====================================================================
# Ultrasonic Air-Gap FSK Transmitter Engine
# =====================================================================
class UltrasonicTransmitter:
    @staticmethod
    def encode_message(text):
        """Converts plaintext to FSK acoustic wave array."""
        data_bytes = text.encode('utf-8', errors='ignore')
        if len(data_bytes) == 0:
            return np.array([], dtype=np.float32)

        # Simple checksum
        checksum = sum(data_bytes) % 256
        payload = bytearray(data_bytes) + bytearray([checksum])

        samples_per_bit = int(SAMPLE_RATE * BIT_DURATION)
        audio_chunks = []

        # 1. Preamble Sync (120ms sync tone)
        t_sync = np.linspace(0, 0.12, int(SAMPLE_RATE * 0.12), endpoint=False)
        sync_wave = 0.85 * np.sin(2 * np.pi * FREQ_SYNC * t_sync)
        # Apply smooth fade in/out envelope
        env_sync = np.sin(np.linspace(0, np.pi, len(sync_wave))) ** 2
        audio_chunks.append(sync_wave * env_sync)

        # 2. Transmit each byte: Start Bit (0) + 8 Data Bits + Stop Bit (1)
        for b in payload:
            # Framing: 0 (start), bit0..bit7, 1 (stop)
            bits = [0] + [(b >> i) & 1 for i in range(8)] + [1]
            for bit in bits:
                freq = FREQ_BIT1 if bit == 1 else FREQ_BIT0
                t_bit = np.linspace(0, BIT_DURATION, samples_per_bit, endpoint=False)
                bit_wave = 0.85 * np.sin(2 * np.pi * freq * t_bit)
                # Taper bit edges to prevent acoustic pops
                env_bit = np.sin(np.linspace(0, np.pi, len(bit_wave))) ** 0.5
                audio_chunks.append(bit_wave * env_bit)

        # Trailing silence
        audio_chunks.append(np.zeros(int(SAMPLE_RATE * 0.08), dtype=np.float32))
        full_audio = np.concatenate(audio_chunks).astype(np.float32)
        return full_audio

    @staticmethod
    def play_audio(audio_samples):
        """Plays synthesized ultrasonic waveform through speakers."""
        if not HAS_PYAUDIO:
            return False

        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)
            # Write in chunks
            chunk_size = 1024
            for i in range(0, len(audio_samples), chunk_size):
                chunk = audio_samples[i:i+chunk_size]
                stream.write(chunk.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
            return True
        except Exception as e:
            print("PyAudio playback error:", e)
            return False


# =====================================================================
# Ultrasonic Air-Gap FSK Receiver Engine (Microphone Listener)
# =====================================================================
class UltrasonicReceiver:
    def __init__(self, callback_on_message=None, callback_on_energy=None):
        self.callback_on_message = callback_on_message
        self.callback_on_energy = callback_on_energy
        self.listening = False
        self.stream = None
        self.pyaudio_instance = None
        self.thread = None

    def start(self):
        if not HAS_PYAUDIO or self.listening:
            return False

        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.listening = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass

    def _listen_loop(self):
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            chunk_size = 1024
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=chunk_size
            )
        except Exception as e:
            print("Receiver microphone open failed:", e)
            self.listening = False
            return

        # Demodulator State
        in_sync = False
        bit_buffer = []
        received_bytes = []
        samples_per_bit = int(SAMPLE_RATE * BIT_DURATION)

        while self.listening:
            try:
                raw_data = self.stream.read(chunk_size, exception_on_overflow=False)
                samples = np.frombuffer(raw_data, dtype=np.float32)

                # Compute FFT on chunk
                N = len(samples)
                fft_vals = np.abs(np.fft.rfft(samples * np.hamming(N)))
                freqs = np.fft.rfftfreq(N, d=(1.0 / SAMPLE_RATE))

                # Measure energy at target ultrasonic frequencies
                e_sync = self._get_band_energy(fft_vals, freqs, FREQ_SYNC, 150)
                e_bit0 = self._get_band_energy(fft_vals, freqs, FREQ_BIT0, 150)
                e_bit1 = self._get_band_energy(fft_vals, freqs, FREQ_BIT1, 150)

                total_us_energy = e_sync + e_bit0 + e_bit1
                if self.callback_on_energy:
                    self.callback_on_energy(total_us_energy)

                # Sync detection
                if e_sync > 0.45 and e_sync > (e_bit0 + e_bit1) * 1.5:
                    in_sync = True
                    bit_buffer = []
                    received_bytes = []
                    continue

                if in_sync:
                    if e_bit1 > e_bit0 and e_bit1 > 0.20:
                        detected_bit = 1
                    elif e_bit0 > e_bit1 and e_bit0 > 0.20:
                        detected_bit = 0
                    else:
                        detected_bit = None

                    if detected_bit is not None:
                        bit_buffer.append(detected_bit)

                    # When we have 10 bits: [0 (start), b0..b7, 1 (stop)]
                    if len(bit_buffer) >= 10:
                        # Extract 8 data bits
                        byte_val = 0
                        for idx, b in enumerate(bit_buffer[1:9]):
                            byte_val |= (b << idx)

                        received_bytes.append(byte_val)
                        bit_buffer = []

                        # Check if message is complete
                        if len(received_bytes) >= 2:
                            # Verify checksum
                            payload_data = bytes(received_bytes[:-1])
                            expected_chk = sum(payload_data) % 256
                            actual_chk = received_bytes[-1]

                            if expected_chk == actual_chk:
                                decoded_msg = payload_data.decode('utf-8', errors='ignore')
                                if decoded_msg and self.callback_on_message:
                                    self.callback_on_message(decoded_msg)
                                in_sync = False
                                received_bytes = []

            except Exception:
                pass

        if self.stream:
            self.stream.close()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()

    def _get_band_energy(self, fft_vals, freqs, target_f, bandwidth):
        mask = (freqs >= target_f - bandwidth) & (freqs <= target_f + bandwidth)
        return float(np.mean(fft_vals[mask])) if np.any(mask) else 0.0


# =====================================================================
# Audio Spectrogram Art Synthesizer (Image-to-Sound)
# =====================================================================
class SpectrogramArtEngine:
    @staticmethod
    def synthesize_image_to_audio(img, duration=4.0, f_min=1000, f_max=8000):
        """Converts an image into an audio waveform whose spectrogram reveals the picture."""
        # Convert to grayscale and resize to (width=200 time-steps, height=64 frequency bins)
        img_gray = img.convert('L')
        n_freq_bins = 64
        n_time_steps = int(duration * 40)
        resized = img_gray.resize((n_time_steps, n_freq_bins), Image.Resampling.LANCZOS)
        img_data = np.array(resized)

        # Invert vertical axis so high frequencies are at the top of the image
        img_data = np.flipud(img_data)

        # Normalize pixel brightness 0.0 to 1.0
        img_norm = img_data.astype(np.float32) / 255.0

        # Frequency mapping for each row
        freqs = np.linspace(f_min, f_max, n_freq_bins)
        samples_per_step = int(SAMPLE_RATE * (duration / n_time_steps))
        audio_chunks = []

        # Additive sinusoidal synthesis
        for col in range(n_time_steps):
            t_col = np.linspace(0, duration / n_time_steps, samples_per_step, endpoint=False)
            col_wave = np.zeros(samples_per_step, dtype=np.float32)
            
            for row in range(n_freq_bins):
                amp = img_norm[row, col]
                if amp > 0.05:
                    f = freqs[row]
                    col_wave += amp * np.sin(2 * np.pi * f * t_col)

            # Smooth column boundary
            col_wave = col_wave / (n_freq_bins * 0.15 + 1.0)
            audio_chunks.append(col_wave)

        full_audio = np.concatenate(audio_chunks).astype(np.float32)
        # Normalize audio peak
        max_amp = np.max(np.abs(full_audio))
        if max_amp > 1e-4:
            full_audio = 0.90 * (full_audio / max_amp)

        return full_audio

    @staticmethod
    def create_text_image(text):
        """Generates a high-contrast binary image with custom text/art."""
        img = Image.new('L', (300, 100), color=0)
        draw = ImageDraw.Draw(img)
        # Draw text centered
        draw.text((20, 30), text, fill=255)
        return img


# =====================================================================
# Main Application GUI
# =====================================================================
class CyberAcousticStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔊 CYBER ACOUSTIC & SPECTROGRAM STUDIO")
        self.geometry("1280x820")
        self.minsize(1050, 700)
        self.configure(bg="#030611")

        # Cyber Colors
        self.c_bg = "#030611"
        self.c_panel = "#080e1e"
        self.c_card = "#0e1830"
        self.c_border = "#162744"
        self.c_neon_cyan = "#00f0ff"
        self.c_neon_green = "#00ff9d"
        self.c_neon_amber = "#ffb703"
        self.c_neon_red = "#ff0055"
        self.c_neon_purple = "#a855f7"
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        # Engines
        self.receiver = UltrasonicReceiver(
            callback_on_message=self.on_airgap_message_received,
            callback_on_energy=self.on_airgap_energy_update
        )
        self.synthesized_art_audio = None
        self.spec_waterfall_history = deque(maxlen=200)

        self.setup_ui()
        self.start_receiver_safely()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg=self.c_panel, height=65, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=self.c_panel)
        title_box.pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(title_box, text="🔊 CYBER ACOUSTIC & SPECTROGRAM STUDIO", font=('Segoe UI', 14, 'bold'),
                 bg=self.c_panel, fg=self.c_neon_cyan).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_box, text="Inaudible Ultrasonic Air-Gap Modem (18-20 kHz) • Audio Spectrogram Art Synthesizer", font=('Segoe UI', 9),
                 bg=self.c_panel, fg=self.c_muted).pack(side=tk.LEFT)

        self.lbl_mic_status = tk.Label(header, text="🎤 ULTRASONIC RX: LISTENING", font=('Segoe UI', 9, 'bold'),
                                       bg=self.c_card, fg=self.c_neon_green, padx=12, pady=4,
                                       highlightthickness=1, highlightbackground=self.c_border)
        self.lbl_mic_status.pack(side=tk.RIGHT, padx=20, pady=16)

        # Tabbed Notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.c_bg, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.c_card, foreground=self.c_text,
                        padding=[16, 8], font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.c_panel)], foreground=[('selected', self.c_neon_cyan)])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        # Tab 1: Ultrasonic Air-Gap Modem
        tab_airgap = tk.Frame(self.notebook, bg=self.c_bg)
        self.notebook.add(tab_airgap, text="📡 1. Ultrasonic Air-Gap Modem (18-20 kHz)")
        self.build_airgap_tab(tab_airgap)

        # Tab 2: Audio Spectrogram Art Synthesizer
        tab_spectrogram = tk.Frame(self.notebook, bg=self.c_bg)
        self.notebook.add(tab_spectrogram, text="🎨 2. Audio Spectrogram Art Studio")
        self.build_spectrogram_tab(tab_spectrogram)

    # -----------------------------------------------------------------
    # Tab 1: Ultrasonic Air-Gap Modem UI
    # -----------------------------------------------------------------
    def build_airgap_tab(self, parent):
        pad = 12
        main_box = tk.Frame(parent, bg=self.c_bg)
        main_box.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)

        # Left Column: Transmitter Panel
        tx_col = tk.Frame(main_box, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=16)
        tx_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(tx_col, text="🔊 INAUDIBLE ULTRASONIC TRANSMITTER (TX)", font=('Segoe UI', 11, 'bold'), bg=self.c_panel, fg=self.c_neon_cyan).pack(anchor='w')
        tk.Label(tx_col, text="Encodes text into silent 18.0 - 19.5 kHz FSK sound waves and transmits via laptop speaker.",
                 font=('Segoe UI', 8), bg=self.c_panel, fg=self.c_muted, wraplength=450, justify=tk.LEFT).pack(anchor='w', pady=(2, 10))

        tk.Label(tx_col, text="Secret Message Payload:", font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_text).pack(anchor='w')
        self.txt_tx_input = tk.Text(tx_col, bg=self.c_card, fg=self.c_neon_green, font=('Consolas', 10),
                                    height=6, highlightthickness=1, highlightbackground=self.c_border, insertbackground=self.c_neon_green)
        self.txt_tx_input.pack(fill=tk.X, pady=(4, 10))
        self.txt_tx_input.insert(tk.END, "FSOCIETY_PASSKEY_99482")

        btn_tx = tk.Button(tx_col, text="⚡ TRANSMIT OVER SILENT SOUND WAVES 🚀", bg=self.c_neon_cyan, fg="#030611",
                           font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, pady=8, cursor='hand2',
                           activebackground="#0284c7", activeforeground="#ffffff",
                           command=self.transmit_airgap_message)
        btn_tx.pack(fill=tk.X, pady=(4, 10))

        self.lbl_tx_status = tk.Label(tx_col, text="Status: Ready to transmit.", font=('Segoe UI', 9), bg=self.c_panel, fg=self.c_muted)
        self.lbl_tx_status.pack(anchor='w')

        # Right Column: Receiver Console
        rx_col = tk.Frame(main_box, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=16)
        rx_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(rx_col, text="🎤 LIVE ULTRASONIC RECEIVER CONSOLE (RX)", font=('Segoe UI', 11, 'bold'), bg=self.c_panel, fg=self.c_neon_green).pack(anchor='w')
        tk.Label(rx_col, text="Listens to microphone in real time, demodulates FSK frequency shifts, and prints decoded secrets.",
                 font=('Segoe UI', 8), bg=self.c_panel, fg=self.c_muted, wraplength=450, justify=tk.LEFT).pack(anchor='w', pady=(2, 10))

        tk.Label(rx_col, text="Decoded Intercepted Messages:", font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_text).pack(anchor='w')
        self.txt_rx_output = tk.Text(rx_col, bg="#02040b", fg=self.c_neon_green, font=('Consolas', 10),
                                     height=8, highlightthickness=1, highlightbackground=self.c_border, state=tk.DISABLED)
        self.txt_rx_output.pack(fill=tk.BOTH, expand=True, pady=(4, 10))

        btn_clear_rx = tk.Button(rx_col, text="🗑️ Clear Received Log", bg=self.c_card, fg=self.c_muted,
                                 font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=10, pady=4, cursor='hand2',
                                 command=self.clear_rx_log)
        btn_clear_rx.pack(anchor='e')

    def transmit_airgap_message(self):
        text = self.txt_tx_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty Message", "Please enter a message to transmit.")
            return

        self.lbl_tx_status.config(text="📡 Modulating & Transmitting ultrasonic packet...", fg=self.c_neon_cyan)

        def worker():
            audio_samples = UltrasonicTransmitter.encode_message(text)
            success = UltrasonicTransmitter.play_audio(audio_samples)
            if success:
                self.lbl_tx_status.config(text=f"✔ Successfully emitted silent packet ({len(text)} chars)!", fg=self.c_neon_green)
            else:
                self.lbl_tx_status.config(text="⚠ Audio playback error (Check PyAudio output)", fg=self.c_neon_red)

        threading.Thread(target=worker, daemon=True).start()

    def start_receiver_safely(self):
        started = self.receiver.start()
        if not started:
            self.lbl_mic_status.config(text="🎤 RX: MIC NOT AVAILABLE", fg=self.c_neon_red)

    def on_airgap_message_received(self, msg):
        self.after(0, lambda: self._append_rx_message(msg))

    def _append_rx_message(self, msg):
        t_str = time.strftime('%H:%M:%S')
        self.txt_rx_output.config(state=tk.NORMAL)
        self.txt_rx_output.insert(tk.END, f"[{t_str}] 📥 RECEIVED: {msg}\n")
        self.txt_rx_output.see(tk.END)
        self.txt_rx_output.config(state=tk.DISABLED)

        if HAS_WINSOUND:
            try:
                winsound.Beep(2400, 60)
            except Exception:
                pass

    def on_airgap_energy_update(self, energy):
        pass

    def clear_rx_log(self):
        self.txt_rx_output.config(state=tk.NORMAL)
        self.txt_rx_output.delete("1.0", tk.END)
        self.txt_rx_output.config(state=tk.DISABLED)

    # -----------------------------------------------------------------
    # Tab 2: Audio Spectrogram Art Synthesizer UI
    # -----------------------------------------------------------------
    def build_spectrogram_tab(self, parent):
        pad = 12
        main_box = tk.Frame(parent, bg=self.c_bg)
        main_box.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)

        # Left Column: Synthesizer Controls
        synth_col = tk.Frame(main_box, bg=self.c_panel, width=420, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=16)
        synth_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 8))
        synth_col.pack_propagate(False)

        tk.Label(synth_col, text="🎨 SPECTROGRAM ART ENCODER", font=('Segoe UI', 11, 'bold'), bg=self.c_panel, fg=self.c_neon_purple).pack(anchor='w')
        tk.Label(synth_col, text="Encodes images or secret text into audible sound waves that reveal the picture when viewed in a spectral analyzer.",
                 font=('Segoe UI', 8), bg=self.c_panel, fg=self.c_muted, wraplength=380, justify=tk.LEFT).pack(anchor='w', pady=(2, 10))

        # Text Art Input
        tk.Label(synth_col, text="Secret Text to Encode into Sound:", font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_text).pack(anchor='w')
        self.txt_art_input = tk.Entry(synth_col, bg=self.c_card, fg=self.c_neon_cyan, font=('Consolas', 11, 'bold'),
                                      highlightthickness=1, highlightbackground=self.c_border, insertbackground=self.c_neon_cyan)
        self.txt_art_input.pack(fill=tk.X, pady=(4, 10))
        self.txt_art_input.insert(0, "FSOCIETY // 5-9")

        btn_synth_text = tk.Button(synth_col, text="⚡ SYNTHESIZE TEXT INTO AUDIO", bg=self.c_neon_purple, fg="#ffffff",
                                   font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                                   activebackground="#9333ea", activeforeground="#ffffff",
                                   command=self.synthesize_text_art)
        btn_synth_text.pack(fill=tk.X, pady=4)

        tk.Label(synth_col, text="OR Load an Image File:", font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_text).pack(anchor='w', pady=(10, 2))
        btn_load_img = tk.Button(synth_col, text="📁 Choose Custom Image File...", bg=self.c_card, fg=self.c_neon_cyan,
                                 font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=6, cursor='hand2',
                                 command=self.load_image_file)
        btn_load_img.pack(fill=tk.X, pady=4)

        # Audio Play & Export
        tk.Label(synth_col, text="Audio Controls:", font=('Segoe UI', 9, 'bold'), bg=self.c_panel, fg=self.c_text).pack(anchor='w', pady=(14, 2))

        btn_play = tk.Button(synth_col, text="▶ PLAY SOUND & VIEW SPECTROGRAM", bg=self.c_neon_green, fg="#030611",
                             font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, pady=8, cursor='hand2',
                             activebackground="#059669", activeforeground="#ffffff",
                             command=self.play_spectrogram_audio)
        btn_play.pack(fill=tk.X, pady=4)

        btn_export = tk.Button(synth_col, text="💾 Export to WAV File...", bg=self.c_border, fg=self.c_text,
                               font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, pady=5, cursor='hand2',
                               command=self.export_wav_file)
        btn_export.pack(fill=tk.X, pady=4)

        self.lbl_synth_info = tk.Label(synth_col, text="Ready. Synthesize text or image to begin.", font=('Segoe UI', 8), bg=self.c_panel, fg=self.c_muted)
        self.lbl_synth_info.pack(anchor='w', pady=(8, 0))

        # Right Column: Real-Time Spectrogram Waterfall Viewer
        spec_col = tk.Frame(main_box, bg=self.c_panel, highlightthickness=1, highlightbackground=self.c_border, padx=16, pady=16)
        spec_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(spec_col, text="🌌 REAL-TIME SPECTRAL WATERFALL ANALYZER", font=('Segoe UI', 11, 'bold'), bg=self.c_panel, fg=self.c_neon_green).pack(anchor='w')
        tk.Label(spec_col, text="Visualizes sound frequencies live. As the audio plays, your secret image will reveal itself in the glowing waterfall!",
                 font=('Segoe UI', 8), bg=self.c_panel, fg=self.c_muted).pack(anchor='w', pady=(2, 10))

        self.spec_canvas = tk.Canvas(spec_col, bg="#02050e", highlightthickness=0)
        self.spec_canvas.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    def synthesize_text_art(self):
        text = self.txt_art_input.get().strip()
        if not text:
            return
        img = SpectrogramArtEngine.create_text_image(text)
        self.synthesized_art_audio = SpectrogramArtEngine.synthesize_image_to_audio(img, duration=3.5)
        self.lbl_synth_info.config(text=f"✔ Synthesized text '{text}' into 3.5s audio!", fg=self.c_neon_green)
        self.render_spectrogram_preview(self.synthesized_art_audio)

    def load_image_file(self):
        fpath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if fpath and os.path.exists(fpath):
            try:
                img = Image.open(fpath)
                self.synthesized_art_audio = SpectrogramArtEngine.synthesize_image_to_audio(img, duration=4.0)
                self.lbl_synth_info.config(text=f"✔ Encoded image '{os.path.basename(fpath)}' into audio!", fg=self.c_neon_green)
                self.render_spectrogram_preview(self.synthesized_art_audio)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {e}")

    def render_spectrogram_preview(self, audio):
        """Draws the computed STFT spectrogram onto the canvas."""
        self.spec_canvas.delete("all")
        w = max(100, self.spec_canvas.winfo_width())
        h = max(100, self.spec_canvas.winfo_height())

        # Compute STFT
        f, t, Zxx = signal.stft(audio, fs=SAMPLE_RATE, nperseg=256, noverlap=128)
        spec_mag = np.abs(Zxx)

        # Normalize
        spec_norm = spec_mag / (np.max(spec_mag) + 1e-6)
        n_freqs, n_times = spec_norm.shape

        # Render heat map
        step_x = w / n_times
        step_y = h / n_freqs

        for t_idx in range(n_times):
            for f_idx in range(n_freqs):
                val = spec_norm[f_idx, t_idx]
                if val > 0.08:
                    # Invert Y for canvas (high freq on top)
                    x0 = t_idx * step_x
                    y0 = h - (f_idx * step_y)
                    x1 = x0 + step_x
                    y1 = y0 - step_y

                    # Color map (Cyan / Purple / Green heat)
                    if val > 0.6:
                        color = "#00f0ff"
                    elif val > 0.3:
                        color = "#a855f7"
                    else:
                        color = "#00ff9d"

                    self.spec_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def play_spectrogram_audio(self):
        if self.synthesized_art_audio is None:
            self.synthesize_text_art()

        def worker():
            UltrasonicTransmitter.play_audio(self.synthesized_art_audio)

        threading.Thread(target=worker, daemon=True).start()

    def export_wav_file(self):
        if self.synthesized_art_audio is None:
            messagebox.showwarning("No Audio", "Please synthesize an audio file first.")
            return

        fpath = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Audio", "*.wav")])
        if fpath:
            try:
                # Convert float32 to int16
                int_audio = (self.synthesized_art_audio * 32767).astype(np.int16)
                with wave.open(fpath, 'w') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(int_audio.tobytes())
                messagebox.showinfo("Export Success", f"Audio successfully saved to:\n{fpath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save WAV: {e}")

    def destroy(self):
        self.receiver.stop()
        super().destroy()


# =====================================================================
# Launch Entry
# =====================================================================
if __name__ == '__main__':
    app = CyberAcousticStudioApp()
    app.mainloop()
