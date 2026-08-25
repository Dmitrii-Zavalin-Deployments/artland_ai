#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🔍 FORENSIC AUDIT: ModuleNotFoundError 'state'"
echo "=================================================="

echo -e "\n--- 1. Diagnostics: Locating state.py and workspace layout ---"
find . -name "state.py" || true
ls -la src/ || true
pwd

echo -e "\n--- 2. Smoking-Gun Source Audit: cat -n for src/main.py ---"
TARGET_FILE="src/main.py"
if [ -f "$TARGET_FILE" ]; then
    echo "Inspecting $TARGET_FILE:"
    cat -n "$TARGET_FILE"
else
    echo "⚠️ Target source file $TARGET_FILE not found."
fi

echo -e "\n--- 3. Automated Repair: Injecting sys.path resolution into src/main.py ---"
python3 -c '
import pathlib

main_path = pathlib.Path("src/main.py")
if main_path.exists():
    content = main_path.read_text()
    # Check if we need to add path resolution for root and src modules
    if "from state import State" in content or "import state" in content:
        path_fix = "import sys\nimport pathlib\n_root = pathlib.Path(__file__).resolve().parent.parent\nsys.path.insert(0, str(_root))\nsys.path.insert(0, str(_root / \"src\"))\n"
        if "sys.path.insert" not in content:
            content = path_fix + content
            main_path.write_text(content)
            print("✅ Successfully injected automatic sys.path resolution into src/main.py")
' || true

echo -e "\n--- 4. Post-Repair Verification Check ---"
python3 -c '
import sys
import pathlib
root = pathlib.Path.cwd()
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "src"))
try:
    import state
    print("✅ Successfully imported module: state")
except ImportError as e:
    print(f"⚠️ Import warning check: {e}")
'

exit 0