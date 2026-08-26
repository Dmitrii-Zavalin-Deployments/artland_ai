# src/processor/generate_cover.py
import json
import logging
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)


def get_extreme_colors(image_path):
    """
    Scans the background image to find absolute lightest and darkest pixels
    using standard perceptual luminance formulas.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        # Resize to a small thumbnail for instant pixel sampling
        img_thumbnail = img.resize((150, 150))
        pixels = list(img_thumbnail.getdata())

        if not pixels:
            return "rgb(255, 255, 255)", "rgb(0, 0, 0)"

        # Perceptual luminance calculation
        def luminance(p):
            return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]

        lightest_pixel = max(pixels, key=luminance)
        darkest_pixel = min(pixels, key=luminance)

        lightest_css = f"rgb({lightest_pixel[0]}, {lightest_pixel[1]}, {lightest_pixel[2]})"
        darkest_css = f"rgb({darkest_pixel[0]}, {darkest_pixel[1]}, {darkest_pixel[2]})"

        logger.info(
            f"🎨 Sampled background extremes from {image_path} -> Lightest: {lightest_css}, Darkest: {darkest_css}"
        )

        return lightest_css, darkest_css
    except Exception as e:
        logger.warning(
            f"Could not sample image colors: {e}. Falling back to default high-contrast theme."
        )
        return "rgb(255, 255, 255)", "rgb(0, 0, 0)"


def run(state=None):
    """
    Generates magazine_cover.html using an elegant, professional layout structured 
    with dynamic background-adaptive text styling, substituting metadata fields strictly 
    from pipeline state or config (No-Default Policy enforcement).
    """
    logger.info("Starting generate_cover execution.")
    output_dir = Path("data/testing-input-output/book_to_publish")
    if state and hasattr(state, "book_to_publish_dir"):
        output_dir = Path(state.book_to_publish_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    cover_html_path = output_dir / "magazine_cover.html"

    # Extract metadata with No-Default Policy enforcement
    title = None
    issue = None
    tagline = None
    subtitle = None
    author = None

    if state:
        # 1. Check state.inputs
        if hasattr(state, "inputs") and isinstance(state.inputs, dict):
            title = title or state.inputs.get("title")
            issue = issue or state.inputs.get("issue")
            tagline = tagline or state.inputs.get("tagline")
            subtitle = subtitle or state.inputs.get("subtitle")
            author = author or state.inputs.get("author")

        # 2. Check state.config (supporting nested "magazine_cover" block and flat config)
        if hasattr(state, "config") and isinstance(state.config, dict):
            mag_cfg = state.config.get("magazine_cover", {})
            if isinstance(mag_cfg, dict):
                title = title or mag_cfg.get("title")
                issue = issue or mag_cfg.get("issue")
                tagline = tagline or mag_cfg.get("tagline")
                subtitle = subtitle or mag_cfg.get("subtitle")
                author = author or mag_cfg.get("author")
            
            title = title or state.config.get("title")
            issue = issue or state.config.get("issue")
            tagline = tagline or state.config.get("tagline")
            subtitle = subtitle or state.config.get("subtitle")
            author = author or state.config.get("author")

    # Enforce No-Default Policy: Raise deterministic error if any required metadata is missing
    missing_meta = [k for k, v in [
        ("title", title), 
        ("issue", issue), 
        ("tagline", tagline), 
        ("subtitle", subtitle), 
        ("author", author)
    ] if not v]

    if missing_meta:
        raise ValueError(
            f"❌ NO-DEFAULT POLICY VIOLATION: Required magazine_cover metadata fields missing from inputs/config: {missing_meta}. "
            f"No default values allowed."
        )

    # Dynamically extract extreme colors from the background image if available
    bg_image_path = output_dir / "cover_background.jpg"
    if bg_image_path.exists():
        lightest_color, darkest_color = get_extreme_colors(bg_image_path)
    else:
        lightest_color, darkest_color = "rgb(255, 255, 255)", "rgb(0, 0, 0)"

    # Internal HTML template using professional layout hierarchy and dynamic color-adaptive text styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Magazine Cover</title>
    <style>
        body {{
            background: url("cover_background.jpg") no-repeat center center fixed;
            background-size: cover;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            box-sizing: border-box;
            padding: 60px 40px;
            text-align: center;
        }}
        .author {{
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: {lightest_color};
            -webkit-text-stroke: 0.5px {darkest_color};
            text-shadow: 1px 1px 3px {darkest_color};
        }}
        .center-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: auto 0;
            max-width: 900px;
        }}
        .tagline {{
            font-size: 18px;
            font-style: italic;
            letter-spacing: 1px;
            margin-bottom: 15px;
            color: {lightest_color};
            -webkit-text-stroke: 1px {darkest_color};
            text-shadow: 2px 2px 4px {darkest_color};
        }}
        .title {{
            font-size: 64px;
            font-weight: 800;
            text-transform: uppercase;
            line-height: 1.1;
            letter-spacing: 2px;
            margin-bottom: 16px;
            color: {lightest_color};
            -webkit-text-stroke: 2px {darkest_color};
            text-shadow: 3px 3px 8px {darkest_color};
        }}
        .subtitle {{
            font-size: 22px;
            font-weight: 400;
            line-height: 1.4;
            max-width: 800px;
            color: {lightest_color};
            -webkit-text-stroke: 0.75px {darkest_color};
            text-shadow: 1px 1px 4px {darkest_color};
        }}
        .issue {{
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: {lightest_color};
            -webkit-text-stroke: 1px {darkest_color};
            text-shadow: 2px 2px 4px {darkest_color};
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="author">By {author}</div>
        <div class="center-content">
            <div class="tagline">{tagline}</div>
            <div class="title">{title}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
        <div class="issue">{issue}</div>
    </div>
</body>
</html>"""

    # Perform placeholder replacements
    rendered_html = html_content.replace("{TITLE}", str(title)) \
                                .replace("{ISSUE}", str(issue)) \
                                .replace("{TAGLINE}", str(tagline)) \
                                .replace("{SUBTITLE}", str(subtitle)) \
                                .replace("{AUTHOR}", str(author))

    cover_html_path.write_text(rendered_html, encoding="utf-8")
    logger.info("✅ Magazine cover HTML generated with dynamic text color adjustments: %s", cover_html_path)

    if state:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["magazine_cover_path"] = str(cover_html_path)


def main():
    # Production direct execution loading real config from disk
    class ProductionRuntimeState:
        def __init__(self):
            self.book_to_publish_dir = "data/testing-input-output/book_to_publish"
            config_file = Path("config/config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                raise FileNotFoundError(f"Production config not found at {config_file}")

    run(ProductionRuntimeState())


if __name__ == "__main__":  # pragma: no cover
    main()