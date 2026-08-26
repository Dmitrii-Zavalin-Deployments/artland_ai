#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING FORENSIC AUDIT & REPAIR (MAGAZINE ASSETS KEY)"
echo "=========================================================="

# ------------------------------------------------------------------
# 1. Diagnostics & Smoking-Gun Audits (cat -n / grep)
# ------------------------------------------------------------------
echo "--- [1/3] Running diagnostics on test_main_schema_validation_failure ---"
if [ -f "tests/test_main_coverage.py" ]; then
    echo "=== Auditing tests/test_main_coverage.py around test_main_schema_validation_failure ==="
    cat -n tests/test_main_coverage.py | head -n 35
    grep -n -C 5 "invalid_input.json" tests/test_main_coverage.py || true
fi

# ------------------------------------------------------------------
# 2. Automated Surgical Repairs via Python
# ------------------------------------------------------------------
echo "--- [2/3] Applying automated surgical repair to test input JSON payload ---"

python3 - << 'EOF'
from pathlib import Path

path = Path("tests/test_main_coverage.py")
if path.exists():
    code = path.read_text(encoding="utf-8")
    
    # Add magazine_assets_zip_path to the invalid input JSON dictionary
    old_payload = 'json.dumps({"input_zip_path": "dummy.zip", "processed_photos_zip_path": "processed.zip", "invalid_field": 123})'
    new_payload = 'json.dumps({"input_zip_path": "dummy.zip", "processed_photos_zip_path": "processed.zip", "magazine_assets_zip_path": "magazine.zip", "invalid_field": 123})'
    
    if old_payload in code:
        code = code.replace(old_payload, new_payload)
        path.write_text(code, encoding="utf-8")
        print("✅ Added 'magazine_assets_zip_path' to test_main_schema_validation_failure payload")
    else:
        # Fallback broad match if payload formatting varied slightly
        if '"magazine_assets_zip_path"' not in code:
            code = code.replace(
                '"invalid_field": 123',
                '"magazine_assets_zip_path": "magazine.zip", "invalid_field": 123'
            )
            path.write_text(code, encoding="utf-8")
            print("✅ Injected 'magazine_assets_zip_path' via fallback replacement")
EOF