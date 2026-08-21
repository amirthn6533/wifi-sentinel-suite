"""
Wi-Fi Radar & Frequency Spectrum Analyzer + Security & Audit Module
Author: Antigravity Pair Programmer
Edition: Cyberpunk Neon HUD & Hardware Antenna Selector (English Edition)
"""

import sys
import os
import re
import math
import time
import subprocess
import threading
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Windows sound for Signal Tracker Beep
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


class MacVendorLookup:
    """Detects hardware manufacturer from MAC Address OUI (Organizationally Unique Identifier)."""
    
    OUI_DATABASE = {
        # TP-Link
        "50:D4:F7": "TP-Link", "E8:48:B8": "TP-Link", "B0:4E:26": "TP-Link", "AC:84:C6": "TP-Link",
        "D8:0D:17": "TP-Link", "C0:06:C3": "TP-Link", "14:EB:B6": "TP-Link", "60:32:B1": "TP-Link",
        "00:1D:0F": "TP-Link", "00:23:CD": "TP-Link", "00:25:86": "TP-Link", "0C:80:63": "TP-Link",
        "1C:3B:F3": "TP-Link", "30:B5:C2": "TP-Link", "38:83:45": "TP-Link", "54:AF:97": "TP-Link",
        "5C:E9:31": "TP-Link", "70:4F:57": "TP-Link", "74:05:A5": "TP-Link", "74:DA:88": "TP-Link",
        "84:16:F9": "TP-Link", "90:F6:52": "TP-Link", "98:48:27": "TP-Link", "A0:F3:C1": "TP-Link",
        "C4:E9:84": "TP-Link", "CC:34:29": "TP-Link", "E4:C3:2A": "TP-Link", "F4:EC:38": "TP-Link",
        "F4:F2:6D": "TP-Link", "00:0A:EB": "TP-Link", "34:60:F9": "TP-Link", "80:8C:97": "TP-Link",
        "CC:32:E5": "TP-Link", "18:A6:F7": "TP-Link", "40:31:3C": "TP-Link", "94:83:C4": "TP-Link",
        
        # Huawei
        "00:E0:FC": "Huawei", "04:25:C5": "Huawei", "04:F9:38": "Huawei", "08:19:A6": "Huawei",
        "08:63:61": "Huawei", "0C:96:BF": "Huawei", "10:1B:54": "Huawei", "10:47:80": "Huawei",
        "14:B9:68": "Huawei", "20:F3:A3": "Huawei", "24:69:A5": "Huawei", "28:6E:D4": "Huawei",
        "34:00:A3": "Huawei", "48:46:FB": "Huawei", "70:7B:E8": "Huawei", "78:D7:52": "Huawei",
        "80:B6:86": "Huawei", "88:86:03": "Huawei", "AC:85:3D": "Huawei", "B4:15:13": "Huawei",
        "CC:96:A0": "Huawei", "E0:24:7F": "Huawei", "F4:C4:D0": "Huawei", "F8:3D:FF": "Huawei",
        "00:1E:10": "Huawei", "00:25:9E": "Huawei", "20:08:89": "Huawei", "30:87:30": "Huawei",
        "60:DE:44": "Huawei", "70:D9:23": "Huawei", "E8:CD:2D": "Huawei", "4C:54:99": "Huawei",
        
        # D-Link
        "00:05:5D": "D-Link", "00:0D:88": "D-Link", "00:15:E9": "D-Link", "00:17:9A": "D-Link",
        "00:19:5B": "D-Link", "00:1B:11": "D-Link", "00:1C:F0": "D-Link", "00:1E:58": "D-Link",
        "00:21:91": "D-Link", "00:22:B0": "D-Link", "00:24:01": "D-Link", "00:26:5A": "D-Link",
        "14:D6:4D": "D-Link", "1C:7E:E5": "D-Link", "28:10:7B": "D-Link", "34:08:04": "D-Link",
        "78:54:2E": "D-Link", "84:C9:B2": "D-Link", "90:94:E4": "D-Link", "B0:C5:54": "D-Link",
        "C8:D3:A3": "D-Link", "CC:B2:55": "D-Link", "E4:6F:13": "D-Link", "FC:75:16": "D-Link",
        
        # Cisco / Linksys
        "00:00:0C": "Cisco", "00:01:42": "Cisco", "00:01:43": "Cisco", "00:01:63": "Cisco",
        "00:01:64": "Cisco", "00:01:96": "Cisco", "00:01:97": "Cisco", "00:06:52": "Linksys/Cisco",
        "00:0F:66": "Cisco", "00:11:20": "Cisco", "00:14:1B": "Cisco", "00:17:DF": "Cisco",
        "00:18:18": "Linksys/Cisco", "00:1A:A1": "Cisco", "00:22:BD": "Cisco", "00:23:EB": "Cisco",
        "18:8B:9D": "Cisco", "28:52:61": "Cisco", "3C:08:F6": "Cisco", "44:AD:D9": "Cisco",
        "50:3D:E5": "Cisco", "64:00:F1": "Cisco", "70:10:5C": "Cisco", "88:5A:92": "Cisco",
        "C4:64:13": "Cisco", "E4:AA:5D": "Cisco", "F4:4E:05": "Cisco", "FC:5B:39": "Cisco",
        
        # Netgear
        "00:09:5B": "Netgear", "00:0F:B5": "Netgear", "00:14:6C": "Netgear", "00:18:4D": "Netgear",
        "00:1E:2A": "Netgear", "00:1F:33": "Netgear", "00:24:B2": "Netgear", "00:26:F2": "Netgear",
        "04:A1:51": "Netgear", "08:BD:43": "Netgear", "10:DA:43": "Netgear", "20:0C:C8": "Netgear",
        "28:C6:8E": "Netgear", "30:46:9A": "Netgear", "84:1B:5E": "Netgear", "9C:3D:CF": "Netgear",
        "A0:04:60": "Netgear", "A4:2B:B0": "Netgear", "B0:39:56": "Netgear", "C0:3F:0E": "Netgear",
        "CC:40:D0": "Netgear", "E0:46:9A": "Netgear", "F8:E9:03": "Netgear", "2C:30:33": "Netgear",
        
        # Xiaomi
        "00:9E:C8": "Xiaomi", "04:CF:8C": "Xiaomi", "0C:1D:AF": "Xiaomi", "14:F6:5A": "Xiaomi",
        "18:59:36": "Xiaomi", "28:6C:07": "Xiaomi", "34:80:B3": "Xiaomi", "3C:BD:3E": "Xiaomi",
        "50:64:2B": "Xiaomi", "58:44:98": "Xiaomi", "64:09:80": "Xiaomi", "74:23:44": "Xiaomi",
        "78:02:F8": "Xiaomi", "7C:49:EB": "Xiaomi", "88:C3:97": "Xiaomi", "9C:2E:A1": "Xiaomi",
        "A4:77:33": "Xiaomi", "AC:C1:EE": "Xiaomi", "B0:E2:35": "Xiaomi", "D4:97:0B": "Xiaomi",
        "E4:AA:EC": "Xiaomi", "F0:B4:29": "Xiaomi", "F4:F5:DB": "Xiaomi", "68:7A:B4": "Xiaomi",
        
        # ZTE & ISP Modems (Sagemcom, Nokia, Arcadyan)
        "00:1E:73": "ZTE", "00:22:93": "ZTE", "00:25:12": "ZTE", "04:79:70": "ZTE",
        "08:18:1A": "ZTE", "10:C6:1F": "ZTE", "14:60:80": "ZTE", "28:FF:3E": "ZTE",
        "30:F3:35": "ZTE", "34:E0:CF": "ZTE", "4C:09:B4": "ZTE", "54:22:F8": "ZTE",
        "68:1A:B2": "ZTE", "74:7D:24": "ZTE", "84:74:2A": "ZTE", "B0:75:D5": "ZTE",
        "C8:7B:5B": "ZTE", "D8:55:A3": "ZTE", "DC:02:8E": "ZTE", "E0:05:C5": "ZTE",
        "F4:6D:E2": "ZTE", "FC:2D:5E": "ZTE", "38:FA:CA": "ZTE", "B0:0A:D5": "ZTE",
        "F0:33:E5": "ZTE", "3C:6A:D2": "ZTE", "18:B0:A4": "ZTE/Sagemcom", "64:13:AB": "Arcadyan/ZTE",
        "24:91:BB": "Sagemcom", "78:4F:24": "Nokia (Vivacom)", "00:18:01": "Nokia",
        "AC:84:C9": "Sagemcom", "DC:53:7C": "Sagemcom", "E8:F1:B0": "Sagemcom",
        "00:1A:2B": "Arcadyan", "44:48:B9": "Arcadyan", "70:9F:2D": "Arcadyan",
        "00:0F:E2": "Fiberhome", "84:79:73": "Fiberhome", "CC:81:DA": "Fiberhome",
        
        # MikroTik & Ubiquiti
        "00:0C:42": "MikroTik", "2C:C8:1B": "MikroTik", "48:8F:5A": "MikroTik", "64:D1:54": "MikroTik",
        "6C:3B:6B": "MikroTik", "74:4D:28": "MikroTik", "78:9A:18": "MikroTik", "AC:FF:77": "MikroTik",
        "00:15:6D": "Ubiquiti", "00:27:22": "Ubiquiti", "04:18:D6": "Ubiquiti", "18:E8:29": "Ubiquiti",
        "24:A4:3C": "Ubiquiti", "44:D9:E7": "Ubiquiti", "68:72:51": "Ubiquiti", "70:8B:CD": "Ubiquiti",
        
        # Apple
        "00:03:93": "Apple", "00:05:02": "Apple", "00:0A:95": "Apple", "00:1B:63": "Apple",
        "00:1E:C2": "Apple", "00:23:12": "Apple", "00:26:08": "Apple", "04:0C:CE": "Apple",
        "10:1C:0C": "Apple", "14:10:9F": "Apple", "18:AF:61": "Apple", "20:76:8F": "Apple",
        "24:F0:94": "Apple", "28:CF:DA": "Apple", "34:36:3B": "Apple", "3C:07:54": "Apple",
        "40:26:19": "Apple", "44:4C:0C": "Apple", "48:60:5F": "Apple", "50:EA:D6": "Apple",
        
        # Samsung
        "00:07:AB": "Samsung", "00:15:99": "Samsung", "00:18:AF": "Samsung", "00:23:39": "Samsung",
        "04:18:0F": "Samsung", "08:08:C2": "Samsung", "10:14:4F": "Samsung", "14:49:E0": "Samsung",
        "18:22:7E": "Samsung", "20:55:31": "Samsung", "24:4B:03": "Samsung", "28:98:7B": "Samsung",
        
        # Realtek / Intel
        "00:E0:4C": "Realtek", "52:54:00": "QEMU/Realtek", "00:02:B3": "Intel", "00:13:02": "Intel",
        "00:15:00": "Intel", "08:11:96": "Intel", "28:B2:BD": "Intel", "44:85:00": "Intel"
    }

    @classmethod
    def lookup(cls, bssid: str) -> str:
        if not bssid or len(bssid) < 8:
            return "Unknown"
        clean_mac = bssid.upper().replace("-", ":")
        parts = clean_mac.split(":")
        if len(parts) >= 3:
            oui = ":".join(parts[:3])
            if oui in cls.OUI_DATABASE:
                return cls.OUI_DATABASE[oui]
            try:
                first_byte = int(parts[0], 16)
                if first_byte & 0x02 != 0:
                    return "📱 Private / Randomized MAC"
            except ValueError:
                pass
        return "Generic Vendor"


