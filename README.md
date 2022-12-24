# cloudmusic_garmin

## 软件说明

由于佳明设备的播放列表需要一个 M3U/M3U8 文件，而网易云音乐在下载歌单时并不会生成 M3U/M3U8 文件，使用这个软件下载歌单音乐会生成 M3U/M3U8 文件

## 环境要求

-   Python3.9.12

## 使用方法

-   克隆或[下载](https://github.com/zHElEARN/cloudmusic_garmin/archive/refs/heads/main.zip)此项目

```terminal
$ git clone https://github.com/zHElEARN/cloudmusic_garmin.git
$ cd cloudmusic_garmin
```

-   安装依赖

```terminal
$ pip install -r requirements.txt
```

-   使用 Python 运行 app.py

```terminal
$ python app.py
```

-   调整手表`设置-系统-USB模式`为`MTP(媒体传输)`

-   将`Downloads\Music`下的所有文件复制到手表 `Music` 文件夹下

## 目前的问题

-   已知部分佳明设备（如 fēnix 5 Plus）上，若歌单内音乐过多，则在播放列表中无法显示所有音乐

    解决方法：分多个歌单

-   下载会突然卡住，原因未知
-   部分音乐封面在佳明设备上无法显示，可能是佳明问题
