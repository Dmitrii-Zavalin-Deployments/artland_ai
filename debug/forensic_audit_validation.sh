#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: Missing book_to_publish/photo_collection.pdf"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Checking book_to_publish and book_compilation directories ---"
find . -name "*pdf*" || true
ls -la data/testing-input-output/book_to_publish/ || true
ls -la data/testing-input-output/book_compilation/ || true

echo -e "\n--- 2. Smoking-Gun Source Audit: cat -n for generate_photo_pdf.py ---"
PDF_SCRIPT="generate_photo_pdf.py"
if [ -f "$PDF_SCRIPT" ]; then
    echo "Inspecting $PDF_SCRIPT:"
    cat -n "$PDF_SCRIPT"
else
    echo "⚠️ $PDF_SCRIPT not found in root. Checking src/processor/"
    if [ -f "src/processor/generate_photo_pdf.py" ]; then
        cat -n "src/processor/generate_photo_pdf.py"
    fi
fi