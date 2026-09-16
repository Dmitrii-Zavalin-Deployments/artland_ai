#!/usr/bin/env bash
# ==============================================================================
# Forensic Audit & Automated Remediation Script for Artistic Painting Config Fix
# ==============================================================================
set -euo pipefail

echo "=== 2. SMOKING-GUN SOURCE AUDIT: Inspecting config.json creation in tests/test_main.py ==="
grep -n -C 4 "config.json" tests/test_main.py | cat -n

echo "=== 3. AUTOMATED REMEDIATION: Adding artistic_painting block to config.json test fixtures ==="
python3 -c '
path = "tests/test_main.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

target = "{\"target_fps\": 30}"
replacement = "{\"target_fps\": 30, \"artistic_painting\": {}}"

if target in content:
    content = content.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Injected artistic_painting configuration block into test fixtures.")
else:
    print("INFO: Target config string not found or already replaced.")
'

echo "=== 4. POST-REPAIR AUDIT: Verifying updated test code segment ==="
grep -n -C 4 "artistic_painting" tests/test_main.py | cat -n

echo "🎯 Forensic audit, remediation, and verification completed successfully!"