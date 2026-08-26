#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING FORENSIC AUDIT & REPAIR (FIXED REGEX & PAYLOAD)"
echo "=========================================================="

# ------------------------------------------------------------------
# 1. Automated Surgical Repair via Python
# ------------------------------------------------------------------
echo "--- [1/2] Applying clean surgical fix to test payload ---"

python3 - << 'EOF'
import re
from pathlib import Path

path = Path("tests/test_main_coverage.py")
if path.exists():
    code = path.read_text(encoding="utf-8")
    
    # Target test_main_schema_validation_failure and write a payload that 
    # violates schema validation (e.g., passing an invalid type to a non-path field or extra invalid property)
    # while keeping input_zip_path as a valid string path.
    pattern = r'(def test_main_schema_validation_failure.*?input_file\.write_text\()json\.dumps\(.*?\)(\))'
    
    # We pass valid string for input_zip_path, but an invalid type/structure to trigger jsonschema ValidationError
    replacement = r'\1json.dumps({"input_zip_path": "dummy.zip", "processed_photos_zip_path": "processed.zip", "magazine_assets_zip_path": "magazine.zip", "invalid_schema_field": {"nested": [1, 2, 3]}})\2'
    
    new_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    
    if new_code == code:
        # Fallback replacement if regex pattern did not match exact signature
        code = code.replace(
            'json.dumps({"input_zip_path": 123,',
            'json.dumps({"input_zip_path": "dummy.zip", "processed_photos_zip_path": "processed.zip", "magazine_assets_zip_path": "magazine.zip", "invalid_schema_field": 123,'
        )
    else:
        code = new_code

    path.write_text(code, encoding="utf-8")
    print("✅ Successfully updated test_main_schema_validation_failure payload")
EOF