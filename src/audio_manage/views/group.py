import os
import json
from uuid import uuid4
from datetime import datetime

from django.views import View
from django.http import JsonResponse, FileResponse

from audio_manage.models.group import Group
from user_manage.models import UserModel
from image_manage.services.image import Img
from md_manage_server.response_status import HttpStatus
from md_manage_server.temp_configs import GROUPS_THEME_PATH


class GroupView(View):
    """分组视图
    @url: /audio/group
    """
    def get(self, request):
        """获取分组列表
        @param:name    名称
        @param:creater_id   创建者ID
        @param:private  是否私密bool
        @param:page     页码
        @param:page_size    页面大小
        """
        # 获取用户信息
        user = request.session.get("user", None)
        user_id = user.get("id") if user else 1
        is_admin = user.get("is_admin") if user else False

        # 获取请求参数
        name = request.GET.get("name", None)
        creater_id = request.GET.get("creater_id", None)
        private = request.GET.get("private", None)
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))

        # 获取数据
        total, data = Group.search(user_id=user_id, is_admin=is_admin, page=page, page_size=page_size, name=name, creater_id=creater_id, private=private)

        # 返回
        return JsonResponse({"total": total, "data": data, "page": page, "page_size": page_size})
    

    def post(self, request):
        """新增分组
        @param:name     名称
        @param:desc     描述
        @param:private  是否私密
        """
        # 获取用户信息
        user = request.session.get("user", None)

        # 获取请求参数
        data = json.loads(request.body)
        name, desc, private = data.get("name", None), data.get("desc", None), data.get("private", False)
        
        # 非空参数验证
        if name is None:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "名称不可为空"})

        # 保存数据
        Group(name=name, desc=desc, create_user=user["id"], create_time=datetime.now(), private=private).save()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "新增成功"})
    

    def delete(self, request):
        """批量删除分组
        @param:ids  要删除的分组ID列表
        """
        # 获取请求参数
        ids = json.loads(request.body).get("ids", list())

        # 删除数据
        Group.delete(ids=ids)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "批量删除成功"})


class GroupDetailView(View):
    """指定分组操作
    @url: /audio/group/{id}
    """
    def get(self, request, id):
        """获取分组信息"""
        # 获取分组信息
        res = Group.get(_id=id)
        if res is None:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到分组信息"})

        # 返回
        return JsonResponse(res)
    

    def put(self, request, id):
        """更新分组信息
        @param:name     名称
        @param:desc     描述
        @param:private  是否私密
        """
        # 获取用户信息
        user = request.session.get("user", None)
        # 获取请求参数
        # 修改信息
        # 返回