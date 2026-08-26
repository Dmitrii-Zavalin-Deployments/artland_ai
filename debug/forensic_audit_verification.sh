#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING FORENSIC AUDIT & REPAIR (RUFF & SYNTAX FIXES)"
echo "=========================================================="

# ------------------------------------------------------------------
# 1. Diagnostics & Smoking-Gun Audits (cat -n / grep)
# ------------------------------------------------------------------
echo "--- [1/3] Running diagnostics on failing test modules ---"

if [ -f "tests/test_artistic_pipeline_magazine_coverage.py" ]; then
    echo "=== Auditing tests/test_artistic_pipeline_magazine_coverage.py (around line 58) ==="
    cat -n tests/test_artistic_pipeline_magazine_coverage.py | sed -n '45,65p'
fi

if [ -f "tests/test_frames_loader_coverage.py" ]; then
    echo "=== Auditing tests/test_frames_loader_coverage.py (indentation blocks) ==="
    cat -n tests/test_frames_loader_coverage.py | sed -n '25,35p;40,50p;75,85p'
fi

# ------------------------------------------------------------------
# 2. Automated Surgical Repairs via Python
# ------------------------------------------------------------------
echo "--- [2/3] Applying automated surgical repairs ---"

python3 - << 'EOF'
from pathlib import Path

# ------------------------------------------------------------------
# Fix 1: Resolve Undefined name 'app' in tests/test_artistic_pipeline_magazine_coverage.py
# ------------------------------------------------------------------
art_test_path = Path("tests/test_artistic_pipeline_magazine_coverage.py")
if art_test_path.exists():
    code = art_test_path.read_text(encoding="utf-8")
    if "delattr(app, 'run')" in code and "import processor.artistic_painting_processor as app" not in code:
        # Insert local import of app inside the test function where delattr is used
        code = code.replace(
            "def test_missing_processor_run_methods(",
            "def test_missing_processor_run_methods(\n    import processor.artistic_painting_processor as app\n"
        )
        art_test_path.write_text(code, encoding="utf-8")
        print("✅ Added local import of app in test_missing_processor_run_methods")

# ------------------------------------------------------------------
# Fix 2: Fix indentation syntax errors after 'with' statement in tests/test_frames_loader_coverage.py
# ------------------------------------------------------------------
frames_test_path = Path("tests/test_frames_loader_coverage.py")
if frames_test_path.exists():
    code = frames_test_path.read_text(encoding="utf-8")
    # Correct unindented statements following BadZipFile context manager
    code = code.replace(
        "with pytest.raises(zipfile.BadZipFile):\n        frames_loader.run(state)",
        "with pytest.raises(zipfile.BadZipFile):\n            frames_loader.run(state)"
    )
    code = code.replace(
        "with pytest.raises(zipfile.BadZipFile):\n    frames_loader.run(state)",
        "with pytest.raises(zipfile.BadZipFile):\n            frames_loader.run(state)"
    )
    frames_test_path.write_text(code, encoding="utf-8")
    print("✅ Fixed indentation syntax errors in test_frames_loader_coverage.py")

EOF