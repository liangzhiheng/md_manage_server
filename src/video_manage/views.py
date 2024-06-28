import os
import json
from uuid import uuid4

import shutil
from django.shortcuts import render
from django.views import View
from django.http import FileResponse, JsonResponse, HttpResponse

from video_manage.defines import HttpStatus
from video_manage.models import VideoMeta, Labels
from md_manage_server.configs import DATA_DEVICE_NAME
from video_manage.configs import FILMS_PATH, TV_DRAMAS_PATH, TEMP_PATH, OTHER_VIDEOS_PATH
from video_manage.utils import to_m3u8, to_mp4, media_info, space_enough




# 标签管理视图
class LabelsView(View):
    """标签管理视图类"""
    def get(self, request):
        """获取所有标签信息列表"""
        # 获取请求参数
        name = json.loads(request.GET.get("name", "[]"))

        # 请求数据
        data = Labels.get(name = name)
        
        # 返回
        return JsonResponse(data, safe=False)
    

    def post(self, request):
        """新增标签"""
        # 获取请求参数
        data = request.body
        if not data:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少请求参数"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        data = json.loads(data)
        
        # 添加标签信息
        res = Labels.add(name=data["name"], desc=data["desc"])

        # 验证标签重复
        if not res:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "标签已存在"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "标签添加成功"})


# 单个标签信息管理
class LabelDetailView(View):
    """单个标签管理视图类"""
    def get(self, request, id):
        """获取单个标签信息"""
        # 获取标签信息
        res = Labels.objects.get(id = id)

        # 验证标签存在
        if res is None:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到标签信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 返回
        return JsonResponse(res.to_dict())
    

    def put(self, request, id):
        """更新单个标签信息"""
        # 验证标签存在
        label = Labels.objects.get(id = id)
        if label is None:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到标签信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 获取请求参数
        data = request.body
        if not data:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少请求参数"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        data = json.loads(data)

        # 验证请求参数合法
        labels = Labels.objects.filter(name = data["name"]).exclude(id = id).values()
        if labels:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message":  "标签已存在"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 更新信息
        Labels.objects.filter(id = id).update(name = data["name"], desc = data["desc"])

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "标签修改成功"})



    def delete(self, request, id):
        """删除单个标签"""
        # 验证标签存在
        label = Labels.objects.get(id = id)
        if label is None:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到标签信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 删除标签
        label.delete()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "标签删除成功"})


# 视频元数据信息管理
class VideoMetaView(View):
    """视频元数据信息管理视图类"""
    def get(self, request):
        """获取视频元数据信息列表"""
        # 获取请求参数
        name = request.GET.get("name", None)
        _type = request.GET.get("type", None)
        labels = request.GET.get("labels", list())
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))
        
        # 验证请求参数存在且合法
        if _type:
            for _t in _type:
                if _t not in VideoMeta.VideoTypes:
                    resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "视频类型参数错误"})
                    resp.status_code = HttpStatus.BAD_REQUEST.value
                    return resp
        
        # 获取视频元数据信息
        total, res = VideoMeta.search(name=name, _type = _type, labels=labels, offset=page_size * (page - 1), limit=page_size)

        # 返回
        return JsonResponse({"total": total, "page": page, "page_size": page_size, "data": res})
    

    def post(self, request):
        """新增视频元数据"""
        data = request.body
        if not data:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少请求参数"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        data = json.loads(data)
        # 获取请求参数
        name = data.get("name", None)
        _type = data.get("type", None)
        labels = data.get("labels", list())
        episodes = data.get("episodes", 0)

        # 验证请求参数
        if name is None:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少名称信息"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        if _type is None:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少类型信息"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        if _type not in VideoMeta.VideoTypes:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "类型错误"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        if episodes is None or episodes == 0:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少集数信息"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 添加元数据
        file_path = uuid4()
        VideoMeta.add({
            "name": name,
            "type": _type,
            "labels": json.dumps(labels),
            "episodes": episodes,
            "file_path": file_path
        })

        # 创建目录
        match _type:
            case VideoMeta.VideoTypes.film:
                path = FILMS_PATH + "/" + file_path
            case VideoMeta.VideoTypes.tv_drama:
                path = TV_DRAMAS_PATH + "/" + file_path
            case VideoMeta.VideoTypes.others:
                path = OTHER_VIDEOS_PATH + "/" + file_path
            case _:
                raise ValueError("视频类型错误")
        os.mkdir(path)


        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "添加视频元数据成功"})
    

    def delete(self, request):
        """批量删除视频元数据"""
        data = request.body
        if not data:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少请求参数"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        data = json.loads(data)
        # 获取请求参数
        ids = data.get("ids", list())
        
        # 删除数据
        metas = VideoMeta.objects.filter(id__in = ids)
        for meta in metas.values():
            _type, file_path = meta['type'], meta['file_path']
            match _type:
                case VideoMeta.VideoTypes.film:
                    path = FILMS_PATH + "/" + file_path
                case VideoMeta.VideoTypes.tv_drama:
                    path = TV_DRAMAS_PATH + "/" + file_path
                case VideoMeta.VideoTypes.others:
                    path = OTHER_VIDEOS_PATH + "/" + file_path
                case _:
                    raise ValueError("视频类型错误")
        
        # 删除元数据
        metas.delete()
        
        if os.path.exists(path):
            shutil.rmtree(path)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})


