import os
import json
from uuid import uuid4

from django.views import View
from django.http import JsonResponse, FileResponse

from audio_manage.models.singer import Singer
from image_manage.services.image import Img
from md_manage_server.response_status import HttpStatus
from md_manage_server.temp_configs import SINGERS_AVATAR_PATH


class SingerView(View):
    def get(self, request):
        """获取歌手信息列表
        @url: /audio/singer
        @param:name     歌手名称
        @param:page     页码
        @param:page_size    页面大小
        """
        print("=====================函数内容========================")
        # 获取请求参数
        name = request.GET.get("name", None)
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))

        # 获取数据
        total, res = Singer.search(page=page, page_size=page_size, name=name)

        # 返回
        return JsonResponse({"total": total, "data": res, "page": page, "page_size": page_size})
    

    def post(self, request):
        """添加歌手信息
        @url: /audio/singer
        @param:name     歌手名称
        @param:desc     歌手描述
        """
        # 获取请求参数
        data = json.loads(request.body)
        name, desc = data.get("name", None), data.get("desc", None)

        # 创建歌手
        Singer(name=name, desc=desc).save()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "创建成功"})
    

    def delete(self, request):
        """批量删除歌手
        @url: /audio/singer
        @param: ids     要删除的歌手ID列表
        """
        # 获取请求参数
        data = json.loads(request.body)
        ids = data.get("ids", list())

        # 删除
        Singer.delete(ids=ids)

        # 返回
        return JsonResponse({"code": 200, "message": "删除成功"})


class SingerDetailView(View):
    def get(self, request, id):
        """获取单个歌手详细信息
        @url: /audio/singer/{id}
        """
        # 获取数据
        singer = Singer.objects.filter(id=id).all()

        # 验证数据存在
        if not singer:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到相关信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 返回
        res = singer[0].to_dict()
        return JsonResponse(res)
    

    def put(self, request, id):
        """更新单个歌手信息
        @url: /audio/singer/{id}
        @param:name     歌手名称
        @param:desc     歌手描述
        """
        # 获取请求参数
        data = json.loads(request.body)
        name, desc = data.get("name", None), data.get("desc", None)

        # 验证数据存在
        query = Singer.objects.filter(id=id)
        if not query.all():
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到相关信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 更新信息
        query.update(name=name, desc=desc)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "更新成功"})
    

    def delete(self, request, id):
        """删除单个歌手信息
        @url: /audio/singer/{id}
        """
        # 验证数据存在
        query = Singer.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到相关信息"})

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})


class SingerAvatarView(View):
    def get(self, request, id):
        """获取歌手头像文件
        @url: /audio/singer/avatar/{id}
        """
        # 验证数据存在
        query = Singer.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到歌手信息"})
        
        # 验证存在头像
        filename = query.all()[0].photo
        if not filename:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未上传头像"})

        avatar_path = os.path.join(SINGERS_AVATAR_PATH, filename)

        # 返回
        return FileResponse(open(avatar_path, 'rb'))
    

    def post(self, request, id):
        """上传歌手头像
        @url: /audio/singer/avatar/{id}
        """
        # 获取请求数据
        file = request.FILES["file"]

        # 验证数据存在
        query = Singer.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到歌手信息"})
        
        # 读取文件信息（名称、格式、大小）
        file_extension, file_size = Img(file)
        if file_extension is None:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "文件识别错误"})
        
        # 文件保存
        new_filename = uuid4()
        Img.save(path=SINGERS_AVATAR_PATH + "/" + new_filename)

        # 元数据修改
        query.update(photo=new_filename)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "头像上传成功"})
    

    def put(self, request, id):
        """更新歌手头像
        @url: /audio/singer/avatar/{id}
        """
        # 获取请求数据
        file = request.FILES["file"]

        # 验证数据存在
        query = Singer.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到歌手信息"})
        
        # 验证有旧文件存在
        singer = query.all()[0]
        if not singer.photo:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "未找到旧头像文件"})
        
        # 读取文件信息（名称、格式、大小）
        file_extension, file_size = Img(file)
        if file_extension is None:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "文件识别错误"})
        
        # 文件保存
        Img.save(path=SINGERS_AVATAR_PATH + "/" + singer.photo)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "更新成功"})