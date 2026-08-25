# src/processor/generate_cover.py
import os
from pathlib import Path

def run(state=None):
    """
    Generates magazine_cover.html from the cover template, substituting metadata fields
    from state inputs/config or fallback defaults.
    """
    if state and hasattr(state, "book_to_publish_dir"):
        output_dir = Path(state.book_to_publish_dir)
    else:
        github_workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
        output_dir = Path("data/testing-input-output/book_to_publish")

    output_dir.mkdir(parents=True, exist_ok=True)
    cover_html_path = output_dir / "magazine_cover.html"

    # Extract metadata from state inputs/config or use robust defaults
    title = "Artistic Landscapes"
    issue = "Issue No. 1"
    tagline = "AI-Generated Visual Poetry"
    subtitle = "Exploring algorithmic synthesis and modern aesthetics"
    author = "Dmitrii Zavalin"

    if state:
        if hasattr(state, "inputs") and isinstance(state.inputs, dict):
            title = state.inputs.get("title", title)
            issue = state.inputs.get("issue", issue)
            tagline = state.inputs.get("tagline", tagline)
            subtitle = state.inputs.get("subtitle", subtitle)
            author = state.inputs.get("author", author)
        elif hasattr(state, "config") and isinstance(state.config, dict):
            title = state.config.get("title", title)
            issue = state.config.get("issue", issue)
            tagline = state.config.get("tagline", tagline)
            subtitle = state.config.get("subtitle", subtitle)
            author = state.config.get("author", author)

    # Read template file or use fallback string
    template_path = Path("src/processor/cover_template.html")
    if template_path.exists():
        html_content = template_path.read_text(encoding="utf-8")
    else:
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
    print(f"✅ Magazine cover HTML generated: {cover_html_path}")

    if state:
        if not hasattr(state, "results") or state.results is None:
            state.results = {}
        state.results["magazine_cover_path"] = str(cover_html_path)

if __name__ == "__main__":
    run()
