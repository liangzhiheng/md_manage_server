from django.db import models
# Create your models here.

class UserModel(models.Model):
    name = models.CharField(max_length=255, unique=False, help_text="昵称")
    avatar = models.CharField(max_length=50, null=True, unique=False, help_text="头像名称")
    account = models.CharField(max_length=255, null=False, unique=True, help_text="账号")
    password = models.CharField(max_length=255, null=False, unique=False, help_text="密码")
    is_admin = models.BooleanField(default=False, help_text = "是否为管理员")


    def __str__(self) -> str:
        return self.name
    

    def to_dict(self):
        # return {m.attname: getattr(self, m.attname) for m in self._meta.get_fields()}
        return {"id": self.id, "name": self.name, "is_admin": self.is_admin}
    

    @classmethod
    def init(cls):
        """初始化管理员账户"""
        cls(name="admin", avatar=None, account="admin", password="123456", is_admin=True).save()
    

    @classmethod
    def exists(cls, account):
        """验证用户账号是否存在
        @param:account  账号

        @return: bool
        """
        user = cls.objects.filter(account = account).all()
        return bool(user)
    

    @classmethod
    def search(cls, name, page, page_size):
        """搜索用户列表
        @param:name 用户名称
        @param:page 页码
        @param:page_size 页面大小

        @return: (total, res)   总数据量，响应数据
        """
        offset = (page - 1) * page_size
        if name is None:
            q = cls.objects.all()
        else:
            q = cls.objects.filter(name__contains = name)
        
        total = len(q)
        res = [c.to_dict() for c in q[offset: offset + page_size]]

        return total, res
        