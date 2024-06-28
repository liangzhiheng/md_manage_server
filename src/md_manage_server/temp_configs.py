import os


temp_path = os.path.abspath("../../temp")


# 图片数据存放路径
IMAGES_PATH = os.path.join(temp_path, "media/images/image")                 # 图片数据位置
USERS_AVATAR_PATH = os.path.join(temp_path, "media/images/users")     # 用户头像位置

SINGERS_AVATAR_PATH = os.path.join(temp_path, "media/audio/singer")     # 歌手头像位置
ALBUMS_THEME_PATH = os.path.join(temp_path, "media/audio/albums")         # 专辑主题图片位置
GROUPS_THEME_PATH = os.path.join(temp_path, "media/audio/group")          # 分组主题图片位置

# 音频数据存放路径
AUDIO_PATH = os.path.join(temp_path, "media/audio/audio")        # 音频文件存放位置