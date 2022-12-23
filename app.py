import eyed3
import requests
import json
import os

from config import *
import utils

from eyed3.id3.frames import ImageFrame
from rich import progress

requests.packages.urllib3.disable_warnings()

ascii_logo = """
      _                 _                     _                                     _       
  ___| | ___  _   _  __| |_ __ ___  _   _ ___(_) ___      __ _  __ _ _ __ _ __ ___ (_)_ __  
 / __| |/ _ \| | | |/ _` | '_ ` _ \| | | / __| |/ __|    / _` |/ _` | '__| '_ ` _ \| | '_ \ 
| (__| | (_) | |_| | (_| | | | | | | |_| \__ \ | (__    | (_| | (_| | |  | | | | | | | | | |
 \___|_|\___/ \__,_|\__,_|_| |_| |_|\__,_|___/_|\___|____\__, |\__,_|_|  |_| |_| |_|_|_| |_|
                                                   |_____|___/                              
"""


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

    save_cookies("cookies.json", login_request.cookies)

    return code, decoded_response["profile"]["nickname"], login_request.cookies, decoded_response["profile"]["userId"]


def save_cookies(filename, cookies):
    with open(filename, "w") as f:
        f.write(json.dumps(requests.utils.dict_from_cookiejar(cookies)))


def check_login_status(cookies):
    encoded_cookies = requests.utils.cookiejar_from_dict(cookies)

    status_request = requests.get(
        f"{config['api_url']}login/status", headers=config["headers"], proxies=config["proxies"], cookies=encoded_cookies, verify=False,
    )

    decoded_response = json.loads(status_request.text)

    if decoded_response["data"]["account"]["status"] == 0:
        return True, decoded_response["data"]["profile"]["nickname"], encoded_cookies, decoded_response["data"]["profile"]["userId"]

    return False, "", None, None


def check_existed_cookie(filename):
    with open(filename, "r") as f:
        load_cookies = json.loads(f.read())

    return check_login_status(load_cookies)


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


def main():
    m_cookies = m_nickname = m_userid = None
    m_created_playlist = m_collected_playlist = []

    print(ascii_logo)

    utils.not_exist_makedirs(config["download_path"])
    utils.not_exist_makedirs(config["tempfile_path"])

    def password():
        nonlocal m_nickname, m_cookies, m_userid
        username = input("请输入您的用户名（手机号）：")
        password = input("请输入您的密码：")

        login_result = login(username, password)
        if login_result[0] != 200:
            print(f"登录失败，错误代码：{str(login_result[0])}，错误信息：{login_result[1]}")
            exit(-1)

        m_nickname, m_cookies, m_userid = login_result[1], login_result[2], login_result[3]

    if os.path.exists(config["saved_cookie"]):
        answer_playlist_type = input("检测到已缓存的Cookies，是否读取已缓存Cookies（Y/N)：")
        if answer_playlist_type in ["Y", "y"]:
            login_result = check_existed_cookie(config["saved_cookie"])
            if login_result[0] != True:
                print("登录失败，请尝试密码登录")
                return

            m_nickname, m_cookies, m_userid = login_result[1], login_result[2], login_result[3]
        else:
            password()
    else:
        password()

    print(f"登录成功，欢迎您，{m_nickname}")
    print("\n正在获取歌单信息......\n")

    m_created_playlist, m_collected_playlist = get_user_playlist(m_userid, m_cookies)

    print("请选择歌单类型：")
    print("    1. 用户创建的歌单（%d个）" % len(m_created_playlist))
    print("    2. 用户收藏的歌单（%d个）" % len(m_collected_playlist))

    answer_playlist_type = input("请输入歌单类型（数字）：")
    if answer_playlist_type not in ["1", "2"]:
        print("输入错误，请输入数字")
        return

    print("\n歌单列表：")

    playlists = m_created_playlist if answer_playlist_type == "1" else m_collected_playlist
    for i, value in enumerate(playlists, start=1):
        print("    %d：%s (%d)" % (i, value["name"], value["id"]))

    answer_playlist_id = input("请输入歌单序号（数字）：")
    playlist = playlists[int(answer_playlist_id) - 1]
    print(
        "\n歌单名称：%s 歌单ID：%d 歌曲数：%d 音乐云盘歌曲数：%d 创建者：%s"
        % (playlist["name"], playlist["id"], playlist["trackCount"], playlist["cloudTrackCount"], playlist["creator"]["nickname"])
    )

    answer_playlist_download = input("\n是否开始下载？(Y/N)：")
    if answer_playlist_download not in ["y", "Y"]:
        print("取消下载，退出程序")
        return

    # raw_bit_rate = input("请输入下载码率（默认为128000）：")
    bit_rate = 128000
    # if len(raw_bit_rate) != 0:
    #    bit_rate = int(raw_bit_rate)

    print("\n正在获取歌单列表......\n")
    # ignore the song_ids for now, it may come in useful later because the ecs
    tracks = get_playlist_tracks(playlist["id"], m_cookies)

    playlist_name = utils.valid_filename(playlist["name"])
    download_path = f"{config['download_path']}/{playlist_name}/"
    tempfile_path = f"{config['tempfile_path']}/{playlist_name}/"
    m3u_path = f"{config['download_path']}/{playlist_name}/{playlist_name}.m3u"

    utils.not_exist_makedirs(download_path)
    utils.not_exist_makedirs(tempfile_path)

    utils.exist_remove(m3u_path)

    with open(m3u_path, "w", encoding="utf-8") as m3u_file:
        for track in progress.track(tracks, description="下载中", auto_refresh=True):
            status, filename = download_track(track, m_cookies, bit_rate, download_path, tempfile_path)
            if status == "failed":
                message = check_music(str([track["id"]]))
                progress.console.print("音乐 %s [%d]，下载失败，提示信息：“%s”" % (track["name"], track["id"], message))
            else:
                m3u_file.write(filename + "\n")


if __name__ == "__main__":
    main()