class SecurityAuditor:
    """Analyzes security vulnerabilities, encryption strength, and detects Rogue AP / Evil Twin."""
    
    @staticmethod
    def audit_network(net: dict) -> dict:
        auth = net.get('auth', '').upper()
        enc = net.get('encryption', '').upper()
        
        if 'OPEN' in auth or 'NONE' in auth or 'NONE' in enc or not auth or auth == 'UNKNOWN':
            return {
                'risk_code': 'CRITICAL',
                'risk_title': '🔴 Critical: Open & Unencrypted Network',
                'risk_badge': '🔴 Insecure (Open)',
                'risk_color': '#f43f5e',
                'is_insecure': True,
                'advice': 'All transmitted packets are broadcast in cleartext over the air. Anyone in range can sniff web traffic, login credentials, and session tokens. Do not connect without an encrypted VPN!'
            }
        if 'WEP' in auth or 'WEP' in enc:
            return {
                'risk_code': 'CRITICAL',
                'risk_title': '🔴 Critical: Obsolete WEP Protocol',
                'risk_badge': '🔴 Obsolete (WEP)',
                'risk_color': '#f43f5e',
                'is_insecure': True,
                'advice': 'WEP has been broken for years and can be cracked in minutes using automated tools (e.g. Aircrack-ng). Upgrade router firmware to WPA2/WPA3 immediately.'
            }
        if ('WPA-' in auth or 'WPA ' in auth or 'TKIP' in enc) and 'WPA2' not in auth and 'WPA3' not in auth:
            return {
                'risk_code': 'HIGH',
                'risk_title': '🟠 High Risk: Deprecated WPA-TKIP',
                'risk_badge': '🟠 Legacy (WPA1)',
                'risk_color': '#fb923c',
                'is_insecure': True,
                'advice': 'TKIP encryption contains known cryptographic weaknesses and throttles Wi-Fi bandwidth. Switch router settings to WPA2-PSK (AES/CCMP) or WPA3.'
            }
        if 'WPA3' in auth or 'SAE' in auth or 'OWE' in auth:
            return {
                'risk_code': 'SECURE',
                'risk_title': '🟢 Excellent: Modern WPA3-SAE Standard',
                'risk_badge': '🟢 Highly Secure (WPA3)',
                'risk_color': '#22c55e',
                'is_insecure': False,
                'advice': 'Utilizes cutting-edge SAE encryption. Immune to offline dictionary attacks and prevents past traffic decryption.'
            }
        if 'ENTERPRISE' in auth or '802.1X' in auth:
            return {
                'risk_code': 'SECURE',
                'risk_title': '🟢 Excellent: 802.1X Enterprise Authentication',
                'risk_badge': '🟢 Enterprise (802.1X)',
                'risk_color': '#38bdf8',
                'is_insecure': False,
                'advice': 'Authentication is managed via a centralized secure RADIUS server. Ideal for corporate and university environments.'
            }
        return {
            'risk_code': 'MODERATE',
            'risk_title': '🟡 Standard: Consumer WPA2-Personal (AES)',
            'risk_badge': '🟡 Standard (WPA2)',
            'risk_color': '#f59e0b',
            'is_insecure': False,
            'advice': 'Standard consumer security. Vulnerable to handshake capture and brute-force/dictionary attacks if a weak password is used. Use a passphrase with >12 characters.'
        }

    @classmethod
    def detect_evil_twins(cls, networks: list) -> dict:
        ssid_groups = defaultdict(list)
        for net in networks:
            ssid = net['ssid']
            if ssid and ssid != '<Hidden Network>':
                ssid_groups[ssid].append(net)
                
        evil_twin_results = {}
        for ssid, bssids in ssid_groups.items():
            if len(bssids) <= 1:
                continue
                
            auth_set = set(b['auth'] for b in bssids)
            vendor_set = set(b['vendor'] for b in bssids)
            
            has_open = any('OPEN' in a.upper() or 'NONE' in a.upper() for a in auth_set)
            has_secure = any('WPA' in a.upper() for a in auth_set)
            
            if has_open and has_secure:
                evil_twin_results[ssid] = {
                    'status': 'CRITICAL_EVIL_TWIN',
                    'tag': '🚨 Evil Twin Clone Attack',
                    'color': '#f43f5e',
                    'detail': f'CRITICAL PHISHING RISK! Multiple APs broadcast "{ssid}" with mismatched encryption (one password-protected, one open). An attacker is attempting to harvest credentials!',
                    'count': len(bssids)
                }
            elif len(vendor_set) > 1 and len(bssids) >= 2:
                evil_twin_results[ssid] = {
                    'status': 'SUSPICIOUS_ROUTER',
                    'tag': '⚠️ Suspicious Rogue AP',
                    'color': '#fb923c',
                    'detail': f'Multiple hardware vendors ({", ".join(list(vendor_set)[:2])}) are broadcasting identical SSID "{ssid}". Possible rogue hotspot or clone.',
                    'count': len(bssids)
                }
            else:
                evil_twin_results[ssid] = {
                    'status': 'LEGITIMATE_MESH',
                    'tag': '🟢 Multi-AP Mesh Roaming',
                    'color': '#22c55e',
                    'detail': f'Legitimate mesh deployment with {len(bssids)} coordinated access points for seamless roaming.',
                    'count': len(bssids)
                }
        return evil_twin_results


