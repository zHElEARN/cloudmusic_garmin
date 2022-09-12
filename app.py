import requests
import json
import os

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
        "https://ncm-api.zhelearn.com/login/cellphone",
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
        "https://ncm-api.zhelearn.com/login/status",
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
        "https://ncm-api.zhelearn.com/user/playlist",
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


def main():
    m_cookies = m_nickname = m_userid = None
    m_created_playlist = m_collected_playlist = []

    print(logo_code)

    if os.path.exists("cookies.json"):
        answer_playlist_type = input("检测到已缓存的Cookies，是否读取已缓存Cookies（Y/N)")
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
    print("正在获取歌单信息")

    m_created_playlist, m_collected_playlist = get_user_playlist(
        m_userid, m_cookies)

    print("请选择歌单类型：")
    print("1. 用户创建的歌单（%d个）" % len(m_created_playlist))
    print("2. 用户收藏的歌单（%d个）" % len(m_collected_playlist))

    answer_playlist_type = input("请输入歌单类型（数字）：")
    if answer_playlist_type != "1" and answer_playlist_type != "2":
        print("输入错误，请输入数字")
        return

    playlists = m_created_playlist if answer_playlist_type == "1" else m_collected_playlist
    i = 1
    for value in playlists:
        print("%d：%s (%d)" % (i, value["name"], value["id"]))
        i += 1

    answer_playlist_id = input("请输入歌单序号（数字）：")
    playlist = playlists[answer_playlist_id - 1]


if __name__ == "__main__":
    main()
