from __future__ import annotations
import logging
import os
import zipfile
from virtualenv.info import IS_WIN, ROOT

def extract(filename, dest):
    """Extract a zip file to a destination directory."""
    if not os.path.exists(dest):
        os.makedirs(dest)
    with zipfile.ZipFile(filename) as zip_file:
        for info in zip_file.infolist():
            name = info.filename
            # Skip directories
            if name.endswith('/'):
                continue
            # Convert forward slashes to backslashes on Windows
            if IS_WIN:
                name = name.replace('/', os.sep)
            target = os.path.join(dest, name)
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(target), exist_ok=True)
            # Extract the file
            with zip_file.open(info) as source, open(target, 'wb') as target_file:
                target_file.write(source.read())

def read(filename):
    """Read a file from a zip file."""
    if os.path.isfile(filename):
        with open(filename, 'rb') as file_obj:
            return file_obj.read()
    # If not a file, try to read from zip
    zip_path = os.path.dirname(filename)
    while zip_path and not os.path.isfile(zip_path):
        zip_path = os.path.dirname(zip_path)
    if not zip_path:
        return None
    rel_path = os.path.relpath(filename, zip_path)
    try:
        with zipfile.ZipFile(zip_path) as zip_file:
            return zip_file.read(rel_path.replace(os.sep, '/'))
    except (KeyError, zipfile.BadZipFile):
        return None

__all__ = ['extract', 'read']