class WifiScanner:
    """Scans Wi-Fi networks using Windows native netsh command with interface-specific support."""
    
    @staticmethod
    def get_interfaces():
        try:
            raw = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], encoding='cp1252', errors='ignore')
            ifaces = []
            cur = None
            for line in raw.splitlines():
                ls = line.strip()
                if ls.startswith('Name') and ':' in ls:
                    if cur: ifaces.append(cur)
                    cur = {'name': ls.split(':', 1)[1].strip(), 'desc': 'Adapter'}
                elif cur and ls.startswith('Description') and ':' in ls:
                    cur['desc'] = ls.split(':', 1)[1].strip()
            if cur: ifaces.append(cur)
            return ifaces
        except Exception:
            return []

    @staticmethod
    def scan(interface_name=None):
        try:
            cmd = ['netsh', 'wlan', 'show', 'networks', 'mode=bssid']
            if interface_name:
                cmd.append(f'interface={interface_name}')
                
            raw = subprocess.check_output(cmd, encoding='cp1252', errors='ignore')
        except Exception:
            return []

        networks = []
        current_net = None
        current_bssid = None

        for line in raw.splitlines():
            line_s = line.strip()
            if line_s.startswith('SSID'):
                m = re.match(r'SSID\s+\d+\s+:\s*(.*)', line_s)
                if m:
                    ssid_name = m.group(1).strip()
                    current_net = {
                        'ssid': ssid_name if ssid_name else '<Hidden Network>',
                        'auth': 'Unknown',
                        'encryption': 'Unknown',
                        'bssids': []
                    }
                    networks.append(current_net)
            elif 'Authentication' in line_s and current_net:
                current_net['auth'] = line_s.split(':', 1)[1].strip()
            elif 'Encryption' in line_s and current_net:
                current_net['encryption'] = line_s.split(':', 1)[1].strip()
            elif line_s.startswith('BSSID') and current_net:
                m = re.match(r'BSSID\s+\d+\s+:\s*([0-9a-fA-F:]+)', line_s)
                if m:
                    current_bssid = {
                        'bssid': m.group(1).strip(),
                        'signal': 0,
                        'channel': 1,
                        'radio': '802.11n',
                        'band': '2.4 GHz'
                    }
                    current_net['bssids'].append(current_bssid)
            elif 'Signal' in line_s and current_bssid:
                m = re.search(r'(\d+)%', line_s)
                if m:
                    current_bssid['signal'] = int(m.group(1))
            elif 'Channel' in line_s and current_bssid:
                m = re.search(r'Channel\s+:\s*(\d+)', line_s)
                if m:
                    ch = int(m.group(1))
                    current_bssid['channel'] = ch
                    current_bssid['band'] = '5 GHz' if ch > 14 else '2.4 GHz'
            elif 'Radio type' in line_s and current_bssid:
                current_bssid['radio'] = line_s.split(':', 1)[1].strip()

        flat_list = []
        for net in networks:
            for b in net['bssids']:
                dbm = int((b['signal'] / 2.0) - 100)
                vendor = MacVendorLookup.lookup(b['bssid'])
                temp_dict = {
                    'ssid': net['ssid'],
                    'bssid': b['bssid'],
                    'signal': b['signal'],
                    'dbm': dbm,
                    'channel': b['channel'],
                    'band': b['band'],
                    'radio': b['radio'],
                    'auth': net['auth'],
                    'encryption': net['encryption'],
                    'vendor': vendor
                }
                audit = SecurityAuditor.audit_network(temp_dict)
                temp_dict.update(audit)
                flat_list.append(temp_dict)

        evil_twins = SecurityAuditor.detect_evil_twins(flat_list)
        for item in flat_list:
            ssid = item['ssid']
            item['evil_twin_info'] = evil_twins.get(ssid)

        flat_list.sort(key=lambda x: x['signal'], reverse=True)
        return flat_list


class ModernWifiRadarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📡 Wi-Fi Radar & Frequency Analyzer | Cyberpunk Edition")
        self.geometry("1180x800")
        self.minsize(1020, 700)
        self.configure(bg="#070c18")

        self.networks = []
        self.is_scanning = False
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval_ms = 3000
        self.sound_enabled = tk.BooleanVar(value=False)
        self.target_network = tk.StringVar(value="")
        self.target_history = []
        self.security_filter = tk.StringVar(value="ALL")
        self.selected_interface = tk.StringVar(value="")

        # Futuristic Cyberpunk Palette
        self.c_bg = "#070c18"
        self.c_card = "#0f172a"
        self.c_card_hover = "#1e293b"
        self.c_border = "#1e293b"
        self.c_cyan = "#00f0ff"
        self.c_blue = "#38bdf8"
        self.c_green = "#00ff9d"
        self.c_purple = "#c084fc"
        self.c_rose = "#ff0055"
        self.c_amber = "#ffb703"
        self.c_text = "#f8fafc"
        self.c_muted = "#64748b"

        self.setup_styles()
        self.build_ui()
        self.init_interface_selection()
        
        self.trigger_scan_thread()
        self.after(500, self.update_radar_animation)
        self.after(self.refresh_interval_ms, self.periodic_refresh)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook', background=self.c_bg, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.c_card, foreground=self.c_text,
                        padding=[18, 9], font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('TNotebook.Tab',
                  background=[('selected', self.c_cyan), ('active', '#1e293b')],
                  foreground=[('selected', '#070c18'), ('active', self.c_text)])
        
        style.configure('Treeview', background=self.c_card, foreground=self.c_text,
                        fieldbackground=self.c_card, borderwidth=0, font=('Segoe UI', 9), rowheight=28)
        style.configure('Treeview.Heading', background='#172554', foreground=self.c_cyan,
                        font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('Treeview', background=[('selected', '#1d4ed8')], foreground=[('selected', '#ffffff')])

    def build_ui(self):
        # Header Bar
        header = tk.Frame(self, bg=self.c_card, height=72, highlightthickness=1, highlightbackground=self.c_border)
        header.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=self.c_card)
        title_box.pack(side=tk.LEFT, padx=18, pady=8)

        title_lbl = tk.Label(title_box, text="📡 WI-FI RADAR & SPECTRUM ANALYZER", 
                             font=('Segoe UI', 13, 'bold'), bg=self.c_card, fg=self.c_cyan)
        title_lbl.pack(anchor='w')

        # Adapter Selector in Header
        adapter_box = tk.Frame(header, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border, padx=8, pady=3)
        adapter_box.pack(side=tk.LEFT, padx=10, pady=8)

        tk.Label(adapter_box, text="🎯 Active Wi-Fi Adapter:", font=('Segoe UI', 8, 'bold'),
                 bg=self.c_card, fg=self.c_amber).pack(anchor='w')

        self.combo_iface = ttk.Combobox(adapter_box, textvariable=self.selected_interface, state="readonly", width=34)
        self.combo_iface.pack(side=tk.LEFT)
        self.combo_iface.bind("<<ComboboxSelected>>", lambda e: self.trigger_scan_thread())

        btn_frame = tk.Frame(header, bg=self.c_card)
        btn_frame.pack(side=tk.RIGHT, padx=18, pady=12)

        self.btn_scan = tk.Button(btn_frame, text="🔄 Live Scan", bg=self.c_cyan, fg="#070c18",
                                  font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, padx=12, pady=4,
                                  cursor='hand2', command=self.trigger_scan_thread)
        self.btn_scan.pack(side=tk.RIGHT, padx=6)

        chk_auto = tk.Checkbutton(btn_frame, text="Auto Refresh", variable=self.auto_refresh,
                                  bg=self.c_card, fg=self.c_text, selectcolor=self.c_card,
                                  activebackground=self.c_card, activeforeground=self.c_cyan,
                                  font=('Segoe UI', 9))
        chk_auto.pack(side=tk.RIGHT, padx=6)

        self.lbl_status = tk.Label(btn_frame, text="Ready", font=('Segoe UI', 9),
                                   bg=self.c_card, fg=self.c_green)
        self.lbl_status.pack(side=tk.RIGHT, padx=6)

        # Tabs Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        # Tab 1: Radar
        self.tab_radar = tk.Frame(self.notebook, bg=self.c_bg)
        self.notebook.add(self.tab_radar, text="  📡 360° Live Radar  ")
        self.build_radar_tab()

        # Tab 2: Security
        self.tab_security = tk.Frame(self.notebook, bg=self.c_bg)
        self.notebook.add(self.tab_security, text="  🛡️ Security & Vulnerability Audit  ")
        self.build_security_tab()

        # Tab 3: Spectrum
        self.tab_spectrum = tk.Frame(self.notebook, bg=self.c_bg)
        self.notebook.add(self.tab_spectrum, text="  📊 Frequency Spectrum (2.4G/5G)  ")
        self.build_spectrum_tab()

        # Tab 4: Tracker
        self.tab_tracker = tk.Frame(self.notebook, bg=self.c_bg)
        self.notebook.add(self.tab_tracker, text="  🎯 Signal Tracker (Geiger)  ")
        self.build_tracker_tab()

        # Tab 5: List
        self.tab_table = tk.Frame(self.notebook, bg=self.c_bg)
        self.notebook.add(self.tab_table, text="  📋 Detailed Inventory  ")
        self.build_table_tab()

    def init_interface_selection(self):
        ifaces = WifiScanner.get_interfaces()
        display_names = []
        best = ""
        for i in ifaces:
            is_tplink = 'TP-LINK' in i['desc'].upper() or 'USB' in i['desc'].upper() or 'REALTEK' in i['desc'].upper()
            tag = "🎯 [High-Gain USB Antenna]" if is_tplink else "[Internal Adapter]"
            d = f"{i['name']} - {i['desc']} {tag}"
            display_names.append(d)
            if is_tplink and not best:
                best = d
        
        self.combo_iface['values'] = display_names
        if best:
            self.selected_interface.set(best)
        elif display_names:
            self.selected_interface.set(display_names[0])

    def get_active_interface_name(self):
        sel = self.selected_interface.get()
        if "-" in sel:
            return sel.split("-")[0].strip()
        return sel if sel else None

    # ----------------------------------------------------
    # TAB 1: RADAR VIEW
    # ----------------------------------------------------
    def build_radar_tab(self):
        radar_container = tk.Frame(self.tab_radar, bg=self.c_bg)
        radar_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_radar = tk.Canvas(radar_container, bg="#040711", highlightthickness=1,
                                      highlightbackground=self.c_border)
        self.canvas_radar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        summary_panel = tk.Frame(radar_container, bg=self.c_card, width=300, highlightthickness=1,
                                 highlightbackground=self.c_border)
        summary_panel.pack(side=tk.RIGHT, fill=tk.Y)
        summary_panel.pack_propagate(False)

        tk.Label(summary_panel, text="RF Environment Summary", font=('Segoe UI', 11, 'bold'),
                 bg=self.c_card, fg=self.c_cyan).pack(anchor='w', padx=15, pady=14)

        self.lbl_count = tk.Label(summary_panel, text="Total Networks: 0", font=('Segoe UI', 10),
                                  bg=self.c_card, fg=self.c_text)
        self.lbl_count.pack(anchor='w', padx=15, pady=3)

        self.lbl_strongest = tk.Label(summary_panel, text="Strongest Signal: -", font=('Segoe UI', 10),
                                      bg=self.c_card, fg=self.c_green)
        self.lbl_strongest.pack(anchor='w', padx=15, pady=3)

        self.lbl_best_ch = tk.Label(summary_panel, text="Best 2.4G Channel: -", font=('Segoe UI', 10),
                                    bg=self.c_card, fg=self.c_amber)
        self.lbl_best_ch.pack(anchor='w', padx=15, pady=3)

        self.lbl_security_status = tk.Label(summary_panel, text="Security Audit: Evaluating...", font=('Segoe UI', 10, 'bold'),
                                            bg=self.c_card, fg=self.c_muted)
        self.lbl_security_status.pack(anchor='w', padx=15, pady=5)

        ttk.Separator(summary_panel, orient='horizontal').pack(fill=tk.X, padx=15, pady=12)

        tk.Label(summary_panel, text="Radar Symbol Legend:", font=('Segoe UI', 10, 'bold'),
                 bg=self.c_card, fg=self.c_text).pack(anchor='w', padx=15, pady=4)
        
        hints = [
            "🟢 Center Rings = Stronger Signal",
            "🔵 Outer Rings = Weaker Signal",
            "🚀 Purple = 5GHz Band | 🌐 Blue = 2.4GHz",
            "🔴 Red Halo = Insecure / Rogue AP",
            "✨ Blip Angle corresponds to Wi-Fi Channel"
        ]
        for h in hints:
            tk.Label(summary_panel, text=h, font=('Segoe UI', 8), bg=self.c_card,
                     fg=self.c_muted, justify=tk.LEFT).pack(anchor='w', padx=15, pady=3)

        self.radar_angle = 0

    def update_radar_animation(self):
        w = self.canvas_radar.winfo_width()
        h = self.canvas_radar.winfo_height()
        if w > 50 and h > 50:
            self.canvas_radar.delete("all")
            cx, cy = w // 2, h // 2
            max_r = min(cx, cy) - 30

            for i, (pct, label) in enumerate([(0.25, "-40 dBm (100%)"), (0.50, "-60 dBm (75%)"), 
                                              (0.75, "-80 dBm (50%)"), (1.00, "-100 dBm (25%)")]):
                r = int(max_r * pct)
                self.canvas_radar.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#111f38", width=1.2)
                self.canvas_radar.create_text(cx + 6, cy - r + 10, text=label, fill="#475569",
                                              font=('Consolas', 7), anchor='w')

            self.canvas_radar.create_line(cx - max_r, cy, cx + max_r, cy, fill="#111f38", width=1)
            self.canvas_radar.create_line(cx, cy - max_r, cx, cy + max_r, fill="#111f38", width=1)

            self.radar_angle = (self.radar_angle + 4) % 360
            rad = math.radians(self.radar_angle)
            lx = cx + max_r * math.cos(rad)
            ly = cy + max_r * math.sin(rad)
            self.canvas_radar.create_line(cx, cy, lx, ly, fill=self.c_cyan, width=2)

            for trail in range(1, 14):
                t_rad = math.radians((self.radar_angle - trail * 2.5) % 360)
                tx = cx + max_r * math.cos(t_rad)
                ty = cy + max_r * math.sin(t_rad)
                alpha_color = f"#{max(10, 40 - trail*2):02x}{max(20, 80 - trail*5):02x}{max(40, 120 - trail*8):02x}"
                self.canvas_radar.create_line(cx, cy, tx, ty, fill=alpha_color, width=1)

            for net in self.networks:
                sig = net['signal']
                ch = net['channel']
                is_5g = (net['band'] == '5 GHz')
                is_insecure = net.get('is_insecure', False)
                evil_info = net.get('evil_twin_info')
                is_evil = bool(evil_info and evil_info.get('status') == 'CRITICAL_EVIL_TWIN')

                dist_pct = max(0.1, (100 - sig) / 100.0)
                r = dist_pct * max_r

                ang_deg = ((ch - 36) * 7.5 + 180) % 360 if is_5g else (ch * 25.7) % 360
                ap_rad = math.radians(ang_deg)
                px = cx + r * math.cos(ap_rad)
                py = cy + r * math.sin(ap_rad)

                color = self.c_purple if is_5g else self.c_cyan
                
                if is_insecure or is_evil:
                    halo_r = 10
                    self.canvas_radar.create_oval(px - halo_r, py - halo_r, px + halo_r, py + halo_r,
                                                  outline=self.c_rose, width=2)
                elif sig > 65:
                    glow_r = 8
                    self.canvas_radar.create_oval(px - glow_r, py - glow_r, px + glow_r, py + glow_r,
                                                  outline=self.c_green, width=1)

                dot_r = 4
                self.canvas_radar.create_oval(px - dot_r, py - dot_r, px + dot_r, py + dot_r,
                                              fill=(self.c_rose if is_evil else color), outline="#ffffff", width=1)

                warn_prefix = "⚠️ " if (is_insecure or is_evil) else ""
                short_name = (net['ssid'][:12] + '..') if len(net['ssid']) > 14 else net['ssid']
                self.canvas_radar.create_text(px + 8, py - 4, text=f"{warn_prefix}{short_name} ({sig}%)",
                                              fill=(self.c_rose if is_evil else self.c_text),
                                              font=('Segoe UI', 8, 'bold'), anchor='w')

        self.after(50, self.update_radar_animation)

    # ----------------------------------------------------
    # TAB 2: SECURITY AUDIT
    # ----------------------------------------------------
    def build_security_tab(self):
        sec_container = tk.Frame(self.tab_security, bg=self.c_bg)
        sec_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        cards_frame = tk.Frame(sec_container, bg=self.c_bg)
        cards_frame.pack(fill=tk.X, pady=(0, 12))

        self.card_insecure = self._create_metric_card(cards_frame, "🔴 Insecure (Open / WEP)", "0", self.c_rose)
        self.card_insecure.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.card_evil = self._create_metric_card(cards_frame, "🚨 Evil Twin & Rogue Alerts", "0", self.c_amber)
        self.card_evil.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.card_wpa2 = self._create_metric_card(cards_frame, "🟡 Standard (WPA2-PSK)", "0", self.c_blue)
        self.card_wpa2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        self.card_wpa3 = self._create_metric_card(cards_frame, "🟢 Enterprise / WPA3 Secure", "0", self.c_green)
        self.card_wpa3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        filter_bar = tk.Frame(sec_container, bg=self.c_card, padx=12, pady=8,
                              highlightthickness=1, highlightbackground=self.c_border)
        filter_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_bar, text="🔍 Audit Filter:", font=('Segoe UI', 9, 'bold'),
                 bg=self.c_card, fg=self.c_cyan).pack(side=tk.LEFT, padx=(0, 10))

        filters = [
            ("All Networks", "ALL"),
            ("🔴 Insecure & Open Only", "INSECURE"),
            ("🚨 Evil Twin & Rogue Only", "EVIL_TWIN"),
            ("🟢 Highly Secure Only", "SECURE")
        ]
        for text, mode in filters:
            btn = tk.Radiobutton(filter_bar, text=text, value=mode, variable=self.security_filter,
                                 indicatoron=False, bg=self.c_bg, fg=self.c_text,
                                 selectcolor=self.c_cyan, activebackground=self.c_card_hover,
                                 font=('Segoe UI', 8, 'bold'), padx=12, pady=4,
                                 command=self.populate_security_table)
            btn.pack(side=tk.LEFT, padx=3)

        main_sec_split = tk.Frame(sec_container, bg=self.c_bg)
        main_sec_split.pack(fill=tk.BOTH, expand=True)

        tbl_frame = tk.Frame(main_sec_split, bg=self.c_card, highlightthickness=1, highlightbackground=self.c_border)
        tbl_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        cols = ("alert", "ssid", "vendor", "auth", "risk", "channel", "signal", "bssid")
        self.tree_sec = ttk.Treeview(tbl_frame, columns=cols, show='headings', selectmode='browse')

        self.tree_sec.heading("alert", text="Audit Status")
        self.tree_sec.heading("ssid", text="SSID (Network Name)")
        self.tree_sec.heading("vendor", text="🏢 Vendor / Hardware")
        self.tree_sec.heading("auth", text="Security Protocol")
        self.tree_sec.heading("risk", text="Risk Rating")
        self.tree_sec.heading("channel", text="Channel")
        self.tree_sec.heading("signal", text="Signal")
        self.tree_sec.heading("bssid", text="BSSID")

        self.tree_sec.column("alert", width=160, anchor='center')
        self.tree_sec.column("ssid", width=150, anchor='w')
        self.tree_sec.column("vendor", width=140, anchor='center')
        self.tree_sec.column("auth", width=120, anchor='center')
        self.tree_sec.column("risk", width=110, anchor='center')
        self.tree_sec.column("channel", width=60, anchor='center')
        self.tree_sec.column("signal", width=65, anchor='center')
        self.tree_sec.column("bssid", width=130, anchor='center')

        sec_scroll = ttk.Scrollbar(tbl_frame, orient=tk.VERTICAL, command=self.tree_sec.yview)
        self.tree_sec.configure(yscroll=sec_scroll.set)
        self.tree_sec.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sec_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_sec.bind('<<TreeviewSelect>>', self.on_security_item_selected)

        self.sec_inspector = tk.Frame(main_sec_split, bg=self.c_card, width=320,
                                      highlightthickness=1, highlightbackground=self.c_border, padx=15, pady=15)
        self.sec_inspector.pack(side=tk.RIGHT, fill=tk.Y)
        self.sec_inspector.pack_propagate(False)

        tk.Label(self.sec_inspector, text="🛡️ Vulnerability Inspector", font=('Segoe UI', 11, 'bold'),
                 bg=self.c_card, fg=self.c_cyan).pack(anchor='w', pady=(0, 10))

        self.lbl_ins_ssid = tk.Label(self.sec_inspector, text="No network selected", font=('Segoe UI', 11, 'bold'),
                                     bg=self.c_card, fg=self.c_text, wraplength=280, justify=tk.LEFT)
        self.lbl_ins_ssid.pack(anchor='w', pady=2)

        self.lbl_ins_vendor = tk.Label(self.sec_inspector, text="Vendor: -", font=('Segoe UI', 9),
                                       bg=self.c_card, fg=self.c_muted)
        self.lbl_ins_vendor.pack(anchor='w', pady=2)

        ttk.Separator(self.sec_inspector, orient='horizontal').pack(fill=tk.X, pady=8)

        self.lbl_ins_risk_title = tk.Label(self.sec_inspector, text="Risk Rating: -", font=('Segoe UI', 10, 'bold'),
                                           bg=self.c_card, fg=self.c_text, wraplength=280, justify=tk.LEFT)
        self.lbl_ins_risk_title.pack(anchor='w', pady=4)

        self.lbl_ins_evil_status = tk.Label(self.sec_inspector, text="Evil Twin Status: -", font=('Segoe UI', 9),
                                            bg=self.c_card, fg=self.c_muted, wraplength=280, justify=tk.LEFT)
        self.lbl_ins_evil_status.pack(anchor='w', pady=4)

        ttk.Separator(self.sec_inspector, orient='horizontal').pack(fill=tk.X, pady=8)

        tk.Label(self.sec_inspector, text="💡 Security Recommendations:", font=('Segoe UI', 9, 'bold'),
                 bg=self.c_card, fg=self.c_amber).pack(anchor='w', pady=(4, 2))

        self.lbl_ins_advice = tk.Label(self.sec_inspector, text="Select any network in the table to view its cryptographic profile, potential risks, and hardening guidance.",
                                       font=('Segoe UI', 8), bg=self.c_card, fg=self.c_text, wraplength=280, justify=tk.LEFT)
        self.lbl_ins_advice.pack(anchor='w', pady=4)

    def _create_metric_card(self, parent, title, value, val_color):
        card = tk.Frame(parent, bg=self.c_card, highlightthickness=1,
                        highlightbackground=self.c_border, padx=12, pady=10)
        tk.Label(card, text=title, font=('Segoe UI', 8), bg=self.c_card, fg=self.c_muted).pack(anchor='w')
        val_lbl = tk.Label(card, text=value, font=('Segoe UI', 16, 'bold'), bg=self.c_card, fg=val_color)
        val_lbl.pack(anchor='w', pady=(2, 0))
        card.val_lbl = val_lbl
        return card

    def populate_security_table(self):
        for item in self.tree_sec.get_children():
            self.tree_sec.delete(item)

        filter_mode = self.security_filter.get()

        for net in self.networks:
            is_insecure = net.get('is_insecure', False)
            evil_info = net.get('evil_twin_info')
            is_evil = bool(evil_info and evil_info.get('status') in ['CRITICAL_EVIL_TWIN', 'SUSPICIOUS_ROUTER'])
            is_secure = (net.get('risk_code') == 'SECURE')

            if filter_mode == 'INSECURE' and not is_insecure:
                continue
            if filter_mode == 'EVIL_TWIN' and not is_evil:
                continue
            if filter_mode == 'SECURE' and not is_secure:
                continue

            alert_tag = "🟢 Normal"
            if evil_info:
                alert_tag = evil_info.get('tag', '🟢 Normal')
            elif is_insecure:
                alert_tag = net.get('risk_badge', '🔴 Insecure')

            self.tree_sec.insert("", tk.END, values=(
                alert_tag,
                net['ssid'],
                net['vendor'],
                net['auth'],
                net.get('risk_badge', '-'),
                f"{net['channel']} ({net['band']})",
                f"{net['signal']}%",
                net['bssid']
            ))

    def on_security_item_selected(self, event):
        sel = self.tree_sec.selection()
        if not sel:
            return
        vals = self.tree_sec.item(sel[0], 'values')
        if not vals:
            return
        
        bssid_selected = vals[7]
        net = next((n for n in self.networks if n['bssid'] == bssid_selected), None)
        if not net:
            return

        self.lbl_ins_ssid.config(text=f"{net['ssid']}")
        self.lbl_ins_vendor.config(text=f"Vendor: {net['vendor']} | BSSID: {net['bssid']}")
        
        risk_title = net.get('risk_title', 'Unknown')
        risk_color = net.get('risk_color', self.c_text)
        self.lbl_ins_risk_title.config(text=f"{risk_title}", fg=risk_color)

        evil_info = net.get('evil_twin_info')
        if evil_info:
            self.lbl_ins_evil_status.config(text=f"{evil_info.get('detail')}", fg=evil_info.get('color', self.c_muted))
        else:
            self.lbl_ins_evil_status.config(text="Single AP deployment. No conflicting SSIDs detected.", fg=self.c_muted)

        self.lbl_ins_advice.config(text=net.get('advice', 'No specific security advisory for this network.'))

    # ----------------------------------------------------
    # TAB 3: SPECTRUM
    # ----------------------------------------------------
    def build_spectrum_tab(self):
        spec_container = tk.Frame(self.tab_spectrum, bg=self.c_bg)
        spec_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(8, 5), facecolor=self.c_bg)
        self.ax_2g = self.fig.add_subplot(211)
        self.ax_5g = self.fig.add_subplot(212)
        self.fig.tight_layout(pad=3.0)

        self.canvas_matplotlib = FigureCanvasTkAgg(self.fig, master=spec_container)
        self.canvas_matplotlib.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.draw_spectrum_charts()

    def draw_spectrum_charts(self):
        self.ax_2g.clear()
        self.ax_5g.clear()

        for ax, title in [(self.ax_2g, "2.4 GHz Wi-Fi Spectrum (Channels 1-14)"),
                          (self.ax_5g, "5 GHz Wi-Fi Spectrum (Channels 36-165)")]:
            ax.set_facecolor(self.c_card)
            ax.set_title(title, color=self.c_cyan, fontsize=10, fontweight='bold')
            ax.tick_params(colors=self.c_muted, labelsize=8)
            ax.grid(True, linestyle='--', alpha=0.15, color='#ffffff')
            ax.set_ylim(0, 105)
            ax.set_ylabel("Signal %", color=self.c_muted, fontsize=8)
            for spine in ax.spines.values():
                spine.set_color(self.c_border)

        self.ax_2g.set_xlim(0, 15)
        self.ax_2g.set_xticks(range(1, 15))
        self.ax_2g.set_xlabel("Channel", color=self.c_muted, fontsize=8)

        x_2g = np.linspace(0, 15, 500)
        colors_palette = ['#00f0ff', '#00ff9d', '#ff0055', '#c084fc', '#ffb703', '#38bdf8', '#14b8a6', '#f43f5e']

        channel_crowding_2g = {ch: 0 for ch in range(1, 15)}

        for i, net in enumerate(self.networks):
            ch = net['channel']
            sig = net['signal']
            if net['band'] == '2.4 GHz' and 1 <= ch <= 14:
                channel_crowding_2g[ch] += 1
                color = colors_palette[i % len(colors_palette)]
                
                width = 2.2
                y = sig * np.exp(-((x_2g - ch) ** 2) / (2 * (width / 2.355) ** 2))
                self.ax_2g.plot(x_2g, y, color=color, linewidth=1.8, label=net['ssid'][:10])
                self.ax_2g.fill_between(x_2g, 0, y, color=color, alpha=0.15)
                self.ax_2g.text(ch, sig + 3, f"{net['ssid'][:8]}\n({sig}%)", color=color,
                                fontsize=7, ha='center', fontweight='bold')

        self.ax_5g.set_xlim(32, 168)
        self.ax_5g.set_xticks([36, 48, 52, 64, 100, 116, 132, 149, 161, 165])
        self.ax_5g.set_xlabel("5 GHz Channel", color=self.c_muted, fontsize=8)

        x_5g = np.linspace(30, 170, 1000)
        for i, net in enumerate(self.networks):
            ch = net['channel']
            sig = net['signal']
            if net['band'] == '5 GHz':
                color = colors_palette[i % len(colors_palette)]
                width = 4.0
                y = sig * np.exp(-((x_5g - ch) ** 2) / (2 * (width / 2.355) ** 2))
                self.ax_5g.plot(x_5g, y, color=color, linewidth=1.8)
                self.ax_5g.fill_between(x_5g, 0, y, color=color, alpha=0.2)
                self.ax_5g.text(ch, sig + 3, f"{net['ssid'][:8]}\n({sig}%)", color=color,
                                fontsize=7, ha='center', fontweight='bold')

        scores = {ch: channel_crowding_2g.get(ch, 0) for ch in [1, 6, 11]}
        best_ch = min(scores, key=scores.get)
        self.lbl_best_ch.config(text=f"Recommended 2.4G Channel: Ch {best_ch} (Lowest Interference)")

        self.canvas_matplotlib.draw_idle()

    # ----------------------------------------------------
    # TAB 4: TARGET TRACKER
    # ----------------------------------------------------
    def build_tracker_tab(self):
        tracker_container = tk.Frame(self.tab_tracker, bg=self.c_bg)
        tracker_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        sel_frame = tk.Frame(tracker_container, bg=self.c_card, highlightthickness=1,
                             highlightbackground=self.c_border, padx=15, pady=12)
        sel_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(sel_frame, text="🎯 Select Target Wi-Fi for Direction Finding & Tracking:", font=('Segoe UI', 10, 'bold'),
                 bg=self.c_card, fg=self.c_cyan).pack(side=tk.LEFT, padx=(0, 10))

        self.combo_target = ttk.Combobox(sel_frame, textvariable=self.target_network, state="readonly", width=35)
        self.combo_target.pack(side=tk.LEFT, padx=5)
        self.combo_target.bind("<<ComboboxSelected>>", self.on_target_changed)

        chk_beep = tk.Checkbutton(sel_frame, text="🔊 Geiger Audio Tone (Pitch by RSSI)",
                                  variable=self.sound_enabled, bg=self.c_card, fg=self.c_text,
                                  selectcolor=self.c_card, activebackground=self.c_card,
                                  activeforeground=self.c_cyan, font=('Segoe UI', 9))
        chk_beep.pack(side=tk.RIGHT, padx=10)

        main_gauge_frame = tk.Frame(tracker_container, bg=self.c_bg)
        main_gauge_frame.pack(fill=tk.BOTH, expand=True)

        left_box = tk.Frame(main_gauge_frame, bg=self.c_card, width=320, highlightthickness=1,
                            highlightbackground=self.c_border, padx=20, pady=20)
        left_box.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_box.pack_propagate(False)

        tk.Label(left_box, text="Live Signal Quality", font=('Segoe UI', 11, 'bold'),
                 bg=self.c_card, fg=self.c_muted).pack(pady=5)

        self.lbl_gauge_pct = tk.Label(left_box, text="-- %", font=('Segoe UI', 38, 'bold'),
                                      bg=self.c_card, fg=self.c_green)
        self.lbl_gauge_pct.pack(pady=10)

        self.lbl_gauge_dbm = tk.Label(left_box, text="-- dBm", font=('Segoe UI', 14),
                                      bg=self.c_card, fg=self.c_cyan)
        self.lbl_gauge_dbm.pack(pady=2)

        self.prog_signal = ttk.Progressbar(left_box, orient='horizontal', length=240, mode='determinate')
        self.prog_signal.pack(pady=18)

        self.lbl_tracker_details = tk.Label(left_box, text="No target network selected",
                                            font=('Segoe UI', 9), bg=self.c_card, fg=self.c_muted, justify=tk.CENTER)
        self.lbl_tracker_details.pack(pady=10)

        right_box = tk.Frame(main_gauge_frame, bg=self.c_card, highlightthickness=1,
                             highlightbackground=self.c_border, padx=10, pady=10)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig_hist = Figure(figsize=(6, 4), facecolor=self.c_card)
        self.ax_hist = self.fig_hist.add_subplot(111)
        self.ax_hist.set_facecolor("#040711")
        self.ax_hist.set_title("Real-Time Signal History (Rotate antenna to locate physical source)", color=self.c_cyan, fontsize=10, fontweight='bold')
        self.ax_hist.set_ylim(0, 100)
        self.ax_hist.grid(True, linestyle='--', alpha=0.2, color='#ffffff')
        self.ax_hist.tick_params(colors=self.c_muted, labelsize=8)
        for spine in self.ax_hist.spines.values():
            spine.set_color(self.c_border)

        self.canvas_hist = FigureCanvasTkAgg(self.fig_hist, master=right_box)
        self.canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_target_changed(self, event=None):
        self.target_history = []
        self.update_target_tracker()

    def update_target_tracker(self):
        target_name = self.target_network.get()
        if not target_name:
            return

        found = None
        for n in self.networks:
            if n['ssid'] == target_name or f"{n['ssid']} ({n['bssid']})" == target_name:
                found = n
                break

        if found:
            sig = found['signal']
            dbm = found['dbm']
            self.lbl_gauge_pct.config(text=f"{sig}%")
            self.lbl_gauge_dbm.config(text=f"{dbm} dBm")
            self.prog_signal['value'] = sig

            color = self.c_green if sig >= 60 else (self.c_amber if sig >= 35 else self.c_rose)
            self.lbl_gauge_pct.config(fg=color)

            vendor_str = f"Vendor: {found.get('vendor', 'Unknown')}"
            details_text = f"BSSID: {found['bssid']}\n{vendor_str}\nChannel: {found['channel']} ({found['band']})\nStandard: {found['radio']}\nSecurity: {found['auth']}"
            self.lbl_tracker_details.config(text=details_text)

            self.target_history.append(sig)
            if len(self.target_history) > 40:
                self.target_history.pop(0)

            self.ax_hist.clear()
            self.ax_hist.set_facecolor("#040711")
            self.ax_hist.set_title(f"Live Target RSSI: {found['ssid']} ({found['bssid']})", color=self.c_cyan, fontsize=10, fontweight='bold')
            self.ax_hist.set_ylim(0, 105)
            self.ax_hist.grid(True, linestyle='--', alpha=0.2, color='#ffffff')
            self.ax_hist.tick_params(colors=self.c_muted, labelsize=8)
            for spine in self.ax_hist.spines.values():
                spine.set_color(self.c_border)

            self.ax_hist.plot(self.target_history, color=color, linewidth=2.5, marker='o', markersize=4)
            self.ax_hist.fill_between(range(len(self.target_history)), 0, self.target_history, color=color, alpha=0.2)
            self.canvas_hist.draw_idle()

            if self.sound_enabled.get() and HAS_SOUND:
                def play_beep():
                    freq = int(400 + (sig / 100.0) * 1400)
                    winsound.Beep(freq, 80)
                threading.Thread(target=play_beep, daemon=True).start()

    # ----------------------------------------------------
    # TAB 5: DETAILED TABLE
    # ----------------------------------------------------
    def build_table_tab(self):
        table_container = tk.Frame(self.tab_table, bg=self.c_bg)
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("ssid", "vendor", "signal", "dbm", "channel", "band", "radio", "auth", "risk", "bssid")
        self.tree = ttk.Treeview(table_container, columns=cols, show='headings', selectmode='browse')

        self.tree.heading("ssid", text="Network Name (SSID)")
        self.tree.heading("vendor", text="🏢 Vendor / Hardware")
        self.tree.heading("signal", text="Quality (%)")
        self.tree.heading("dbm", text="RSSI (dBm)")
        self.tree.heading("channel", text="Channel")
        self.tree.heading("band", text="Frequency Band")
        self.tree.heading("radio", text="Radio Standard")
        self.tree.heading("auth", text="Authentication")
        self.tree.heading("risk", text="Security Level")
        self.tree.heading("bssid", text="MAC Address (BSSID)")

        self.tree.column("ssid", width=160, anchor='w')
        self.tree.column("vendor", width=130, anchor='center')
        self.tree.column("signal", width=75, anchor='center')
        self.tree.column("dbm", width=80, anchor='center')
        self.tree.column("channel", width=65, anchor='center')
        self.tree.column("band", width=85, anchor='center')
        self.tree.column("radio", width=95, anchor='center')
        self.tree.column("auth", width=120, anchor='center')
        self.tree.column("risk", width=110, anchor='center')
        self.tree.column("bssid", width=135, anchor='center')

        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def populate_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for net in self.networks:
            self.tree.insert("", tk.END, values=(
                net['ssid'],
                net.get('vendor', 'Unknown'),
                f"{net['signal']}%",
                f"{net['dbm']} dBm",
                net['channel'],
                net['band'],
                net['radio'],
                net['auth'],
                net.get('risk_badge', '-'),
                net['bssid']
            ))

    # ----------------------------------------------------
    # SCAN ENGINE
    # ----------------------------------------------------
    def trigger_scan_thread(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        self.lbl_status.config(text="Scanning RF Spectrum...", fg=self.c_cyan)
        iface = self.get_active_interface_name()
        threading.Thread(target=self._scan_worker, args=(iface,), daemon=True).start()

    def _scan_worker(self, iface_name):
        nets = WifiScanner.scan(iface_name)
        self.after(0, self._on_scan_completed, nets)

    def _on_scan_completed(self, results):
        self.networks = results
        self.is_scanning = False
        self.lbl_status.config(text=f"Updated ({len(results)} networks)", fg=self.c_green)

        self.lbl_count.config(text=f"Total Networks: {len(results)}")
        if results:
            strongest = results[0]
            self.lbl_strongest.config(text=f"Strongest: {strongest['ssid']} ({strongest['signal']}%)")

        insecure_count = sum(1 for n in results if n.get('is_insecure', False))
        evil_count = sum(1 for n in results if n.get('evil_twin_info') and n['evil_twin_info']['status'] in ['CRITICAL_EVIL_TWIN', 'SUSPICIOUS_ROUTER'])
        wpa2_count = sum(1 for n in results if n.get('risk_code') == 'MODERATE')
        wpa3_count = sum(1 for n in results if n.get('risk_code') == 'SECURE')

        self.card_insecure.val_lbl.config(text=str(insecure_count))
        self.card_evil.val_lbl.config(text=str(evil_count))
        self.card_wpa2.val_lbl.config(text=str(wpa2_count))
        self.card_wpa3.val_lbl.config(text=str(wpa3_count))

        if insecure_count > 0 or evil_count > 0:
            self.lbl_security_status.config(text=f"⚠️ {insecure_count} Insecure / {evil_count} Rogue Alerts", fg=self.c_rose)
        else:
            self.lbl_security_status.config(text="🟢 Environment Secure (No Open APs)", fg=self.c_green)

        names = [f"{n['ssid']}" for n in results if n['ssid'] != '<Hidden Network>']
        unique_names = list(dict.fromkeys(names))
        self.combo_target['values'] = unique_names
        if not self.target_network.get() and unique_names:
            self.target_network.set(unique_names[0])

        self.populate_table()
        self.populate_security_table()
        self.draw_spectrum_charts()
        self.update_target_tracker()

    def periodic_refresh(self):
        if self.auto_refresh.get() and not self.is_scanning:
            self.trigger_scan_thread()
        self.after(self.refresh_interval_ms, self.periodic_refresh)


if __name__ == '__main__':
    app = ModernWifiRadarApp()
    app.mainloop()
