@echo off
chcp 65001 > nul
title Wi-Fi Radar & Frequency Analyzer
echo Starting Wi-Fi Radar...
start pythonw "%~dp0wifi_radar.py"
exit
