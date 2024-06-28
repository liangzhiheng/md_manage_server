from django.db import models


class AudioGroupMap(models.Model):

    audio = models.ForeignKey("Audio", on_delete=models.CASCADE, help_text="音频ID外键")
    group = models.ForeignKey("Group", on_delete=models.CASCADE, help_text="分组ID外键")

    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}
    

    @classmethod
    def get(cls, group_id):
        """获取分组内音乐信息
        @param: group_id
        """
        maps = cls.objects.filter(group=group_id).all()
        return [m.audio.to_dict() for m in maps]