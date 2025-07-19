import os
from pathlib import Path

# Define upload path
UPLOAD_FOLDER = Path("data/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def save_uploaded_files(uploaded_files):
    saved_paths = []

    for file in uploaded_files:
        # Define path to save the file
        save_path = UPLOAD_FOLDER / file.name

        # Save the file to disk
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())
        
        saved_paths.append(str(save_path))

    return saved_paths
