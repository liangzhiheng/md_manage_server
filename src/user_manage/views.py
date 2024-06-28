import os
import json
from uuid import uuid4

from django.views import View
from django.http import JsonResponse, FileResponse

from user_manage.models import UserModel
from video_manage.defines import HttpStatus
from image_manage.services.image import Img
from md_manage_server.temp_configs import USERS_AVATAR_PATH
# Create your views here.

class UserManageView(View):
    """用户管理
    @url: /user/manage
    """
    def get(self, request):
        """获取用户信息列表
        @param:name 用户名称
        @param:page 页码
        @param:page_size    页面大小
        """
        # 获取请求参数
        name = request.GET.get("name", None)
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))

        # 获取数据
        total, data = UserModel.search(name=name, page=page, page_size=page_size)

        # 返回
        resp = JsonResponse({"total": total, "page": page, "page_size": page_size, "data": data})
        return resp
    

    def post(self, request):
        """创建用户
        @param:account  账号
        @param:name     昵称
        @param:password 密码
        @param:is_admin 是否为管理员
        """
        # 获取请求参数
        data = json.loads(request.body)
        account, name, password, is_admin = data["account"], data["name"], data["password"], data["is_admin"]

        # 验证账号重复
        user = UserModel.objects.filter(account=account).all()
        if user:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "账号已存在"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        # 创建用户
        UserModel(account = account, name = name, password = password, is_admin = is_admin).save()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "新建用户成功"})
    

    def delete(self, request):
        """批量删除用户
        @param:ids  用户ID列表
        """
        # 获取请求参数
        ids = json.loads(request.body).get("ids", list())

        # 删除用户
        q = UserModel.objects.filter(id__in = ids)
        q.delete()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})


class UserDetailManageView(View):
    """单个用户管理
    @url: /user/manage/{id}
    """
    def get(self, request, id):
        """获取单个用户信息"""
        # 验证用户存在
        try:
            user = UserModel.objects.get(id=id)
            resp = JsonResponse(user.to_dict())
        except:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到用户信息"})
        finally:
            return resp

    
    def put(self, request, id):
        """修改指定用户信息
        @param:name     名称
        @param:password 密码
        @param:is_admin 是否为管理员
        """
        # 获取请求参数
        data = json.loads(request.body)
        name, password, is_admin = data["name"], data["password"], data["is_admin"]

        # 验证用户存在
        query = UserModel.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到用户信息"})
        
        # 修改用户信息
        query.update(name=name, password=password, is_admin=is_admin)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "修改成功"})
    

    def delete(self, request, id):
        """删除指定用户"""
        # 验证用户存在
        query = UserModel.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到用户信息"})
        
        # 删除用户
        query.delete()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})


class UserAvatarView(View):
    """用户头像管理
    @url: /user/avatar/{id}
    """
    def get(self, request, id):
        """获取指定用户头像"""
        # 验证用户存在
        query = UserModel.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到用户信息"})
        
        # 验证头像存在
        user_avatar = query.all()[0].avatar
        if not user_avatar:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到头像文件"})
        
        # 返回头像文件
        return FileResponse(open(os.path.join(USERS_AVATAR_PATH, user_avatar), "rb"))
    

    def post(self, request, id):
        """上传用户头像"""
        # 获取上传文件
        file = request.FILES["file"]

        # 验证用户存在
        query = UserModel.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到用户信息"})
        
        # 验证头像不存在
        user_avatar = query.all()[0].avatar
        if user_avatar:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "头像已存在"})
        
        # 验证图片格式
        img = Img(file)
        if not img.format:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "无法识别头像文件"})
        
        # 保存头像文件
        avatar_name = uuid4()
        img.save(path=os.path.join(USERS_AVATAR_PATH, avatar_name))

        # 更新数据记录
        query.update(avatar=avatar_name)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "上传成功"})
    

    def put(self, request, id):
        """修改用户头像"""
        # 获取上传文件
        file = request.FILES["file"]

        # 验证用户存在
        query = UserModel.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到用户信息"})
        
        # 验证头像存在
        user_avatar = query.all()[0].avatar
        if not user_avatar:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "头像不存在"})
        
        # 验证上传文件格式
        img = Img(file)
        if not img.format:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "无法识别头像文件"})

        # 更新头像文件
        Img.save(path=os.path.join(USERS_AVATAR_PATH, user_avatar))

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "修改成功"})
    

    def delete(self, request, id):
        """删除用户头像"""
        # 验证用户存在
        query = UserModel.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到用户信息"})
        
        # 验证头像存在
        user_avatar = query.all()[0].avatar
        if not user_avatar:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "头像不存在"})
        
        # 删除文件
        os.remove(os.path.join(USERS_AVATAR_PATH, user_avatar))

        # 删除记录
        query.update(avatar=None)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})


