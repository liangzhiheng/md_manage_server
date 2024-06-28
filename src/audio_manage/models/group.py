import os

from django.db import models
from django.db.models import When, Q

from user_manage.models import UserModel
from audio_manage.models.audio_group_map import AudioGroupMap
from md_manage_server.temp_configs import GROUPS_THEME_PATH

class Group(models.Model):

    name = models.CharField(max_length=50, help_text="分组名称")
    desc = models.CharField(max_length=200, help_text="分组描述")
    photo = models.CharField(max_length=50, null=True, help_text="主题图片文件名称")
    create_user = models.ForeignKey("user_manage.UserModel", on_delete=models.CASCADE, help_text="创建用户ID")
    create_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    private = models.BooleanField(null=False, default=True, help_text="分组是否私密")

    
    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}
    

    @classmethod
    def get(cls, _id):
        """获取分组信息
        @param:_id  分组ID
        """
        try:
            group = cls.objects.get(id=_id).to_dict()
        except Exception:
            return None
        
        audio_info = AudioGroupMap.get(group_id=_id)

        group["audios"] = audio_info

        return group
        

    @classmethod
    def search(cls, user_id, is_admin, page, page_size, name=None, creater_id=None, private=None):
        """获取分组列表
        @param:name 分组名称
        @param:creater_id   创建者ID
        @param:private  是否私密
        @param:user_id  用户ID
        @param:is_admim 查询用户是否为管理员
        """
        offset = (page - 1) * page_size

        # 判断查询方式
        is_admin = True if user_id == creater_id else is_admin

        # 进行查询
        query = cls.objects
        if name is not None:
            query = query.filter(name__contains=name)
        if creater_id is not None:
            query = query.filter(create_user=creater_id)
        if private is not None:
            query = query.filter(private=private)
        
        if not is_admin:
            query = query.exclude(create_user=user_id).filter(private=False) | query.filter(create_user=user_id)

        groups = query.all()
        res = [g.to_dict() for g in groups[offset: offset + page_size]]

        # 返回
        return len(groups), res
    

    @classmethod
    def delete(cls, ids):
        """批量删除分组信息
        @param:ids  分组ID列表
        """
        query = cls.objects.filter(id__in=ids)
        photos = [c.photo for c in query.all()]

        # 删除文件
        for p in photos:
            os.remove(GROUPS_THEME_PATH + "/" + p)
        
        # 删除数据库信息
        query.delete()

        # 返回
        return True