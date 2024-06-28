import json
from pymediainfo import MediaInfo


class Img(object):
    """图片数据处理类"""
    def __init__(self, file):
        """保存文件对象并返回部分文件信息"""
        self.file = file
        self.format, self.size = self.__info__()


    def __info__(self):
        """读取file文件对象获取具体的图片格式
        @return 格式, 大小
        """
        try: 
            f = json.load(MediaInfo.parse(self.file).to_json())
            file_type = f["tracks"][1]["track_type"]
            file_format = f["tracks"][1]["format"]
            file_size = f["tracks"][1]["stream_size"]

            if file_type != "Image":
                return None, None
            
            return "." + file_format.lower(), file_size
        except:
            return None, None
    

    def save(self, path):
        """保存文件数据到指定目录
        @param: path    文件保存路径，包含文件名称
        """
        # 保存文件
        with open(path, "wb") as f:
            f.write(self.file)
        
        return True