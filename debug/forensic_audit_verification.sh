#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "=== [FORENSIC AUDIT] Scikit-Image Warning Fix ==="
echo "=================================================="

# 1. Grep/cat diagnostics for code/output root causes
echo "--- [1/3] Checking existing warning filters and test setup ---"
grep -rn "filterwarnings" tests/ src/ conftest.py pyproject.toml 2>/dev/null || echo "No explicit warning filters found in searched files."

if [ -f "conftest.py" ]; then
    echo "ℹ️ conftest.py exists."
else
    echo "ℹ️ conftest.py does not exist. A new one will be generated."
fi

# 2. Cat -n for smoking-gun source audits
echo "--- [2/3] Inspecting conftest.py or test entry points ---"
if [ -f "conftest.py" ]; then
    echo "--- conftest.py audit ---"
    cat -n conftest.py
else
    echo "--- tests/test_integration.py audit (first 30 lines) ---"
    if [ -f "tests/test_integration.py" ]; then
        cat -n tests/test_integration.py | head -n 30
    else
        echo "❌ Error: tests/test_integration.py not found."
    fi
fi

# 3. Automated repairs via python/sed injections
echo "--- [3/3] Injecting global warning suppression for skimage low-contrast ---"
python3 -c '
import os

conftest_path = "conftest.py"
warning_snippet = """
import warnings
# Automatically suppress scikit-image low-contrast warnings in test suite
warnings.filterwarnings("ignore", category=UserWarning, message=".*is a low contrast image.*")
"""

if not os.path.exists(conftest_path):
    with open(conftest_path, "w", encoding="utf-8") as f:
        f.write(warning_snippet.strip() + "\n")
    print("✅ Created conftest.py with scikit-image low-contrast warning filter.")
else:
    with open(conftest_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "is a low contrast image" not in content:
        with open(conftest_path, "a", encoding="utf-8") as f:
            f.write("\n" + warning_snippet.strip() + "\n")
        print("✅ Appended low-contrast warning filter to existing conftest.py.")
    else:
        print("ℹ️ Warning filter already present in conftest.py.")
'