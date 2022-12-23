# cloudmusic_garmin

## 软件说明

由于佳明设备的播放列表需要一个 M3U 文件，而网易云音乐在下载歌单时并不会生成 M3U 文件，使用这个软件下载歌单音乐会生成 M3U 文件

## 环境要求

-   Python3.9.12

## 使用方法

-   克隆或[下载](https://github.com/zHElEARN/cloudmusic_garmin/archive/refs/heads/main.zip)此项目

```terminal
$ git clone https://github.com/zHElEARN/cloudmusic_garmin.git
$ cd cloudmusic_garmin
```

-   在 config.py 中配置[网易云音乐 Node.js API service](https://github.com/Binaryify/NeteaseCloudMusicApi)服务网址，默认 API 地址由[Zhe_Learn](https://github.com/zHElEARN)提供[https://ncm-api.zhelearn.com/](https://ncm-api.zhelearn.com/)

-   使用 Python 运行 app.py

```terminal
$ python app.py
```

-   使用 [Garmin Express](https://www.garmin.com/zh-CN/software/express/windows/) 连接你的佳明设备

-   在 Garmin Express 中的`音乐`选择 cloudmusic_garmin 文件夹，选择歌单并发送到设备

![步骤图](https://assets.zhelearn.com/pictures/1671785081.gif)

## 目前的问题

-   已知部分佳明设备（如 fēnix 5 Plus）上，若歌单内音乐过多，则在播放列表中无法显示所有音乐

    解决方法：分多个歌单

-   下载会突然卡住，原因未知
-   手表内音乐过多情况下 Garmin Express 会卡死，可能是佳明原因
-   部分音乐封面在佳明设备上无法显示，可能是佳明问题

## 未来发展

个人比较想制作一个 Connect IQ 程序，但由于不了解 Monkey C，制作 CIQ 程序的计划只能搁置...
