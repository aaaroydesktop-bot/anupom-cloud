import os
import uuid
import shutil

UPLOAD_DIR = "uploads"

def save_file(upload_file, sender):

    user_folder = os.path.join(UPLOAD_DIR, sender)
    os.makedirs(user_folder, exist_ok=True)

    unique_name = str(uuid.uuid4()) + "_" + upload_file.filename
    file_path = os.path.join(user_folder, unique_name)

    # ⭐ chunk writing (BIG FILE SUPPORT)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return unique_name


def get_file(sender, filename):
    return os.path.join(UPLOAD_DIR, sender, filename)
