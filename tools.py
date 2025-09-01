import os


def path_smart_shorten(path:str) -> str:
    home_path = os.path.expanduser("~")
    cwd = os.getcwd()

    if path.startswith(home_path):
        tilde_path = path.replace(home_path, "~", 1)
    else:
        tilde_path = path

    try:
        rel_path = os.path.relpath(path, cwd)
    except ValueError:
        rel_path = path  # Falls z. B. Laufwerkswechsel unter Windows

    return rel_path if len(rel_path) < len(tilde_path) else tilde_path