import os

def create_script(filename, content):
    """Writes the script content into a file."""
    with open(filename, "w") as f:
        f.write(content)

    print(f"[INFO] {filename} created successfully.")

# Get script contents from environment variables
artistic_painting_code = os.getenv("ARTISTIC_PAINTING_PROCESSOR", "# No data found")
fading_edges_code = os.getenv("ADD_FADING_EDGES", "# No data found")

# Create the Python files
create_script("artistic_painting_processor.py", artistic_painting_code)
create_script("add_fading_edges.py", fading_edges_code)



