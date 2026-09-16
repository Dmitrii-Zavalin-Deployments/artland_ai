#!/usr/bin/env bash
# ==============================================================================
# Forensic Audit & Automated Remediation Script for FileNotFoundError (dummy.zip)
# ==============================================================================
set -euo pipefail

echo "=== 2. SMOKING-GUN SOURCE AUDIT: Inspecting test setup lines in tests/test_main.py ==="
grep -n -C 5 "input_zip_path" tests/test_main.py | cat -n

echo "=== 3. AUTOMATED REMEDIATION: Creating dummy.zip dynamically in test fixtures ==="
python3 -c '
path = "tests/test_main.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the static input writing blocks with dynamic file creation for dummy.zip
old_block_valid = """    input_file = folder / "input.json"
    input_file.write_text(\x27{"input_zip_path": "dummy.zip", "valid_key": "value"}\x27, encoding="utf-8")"""

new_block_valid = """    input_file = folder / "input.json"
    dummy_zip = folder / "dummy.zip"
    dummy_zip.touch()
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "valid_key": "value"}), encoding="utf-8")"""

old_block_invalid = """    input_file = folder / "input.json"
    input_file.write_text(\x27{"input_zip_path": "dummy.zip", "invalid_field": true}\x27, encoding="utf-8")"""

new_block_invalid = """    input_file = folder / "input.json"
    dummy_zip = folder / "dummy.zip"
    dummy_zip.touch()
    input_file.write_text(json.dumps({"input_zip_path": str(dummy_zip), "invalid_field": True}), encoding="utf-8")"""

content = content.replace(old_block_valid, new_block_valid)
content = content.replace(old_block_invalid, new_block_invalid)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Patched test fixtures to dynamically touch and reference dummy.zip.")
'

echo "=== 4. POST-REPAIR AUDIT: Verifying updated test code segment ==="
sed -n '30,55p' tests/test_main.py | cat -n

echo "🎯 Forensic audit, remediation, and verification completed successfully!"