#!/usr/bin/env bash
# ==============================================================================
# Forensic Audit & Automated Remediation Script for Ruff SIM117 Violation
# ==============================================================================
set -euo pipefail

echo "=== 1. DIAGNOSTICS: Inspecting current Ruff violations ==="
ruff check src tests || true

echo "=== 2. SMOKING-GUN SOURCE AUDIT: Inspecting tests/test_main.py lines 255 to 275 ==="
sed -n '255,275p' tests/test_main.py | cat -n

echo "=== 3. AUTOMATED REPAIR: Combining nested with statements to satisfy SIM117 ==="
python3 -c '
path = "tests/test_main.py"
content = open(path, "r", encoding="utf-8").read()

# Target nested structure causing SIM117
target = """    with patch.object(sys, "argv", test_args):
        with pytest.raises(RuntimeError, match="Unexpected crash in loader"):
            main()"""

# Combined single-statement structure compliant with Ruff SIM117
replacement = """    with patch.object(sys, "argv", test_args), pytest.raises(
        RuntimeError, match="Unexpected crash in loader"
    ):
        main()"""

if target in content:
    content = content.replace(target, replacement)
    open(path, "w", encoding="utf-8").write(content)
    print("SUCCESS: Target nested with block successfully replaced.")
else:
    print("WARNING: Exact target match not found. Attempting regex fallback...")
    import re
    pattern = r"with patch\.object\(sys,\s*\"argv\",\s*test_args\):\s+with pytest\.raises\((.*?)\):\s+main\(\)"
    replacement_re = r"with patch.object(sys, \"argv\", test_args), pytest.raises(\1):\n        main()"
    content, count = re.subn(pattern, replacement_re, content)
    if count > 0:
        open(path, "w", encoding="utf-8").write(content)
        print(f"SUCCESS: Successfully patched {count} occurrence(s) via regex.")
    else:
        print("ERROR: Failed to locate target pattern for SIM117 remediation.")
        exit(1)
'

echo "=== 4. POST-REPAIR AUDIT: Verifying updated source code segment ==="
sed -n '255,275p' tests/test_main.py | cat -n

echo "=== 5. VERIFICATION: Running Ruff check to confirm clean status ==="
ruff check src tests
echo "🎯 Forensic audit and automated remediation completed successfully!"