logo_code = """
       _                 _                     _             _                     _                 _           
   ___| | ___  _   _  __| |_ __ ___  _   _ ___(_) ___     __| | _____      ___ __ | | ___   __ _  __| | ___ _ __ 
  / __| |/ _ \| | | |/ _` | '_ ` _ \| | | / __| |/ __|   / _` |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
 | (__| | (_) | |_| | (_| | | | | | | |_| \__ \ | (__   | (_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   
  \___|_|\___/ \__,_|\__,_|_| |_| |_|\__,_|___/_|\___|___\__,_|\___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   
                                                    |_____|                                                      
"""
api_url = "https://ncm-api.zhelearn.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}
proxies = {"http": None, "https": None}
saved_cookie = "cookies.json"
download_path = "./downloads/music"
tempfile_path = "./downloads/temp"
