#!/bin/bash
echo "[+] Installing GhostPin v3.1"

pkg update -y && pkg upgrade -y
pkg install php python git curl wget -y
pip install requests flask colorama pycryptodome fpdf 2>/dev/null
pip install pyshorteners 2>/dev/null

mkdir -p templates modules db reports
chmod +x ghostpin.py install.sh

echo "[+] Installation Complete"
echo "[+] Run: python3 ghostpin.py"
