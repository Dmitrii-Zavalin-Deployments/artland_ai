import json
import sys
import warnings
from pathlib import Path

import pytest

# Automatically suppress scikit-image low-contrast warnings in test suite
warnings.filterwarnings("ignore", category=UserWarning, message=".*is a low contrast image.*")

# Ensure 'src' is in pythonpath for direct module imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def setup_pipeline_environment(tmp_path, monkeypatch):
    """Sets up required schemas, config files, working directory, and sys.path."""
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project_root)

    # 1. Create Schema Directory and Files
    schema_dir = project_root / "schema"
    schema_dir.mkdir(parents=True, exist_ok=True)
    
    permissive_schema = {"type": "object"}
    (schema_dir / "input_schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")
    (schema_dir / "config_schema.json").write_text(json.dumps(permissive_schema), encoding="utf-8")

    # 2. Create Config Directory and File with required parameters
    config_dir = project_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_data = {
        "artistic_painting": {
            "bilateral_d": 5,
            "sigma_color": 50.0,
            "sigma_space": 50.0,
            "canny_threshold1": 50,
            "canny_threshold2": 150,
            "depth_alpha": 1.0,
            "depth_beta": 0.0,
            "saturation_multiplier": 1.2,
            "brightness_multiplier": 1.0,
            "stylization_sigma_s": 60.0,
            "stylization_sigma_r": 0.4,
            "detail_sigma_s": 10.0,
            "detail_sigma_r": 0.15
        },
        "fading_edges": {
            "canvas_width": 200,
            "canvas_height": 200,
            "top_bottom_divisor": 4,
            "left_right_divisor": 4
        },
        "expand_image": {
            "scale_factor_y": 2,
            "num_repeats_x": 2
        },
        "generate_background": {
            "brightness_threshold": 50,
            "num_colors_per_image": 3,
            "gradient_width": 100,
            "gradient_height": 100,
            "fallback_colors": [[255, 255, 255], [200, 200, 200]]
        },
        "magazine_cover": {
            "title": "Artland Magazine",
            "issue": "Issue #1",
            "tagline": "Creative Visuals",
            "subtitle": "Special Edition",
            "author": "Pipeline Tester"
        }
    }
    (config_dir / "config.json").write_text(json.dumps(config_data, indent=2), encoding="utf-8")

    return project_root
