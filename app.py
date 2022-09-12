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

    return code, decoded_response["profile"]["nickname"], login_request.cookies


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
        return True, decoded_response["data"]["profile"]["nickname"], encoded_cookies

    return False, "", None


def check_existed_cookie(filename):
    with open(filename, "r") as f:
        load_cookies = json.loads(f.read())

    return check_login_status(load_cookies)


def main():
    m_cookies = None
    m_nickname = None

    print(logo_code)

    if os.path.exists("cookies.json"):
        answer = input("检测到已缓存的Cookies，是否读取已缓存Cookies（Y/N)")
        if answer == "Y" or answer == "y":
            login_result = check_existed_cookie("cookies.json")
            if login_result[0] != True:
                print("登录失败，请尝试密码登录")
                return

            m_nickname = login_result[1]
            m_cookies = login_result[2]
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

    print("登录成功，欢迎您，" + m_nickname)


if __name__ == "__main__":
    main()
