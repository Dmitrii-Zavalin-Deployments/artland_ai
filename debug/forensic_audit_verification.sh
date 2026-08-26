#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING FORENSIC AUDIT & REPAIR (SCHEMA VALIDATION FIX)"
echo "=========================================================="

# ------------------------------------------------------------------
# 1. Diagnostics & Smoking-Gun Audits (cat -n / grep)
# ------------------------------------------------------------------
echo "--- [1/3] Running diagnostics on test_main_schema_validation_failure ---"
if [ -f "tests/test_main_coverage.py" ]; then
    echo "=== Auditing tests/test_main_coverage.py around test_main_schema_validation_failure ==="
    grep -n -C 10 "test_main_schema_validation_failure" tests/test_main_coverage.py || true
    cat -n tests/test_main_coverage.py | head -n 40
fi

if [ -f "src/input_schema.json" ]; then
    echo "=== Auditing src/input_schema.json ==="
    cat -n src/input_schema.json || true
fi

# ------------------------------------------------------------------
# 2. Automated Surgical Repairs via Python
# ------------------------------------------------------------------
echo "--- [2/3] Applying automated surgical repair to trigger schema validation failure ---"

python3 - << 'EOF'
from pathlib import Path

path = Path("tests/test_main_coverage.py")
if path.exists():
    code = path.read_text(encoding="utf-8")
    
    # To force a schema validation error, provide an invalid type for a required field 
    # (e.g., input_zip_path as an integer instead of a string) or violate schema rules.
    old_payload = 'json.dumps({"input_zip_path": "dummy.zip", "processed_photos_zip_path": "processed.zip", "magazine_assets_zip_path": "magazine.zip", "invalid_field": 123})'
    new_payload = 'json.dumps({"input_zip_path": 123, "processed_photos_zip_path": "processed.zip", "magazine_assets_zip_path": "magazine.zip"})'
    
    if old_payload in code:
        code = code.replace(old_payload, new_payload)
        path.write_text(code, encoding="utf-8")
        print("✅ Updated payload in test_main_schema_validation_failure to violate type constraints")
    else:
        # Fallback: replace any json.dumps inside test_main_schema_validation_failure with invalid type payload
        import re
        pattern = r'(def test_main_schema_validation_failure.*?input_file\.write_text\()json\.dumps\(.*?\)(\))'
        replacement = r'\1json.dumps({"input_zip_path": 123})\2'
        new_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
        if new_code != code:
            path.write_text(new_code, encoding="utf-8")
            print("✅ Replaced test payload via regex pattern match")
EOF