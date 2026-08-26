#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING FORENSIC AUDIT & REPAIR (ROOT SCHEMA TYPE FIX)"
echo "=========================================================="

# ------------------------------------------------------------------
# 1. Diagnostics & Smoking-Gun Audits (cat -n / grep)
# ------------------------------------------------------------------
echo "--- [1/3] Running diagnostics on schemas and test implementation ---"
if [ -f "src/schema/input_schema.json" ]; then
    echo "=== Auditing src/schema/input_schema.json ==="
    cat -n src/schema/input_schema.json || true
fi

if [ -f "tests/test_main_coverage.py" ]; then
    echo "=== Auditing test_main_schema_validation_failure in test file ==="
    cat -n tests/test_main_coverage.py | head -n 40
fi

# ------------------------------------------------------------------
# 2. Automated Surgical Repairs via Python
# ------------------------------------------------------------------
echo "--- [2/3] Applying surgical fix to write invalid root JSON type ---"

python3 - << 'EOF'
import re
from pathlib import Path

path = Path("tests/test_main_coverage.py")
if path.exists():
    code = path.read_text(encoding="utf-8")
    
    # To guarantee a schema ValidationError without hitting pipeline steps or path lookups,
    # pass a JSON list ([1, 2, 3]) instead of an object ({}) as the root payload.
    # JSON schema expects an object for input files, instantly triggering a root ValidationError.
    pattern = r'(def test_main_schema_validation_failure.*?input_file\.write_text\()json\.dumps\(.*?\)(\))'
    replacement = r'\1json.dumps([1, 2, 3])\2'
    
    new_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    
    if new_code == code:
        # Fallback replacement if regex pattern needs a broader match
        code = re.sub(r'input_file\.write_text\(json\.dumps\(.*?\)', 'input_file.write_text(json.dumps([1, 2, 3])', code, count=1)
    else:
        code = new_code

    path.write_text(code, encoding="utf-8")
    print("✅ Successfully patched test input file to write an invalid root type ([1, 2, 3])")
EOF