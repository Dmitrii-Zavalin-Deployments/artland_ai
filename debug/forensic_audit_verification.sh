#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING FORENSIC AUDIT & REPAIR FOR IMAGE BACKEND ERROR"
echo "=========================================================="

# ------------------------------------------------------------------
# 1. Diagnostics & Smoking-Gun Audits
# ------------------------------------------------------------------
echo "--- [1/3] Running diagnostics on test_main_schema_validation_failure ---"
if [ -f "tests/test_main_coverage.py" ]; then
    echo "=== Auditing test_main_schema_validation_failure in tests/test_main_coverage.py ==="
    grep -n -C 12 "test_main_schema_validation_failure" tests/test_main_coverage.py || true
fi

# ------------------------------------------------------------------
# 2. Automated Surgical Repair via Python
# ------------------------------------------------------------------
echo "--- [2/3] Applying surgical fix to generate valid JPEG images using Pillow ---"

python3 - << 'EOF'
from pathlib import Path

path = Path("tests/test_main_coverage.py")
if path.exists():
    code = path.read_text(encoding="utf-8")
    
    # Ensure Pillow is imported
    if "from PIL import Image" not in code:
        code = "from PIL import Image\n" + code
        
    # Replace dummy frame writes with valid Pillow JPEG creation
    if 'write_text("dummy data"' in code:
        code = code.replace(
            'write_text("dummy data"', 
            'parent.mkdir(parents=True, exist_ok=True); Image.new("RGB", (10, 10), color="red").save('
        )
    elif 'write_bytes(b"dummy data"' in code:
        code = code.replace(
            'write_bytes(b"dummy data"', 
            'parent.mkdir(parents=True, exist_ok=True); Image.new("RGB", (10, 10), color="red").save('
        )
        
    path.write_text(code, encoding="utf-8")
    print("✅ Patched test_main_coverage.py to write valid Pillow-generated JPEGs")
EOF