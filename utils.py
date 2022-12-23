import os


def not_exist_makedirs(name):
    if not os.path.exists(name):
        return os.makedirs(name)
    return None


def exist_remove(path):
    if os.path.exists(path):
        return os.remove(path)
    return None
