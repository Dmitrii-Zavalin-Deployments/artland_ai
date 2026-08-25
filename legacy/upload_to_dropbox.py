import dropbox
import os
import requests
import sys

# Function to refresh the access token
def refresh_access_token(refresh_token, client_id, client_secret):
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to refresh access token")

# Function to upload a file to Dropbox
def upload_file_to_dropbox(local_file_path, dropbox_file_path, refresh_token, client_id, client_secret):
    # Refresh the access token
    access_token = refresh_access_token(refresh_token, client_id, client_secret)
    dbx = dropbox.Dropbox(access_token)

    try:
        with open(local_file_path, "rb") as f:
            dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode.overwrite)
        print(f"✅ Uploaded file to Dropbox: {dropbox_file_path}")
    except Exception as e:
        print(f"❌ Failed to upload file to Dropbox: {e}")

# Function to upload all files from a local directory to Dropbox
def upload_directory(local_directory, dropbox_folder, refresh_token, client_id, client_secret):
    # Check if the local directory exists
    if not os.path.isdir(local_directory):
        print(f"[ERROR] Directory '{local_directory}' does not exist.")
        sys.exit(1)

    # Iterate through all files in the directory and upload them
    for file_name in os.listdir(local_directory):
        local_file_path = os.path.join(local_directory, file_name)
        dropbox_file_path = f"{dropbox_folder}/{file_name}"

        # Ensure it's a file (not a subdirectory)
        if os.path.isfile(local_file_path):
            upload_file_to_dropbox(local_file_path, dropbox_file_path, refresh_token, client_id, client_secret)

    print(f"[INFO] ✅ All files from '{local_directory}' have been uploaded to Dropbox.")

# Entry point for the script
if __name__ == "__main__":
    # Command-line arguments
    refresh_token = sys.argv[1]      # Dropbox refresh token
    client_id = sys.argv[2]          # Dropbox client ID
    client_secret = sys.argv[3]      # Dropbox client secret

    # Upload files from 'converted_sketches'
    upload_directory("converted_sketches", "/artland_ai/converted_sketches", refresh_token, client_id, client_secret)

    # Upload files from 'book_compilation'
    upload_directory("book_compilation", "/artland_ai/book_compilation", refresh_token, client_id, client_secret)

    # Upload files from 'book_to_publish' (NEW ADDITION!)
    upload_directory("book_to_publish", "/artland_ai/book_to_publish", refresh_token, client_id, client_secret)