class SelfView(View):
    """个人信息管理
    @url: /user/self
    """
    def get(self, request):
        """获取个人信息"""
        # 获取个人信息
        user_id = request.session["user"].get("id")

        # 获取个人信息
        res = UserModel.objects.get(id=user_id).to_dict()

        # 返回
        return JsonResponse(res)


    def put(self, request):
        """个人信息更新
        @param:name     昵称
        @param:password 密码
        """
        # 获取请求参数
        data = json.loads(request.body)
        # account, password = data["account"], data["password"]

        # 获取当前登录用户ID
        user_id = request.session["user"].get("id")

        # 更新信息
        UserModel.objects.filter(id = user_id).update(name=data["name"], password=data["password"])

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "更新成功"})
    

    def delete(self, request):
        """注销个人账号"""
        # 获取用户ID
        user_id = request.session["user"].get("id")

        # 删除个人信息并级联删除相关合集（歌单、图集等）
        UserModel.objects.filter(id=user_id).delete()

        # 清空当前session中用户信息
        del request.session["user"]

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "注销账号成功"})


class SelfAvatarView(View):
    """个人头像管理视图
    @url: /user/self/avatar
    """
    def get(self, request):
        """获取个人头像"""
        # 获取用户ID
        user_id = request.session["user"].get("id")

        # 验证头像文件存在
        user_avatar = UserModel.objects.get(id=user_id).avatar
        if not user_avatar:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "头像文件不存在"})
        
        # 返回头像文件
        avatar_path = os.path.join(USERS_AVATAR_PATH, user_avatar)

        return FileResponse(open(avatar_path, "rb"))
    

    def post(self, request):
        """上传个人头像"""
        # 获取用户ID
        user_id = request.session["user"].get("id")

        # 获取上传文件
        file = request.FILES["file"]

        # 验证头像文件不存在
        user = UserModel.objects.get(id=user_id)
        if user.avatar:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "头像已存在"})
        
        # 验证头像文件
        img = Img(file)
        if img.format is None:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "无法识别头像文件"})
        
        # 保存头像文件
        avatar_name = uuid4()
        img.save(path=os.path.join(USERS_AVATAR_PATH, avatar_name))

        # 更新数据记录
        user.avatar = avatar_name
        user.save()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "头像上传成功"})
    

    def put(self, request):
        """更新个人头像"""
        # 获取用户ID
        user_id = request.session["user"].get("id")

        # 获取上传文件
        file = request.FILES["file"]

        # 验证用户头像存在
        user = UserModel.objects.get(id=user_id)
        if not user.avatar:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "头像不存在"})

        # 验证上传文件格式
        img = Img(file)
        if not img.format:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "无法识别头像文件"})

        # 更新头像文件
        Img.save(path=os.path.join(USERS_AVATAR_PATH, user.avatar))

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "头像更新成功"})


class RegisertView(View):
    def post(self, request):
        """用户注册
        @param:account  账号
        @param:name 名称
        @param:password 密码
        """
        # 获取请求参数
        data = json.loads(request.body)
        account, name, password = data["account"], data["name"], data["password"]

        # 账号重复验证
        if UserModel.exists(account):
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "账号已存在"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 创建账号
        UserModel(account = account, name = name, password = password, is_admin = False).save()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "账号注册成功"})


class LoginView(View):
    def post(self, request):
        """用户登录
        @param:account  账号
        @param:password 密码
        """
        # 获取请求参数
        data = json.loads(request.body)
        account, password = data["account"], data["password"]

        # 账号密码验证
        user = UserModel.objects.filter(account = account, password = password)
        if not user:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "账号或密码错误"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 向session写入信息
        request.session["user"] = {
            "id": user[0].id,
            "name": user[0].name,
            "is_admin": user[0].is_admin,
        }

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "登录成功"})


class LogoutView(View):
    def get(self, request):
        """用户登出"""
        # 删除session信息
        del request.session["user"]

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "登出成功"})
    

