from django.db import models


class Audio(models.Model):

    name = models.CharField(max_length=50, help_text="歌手名称")
    file_name = models.CharField(max_length=50, help_text="图片文件名称")
    singer = models.ForeignKey("Singer", on_delete=models.CASCADE, help_text="歌手ID外键")
    album = models.ForeignKey("Album", on_delete = models.CASCADE, help_text="专辑ID外键")
    upload_time = models.DateTimeField(auto_now=True, help_text="上传时间")
    

    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}