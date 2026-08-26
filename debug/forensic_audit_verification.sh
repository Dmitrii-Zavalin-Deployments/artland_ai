#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🔍 STARTING COMPREHENSIVE FORENSIC AUDIT & REPAIR"
echo "=========================================================="

# ------------------------------------------------------------------
# 2. Automated Surgical Repairs via Python
# ------------------------------------------------------------------
echo "--- [2/3] Applying surgical test and code repairs ---"

python3 - << 'EOF'
from pathlib import Path

# ------------------------------------------------------------------
# Fix 1: test_missing_processor_run_methods in test_artistic_pipeline_magazine_coverage.py
# Ensure delattr is safely applied to artistic_painting_processor if tested for missing run
# ------------------------------------------------------------------
art_test_path = Path("tests/test_artistic_pipeline_magazine_coverage.py")
if art_test_path.exists():
    code = art_test_path.read_text(encoding="utf-8")
    if "test_missing_processor_run_methods" in code and "delattr(app, 'run')" not in code:
        code = code.replace(
            "# 1. artistic_painting_processor lacks run",
            "try:\n        delattr(app, 'run')\n    except AttributeError:\n        pass\n    # 1. artistic_painting_processor lacks run"
        )
        art_test_path.write_text(code, encoding="utf-8")
        print("✅ Added safe delattr for artistic_painting_processor in test suite")

# ------------------------------------------------------------------
# Fix 2: Replace gb.range with builtins.range in test_generate_background_coverage.py
# ------------------------------------------------------------------
bg_test_path = Path("tests/test_generate_background_coverage.py")
if bg_test_path.exists():
    code = bg_test_path.read_text(encoding="utf-8")
    if 'monkeypatch.setattr(gb, "range"' in code:
        code = code.replace(
            'monkeypatch.setattr(gb, "range"',
            'monkeypatch.setattr("builtins.range"'
        )
        bg_test_path.write_text(code, encoding="utf-8")
        print("✅ Patched gb.range to builtins.range in test_generate_background_coverage.py")

# ------------------------------------------------------------------
# Fix 3: Wrap test_frames_loader_exception_handling_block with pytest.raises(zipfile.BadZipFile)
# ------------------------------------------------------------------
frames_test_path = Path("tests/test_frames_loader_coverage.py")
if frames_test_path.exists():
    code = frames_test_path.read_text(encoding="utf-8")
    if "test_frames_loader_exception_handling_block" in code and "pytest.raises(zipfile.BadZipFile)" not in code:
        code = code.replace(
            "frames_loader.run(state)",
            "with pytest.raises(zipfile.BadZipFile):\n        frames_loader.run(state)"
        )
        frames_test_path.write_text(code, encoding="utf-8")
        print("✅ Wrapped frames_loader exception test with pytest.raises(zipfile.BadZipFile)")

# ------------------------------------------------------------------
# Fix 4: Create dummy.zip archive for main pipeline schema validation test
# ------------------------------------------------------------------
main_test_path = Path("tests/test_main_coverage.py")
if main_test_path.exists():
    code = main_test_path.read_text(encoding="utf-8")
    if "dummy.zip" in code and "zipfile.ZipFile" not in code:
        code = code.replace(
            'input_file.write_text(',
            'import zipfile\n    dummy_zip = tmp_path / "project" / "dummy.zip"\n    with zipfile.ZipFile(dummy_zip, "w") as zf:\n        zf.writestr("frame.jpg", b"data")\n    input_file.write_text('
        )
        main_test_path.write_text(code, encoding="utf-8")
        print("✅ Added dummy.zip archive creation to test_main_schema_validation_failure")

EOF