import os


def make_path(*file_path):
    """Make a file path as though this file's directory is a root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *file_path))
