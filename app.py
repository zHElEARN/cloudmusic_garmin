import string
import eyed3
import requests
import json
import os
import tqdm

import config

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}
proxies = {"http": None, "https": None}
logo_code = """
    _   __________  ___      __________  ____        _________    ____  __  ________   __
   / | / / ____/  |/  /     / ____/ __ \/ __ \      / ____/   |  / __ \/  |/  /  _/ | / /
  /  |/ / /   / /|_/ /_____/ /_  / / / / /_/ /_____/ / __/ /| | / /_/ / /|_/ // //  |/ /
 / /|  / /___/ /  / /_____/ __/ / /_/ / _, _/_____/ /_/ / ___ |/ _, _/ /  / // // /|  /
/_/ |_/\____/_/  /_/     /_/    \____/_/ |_|      \____/_/  |_/_/ |_/_/  /_/___/_/ |_/
"""

requests.packages.urllib3.disable_warnings()


def login(username, password):
    login_request = requests.get(
        config.api_url + "login/cellphone",
        params={"phone": username, "password": password},
        headers=headers,
        proxies=proxies,
        verify=False
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
        config.api_url + "login/status",
        headers=headers,
        proxies=proxies,
        cookies=encoded_cookies,
        verify=False
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
        config.api_url + "user/playlist",
        params={"uid": uid},
        headers=headers,
        proxies=proxies,
        cookies=cookies,
        verify=False
    )

    decoded_response = json.loads(playlist_request.text)

    for value in decoded_response["playlist"]:
        if value["creator"]["userId"] == uid:
            created_playlist.append(value)
        else:
            collected_playlist.append(value)

    return created_playlist, collected_playlist


def get_playlist_tracks(playlist_id, cookies):
    song_id_list = []

    tracks_request = requests.get(
        config.api_url + "playlist/track/all",
        params={"id": playlist_id},
        headers=headers,
        proxies=proxies,
        cookies=cookies,
        verify=False
    )

    decoded_response = json.loads(tracks_request.text)
    for song in decoded_response["songs"]:
        song_id_list.append(str(song["id"]))

    return decoded_response["songs"], ",".join(song_id_list)


def half_to_full(uchar):
    inside_code = ord(uchar)
    if inside_code < 0x0020 or inside_code > 0x7e:
        return uchar
    if inside_code == 0x0020:
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return chr(inside_code)


def check_filename(filename):
    modified_filename = ""

    validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    for i in range(0, len(filename)):
        if filename[i] not in validFilenameChars:
            modified_filename += half_to_full(filename[i])
        else:
            modified_filename += filename[i]

    return modified_filename


def download_track(track, cookies, br, path, local_path):
    filename = ""
    ar_list = []
    if "pc" in track:
        filename = track["pc"]["fn"]
    else:
        for ar in track["ar"]:
            ar_list.append(ar["name"])

        filename = track["name"] + " - " + ",".join(ar_list)

    music_filename = path + check_filename(filename) + ".mp3"
    cover_filename = local_path + check_filename(filename) + ".jpg"

    if os.path.exists(music_filename):
        return (check_filename(filename) + ".mp3")

    track_request = requests.get(
        config.api_url + "song/download/url",
        params={"id": track["id"], "br": br},
        headers=headers,
        proxies=proxies,
        cookies=cookies,
        verify=False
    )

    decoded_response = json.loads(track_request.text)
    if decoded_response["data"]["url"] == None:
        tqdm.tqdm.write("音乐：%s，下载失败" % track["name"])
        return (check_filename(filename) + ".mp3")

    file_request = requests.get(
        decoded_response["data"]["url"], headers=headers, proxies=proxies, verify=False, stream=True)

    with open(music_filename, "wb") as f:
        for chunk in file_request.iter_content(chunk_size=512):
            f.write(chunk)

    if "pc" not in track:
        cover_request = requests.get(
            track["al"]["picUrl"], headers=headers, proxies=proxies, verify=False, stream=True)
        with open(cover_filename, "wb") as f:
            for chunk in cover_request.iter_content(chunk_size=512):
                f.write(chunk)

        audio = eyed3.load(music_filename)
        audio.tag.title = track["name"]
        audio.tag.artist = ",".join(ar_list)
        audio.tag.album = track["al"]["name"]

        with open(cover_filename, "rb") as cover:
            audio.tag.images.set(3, cover.read(), "image/jpeg")
        audio.tag.save(encoding='utf-8')

    return (check_filename(filename) + ".mp3")


