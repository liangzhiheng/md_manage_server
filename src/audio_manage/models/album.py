import os

from django.db import models

from md_manage_server.temp_configs import ALBUMS_THEME_PATH


class Album(models.Model):

    name = models.CharField(max_length=50, help_text="歌手名称")
    photo = models.CharField(max_length=50,null=True, help_text="图片文件名称")
    desc = models.CharField(max_length=1000, help_text="描述")
    singer = models.ForeignKey("Singer", null=True, on_delete=models.CASCADE, help_text="歌手ID外键")

    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}
    

    @classmethod
    def get(cls, _id):
        """获取专辑信息
        @param: _id 专辑ID
        """
        query = cls.objects.filter(id=_id)
        if not query.all():
            return None
        
        album = query.all()[0]
        singer = album.singer

        res = {"id": album.id, "name": album.name, "desc": album.desc, "singer": None}
        res["singer"] = {"id": singer.id, "name": singer.name, "desc": singer.desc}

        return res
    

    @classmethod
    def search(cls, page=1, page_size=20, name=None):
        """获取歌手信息
        @param:page     页码
        @param:page_size    页面大小
        @param:name     歌手名称
        """
        q = cls.objects
        offset = (page - 1) * page_size

        if name is not None:
            q = q.filter(name__contains=name)
        
        query = q.all()
        total = len(query)
        res = [c.to_dict() for c in query[offset: offset + page_size]]

        return total, res
    

    @classmethod
    def delete(cls, ids):
        """删除歌手信息，包括数据库信息与头像文件
        @param:ids  歌手ID列表
        """
        query = cls.objects.filter(id__in=ids)
        photos = [c.photo for c in query.all()]

        # 删除文件
        for p in photos:
            os.remove(ALBUMS_THEME_PATH + "/" + p)
        
        # 删除数据库信息
        query.delete()

        # 返回
        return True