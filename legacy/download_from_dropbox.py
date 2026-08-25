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

# Function to delete all files in a specific Dropbox folder
def delete_all_files_in_folder(dbx, folder_path, log_file):
    try:
        result = dbx.files_list_folder(folder_path)
        for entry in result.entries:
            dbx.files_delete_v2(entry.path_lower)
            log_file.write(f"Deleted file: {entry.path_lower}\n")
            print(f"Deleted file: {entry.path_lower}")  # Print to GitHub Actions logs
    except dropbox.exceptions.ApiError as e:
        log_file.write(f"Failed to delete files in {folder_path}, error: {e}\n")
        print(f"Failed to delete files in {folder_path}, error: {e}")  # Log error

# Function to download JPG images from a specified Dropbox folder and delete them afterwards
def download_jpgs_from_dropbox(dropbox_folder, local_folder, refresh_token, client_id, client_secret, log_file_path):
    # Ensure dropbox_folder path starts with '/'
    if not dropbox_folder.startswith('/'):
        dropbox_folder = f"/{dropbox_folder}"

    # Refresh the access token
    access_token = refresh_access_token(refresh_token, client_id, client_secret)
    dbx = dropbox.Dropbox(access_token)

    with open(log_file_path, "a") as log_file:
        log_file.write("Starting download process for JPG files...\n")
        try:
            os.makedirs(local_folder, exist_ok=True)

            # Handle pagination
            has_more = True
            cursor = None
            while has_more:
                if cursor:
                    result = dbx.files_list_folder_continue(cursor)
                else:
                    result = dbx.files_list_folder(dropbox_folder)
                log_file.write(f"Listing files in Dropbox folder: {dropbox_folder}\n")

                for entry in result.entries:
                    if isinstance(entry, dropbox.files.FileMetadata) and entry.name.lower().endswith('.jpg'):
                        local_path = os.path.join(local_folder, entry.name)
                        with open(local_path, "wb") as f:
                            metadata, res = dbx.files_download(path=entry.path_lower)
                            f.write(res.content)
                        log_file.write(f"Downloaded {entry.name} to {local_path}\n")
                        print(entry.name)  # Print only the name of the downloaded file to GitHub Actions logs

                        # Delete the file from Dropbox after downloading
                        dbx.files_delete_v2(entry.path_lower)
                        log_file.write(f"Deleted {entry.path_lower}\n")
                        print(f"Deleted {entry.path_lower}")

                has_more = result.has_more
                cursor = result.cursor

            log_file.write("Download and delete process for JPG files completed successfully.\n")

            # **Now delete all files from the specified Dropbox folders**
            folders_to_clear = [
                "/artland_ai/book_compilation",
                "/artland_ai/book_to_publish",
                "/artland_ai/converted_sketches"
            ]
            for folder in folders_to_clear:
                delete_all_files_in_folder(dbx, folder, log_file)
                log_file.write(f"✅ All files in {folder} have been deleted.\n")
                print(f"✅ All files in {folder} have been deleted.")

        except dropbox.exceptions.ApiError as err:
            log_file.write(f"Error downloading files: {err}\n")
            print(f"Error downloading files: {err}")  # Log error
        except Exception as e:
            log_file.write(f"Unexpected error: {e}\n")
            print(f"Unexpected error: {e}")  # Log error

# Entry point for the script
if __name__ == "__main__":
    # Validate command-line arguments
    if len(sys.argv) < 7:
        print("[ERROR] Missing required arguments! Expected format:")
        print("python3 download_from_dropbox.py <dropbox_folder> <local_folder> <refresh_token> <client_id> <client_secret> <log_file>")
        sys.exit(1)  # Exit to prevent further errors

    # Read command-line arguments
    dropbox_folder = sys.argv[1]  # Dropbox folder path
    local_folder = sys.argv[2]  # Local folder path
    refresh_token = sys.argv[3]  # Dropbox refresh token
    client_id = sys.argv[4]  # Dropbox client ID
    client_secret = sys.argv[5]  # Dropbox client secret
    log_file_path = sys.argv[6]  # Path to the log file

    # Call the function to download JPGs
    download_jpgs_from_dropbox(dropbox_folder, local_folder, refresh_token, client_id, client_secret, log_file_path)



