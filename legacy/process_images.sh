#!/bin/bash

# Define directories
SOURCE_DIR="google_photo_albums"
DEST_DIR="original_photos"
PROCESSED_DIR="processed_images"
TEMP_FILE="photo.jpg"

# Ensure the directories exist
mkdir -p "$DEST_DIR"
mkdir -p "$PROCESSED_DIR"

# Check for .jpg files
jpg_files=( "$SOURCE_DIR"/*.jpg )

if [[ ${#jpg_files[@]} -eq 0 ]]; then
    echo "[ERROR] No .jpg files found in $SOURCE_DIR. Please convert non-JPG files to JPG format."
    exit 1
fi

# Process each .jpg file
for file in "${jpg_files[@]}"; do
    echo "Processing: $file"

    # Move and rename the file
    mv "$file" "$DEST_DIR/$TEMP_FILE"

    # Run the processing steps
    python3 artistic_painting_processor.py
    python3 add_fading_edges.py

    # Run sequential image saver
    chmod +x sequential_image_saver.sh
    ./sequential_image_saver.sh

    # Move processed image to prevent duplicate processing
    mv "$DEST_DIR/$TEMP_FILE" "$PROCESSED_DIR/$(basename "$file")"

    echo "Finished processing: $file"
done

echo "[INFO] All images processed successfully!"



