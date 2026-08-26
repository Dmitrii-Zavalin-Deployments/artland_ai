#!/usr/bin/env bash
set -euo pipefail

echo "================================================================="
echo "🔍 [FORENSIC AUDIT] Starting Pipeline Environment & Code Audit..."
echo "================================================================="

# 1. Environment & Dependency Diagnostics (Targeting scikit-learn)
echo "--- [1/3] Environment & Package Inspection ---"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python3 --version)"
echo "Python Executable: $(which python3)"
echo "PYTHONPATH: ${PYTHONPATH:-Not Set}"

echo "Checking installed Python packages:"
python3 -m pip list

echo "Testing scikit-learn (sklearn) module import directly:"
if python3 -c "import sklearn; print('✅ scikit-learn version:', sklearn.__version__)" 2>&1; then
    echo "scikit-learn import test passed successfully."
else
    echo "❌ WARNING: scikit-learn import failed! Missing dependency detected."
    echo "Attempting automated repair: Installing scikit-learn..."
    python3 -m pip install --upgrade scikit-learn
fi

# 2. Smoking-Gun Source Audits (cat -n)
echo "--- [2/3] Smoking-Gun Source Audits ---"
TARGET_FILES=(
    "requirements.txt"
    "src/processor/generate_background.py"
    "src/artistic_pipeline_magazine.py"
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

# 3. Automated Repairs & Requirements Adjustments (sed/echo injections)
echo "--- [3/3] Applying Automated Repairs & Safeguards ---"

# Ensure scikit-learn is present in requirements.txt
REQ_FILE="requirements.txt"
if [ -f "$REQ_FILE" ]; then
    echo "Checking scikit-learn presence in $REQ_FILE..."
    if ! grep -q "scikit-learn" "$REQ_FILE"; then
        echo "Injecting scikit-learn into $REQ_FILE..."
        printf "\n# Machine Learning & Clustering Pipeline\nscikit-learn>=1.3.0\n" >> "$REQ_FILE"
        echo "✅ scikit-learn added to $REQ_FILE."
    else
        echo "scikit-learn already listed in $REQ_FILE."
    fi
fi

echo "================================================================="
echo "🏁 [FORENSIC AUDIT] Diagnostic and repair sequence completed."
echo "================================================================="