#!/usr/bin/env bash
# ==============================================================================
# Forensic Audit & Automated Remediation Script for No-Default Policy Image Error
# ==============================================================================
set -euo pipefail

echo "=== 2. SMOKING-GUN SOURCE AUDIT: Inspecting zip archive contents in tests/test_main.py ==="
grep -n -C 6 "ZipFile" tests/test_main.py | cat -n

echo "=== 3. AUTOMATED REMEDIATION: Replacing sample.txt with a valid minimal PNG frame in dummy.zip ==="
python3 -c '
path = "tests/test_main.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Target block writing sample.txt into dummy.zip
old_zip_code = """    with zipfile.ZipFile(dummy_zip, "w") as zf:
        zf.writestr("sample.txt", "data")"""

# Replacement writing a valid minimal 1x1 PNG frame accepted by frames_loader
new_zip_code = """    with zipfile.ZipFile(dummy_zip, "w") as zf:
        png_bytes = b"\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x06\\x00\\x00\\x00\\x1f\\x15c4\\x00\\x00\\x00\\nIDATx\\x9cc\\x00\\x01\\x00\\x00\\x05\\x00\\x01\\r\\n-\\xb4\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82"
        zf.writestr("frame_01.png", png_bytes)"""

if old_zip_code in content:
    content = content.replace(old_zip_code, new_zip_code)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Successfully injected valid PNG frame into dummy.zip creation.")
else:
    print("WARNING: Exact zip block pattern not matched. Attempting broader regex replacement...")
    import re
    pattern = r"with zipfile\.ZipFile\(dummy_zip,\s*\"w\"\)\s+as\s+zf:\s+zf\.writestr\([^)]+\)"
    replacement = "with zipfile.ZipFile(dummy_zip, \"w\") as zf:\n        png_bytes = b\"\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x06\\x00\\x00\\x00\\x1f\\x15c4\\x00\\x00\\x00\\nIDATx\\x9cc\\x00\\x01\\x00\\x00\\x05\\x00\\x01\\r\\n-\\xb4\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82\"\n        zf.writestr(\"frame_01.png\", png_bytes)"
    content, count = re.subn(pattern, replacement, content)
    if count > 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"SUCCESS: Replaced {count} zip fixture occurrence(s) via regex.")
    else:
        print("ERROR: Failed to locate zip fixture block.")
        exit(1)
'

echo "=== 4. POST-REPAIR AUDIT: Verifying updated test code segment ==="
grep -n -C 6 "frame_01.png" tests/test_main.py | cat -n

echo "🎯 Forensic audit, remediation, and verification completed successfully!"