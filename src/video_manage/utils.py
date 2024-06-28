# 工具模块
import os
import copy
import json

import psutil
from pymediainfo import MediaInfo
from ffmpy import FFmpeg

from video_manage.configs import TEMP_PATH


def media_info(file):
    """获取多媒体文件信息
    @param:file 文件对象
    @return: name type size
    """
    info = json.loads(MediaInfo.parse(file).to_json())
    name = info["tracks"][0]["file_name"]
    extension = info["tracks"][0]["file_extension"]
    file_size = info["tracks"][0]["file_size"]

    return name, extension, file_size


def space_enough(disk_name:str, file_size:int) -> bool:
    """判断磁盘剩余空间是否充足
    @param:disk_name    磁盘名称
    @param:file_size    文件大小
    @return:bool
    """
    free_space = psutil.disk_usage(disk_name)
    return free_space > file_size + 51200


def is_cross(l1:list[int], l2:list[int]) -> bool:
    """判断两个数字列表是否相交
    @param:l1   列表一
    @param:l2   列表二
    @return:bool
    """
    l = copy.deepcopy(l1)
    l.extend(l2)

    return len(l) == len(set(l))


def to_m3u8(input, output):
    """生成m3u8视频
    @param:input    临时视频文件位置
    @param:output   m3u8目标位置
    """
    # 视频切片
    ff = FFmpeg(
        inputs={input: None},
        outputs={output: ['-c', 'copy', '-hls_time', '5', '-hls_list_size', '0']}
    )
    ff.run()

    # 删除临时文件
    os.remove(input)


def to_mp4(input, file_path):
    """将m3u8视频转为mp4
    @param:input    m3u8文件位置
    @param:file_path    文件uuid
    """
    # 视频处理
    ff = FFmpeg(
        inputs = {input: None},
        outputs={TEMP_PATH + "/" + file_path + ".mp4": None}
    )
    ff.run()
    return TEMP_PATH + "/" + file_path + ".mp4"