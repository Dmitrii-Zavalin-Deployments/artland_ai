#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: Missing original_photos.zip"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Searching for references to original_photos.zip ---"
grep -rn "original_photos.zip" . || true
ls -la data/testing-input-output/ || true

echo -e "\n--- 2. Smoking-Gun Source Audit: Inspecting test/verification scripts ---"
for test_script in test.sh run_tests.sh verify.sh .github/workflows/*.yml; do
    if [ -f "$test_script" ]; then
        echo "Inspecting $test_script:"
        cat -n "$test_script" | grep -C 3 "original_photos" || true
    fi
done
