@echo off
chcp 65001 > nul
title 🔊 Cyber Acoustic & Spectrogram Studio
echo Launching Cyber Acoustic Studio...
start pythonw "%~dp0cyber_acoustic_studio.py"
exit
