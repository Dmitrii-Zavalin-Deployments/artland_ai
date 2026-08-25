#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: Missing artistic_painting_processor.py"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Locating processor files and references ---"
find . -name "*processor*" -o -name "*painting*" || true
echo "Searching for references to artistic_painting_processor:"
grep -rn "artistic_painting_processor" . || true

echo -e "\n--- 2. Smoking-Gun Source Audit: Inspecting workflow or caller files ---"
WORKFLOW_DIR=".github/workflows"
if [ -d "$WORKFLOW_DIR" ]; then
    echo "Inspecting workflows for references:"
    for f in "$WORKFLOW_DIR"/*.yml; do
        if [ -f "$f" ]; then
            echo "--- $f ---"
            cat -n "$f" | grep -C 3 "artistic_painting_processor" || true
        fi
    done
else
    echo "⚠️ Workflow directory not found."
fi
