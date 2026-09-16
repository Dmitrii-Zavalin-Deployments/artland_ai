#!/usr/bin/env bash
# ==============================================================================
# Forensic Audit & Automated Remediation Script for zipfile.BadZipFile Error
# ==============================================================================
set -euo pipefail

echo "=== 1. DIAGNOSTICS: Running pytest to confirm BadZipFile failures ==="
pytest tests/test_main.py || true

echo "=== 2. SMOKING-GUN SOURCE AUDIT: Inspecting dummy.zip creation in tests/test_main.py ==="
grep -n -C 5 "dummy.zip" tests/test_main.py | cat -n

echo "=== 3. AUTOMATED REMEDIATION: Replacing empty touch() with valid minimal zip creation ==="
python3 -c '
path = "tests/test_main.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Target statement creating an empty file via touch()
target = "dummy_zip.touch()"

# Replacement creating a valid minimal zip file using Python zipfile module
replacement = """import zipfile
    with zipfile.ZipFile(dummy_zip, "w") as zf:
        zf.writestr("sample.txt", "data")"""

if target in content:
    content = content.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Replaced dummy_zip.touch() with valid zip file creation.")
else:
    print("INFO: Target touch() statement not found or already replaced.")
'

echo "=== 4. POST-REPAIR AUDIT: Verifying updated test code segment ==="
grep -n -C 5 "zipfile.ZipFile" tests/test_main.py | cat -n

echo "=== 5. VERIFICATION: Running full test suite with 100% coverage check ==="
pytest --cov=src --cov-fail-under=100 -v

echo "🎯 Forensic audit, remediation, and verification completed successfully!"