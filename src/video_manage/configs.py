# 环境变量
import os

# 视频文件位置
FILMS_PATH = os.environ.get("FILMS_PATH", "/data/video/films")
TV_DRAMAS_PATH = os.environ.get("TV_DRAMAS_PATH", "/data/video/tv_drams")
OTHER_VIDEOS_PATH = os.environ.get("OTHER_VIDEOS_PATH", "/data/video/otheres")
TEMP_PATH = os.environ.get("TEMP_PATH", "/data/video/temp")