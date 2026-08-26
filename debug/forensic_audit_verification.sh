#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING FORENSIC AUDIT & REPAIR (KEYERROR FIX)"
echo "=========================================================="

# ------------------------------------------------------------------
# 1. Diagnostics & Smoking-Gun Audits (cat -n / grep)
# ------------------------------------------------------------------
echo "--- [1/3] Running diagnostics on test_main_schema_validation_failure ---"
if [ -f "tests/test_main_coverage.py" ]; then
    echo "=== Auditing tests/test_main_coverage.py around test_main_schema_validation_failure ==="
    cat -n tests/test_main_coverage.py | sed -n '10,35p'
fi

# ------------------------------------------------------------------
# 2. Automated Surgical Repairs via Python
# ------------------------------------------------------------------
echo "--- [2/3] Applying automated surgical repair to test input JSON ---"

python3 - << 'EOF'
from pathlib import Path

path = Path("tests/test_main_coverage.py")
if path.exists():
    code = path.read_text(encoding="utf-8")
    
    # Ensure the test schema validation JSON payload includes the required processed_photos_zip_path key
    old_payload = 'json.dumps({"input_zip_path": "dummy.zip", "invalid_field": 123})'
    new_payload = 'json.dumps({"input_zip_path": "dummy.zip", "processed_photos_zip_path": "processed.zip", "invalid_field": 123})'
    
    if old_payload in code:
        code = code.replace(old_payload, new_payload)
        path.write_text(code, encoding="utf-8")
        print("✅ Added 'processed_photos_zip_path' to test_main_schema_validation_failure payload")
EOF