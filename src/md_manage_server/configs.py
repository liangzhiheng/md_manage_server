import os


# 数据盘名称
DATA_DEVICE_NAME = os.environ.get("DATA_DEVICE_NAME", "/dev/sda")
# 日志等级
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG")

# 数据库信息
DB_HOST = os.environ.get("DB_HOST", "192.168.100.2")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "media_data")
DB_USER = os.environ.get("DB_USER", "liang")
DB_PWD = os.environ.get("DB_PWD", "123456")

# REDIS缓存数据信息
REDIS_HOST = os.environ.get("REDIS_HOST", "192.168.100.2")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")

# 图片数据存放路径
IMAGES_PATH = os.environ.get("IMAGES_PATH", "/data/media/images/image")                 # 图片数据位置
USERS_AVATAR_PATH = os.environ.get("USERS_AVATAR_PATH", "/data/media/images/users")     # 用户头像位置

SINGERS_AVATAR_PATH = os.environ.get("SINGERS_AVATAR_PATH", "/data/media/audio/singer")     # 歌手头像位置
ALBUMS_THEME_PATH = os.environ.get("ALBUMS_THEME_PATH", "/data/media/audio/albums")         # 专辑主题图片位置
GROUPS_THEME_PATH = os.environ.get("GROUPS_THEME_PATH", "/data/media/audio/group")          # 分组主题图片位置

# 音频数据存放路径
AUDIO_PATH = os.environ.get("AUDIO_PATH", "/data/media/audio/audio")        # 音频文件存放位置