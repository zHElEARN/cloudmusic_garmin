from rich import console, progress, inspect
from pyncm import apis
import pyncm
import os
import time

from config import config
import utils

ascii_logo = """
      _                 _                     _                                     _       
  ___| | ___  _   _  __| |_ __ ___  _   _ ___(_) ___      __ _  __ _ _ __ _ __ ___ (_)_ __  
 / __| |/ _ \| | | |/ _` | '_ ` _ \| | | / __| |/ __|    / _` |/ _` | '__| '_ ` _ \| | '_ \ 
| (__| | (_) | |_| | (_| | | | | | | |_| \__ \ | (__    | (_| | (_| | |  | | | | | | | | | |
 \___|_|\___/ \__,_|\__,_|_| |_| |_|\__,_|___/_|\___|____\__, |\__,_|_|  |_| |_| |_|_|_| |_|
                                                   |_____|___/                              
"""

__version__ = "0.0.1"


def main():
    c = console.Console()
    c.print(ascii_logo, highlight=False, style="red bold")

    if os.path.exists(config["saved_authorizations"]):
        use_saved_authorizations = c.input("检测到本地已保存的Session信息，是否使用登录？[green]Y(y)[/green]/[red]N(n)[/red]：")

    if use_saved_authorizations in ["Y", "y"]:
        pyncm.SetCurrentSession(pyncm.LoadSessionFromString(utils.load_sesion()))
    else:
        username = c.input("请输入账号（手机号）：")
        password = c.input("账号密码：")
        try:
            apis.login.LoginViaCellphone(phone=username, password=password)
        except apis.login.LoginFailedException as e:
            inspect(e)
            exit()

        utils.exist_remove(config["saved_authorizations"])
        utils.save_session(pyncm.DumpSessionAsString(pyncm.GetCurrentSession()))

    c.print(f'登录成功，用户名：[cyan]{apis.user.GetUserDetail()["profile"]["nickname"]}[/cyan]', end="\n\n")

    total_playlists = apis.user.GetUserPlaylists()["playlist"]
    created_playlists = []
    subscribed_playlists = []
    for playlist in total_playlists:
        if playlist["subscribed"] == False:
            created_playlists.append(playlist)
        else:
            subscribed_playlists.append(playlist)

    playlist_type = c.input("请输入你要下载的歌单类型，输入[green]1[/green]为用户[green]创建[/green]的歌单，[red]2[/red]为用户[red]收藏[/red]的歌单：")
    if playlist_type not in ["1", "2"]:
        c.print("输入错误，退出程序")
        exit()

    total_playlists = created_playlists if (playlist_type == "1") else subscribed_playlists

    c.print("\n歌单列表：")
    for i, playlist in enumerate(total_playlists, start=1):
        c.print(f'\t[bold cyan]{i}[/bold cyan]: {playlist["name"]} [i red]({playlist["id"]})[/i red]')

    playlist_id = int(c.input("请输入你要下载的歌单[red bold]序号[/red bold]："))
    if playlist_id >= (len(total_playlists) + 1):
        c.print("输入错误，退出程序")
        exit()

    playlist = apis.playlist.GetPlaylistInfo(total_playlists[playlist_id - 1]["id"])["playlist"]

    c.print(
        "歌单名称：[green]%s[/green] ID：[green]%d[/green] 网易云歌曲数：[green]%d[/green] 云盘歌曲数：[green]%d[/green] 创建者：[green]%s[/green]"
        % (playlist["name"], playlist["id"], playlist["trackCount"], playlist["cloudTrackCount"], playlist["creator"]["nickname"])
    )

    c.print("开始下载")

    tracks = playlist["tracks"]
    playlist_name = utils.valid_filename(playlist["name"])
    download_path = f'{config["download_path"]}/{playlist_name}/'
    tempfile_path = f'{config["tempfile_path"]}/{playlist_name}/'

    m3u8_path = f'{config["download_path"]}/{playlist_name}.m3u8'

    utils.not_exist_makedirs(download_path)
    utils.not_exist_makedirs(tempfile_path)
    utils.exist_remove(m3u8_path)

    with open(m3u8_path, "w", encoding="utf-8") as f:

        def write(playlist_name, filename, track):
            f.write(f'Music/{playlist_name}/{utils.valid_filename(filename) + (".mp3" if "pc" not in track else "")}\n')

        p = progress.Progress(
            progress.SpinnerColumn(),
            progress.TimeElapsedColumn(),
            progress.TextColumn("下载中...", style="i green"),
            progress.BarColumn(),
            progress.TaskProgressColumn(),
            progress.MofNCompleteColumn(),
            progress.TimeRemainingColumn(),
            console=c,
        )
        with p:
            for track in p.track(tracks):
                artist_list = []
                if "pc" in track:
                    filename = track["pc"]["fn"]
                else:
                    artist_list.extend(ar["name"] for ar in track["ar"])
                    filename = f'{track["name"]} - {",".join(artist_list)}'

                music_filename = download_path + utils.valid_filename(filename) + (".mp3" if "pc" not in track else "")
                cover_filename = tempfile_path + utils.valid_filename(filename) + ".jpg"

                if os.path.exists(music_filename):
                    write(playlist_name, filename, track)
                    continue

                utils.download_file(apis.track.GetTrackAudioV1([track["id"]])["data"][0]["url"], music_filename, config)

                if "pc" not in track:
                    utils.download_file(track["al"]["picUrl"], cover_filename, config)
                    utils.config_music(
                        music_filename,
                        {"title": track["name"], "artists": artist_list, "album": track["al"]["name"], "cover": cover_filename},
                    )

                write(playlist_name, filename, track)

    c.print("下载完成")


if __name__ == "__main__":
    main()
