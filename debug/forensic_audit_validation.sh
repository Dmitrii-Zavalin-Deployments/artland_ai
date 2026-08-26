#!/usr/bin/env bash
set -euo pipefail

echo "================================================================="
echo "🔍 [FORENSIC AUDIT] Starting Pipeline Environment & Code Audit..."
echo "================================================================="

# 1. Environment & Dependency Diagnostics
echo "--- [1/3] Environment & Package Inspection ---"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python3 --version)"
echo "Python Executable: $(which python3)"
echo "PYTHONPATH: ${PYTHONPATH:-Not Set}"

echo "Checking installed Python packages:"
python3 -m pip list

echo "Testing OpenCV (cv2) module import directly:"
if python3 -c "import cv2; print('✅ OpenCV version:', cv2.__version__)" 2>&1; then
    echo "OpenCV import test passed successfully."
else
    echo "❌ WARNING: OpenCV import failed! Missing dependency or headless package mismatch detected."
    echo "Attempting automated repair: Installing opencv-python-headless..."
    python3 -m pip install --upgrade opencv-python-headless
fi

# 2. Smoking-Gun Source Audits (cat -n)
echo "--- [2/3] Smoking-Gun Source Audits ---"
TARGET_FILES=(
    "src/main.py"
    "src/artistic_pipeline_video.py"
    "src/processor/artistic_painting_processor.py"
)

for file in "${TARGET_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "========================================================="
        echo "📄 File Audit (cat -n): $file"
        echo "========================================================="
        cat -n "$file"
    else
        echo "❌ ERROR: Critical source file not found: $file"
    fi
done