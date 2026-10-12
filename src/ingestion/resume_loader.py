import os


def load_resume(path):
    """Read a resume from disk and return its text.

    Raises FileNotFoundError when the path does not exist, which the console
    interface reports instead of crashing.
    """
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def list_resumes(directory):
    """Return the sorted names of the .txt resumes held in a directory.

    Returns an empty list when the directory does not exist.
    """
    if not os.path.isdir(directory):
        return []
    return sorted(name for name in os.listdir(directory)
                  if name.endswith(".txt"))