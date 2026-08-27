#!/usr/bin/env bash
set -euo pipefail

echo "======================================================================"
echo "               🔍 ART_LAND AI: GENERATE_BACKGROUND FORENSIC AUDIT     "
echo "======================================================================"

# 1. Environment & Package Diagnostics
echo -n ">>> Python Version: "
python3 --version

echo ">>> Installed Dependencies:"
pip list | grep -E "pytest|numpy|opencv-python|scikit-learn|Pillow" || true

echo ""
echo "----------------------------------------------------------------------"
echo " 1. SMOKING-GUN SOURCE AUDIT (src/processor/generate_background.py)  "
echo "----------------------------------------------------------------------"
if [ -f "src/processor/generate_background.py" ]; then
    cat -n src/processor/generate_background.py
else
    echo "❌ ERROR: src/processor/generate_background.py not found!"
    exit 1
fi

echo ""
echo "----------------------------------------------------------------------"
echo " 2. TEST FILE AUDIT (tests/test_generate_background_coverage.py)     "
echo "----------------------------------------------------------------------"
if [ -f "tests/test_generate_background_coverage.py" ]; then
    cat -n tests/test_generate_background_coverage.py
else
    echo "❌ ERROR: tests/test_generate_background_coverage.py not found!"
    exit 1
fi

echo ""
echo "----------------------------------------------------------------------"
echo " 3. EXECUTING PYTEST WITH COVERAGE REPORT                             "
echo "----------------------------------------------------------------------"
pytest --cov=src/processor/generate_background --cov-report=term-missing tests/test_generate_background_coverage.py || {
    EXIT_CODE=$?
    echo "⚠ Pytest encountered failures (Exit code: $EXIT_CODE). Continuing forensic capture..."
}

echo ""
echo "----------------------------------------------------------------------"
echo " 4. GIT STATUS & DIFF CHECK                                           "
echo "----------------------------------------------------------------------"
git status --short
git diff || true

echo "======================================================================"
echo "                     ✅ FORENSIC AUDIT COMPLETE                       "
echo "======================================================================"