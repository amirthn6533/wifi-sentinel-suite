"""
=============================================================================
💀 FSOCIETY CYBER TERMINAL & HACK SIMULATOR (Mr. Robot Edition)
=============================================================================
Author: Antigravity Pair Programmer
Architecture: Story-Driven Cyber CTF Terminal & Cryptographic Sandbox
Inspired by: Mr. Robot (Elliot Alderson & fsociety)
=============================================================================
"""

import sys
import os
import time
import random
import threading

# Enable VT100 ANSI terminal escape sequences on Windows
if os.name == 'nt':
    os.system('')

# Audio Engine for Keystrokes & Cyber HUD
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# Cyberpunk Terminal Color Codes
class Colors:
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"


def play_click(freq=1200, duration=15):
    """Subtle mechanical keyboard click sound."""
    if HAS_SOUND:
        try:
            winsound.Beep(freq, duration)
        except Exception:
            pass


def play_cyber_beep(seq="success"):
    if not HAS_SOUND:
        return
    try:
        if seq == "success":
            winsound.Beep(1400, 50)
            winsound.Beep(1800, 80)
            winsound.Beep(2400, 120)
        elif seq == "alert":
            winsound.Beep(600, 100)
            winsound.Beep(450, 120)
        elif seq == "matrix":
            for f in [1200, 1500, 1800, 2200, 2600, 3200]:
                winsound.Beep(f, 35)
    except Exception:
        pass


def typewriter(text, speed=0.015, color=Colors.WHITE, newline=True, audio=True):
    """Prints text with real-time typewriter glitch effect."""
    for char in text:
        sys.stdout.write(f"{color}{char}{Colors.RESET}")
        sys.stdout.flush()
        if audio and random.random() < 0.25:
            play_click(random.randint(900, 1600), 10)
        time.sleep(speed)
    if newline:
        sys.stdout.write("\n")
        sys.stdout.flush()


def print_fsociety_banner():
    banner = f"""{Colors.RED}{Colors.BOLD}
             .---.
            /     \\
           | () () |
            \\  _  /
             `---`
      ███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
      ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
      █████╗  ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝ 
      ██╔══╝  ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝  
      ██║     ███████║╚██████╔╝╚██████╗██║███████╗   ██║      ██║   
      ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
    {Colors.WHITE}░▒▓ F S O C I E T Y   I N T E R A C T I V E   T E R M I N A L ▓▒░{Colors.RESET}
    {Colors.DIM}[Welcome, friend. Democracy has been hacked. We are fsociety.]{Colors.RESET}
    """
    print(banner)


# =====================================================================
# Matrix Rain Animation on Final Victory
# =====================================================================
def matrix_rain_effect():
    play_cyber_beep("matrix")
    chars = "011010010101011101010101FSOCIETY_ECORP_ENCRYPTED_999999"
    print(f"\n{Colors.GREEN}{Colors.BOLD}=== INITIATING GLOBAL E-CORP ENCRYPTED REVOLUTION ==={Colors.RESET}")
    for _ in range(35):
        line = "".join(random.choice(chars) if random.random() < 0.3 else " " for _ in range(75))
        print(f"{Colors.GREEN}{line}{Colors.RESET}")
        time.sleep(0.04)
    print(f"\n{Colors.GREEN}{Colors.BOLD}[✔] DEBT RECORDS WIPED OUT WORLDWIDE. WE ARE FREE.{Colors.RESET}\n")


