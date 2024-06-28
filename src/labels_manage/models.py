from django.db import models

# Create your models here.
class LabelModel(models.Model):
    class Types(models.TextChoices):
        text = "text", "文本"
        audio = "audio", "音频"
        video = "video", "视频"

    name = models.CharField(max_length=255, help_text="标签名称")
    type = models.CharField(choices=Types.choices, max_length=10, help_text="标签类型")
    desc = models.CharField(max_length=255, help_text="标签描述")


    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}
    

    @classmethod
    def search(cls, page, page_size, type=None, name=None):
        """搜索标签
        @param:page     页码
        @param:page_size    页面大小
        @param:type     标签类型
        @param:name     标签名称
        """
        offset = (page - 1) * page_size

        query = cls.objects
        if type is not None:
            query = query.filter(type = type)
        if name is not None:
            query = query.filter(name__contains = name)
        
        query = query.all()
        total = len(query)
        res = [c.to_dict() for c in query[offset: offset + page_size]]

        return total, res