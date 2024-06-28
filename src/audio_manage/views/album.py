import os
import json
from uuid import uuid4

from django.views import View
from django.http import JsonResponse, FileResponse

from audio_manage.models.album import Album
from audio_manage.models.singer import Singer
from image_manage.services.image import Img
from md_manage_server.response_status import HttpStatus
from md_manage_server.temp_configs import ALBUMS_THEME_PATH


class AlbumView(View):
    """专辑操作视图
    @url: /audio/album
    """
    def get(self, request):
        """获取专辑列表
        @param: page    页码
        @param: page_size   页面大小
        @param: name    专辑名称
        """
        # 获取参数
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))
        name = request.GET.get("name", None)

        # 获取数据
        total, res = Album.search(page=page, page_size=page_size, name=name)

        # 返回
        return JsonResponse({"total": total, "data": res, "page": page, "page_size": page_size})
    

    def post(self, request):
        """新增专辑
        @param: name    专辑名称
        @param: desc    专辑描述
        @param: singer_id   歌手ID
        """
        # 获取请求参数
        data = json.loads(request.body)
        name, desc, singer_id = data.get("name", None), data.get("desc", None), data.get("singer_id", None)

        # 验证歌手存在
        singer = Singer.objects.filter(id=id).all()
        if not singer:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到歌手信息"})

        # 保存信息
        Album(name=name, desc=desc, singer_id=singer_id).save()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "添加专辑成功"})
    

    def delete(self, request):
        """批量删除专辑
        @param: ids     要删除的专辑ID列表
        """
        # 获取请求参数
        data = json.loads(request.body)
        ids = data.get("ids", list())

        # 删除数据
        Album.delete(ids=ids)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})


class AlbumDetailView(View):
    """单个专辑操作接口
    @url: /audio/album/{id}
    """
    def get(self, request, id):
        """获取单个专辑具体信息"""
        # 获取数据
        data = Album.get(_id=id)
        if not data:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到专辑信息"})
        
        # 返回
        return JsonResponse({"code": 200, "message": "test"})
    

    def put(self, request, id):
        """修改单个专辑信息
        @param: name    名称
        @param: desc    描述
        @param: singer_id   歌手ID
        """
        # 获取请求参数
        data = json.loads(request.body)
        name, desc, singer_id = data.get("name", None), data.get("desc", None), data.get("singer_id", None)

        # 验证专辑存在
        album_query = Album.objects.filter(id=id)
        if not album_query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到专辑信息"})
        # 验证歌手存在
        if singer_id is not None:
            singer_query = Singer.objects.filter(id=id)
            if not singer_query.all():
                return JsonResponse({"code": HttpStatus.BAD_REQUEST.value(), "message": "未找到歌手信息"})

        # 更新专辑信息
        album_query.update(name=name, desc=desc, singer=singer_id)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "修改成功"})
    

    def delete(self, request, id):
        """删除单个专辑"""
        # 验证专辑存在
        query = Album.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到专辑信息"})

        # 删除专辑主题文件
        album = query.all()[0]
        filename = album.photo
        if filename:
            os.remove(ALBUMS_THEME_PATH + "/" + filename)

        # 删除专辑信息
        query.delete()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})


class AlbumThemeView(View):
    """专辑主题视图
    @url: /audio/album/theme
    """
    def get(self, request, id):
        """获取指定专辑主题图片"""
        # 验证专辑存在
        query = Album.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到专辑信息"})

        # 验证专辑存在主题图片
        album_photo = query.all()[0].photo
        if not album_photo:
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "专辑未设置主题图片"})
        
        # 验证专辑主题图片存在
        photo_path = os.path.join(ALBUMS_THEME_PATH, album_photo)
        if not os.path.exists(photo_path) or not os.path.isfile(photo_path):
            return JsonResponse({"code": HttpStatus.INTERNAL_SERVER_ERROR.value, "message": "数据库记录与磁盘文件不符"})

        # 返回文件
        return FileResponse(open(photo_path))
    

    def post(self, request, id):
        """上传指定专辑主题图片"""
        # 获取请求
        file = request.FILES["file"]

        # 验证专辑存在
        query = Album.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到专辑信息"})

        # 验证专辑未设定主题图片
        album = query.all()[0]
        if album.photo is not None:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "此专辑已设定主图图片"})

        # 保存更改
        photo_name = uuid4()
        Img.save(path=os.path.join(ALBUMS_THEME_PATH, photo_name))
        query.update(photo=photo_name)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": '上传成功'})
    

    def put(self, request, id):
        """更新指定专辑主题图片"""
        # 获取请求
        file = request.FILES["file"]

        # 验证专辑存在
        query = Album.objects.filter(id=id)
        if not query.all():
            return JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到专辑信息"})

        # 验证专辑已设定主题图片
        album = query.all()[0]
        if album.photo is None:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "此专辑未设定主图图片"})

        # 保存更改
        photo_name = uuid4()
        Img.save(path=os.path.join(ALBUMS_THEME_PATH, photo_name))
        query.update(photo=photo_name)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": '更新成功'})