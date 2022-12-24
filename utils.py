from eyed3.id3.frames import ImageFrame
import os
import string
import eyed3
import requests

from config import config


def not_exist_makedirs(name):
    return None if os.path.exists(name) else os.makedirs(name)


def exist_remove(path):
    return os.remove(path) if os.path.exists(path) else None


# set the file name to valid
def valid_filename(filename):
    def half_to_full(uchar):
        inside_code = ord(uchar)
        if inside_code < 0x0020 or inside_code > 0x7E:
            return uchar
        if inside_code == 0x0020:
            inside_code = 0x3000
        else:
            inside_code += 0xFEE0
        return chr(inside_code)

    modified_filename = ""

    validFilenameChars = f"-_.() {string.ascii_letters}{string.digits}"
    for i in range(len(filename)):
        if filename[i] not in validFilenameChars:
            modified_filename += half_to_full(filename[i])
        else:
            modified_filename += filename[i]

    return modified_filename


def config_music(filename, info):
    audio = eyed3.load(filename)
    audio.initTag()
    audio.tag.title = info["title"]
    audio.tag.artist = "; ".join(info["artists"])
    audio.tag.album = info["album"]

    with open(info["cover"], "rb") as cover:
        audio.tag.images.set(ImageFrame.FRONT_COVER, cover.read(), "image/jpeg")
    audio.tag.save(encoding="utf-8")


def download_file(url, filename, config):
    r = requests.get(url, headers=config["headers"], proxies=config["proxies"], verify=False, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)


def save_session(session: str):
    with open(config["saved_authorizations"], "w") as f:
        f.write(session)


def load_sesion():
    with open(config["saved_authorizations"], "r") as f:
        return f.read()
