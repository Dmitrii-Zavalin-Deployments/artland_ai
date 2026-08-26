# src/processor/generate_cover.py
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def run(state=None):
    """
    Generates magazine_cover.html from the cover template, substituting metadata fields
    strictly from pipeline state or config (No-Default Policy enforcement).
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

    # Read template file or use fallback HTML structure
    template_path = Path("src/processor/cover_template.html")
    if template_path.exists():
        logger.debug("Reading cover template from: %s", template_path)
        html_content = template_path.read_text(encoding="utf-8")
    else:
        logger.warning("⚠️ Template file not found at %s. Using default fallback HTML structure.", template_path)
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Magazine Cover</title>
    <style>
        body {
            background: url("cover_background.jpg") no-repeat center center fixed;
            background-size: cover;
            font-family: Arial, sans-serif;
            color: white;
            text-align: center;
            padding: 50px;
        }
        .container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .title { font-size: 50px; font-weight: bold; text-transform: uppercase; }
        .issue { font-size: 25px; margin-top: 10px; }
        .tagline { font-size: 20px; font-style: italic; margin-top: 15px; }
        .subtitle { font-size: 18px; margin-top: 10px; opacity: 0.8; }
        .author { font-size: 18px; margin-top: 20px; opacity: 0.7; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="title">{TITLE}</div>
        <div class="issue">{ISSUE}</div>
        <div class="tagline">{TAGLINE}</div>
        <div class="subtitle">{SUBTITLE}</div>
        <div class="author">{AUTHOR}</div>
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
    logger.info("✅ Magazine cover HTML generated: %s", cover_html_path)

    if state:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["magazine_cover_path"] = str(cover_html_path)


if __name__ == "__main__":
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