# =====================================================================
# Mission Engine & State Controller
# =====================================================================
class GameEngine:
    def __init__(self):
        self.current_mission = 1  # 1: Ron's Coffee, 2: Steel Mountain, 3: E-Corp 5/9
        self.mission_step = 0
        self.ssh_connected = False
        self.temp_overridden = False

    def get_prompt(self):
        if self.ssh_connected:
            return f"{Colors.MAGENTA}pi@steelmountain-hvac:~# {Colors.RESET}"
        return f"{Colors.RED}elliot@fsociety:~$ {Colors.RESET}"

    def show_status(self):
        missions_info = {
            1: {
                "title": "☕ MISSION 1: Ron's Coffee Shop (The Pinhole)",
                "brief": "You are sitting at Ron's Coffee. Their gigabit Wi-Fi is abnormally fast. Find the hidden server, gain root access, and pull the dark web evidence.",
                "steps": [
                    "1. Scan the local Wi-Fi network (`scan wifi`)",
                    "2. Probe the suspicious IP with Nmap (`nmap 192.168.1.105`)",
                    "3. Crack the FTP password (`crack ftp 192.168.1.105`)",
                    "4. Download and inspect the evidence file (`cat evidence.log`)"
                ]
            },
            2: {
                "title": "🏢 MISSION 2: Steel Mountain (Operation Climate Melt)",
                "brief": "Offline tape backups are stored in an ultra-secure vault. You installed a rogue Raspberry Pi on the HVAC climate controller. Connect to it and override the thermostat to 120°F to melt the magnetic tapes.",
                "steps": [
                    "1. Connect via remote SSH tunnel (`ssh hvac.steelmountain.local`)",
                    "2. Decrypt the firmware key (`decrypt firmware.enc`)",
                    "3. Override the thermostat failsafe (`override 120F`)"
                ]
            },
            3: {
                "title": "🏦 MISSION 3: E-Corp 5/9 Infiltration (The Revolution)",
                "brief": "The final stage. Infiltrate Evil Corp's central HSM proxy, inject the self-replicating encryption rootkit, and execute the global debt wipeout.",
                "steps": [
                    "1. Scan the E-Corp HSM proxy network (`scan ecorp`)",
                    "2. Inject the custom rootkit payload (`inject rootkit.py`)",
                    "3. Execute the global 5/9 encryption payload (`execute 5-9`)"
                ]
            }
        }

        m = missions_info[self.current_mission]
        print(f"\n{Colors.YELLOW}{Colors.BOLD}====================================================================={Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{m['title']}{Colors.RESET}")
        print(f"{Colors.YELLOW}{Colors.BOLD}====================================================================={Colors.RESET}")
        print(f"{Colors.WHITE}{m['brief']}{Colors.RESET}\n")
        print(f"{Colors.BOLD}CURRENT OBJECTIVES:{Colors.RESET}")
        for idx, s in enumerate(m['steps']):
            if idx < self.mission_step:
                print(f"  {Colors.GREEN}✔ [COMPLETED] {s}{Colors.RESET}")
            elif idx == self.mission_step:
                print(f"  {Colors.YELLOW}➔ [ACTIVE]    {s}{Colors.RESET}")
            else:
                print(f"  {Colors.DIM}○ [PENDING]   {s}{Colors.RESET}")
        print("")

    def handle_command(self, cmd_line):
        parts = cmd_line.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        # Global utility commands
        if cmd in ["help", "?"]:
            self.cmd_help()
        elif cmd in ["status", "objectives", "mission"]:
            self.show_status()
        elif cmd in ["clear", "cls"]:
            os.system('cls' if os.name == 'nt' else 'clear')
            print_fsociety_banner()
        elif cmd in ["ls", "dir"]:
            self.cmd_ls()
        elif cmd == "cat":
            self.cmd_cat(args)
        elif cmd == "hint":
            self.cmd_hint()
        elif cmd == "dossier":
            self.cmd_dossier(args)

        # Mission specific commands
        elif cmd == "scan":
            self.cmd_scan(args)
        elif cmd == "nmap":
            self.cmd_nmap(args)
        elif cmd == "crack":
            self.cmd_crack(args)
        elif cmd == "ssh":
            self.cmd_ssh(args)
        elif cmd == "decrypt":
            self.cmd_decrypt(args)
        elif cmd == "override":
            self.cmd_override(args)
        elif cmd == "inject":
            self.cmd_inject(args)
        elif cmd == "execute":
            self.cmd_execute(args)
        elif cmd == "exit":
            if self.ssh_connected:
                self.ssh_connected = False
                print(f"{Colors.YELLOW}[*] Closed SSH connection to Steel Mountain.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}[*] Goodbye, friend. Stay vigilant.{Colors.RESET}\n")
                sys.exit(0)
        else:
            print(f"{Colors.RED}bash: {cmd}: command not found. Type 'help' for available fsociety tools.{Colors.RESET}")

    # -----------------------------------------------------------------
    # Command Implementations
    # -----------------------------------------------------------------
    def cmd_help(self):
        help_text = f"""
{Colors.CYAN}{Colors.BOLD}FSOCIETY CYBER COMMAND SUITE:{Colors.RESET}
  {Colors.GREEN}status{Colors.RESET}       - Display active mission intel & remaining objectives
  {Colors.GREEN}scan <target>{Colors.RESET} - Run deep RF/network surveillance scan (e.g. `scan wifi`, `scan ecorp`)
  {Colors.GREEN}nmap <ip>{Colors.RESET}     - Port scan and OS fingerprinting probe
  {Colors.GREEN}crack <svc>{Colors.RESET}   - Run targeted dictionary password brute-force (e.g. `crack ftp`)
  {Colors.GREEN}ssh <host>{Colors.RESET}    - Open encrypted remote shell tunnel (e.g. `ssh hvac.steelmountain.local`)
  {Colors.GREEN}decrypt <file>{Colors.RESET}- Solve cryptographic cipher key
  {Colors.GREEN}override <val>{Colors.RESET}- Override industrial failsafe control parameters
  {Colors.GREEN}inject <file>{Colors.RESET} - Inject malicious payload into compromised daemon
  {Colors.GREEN}execute <op>{Colors.RESET}  - Trigger global execution payload (e.g. `execute 5-9`)
  {Colors.GREEN}ls, cat <f>{Colors.RESET}   - Inspect local filesystem files
  {Colors.GREEN}hint{Colors.RESET}         - Elliot's internal monologue / guidance
  {Colors.GREEN}clear, exit{Colors.RESET}  - Terminal control
"""
        print(help_text)

    def cmd_ls(self):
        if self.current_mission == 1:
            if self.mission_step >= 3:
                print(f"{Colors.WHITE}fsociety_tools/   {Colors.YELLOW}evidence.log{Colors.RESET}   notes.txt")
            else:
                print(f"{Colors.WHITE}fsociety_tools/   notes.txt{Colors.RESET}")
        elif self.current_mission == 2:
            if self.ssh_connected:
                print(f"{Colors.RED}firmware.enc{Colors.RESET}   hvac_daemon.py   thermostat_state.cfg")
            else:
                print(f"{Colors.WHITE}pi_tunnel.sh   notes_steel_mountain.txt{Colors.RESET}")
        elif self.current_mission == 3:
            print(f"{Colors.RED}rootkit.py{Colors.RESET}   5_9_payload.aes   ecorp_nodes.map")

    def cmd_cat(self, args):
        if not args:
            print(f"{Colors.RED}Usage: cat <filename>{Colors.RESET}")
            return
        fname = args[0]
        if fname == "notes.txt":
            print(f"\n{Colors.CYAN}[NOTES] Ron's Coffee uses a commercial fiber line with 10Gbps bandwidth. Nobody needs that much bandwidth just for coffee shop patrons. There's a hidden server hosting illegal content in the back.{Colors.RESET}\n")
        elif fname == "evidence.log":
            if self.current_mission == 1 and self.mission_step >= 3:
                play_cyber_beep("success")
                typewriter(f"\n[EVIDENCE LOG DUMP - TARGET: RON (ROHIT MEHTA)]", speed=0.01, color=Colors.RED)
                typewriter(f"Tor Onion Node: 4b6v7x...onion", speed=0.01, color=Colors.YELLOW)
                typewriter(f"Total Traffic: 8.4 Terabytes of dark web illicit material.", speed=0.01, color=Colors.YELLOW)
                typewriter(f"Admin MAC: 00:1A:2B:3C:4D:5E (Matching Ron's laptop under the counter)", speed=0.01, color=Colors.YELLOW)
                typewriter(f"CONFIRMATION: Evidence secured. Forwarded to NYPD cyber crimes division.\n", speed=0.01, color=Colors.GREEN)
                self.mission_step = 4
                self.check_mission_progress()
            else:
                print(f"{Colors.RED}Error: File not found or unreadable.{Colors.RESET}")
        elif fname == "notes_steel_mountain.txt":
            print(f"\n{Colors.CYAN}[INTEL] Steel Mountain tape backups are stored in vault room 4B. The tapes decompose if ambient temperature exceeds 110°F. The Raspberry Pi was plugged into the HVAC thermostat control board.{Colors.RESET}\n")
        elif fname in ["firmware.enc", "hvac_daemon.py"]:
            print(f"\n{Colors.YELLOW}[ENCRYPTED FIRMWARE DATA] Key required to decrypt failsafe overrides.{Colors.RESET}\n")
        else:
            print(f"{Colors.RED}cat: {fname}: No such file or directory.{Colors.RESET}")

    def cmd_hint(self):
        hints = {
            1: [
                "I need to scan the coffee shop's Wi-Fi network to find Ron's hidden server. Try `scan wifi`.",
                "Let's probe the open ports on `192.168.1.105` with `nmap 192.168.1.105`.",
                "The FTP server is running on port 21. Let's crack it with `crack ftp 192.168.1.105`.",
                "The evidence file is downloaded. Read it with `cat evidence.log` to take down Ron."
            ],
            2: [
                "I planted a Raspberry Pi on the HVAC controller. I need to SSH into it: `ssh hvac.steelmountain.local`.",
                "The HVAC firmware is encrypted. Use `decrypt firmware.enc` to crack the temperature override key.",
                "Now that the override is unlocked, crank up the temperature to melt the tapes: `override 120F`."
            ],
            3: [
                "We are ready for the 5/9 hack. First, probe E-Corp's HSM proxy: `scan ecorp`.",
                "Inject the rootkit payload into the HSM daemon: `inject rootkit.py`.",
                "This is it. Trigger the global revolution: `execute 5-9`."
            ]
        }
        step_hints = hints[self.current_mission]
        current_hint = step_hints[min(self.mission_step, len(step_hints) - 1)]
        typewriter(f"\n[Elliot's inner voice]: \"{current_hint}\"\n", speed=0.015, color=Colors.CYAN)

    def cmd_scan(self, args):
        target = args[0].lower() if args else ""
        if self.current_mission == 1:
            if "wifi" in target or not target:
                typewriter("[*] Initializing wireless RF sniffer on interface wlan0...", speed=0.01, color=Colors.CYAN)
                time.sleep(0.4)
                print(f"{Colors.GREEN}[+] BSSID: C0:4A:00:11:22:33  SSID: 'Rons_Coffee_Guest'    [192.168.1.1] (Public Gateway){Colors.RESET}")
                time.sleep(0.3)
                print(f"{Colors.GREEN}[+] BSSID: C0:4A:00:11:22:99  SSID: 'Rons_Coffee_Staff'    [192.168.1.50]{Colors.RESET}")
                time.sleep(0.4)
                print(f"{Colors.RED}{Colors.BOLD}[!] BSSID: 00:1A:2B:3C:4D:5E  SSID: '<HIDDEN_GIGABIT>' [192.168.1.105] (UNUSUALLY HIGH TRAFFIC: 10 Gbps){Colors.RESET}")
                play_cyber_beep("success")
                if self.mission_step == 0:
                    self.mission_step = 1
                print(f"\n{Colors.YELLOW}[!] Target identified: 192.168.1.105. Run `nmap 192.168.1.105` to scan open services.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Unknown scan target. Try `scan wifi`.{Colors.RESET}")

        elif self.current_mission == 3:
            if "ecorp" in target or not target:
                typewriter("[*] Probing E-Corp Global Data Center Infrastructure...", speed=0.01, color=Colors.CYAN)
                time.sleep(0.5)
                print(f"{Colors.GREEN}[+] Node 01: tape-vault-alpha.ecorp.internal  [10.0.4.12]{Colors.RESET}")
                print(f"{Colors.GREEN}[+] Node 02: debt-ledger-db.ecorp.internal    [10.0.4.15]{Colors.RESET}")
                print(f"{Colors.RED}{Colors.BOLD}[!] Target: hsm-proxy-master.ecorp.internal   [10.0.4.100] (RSA-4096 HSM Daemon Active){Colors.RESET}")
                play_cyber_beep("success")
                if self.mission_step == 0:
                    self.mission_step = 1
                print(f"\n{Colors.YELLOW}[!] Target locked: 10.0.4.100. Inject rootkit with `inject rootkit.py`.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Unknown scan target. Try `scan ecorp`.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[*] No active scan targets in current mission scope.{Colors.RESET}")

    def cmd_nmap(self, args):
        if not args:
            print(f"{Colors.RED}Usage: nmap <target_ip>{Colors.RESET}")
            return
        ip = args[0]
        if self.current_mission == 1 and ip == "192.168.1.105":
            typewriter(f"Starting Nmap 7.94 scan on {ip}...", speed=0.01, color=Colors.CYAN)
            time.sleep(0.5)
            print(f"{Colors.BOLD}PORT     STATE SERVICE      VERSION{Colors.RESET}")
            print(f"21/tcp   {Colors.GREEN}open{Colors.RESET}  ftp          vsftpd 2.3.4 (Anonymous: Disabled)")
            print(f"80/tcp   {Colors.GREEN}open{Colors.RESET}  http         Apache/2.4.41 (Hidden Admin Portal)")
            print(f"9050/tcp {Colors.GREEN}open{Colors.RESET}  tor-socks    Tor Onion Routing Relay")
            play_cyber_beep("success")
            if self.mission_step == 1:
                self.mission_step = 2
            print(f"\n{Colors.YELLOW}[!] Port 21 (FTP) is vulnerable. Run `crack ftp 192.168.1.105` to brute-force the password.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Nmap: Host {ip} is filtered or unreachable.{Colors.RESET}")

    def cmd_crack(self, args):
        if self.current_mission == 1 and self.mission_step >= 2:
            typewriter("[*] Loading fsociety targeted dictionary permutation engine...", speed=0.01, color=Colors.CYAN)
            passwords = ["admin", "ron123", "coffee2024", "password", "rohit_coffee", "r0ns_c0ff33"]
            for pwd in passwords:
                sys.stdout.write(f"\r{Colors.DIM}[CRACKING FTP] Testing: {pwd:<20}{Colors.RESET}")
                sys.stdout.flush()
                play_click(1400, 20)
                time.sleep(0.2)
            
            print(f"\n\n{Colors.GREEN}{Colors.BOLD}[+] PASSWORD CRACKED: 'r0ns_c0ff33'{Colors.RESET}")
            print(f"{Colors.GREEN}[+] Authenticated as: root@192.168.1.105{Colors.RESET}")
            print(f"{Colors.CYAN}[+] Extracted 'evidence.log' to local directory.{Colors.RESET}")
            play_cyber_beep("success")
            self.mission_step = 3
            print(f"\n{Colors.YELLOW}[!] Evidence downloaded. Inspect it with `cat evidence.log`.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Crack failed: No exploitable service discovered yet.{Colors.RESET}")

    def cmd_ssh(self, args):
        if not args:
            print(f"{Colors.RED}Usage: ssh <host>{Colors.RESET}")
            return
        host = args[0].lower()
        if self.current_mission == 2 and ("steelmountain" in host or "hvac" in host):
            typewriter("[*] Connecting to rogue Raspberry Pi hardware implant...", speed=0.01, color=Colors.CYAN)
            time.sleep(0.4)
            print(f"{Colors.GREEN}[+] Tunnel Established: 127.0.0.1:4444 ➔ hvac-node-4B [Steel Mountain Vault]{Colors.RESET}")
            self.ssh_connected = True
            play_cyber_beep("success")
            if self.mission_step == 0:
                self.mission_step = 1
            print(f"\n{Colors.YELLOW}[!] Connected to HVAC. Run `decrypt firmware.enc` to unlock temperature failsafe.{Colors.RESET}")
        else:
            print(f"{Colors.RED}ssh: Could not resolve hostname {host}: Connection timed out.{Colors.RESET}")

    def cmd_decrypt(self, args):
        if self.current_mission == 2 and self.ssh_connected and self.mission_step >= 1:
            print(f"\n{Colors.CYAN}[*] HVAC Cryptographic Challenge: Caesar Shift Cipher{Colors.RESET}")
            print(f"{Colors.YELLOW}Ciphertext: 'WKHUPDO-RYHUULGH-NHB'{Colors.RESET}")
            print(f"{Colors.DIM}Hint: Shift each letter backward by 3 (D ➔ A, E ➔ B, etc.){Colors.RESET}\n")
            
            ans = input(f"{Colors.BOLD}Enter Plaintext Key: {Colors.RESET}").strip().upper()
            if ans == "THERMAL-OVERRIDE-KEY":
                print(f"\n{Colors.GREEN}{Colors.BOLD}[+] KEY ACCEPTED! Firmware failsafe unlocked.{Colors.RESET}")
                play_cyber_beep("success")
                self.mission_step = 2
                print(f"{Colors.YELLOW}[!] Now crank the temperature to 120°F with: `override 120F`{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}[!] Invalid key! Try decrypting 'WKHUPDO-RYHUULGH-NHB' (Shift by -3).{Colors.RESET}")
        else:
            print(f"{Colors.RED}Cannot decrypt: Connect via SSH to Steel Mountain first.{Colors.RESET}")

    def cmd_override(self, args):
        if not args:
            print(f"{Colors.RED}Usage: override <temperature> (e.g. `override 120F`){Colors.RESET}")
            return
        temp = args[0].upper()
        if self.current_mission == 2 and self.ssh_connected and self.mission_step >= 2:
            if "120" in temp or "130" in temp:
                typewriter(f"[*] Overriding HVAC Zone 4B climate control to {temp}...", speed=0.015, color=Colors.CYAN)
                time.sleep(0.4)
                print(f"{Colors.YELLOW}[!] Thermostat setpoint changed: 68.0°F ➔ {temp}{Colors.RESET}")
                time.sleep(0.3)
                print(f"{Colors.RED}{Colors.BOLD}[!] ALERT: TAPE BACKUP VAULT TEMPERATURE CRITICAL: 121.4°F{Colors.RESET}")
                print(f"{Colors.GREEN}{Colors.BOLD}[✔] MAGNETIC BACKUP TAPES PERMANENTLY MELTED & DESTROYED!{Colors.RESET}")
                play_cyber_beep("success")
                self.mission_step = 3
                self.check_mission_progress()
            else:
                print(f"{Colors.RED}[!] Temperature too low to melt tapes. Target at least 120°F (`override 120F`).{Colors.RESET}")
        else:
            print(f"{Colors.RED}Override error: Failsafe is still locked. Decrypt the key first.{Colors.RESET}")

    def cmd_inject(self, args):
        if not args:
            print(f"{Colors.RED}Usage: inject <payload_file>{Colors.RESET}")
            return
        payload = args[0].lower()
        if self.current_mission == 3 and self.mission_step >= 1:
            if "rootkit" in payload:
                typewriter("[*] Injecting rootkit into E-Corp HSM Master Daemon...", speed=0.01, color=Colors.CYAN)
                time.sleep(0.5)
                print(f"{Colors.GREEN}[+] Memory Hook Succeeded: Process PID 1337 (hsm_daemon) Patched.{Colors.RESET}")
                print(f"{Colors.GREEN}[+] AES-256 Self-Replicating Encryption Hook: READY.{Colors.RESET}")
                play_cyber_beep("success")
                self.mission_step = 2
                print(f"\n{Colors.YELLOW}{Colors.BOLD}[!] ALL NODES COMPROMISED. Type `execute 5-9` to execute the revolution.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Unknown payload. Use `inject rootkit.py`.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Cannot inject: Scan E-Corp nodes first (`scan ecorp`).{Colors.RESET}")

    def cmd_execute(self, args):
        if not args:
            print(f"{Colors.RED}Usage: execute <operation_name>{Colors.RESET}")
            return
        op = args[0].lower()
        if self.current_mission == 3 and self.mission_step >= 2 and op in ["5-9", "5/9", "fsociety"]:
            matrix_rain_effect()
            typewriter("Elliot: \"It happened. The world has changed. All consumer debts have been erased.\"", speed=0.02, color=Colors.CYAN)
            typewriter("fsociety: \"Leave me here. We did it.\"\n", speed=0.02, color=Colors.RED)
            print(f"{Colors.YELLOW}{Colors.BOLD}🏆 CONGRATULATIONS! YOU HAVE COMPLETED ALL MR. ROBOT MISSIONS! 🏆{Colors.RESET}\n")
            self.mission_step = 3
        else:
            print(f"{Colors.RED}Execution denied: Prerequisites not met.{Colors.RESET}")

    def check_mission_progress(self):
        if self.current_mission == 1 and self.mission_step >= 4:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 MISSION 1 COMPLETE: Ron's dark web ring is dismantled!{Colors.RESET}")
            print(f"{Colors.CYAN}[*] Loading Mission 2: Steel Mountain Operation Climate Melt...{Colors.RESET}\n")
            time.sleep(1.5)
            self.current_mission = 2
            self.mission_step = 0
            self.show_status()
        elif self.current_mission == 2 and self.mission_step >= 3:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 MISSION 2 COMPLETE: Steel Mountain offline backups destroyed!{Colors.RESET}")
            print(f"{Colors.CYAN}[*] Loading Mission 3: E-Corp 5/9 Global Infiltration...{Colors.RESET}\n")
            time.sleep(1.5)
            self.current_mission = 3
            self.mission_step = 0
            self.ssh_connected = False
            self.show_status()


# =====================================================================
# Main Game Loop
# =====================================================================
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_fsociety_banner()
    
    engine = GameEngine()
    typewriter("Hello, friend. Let's begin.", speed=0.03, color=Colors.CYAN)
    engine.show_status()

    while True:
        try:
            prompt = engine.get_prompt()
            cmd_input = input(prompt)
            engine.handle_command(cmd_input)
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{Colors.RED}[*] Session terminated.{Colors.RESET}")
            break


if __name__ == '__main__':
    main()