# 单条视频元数据管理
class VideoMetaDetailView(View):
    """单条视频元数据管理视图类"""
    def get(self, request, id):
        """获取单条视频元数据"""
        # 验证元数据存在
        meta = VideoMeta.objects.get(id = id)
        if meta is None:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到目标信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 返回数据对象
        return JsonResponse(meta.to_dict())
    

    def put(self, request, id):
        """更新元数据信息"""
        # 验证元数据存在
        meta = VideoMeta.objects.get(id = id)
        if meta is None:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到目标信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 获取请求参数
        name = request.form.get("name", None)
        labels = request.form.get("labels", list())

        # 验证请求参数
        # 更新数据
        meta.update({"name": name, "labels": json.dumps(labels)})

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "元数据更新成功"})


class VideoDataView(View):
    """数据操作视图"""
    def get(self, request):
        """视频下载
        @param: id  视频ID
        @param: type    视频类型
        @param: episode    集数
        """
        # 获取请求参数
        _id = request.GET.get("id", None)
        episode = request.GET.get("episode", None)

        # 验证请求参数非空
        if _id is None:
            resp =  JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少视频ID参数"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 验证视频元数据存在
        meta = VideoMeta.objects.get(id = _id)
        if meta is None:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到视频元数据信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 验证集数合法
        _type, episodes, video_type = meta.type, meta.episodes, VideoMeta.VideoTypes
        if _type != video_type.others:
            if not episode:
                resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少集数信息"})
                resp.status_code = HttpStatus.BAD_REQUEST.value
                return resp
            if episode > episodes or episode < 1:
                resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "集数信息错误"})
                resp.status_code = HttpStatus.BAD_REQUEST.value
                return resp
        
        # 验证数据存在
        match _type:
            case video_type.film:
                file_path = FILMS_PATH + "/" + meta.file_path + "/" + str(episode)
            case video_type.tv_drama:
                file_path = TV_DRAMAS_PATH + "/" + meta.file_path + "/" + str(episode)
            case video_type.others:
                file_path = OTHER_VIDEOS_PATH + "/" + meta.file_path
            case _:
                raise ValueError("视频类型参数错误")
        if not os.path.exists(file_path):
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到视频数据"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 视频处理
        if _type == video_type.others:
            input_path = file_path + "/index.m3u8"
        else:
            input_path = file_path + "/" + episode + "/index.m3u8"
        temp_file_path = to_mp4(input=input_path, file_path=meta.file_path)

        # 返回
        response = FileResponse(open(temp_file_path, 'rb'))
        response.close()
        os.remove(temp_file_path)
        return response
    

    def post(self, request):
        """上传视频"""
        # 获取请求参数
        _id = request.form.get("id", None)
        episode = request.form.get("episode", None)

        # 验证请求参数
        if _id is None:
            return JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少视频ID请求参数"})
        if episode is None:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少集数请求参数"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 验证元数据存在
        meta = VideoMeta.objects.get(id = _id)
        if meta is None:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到元数据信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 验证集数
        if episode > meta.episodes or episode < 1:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "集数错误"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp

        # 获取视频信息：名称、类型、大小
        file = request.FILES['file']    # 文件对象
        _, extension, file_size = media_info(file=file)

        # TODO:验证文件类型为视频

        # 验证磁盘空间
        if not space_enough(DATA_DEVICE_NAME, file_size):
            resp = JsonResponse({"code": HttpStatus.FORBIDDEN.value, "message": "服务器空间不足"})
            resp.status_code = HttpStatus.FORBIDDEN.value
            return resp
        
        # 视频临时保存
        temp_path = TEMP_PATH + "/" + meta.file_path + episode + "." + extension
        with open(temp_path, 'wb') as f:
            f.write(file.read())
        
        # 视频切片处理
        if meta.type == VideoMeta.VideoTypes.film:
            path = FILMS_PATH + "/" + meta.file_path + "/" + str(episode)
        elif meta.type == VideoMeta.VideoTypes.tv_drama:
            path = TV_DRAMAS_PATH + "/" + meta.file_path + "/" + str(episode)
        else:
            path = OTHER_VIDEOS_PATH + "/" + meta.file_path
        if not os.path.exists(path):
            os.makedirs(path)
        to_m3u8(input=temp_path, output=path + "/" + "index.m3u8")

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "视频上传成功"})


