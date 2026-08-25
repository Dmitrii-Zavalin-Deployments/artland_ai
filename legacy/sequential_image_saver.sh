#!/bin/bash

# Define source and destination directories
SOURCE_DIR="converted_sketches"
DEST_DIR="book_compilation"
FILENAME="proportional_whitened_edges_painting.jpg"

# Ensure the destination directory exists
mkdir -p "$DEST_DIR"

# Find the highest numbered file in the destination directory
highest_num=$(ls "$DEST_DIR" 2>/dev/null | grep -E '^[0-9]+\.jpg$' | sed 's/\.jpg//' | sort -n | tail -n 1)

# Determine the next available number
if [[ -z "$highest_num" ]]; then
    next_num=1  # Start numbering from 1 if the directory is empty
else
    next_num=$((highest_num + 1))
fi

# Copy the file and rename it
cp "$SOURCE_DIR/$FILENAME" "$DEST_DIR/$next_num.jpg"

echo "File copied and saved as $next_num.jpg in $DEST_DIR"



