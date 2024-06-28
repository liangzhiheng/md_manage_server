from django.db import models


class AudioLabelMap(models.Model):

    audio = models.ForeignKey("Audio", on_delete=models.CASCADE, help_text="音频ID外键")
    label = models.ForeignKey("label_manage.LabelModel", on_delete=models.CASCADE, help_text="标签ID外键")

    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}