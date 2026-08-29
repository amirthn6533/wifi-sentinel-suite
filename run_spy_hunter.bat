@echo off
chcp 65001 > nul
title Wi-Fi Spy Cam & Drone RF Hunter
echo Starting Spy Cam & Drone RF Hunter...
start pythonw "%~dp0wifi_spy_hunter.py"
exit
