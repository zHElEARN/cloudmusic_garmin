import requests
import json
import os

from config import *
import utils


def login(username, password):
    login_request = requests.get(
        f"{config['api_url']}login/cellphone",
        params={"phone": username, "password": password},
        headers=config["headers"],
        proxies=config["proxies"],
        verify=False,
    )

    decoded_response = json.loads(login_request.text)
    code = decoded_response["code"]

    if code != 200:
        return code, decoded_response["msg" if "msg" in decoded_response else "message"]

    return code, decoded_response["profile"]["nickname"], login_request.cookies, decoded_response["profile"]["userId"]


def check_login_status(cookies):
    encoded_cookies = requests.utils.cookiejar_from_dict(cookies)

    status_request = requests.get(
        f"{config['api_url']}login/status", headers=config["headers"], proxies=config["proxies"], cookies=encoded_cookies, verify=False,
    )

    decoded_response = json.loads(status_request.text)

    if decoded_response["data"]["account"]["status"] == 0:
        return True, decoded_response["data"]["profile"]["nickname"], encoded_cookies, decoded_response["data"]["profile"]["userId"]

    return False, "", None, None


def get_user_playlist(uid, cookies):
    created_playlist = []
    collected_playlist = []

    playlist_request = requests.get(
        f"{config['api_url']}user/playlist",
        params={"uid": uid},
        headers=config["headers"],
        proxies=config["proxies"],
        cookies=cookies,
        verify=False,
    )

    decoded_response = json.loads(playlist_request.text)

    for value in decoded_response["playlist"]:
        if value["creator"]["userId"] == uid:
            created_playlist.append(value)
        else:
            collected_playlist.append(value)

    return created_playlist, collected_playlist


def get_playlist_tracks(playlist_id, cookies):
    tracks_request = requests.get(
        f"{config['api_url']}playlist/track/all",
        params={"id": playlist_id},
        headers=config["headers"],
        proxies=config["proxies"],
        cookies=cookies,
        verify=False,
    )

    decoded_response = json.loads(tracks_request.text)
    return decoded_response["songs"]


def download_track(track, cookies, br, path, local_path):
    filename = ""
    artist_list = []

    # cloud storage music
    if "pc" in track:
        filename = track["pc"]["fn"]
    else:
        artist_list.extend(ar["name"] for ar in track["ar"])
        filename = track["name"] + " - " + ",".join(artist_list)

    music_filename = path + utils.valid_filename(filename) + (".mp3" if "pc" not in track else "")
    cover_filename = local_path + utils.valid_filename(filename) + ".jpg"

    if os.path.exists(music_filename):
        return "exist", (utils.valid_filename(filename) + (".mp3" if "pc" not in track else ""))

    track_request = requests.get(
        f"{config['api_url']}song/download/url",
        params={"id": track["id"], "br": br},
        headers=config["headers"],
        proxies=config["proxies"],
        cookies=cookies,
        verify=False,
    )

    decoded_response = json.loads(track_request.text)
    if decoded_response["data"]["url"] is None:
        return "failed", f"{utils.valid_filename(filename)}.mp3"

    utils.download_file(decoded_response["data"]["url"], music_filename, config)

    # if the music is cloud stroage music, it is not processed
    # otherwise, need to manually add the id3v2 label
    if "pc" not in track:
        utils.download_file(track["al"]["picUrl"], cover_filename, config)

        utils.config_music(
            music_filename, {"title": track["name"], "artists": artist_list, "album": track["al"]["name"], "cover": cover_filename}
        )

    return "success", (utils.valid_filename(filename) + (".mp3" if "pc" not in track else ""))


def check_music(ids):
    check_request = requests.get(
        f"{config['api_url']}check/music", headers=config["headers"], proxies=config["proxies"], verify=False, params={ids: ",".join(ids)},
    )

    decoded_response = json.loads(check_request.text)
    return decoded_response["message"]

