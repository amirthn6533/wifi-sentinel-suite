@echo off
chcp 65001 > nul
title Wi-Fi 2D/3D Heatmap & RF Raytracer
echo Starting Wi-Fi Heatmap & RF Raytracer...
start pythonw "%~dp0wifi_heatmap.py"
exit
