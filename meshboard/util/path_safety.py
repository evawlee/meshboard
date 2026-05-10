import os


def safe_join(root, user_path):
    root_abs = os.path.abspath(root)
    candidate = os.path.abspath(os.path.join(root_abs, user_path))
    if not candidate.startswith(root_abs + os.sep) and candidate != root_abs:
        raise ValueError("path escapes root")
    return candidate
