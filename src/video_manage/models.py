import shutil
import json

from django.db import models

from video_manage.utils import is_cross
from video_manage.configs import FILMS_PATH, TV_DRAMAS_PATH, OTHER_VIDEOS_PATH

# 标签表
class Labels(models.Model):
    id = models.AutoField(primary_key=True, unique=True, help_text='标签ID')
    name = models.CharField(max_length=10, help_text='标签名称')
    desc = models.TextField(help_text='标签描述')

    
    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}
    

    @classmethod
    def get(cls, name: list):
        """获取标签列表"""
        # 获取列表
        if not name:
            res = cls.objects.all()
        else:
            res = cls.objects.filter(name__in = name).all()

        # 转换结果为json列表
        res = [c.to_dict() for c in res]

        return res


    @classmethod
    def add(cls, name:str, desc:str)->bool:
        """添加新标签
        @param:name 标签名称
        @param:desc 标签描述
        @return:bool
        """
        # 检查名称是否重复
        exist = cls.objects.filter(name=name).values()
        if exist:
            return False
        
        # 添加新标签
        cls(name = name, desc = desc).save()
        return True


class VideoMeta(models.Model):
    class VideoTypes(models.TextChoices):
        film = "Film", "电影"
        tv_drama = "TvDrama", "电视剧"
        others = "Others", "其它"

    id = models.AutoField(primary_key=True, unique=True, help_text='视频信息ID')
    name = models.CharField(max_length=20, help_text='视频名称')
    type = models.TextField(choices=VideoTypes.choices, help_text="视频类型")
    labels = models.TextField(help_text="标签ID列表")
    episodes = models.IntegerField(help_text="总集数")
    file_path = models.TextField(help_text="文件路径")


    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: self.get_attr(m.attname) for m in self._meta.get_fields()}
    

    def get_attr(self, name):
        if name == "labels":
            return json.loads(getattr(self, name))
        
        return getattr(self, name)
    

    @classmethod
    def search(cls, _id = None, name = None, _type = None, labels = list(), offset=0, limit=20):
        """检索信息
        @param: _id 视频ID
        @param: name    视频名称
        @param: type    视频类型
        @param: labels  视频标签
        """
        # 检索
        q = cls.objects
        if _id:
            q = q.filter(id = _id)
        if name:
            q = q.filter(name__contains = name)
        if _type:
            q = q.filter(type=_type)
        
        q = q.order_by("id")
        total = q.count()

        # 标签检索
        res = list()
        for c in q.all()[offset:limit]:
            data = c.to_dict()
            data_labels = list()
            for label_id in data["labels"]:
                label = Labels.objects.get(id = label_id)
                data_labels.append(label.name) if label else None
            data["labels"] = data_labels
            res.append(data)
        if labels:
            res = [r for r in res if is_cross(labels, r["labels"])]
        
        # 返回
        return total, res


    @classmethod
    def add(cls, data:dict):
        """添加数据
        @param:data 视频元数据
        """
        cls(name = data["name"], type = data["type"], labels = data["labels"], episodes = data["episodes"], file_path = data["file_path"]).save()
    

    @classmethod
    def update(cls, _id, data):
        """更新数据
        @param:_id  元数据ID
        @param:data 新元数据
        @return
        """
        # 更新数据
        cls.objects.filter(id = _id).update(data)


    @classmethod
    def delete(cls, name):
        """删除数据
        @param:name 视频名称
        """
        # 获取元数据信息
        d = cls.objects.get(name = name)
        file_path = d.file_path
        _type = d.type

        # 删除数据
        match _type:
            case cls.VideoTypes.film:
                shutil.rmtree(FILMS_PATH + "/" + file_path)
            case cls.VideoTypes.tv_drama:
                shutil.rmtree(TV_DRAMAS_PATH + "/" + file_path)
            case cls.VideoTypes.others:
                shutil.rmtree(OTHER_VIDEOS_PATH + "/" + file_path)
            case _:
                raise ValueError("视频类型错误")
        
        # 删除元数据
        d.delete()