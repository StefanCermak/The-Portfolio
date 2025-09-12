#!/bin/bash

set -e

# 1. Systemabhängigkeiten installieren (macOS)
echo "Installiere Systemabhängigkeiten (macOS)..."
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew wird benötigt. Installiere es zuerst: https://brew.sh/"
  exit 1
fi
brew install --cask xquartz || true  # Für tkinter-GUI, falls nicht vorhanden

# 2. Python-Abhängigkeiten installieren
echo "Installiere Python-Abhängigkeiten..."
pip3 install -r requirements.txt
pip3 install pyinstaller

# 3. Kernfunktionalität validieren
echo "Validiere Kernmodule und Datenbank..."
python3 -c "
import globals, Db, stockdata, tools
print('✓ Core modules loaded')
db = Db.Db()
print('✓ Database initialized')
db.close()
"

# 4. GUI-Anwendung testen
echo "Teste GUI-Anwendung..."
python3 -c "
from Gui import BrokerApp
app = BrokerApp()
print('✓ GUI application ready')
"

# 5. Anwendung als Standalone-Binary bauen
echo "Erstelle Standalone-Binary mit PyInstaller..."
#python3 -m PyInstaller --onedir --windowed --name The-Portfolio main.py
python3 -m PyInstaller --onefile --name The-Portfolio main.py

echo "Setup, Validierung und Build abgeschlossen."

echo "Die ausführbare Datei befindet sich im Verzeichnis 'dist'."
echo "Führe die Anwendung mit folgendem Befehl aus:"
echo "./dist/The-Portfolio"