class WatchView(View):
    """视频观看使用接口"""
    def get(self, request, filename):
        """获取文件"""
        # 获取请求参数
        _id = request.GET.get("id", None)
        episode = request.GET.get("episode", None)

        # 验证请求参数
        if _id is None:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "缺少视频ID参数"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 验证视频元数据存在
        meta = VideoMeta.objects.get(id = _id)
        if meta is None:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "未找到视频信息"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 验证视频数据存在
        if meta.type == VideoMeta.VideoTypes.others:
            path = OTHER_VIDEOS_PATH + "/" + meta.file_path + "/" + filename
        elif meta.type == VideoMeta.VideoTypes.film:
            path = FILMS_PATH + "/" + meta.file_path + "/" + str(episode) + "/" + filename
        else:
            path = TV_DRAMAS_PATH + "/" + meta.file_path + "/" + str(episode) + "/" + filename
        if not os.path.exists(path):
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到视频数据"})
            resp.status_code == HttpStatus.NOT_FOUND.value
            return resp
        
        # 返回
        response = FileResponse(open(path, 'rb'))
        response.status_code = HttpStatus.SUCCESS.value
        return response


class PostersView(View):
    """海报处理接口"""
    def get(self, request, id):
        """获取海报"""
        # 检查视频是否存在
        meta = VideoMeta.objects.get(id=id)
        if not meta:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到视频对象"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp

        # 检查海报文件是否存在
        _type = meta.type
        match (_type):
            case VideoMeta.VideoTypes.film:
                path = FILMS_PATH
            case VideoMeta.VideoTypes.tv_drama:
                path = TV_DRAMAS_PATH
            case VideoMeta.VideoTypes.others:
                path = OTHER_VIDEOS_PATH
        path += "/" + meta.file_path + "/" + "posters.png"
        if not os.path.exists(path):
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到海报文件"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 返回
        return FileResponse(open(path, 'rb'))
    

    def post(self, request, id):
        """上传海报"""
        # 检查视频是否存在
        meta = VideoMeta.objects.get(id=id)
        if not meta:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到视频对象"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp

        # 检查文件是否为png图片
        img = request.FILES['file']
        _, extension, _ = media_info(img)
        if extension != "png":
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "仅支持png格式图片"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp

        # 保存海报
        match (meta.type):
            case VideoMeta.VideoTypes.film:
                path = FILMS_PATH
            case VideoMeta.VideoTypes.tv_drama:
                path = TV_DRAMAS_PATH
            case VideoMeta.VideoTypes.others:
                path = OTHER_VIDEOS_PATH
        path += "/" + meta.file_path + "/" + "posters.png"
        with open(path, 'wb') as f:
            f.write(img)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "海报上传成功"})


    def put(self, request, id):
        """更新海报-与post接口内容完全相同"""
        # 检查视频是否存在
        meta = VideoMeta.objects.get(id=id)
        if not meta:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到视频对象"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp

        # 检查文件是否为png图片
        img = request.FILES['file']
        _, extension, _ = media_info(img)
        if extension != "png":
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "仅支持png格式图片"})
            resp.status_code == HttpStatus.BAD_REQUEST.value
            return resp

        # 保存海报
        match (meta.type):
            case VideoMeta.VideoTypes.film:
                path = FILMS_PATH
            case VideoMeta.VideoTypes.tv_drama:
                path = TV_DRAMAS_PATH
            case VideoMeta.VideoTypes.others:
                path = OTHER_VIDEOS_PATH
        path += "/" + meta.file_path + "/" + "posters.png"
        with open(path, 'wb') as f:
            f.write(img)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "海报上传成功"})
    

    def delete(self, request, id):
        """删除海报"""
        # 检查视频是否存在
        meta = VideoMeta.objects.get(id=id)
        if not meta:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到视频对象"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 检查海报是否存在
        match (meta.type):
            case VideoMeta.VideoTypes.film:
                path = FILMS_PATH
            case VideoMeta.VideoTypes.tv_drama:
                path = TV_DRAMAS_PATH
            case VideoMeta.VideoTypes.others:
                path = OTHER_VIDEOS_PATH
        path += "/" + meta.file_path + "/" + "posters.png"
        if not os.path.exists(path):
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到海报"})
            resp.status_code = HttpStatus.NOT_FOUND.value

        # 删除海报
        os.remove(path)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, 'message': '删除海报成功'})