def main():
    m_cookies = m_nickname = m_userid = None
    m_created_playlist = m_collected_playlist = []

    print(logo_code)

    if os.path.exists("cookies.json"):
        answer_playlist_type = input("检测到已缓存的Cookies，是否读取已缓存Cookies（Y/N)：")
        if answer_playlist_type == "Y" or answer_playlist_type == "y":
            login_result = check_existed_cookie("cookies.json")
            if login_result[0] != True:
                print("登录失败，请尝试密码登录")
                return

            m_nickname = login_result[1]
            m_cookies = login_result[2]
            m_userid = login_result[3]
        else:
            username = input("请输入您的用户名（手机号）：")
            password = input("请输入您的密码：")

            login_result = login(username, password)
            if login_result[0] != 200:
                print("登录失败，错误代码：" +
                      str(login_result[0]) + "，错误信息：" + login_result[1])
                return

            m_nickname = login_result[1]
            m_cookies = login_result[2]
            m_userid = login_result[3]

    print("登录成功，欢迎您，" + m_nickname)
    print("\n正在获取歌单信息......\n")

    m_created_playlist, m_collected_playlist = get_user_playlist(
        m_userid, m_cookies)

    print("请选择歌单类型：")
    print("    1. 用户创建的歌单（%d个）" % len(m_created_playlist))
    print("    2. 用户收藏的歌单（%d个）" % len(m_collected_playlist))

    answer_playlist_type = input("请输入歌单类型（数字）：")
    if answer_playlist_type != "1" and answer_playlist_type != "2":
        print("输入错误，请输入数字")
        return

    print("\n歌单列表：")

    playlists = m_created_playlist if answer_playlist_type == "1" else m_collected_playlist
    i = 1
    for value in playlists:
        print("    %d：%s (%d)" % (i, value["name"], value["id"]))
        i += 1

    answer_playlist_id = input("请输入歌单序号（数字）：")
    playlist = playlists[int(answer_playlist_id) - 1]
    print("\n歌单名称：%s 歌单ID：%d 歌曲数：%d 音乐云盘歌曲数：%d 创建者：%s" %
          (playlist["name"], playlist["id"], playlist["trackCount"], playlist["cloudTrackCount"], playlist["creator"]["nickname"]))

    answer_playlist_download = input("\n是否开始下载？(Y/N)：")
    if answer_playlist_download != "y" and answer_playlist_download != "Y":
        print("取消下载，退出程序")
        return

    raw_bit_rate = input("请输入下载码率（默认为128000）：")
    bit_rate = 128000
    if len(raw_bit_rate) != 0:
        bit_rate = int(raw_bit_rate)

    print("\n正在获取歌单列表......\n")
    # ignore the song_ids for now, it may come in useful later because the ecs
    tracks, song_ids = get_playlist_tracks(playlist["id"], m_cookies)
    if not os.path.exists("./ncm-garmin-music/%s/" % check_filename(playlist["name"])):
        os.mkdir("./ncm-garmin-music/%s/" % check_filename(playlist["name"]))
    if not os.path.exists("./local-files/%s/" % check_filename(playlist["name"])):
        os.mkdir("./local-files/%s/" % check_filename(playlist["name"]))

    if os.path.exists("./ncm-garmin-music/%s/%s.m3u" % (check_filename(playlist["name"]), check_filename(playlist["name"]))):
        os.remove("./ncm-garmin-music/%s/%s.m3u" %
                  (check_filename(playlist["name"]), check_filename(playlist["name"])))

    with open("./ncm-garmin-music/%s/%s.m3u" % (check_filename(playlist["name"]), check_filename(playlist["name"])), "w", encoding="utf-8") as f:
        for track in tqdm.tqdm(tracks, desc="下载中", unit="music"):
            filename = download_track(track, m_cookies, bit_rate,
                                      "./ncm-garmin-music/%s/" % check_filename(playlist["name"]), "./local-files/%s/" % check_filename(playlist["name"]))
            f.write(".\\" + filename + "\n")


if __name__ == "__main__":
    main()
