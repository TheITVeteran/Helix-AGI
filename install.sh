#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#   Helix‑AGI — Setup Wizard Launcher
#
#   Checks for Python dependencies and launches the setup wizard.
#   Run this from the repository root:
#     chmod +x install.sh && ./install.sh
# ──────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════╗"
echo "║       HELIX‑AGI SETUP WIZARD             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Check Python ──────────────────────────────────────────────
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" --version 2>&1 | grep -oP '\d+\.\d+')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; }; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python 3.11+ is required but not found."
    echo "   Install Python from https://python.org/downloads"
    exit 1
fi

echo "✓ Using $PYTHON ($($PYTHON --version))"

# ── Check virtual environment ─────────────────────────────────
if [ -x "venv/bin/python" ]; then
    echo "✓ Virtual environment found"
    source venv/bin/activate
    PYTHON="$SCRIPT_DIR/venv/bin/python"
elif [ -x ".venv/bin/python" ]; then
    echo "✓ Virtual environment found (.venv)"
    source .venv/bin/activate
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
    echo "Creating virtual environment..."
    $PYTHON -m venv venv
    source venv/bin/activate
    PYTHON="$SCRIPT_DIR/venv/bin/python"
    echo "✓ Virtual environment created"
fi

# ── Install dependencies ──────────────────────────────────────
echo ""
echo "Checking dependencies..."
"$PYTHON" -m pip install --quiet --upgrade pip

# Install PyQt6 first (needed for the wizard GUI)
"$PYTHON" -m pip install --quiet PyQt6 PyQt6-WebEngine || {
    echo "⚠ PyQt6 installation failed. You may need to install system Qt libraries:"
    echo "   sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine"
}

# Install remaining requirements
if [ -f "requirements-mindscape.txt" ]; then
    "$PYTHON" -m pip install --quiet -r requirements-mindscape.txt
fi

echo "✓ Dependencies ready"
echo ""

# ── Launch Wizard ─────────────────────────────────────────────
echo "Launching Helix‑AGI Setup Wizard..."
echo ""
"$PYTHON" -m wizard "$@"
