import json

from django.views import View
from django.http import JsonResponse

from labels_manage.models import LabelModel
from md_manage_server.response_status import HttpStatus


class LabelsView(View):
    def get(self, request):
        """获取标签列表
        @url: /label
        @param:name 标签名称
        @param:type 类型
        @param:page 页码
        @param:page_size    页面大小
        """
        # 获取请求参数
        name = request.GET.get("name", None)
        _type = request.GET.get("type", None)
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))

        # 获取数据
        total, data = LabelModel.search(page=page, page_size=page_size, name=name, type=_type)

        # 返回
        resp = JsonResponse({"total": total, "page": page, "page_size": page_size, "data": data})
        return resp
    

    def post(self, request):
        """新建标签
        @url: /label
        @param:name     标签名称
        @param:type     标签类型
        @param:desc     标签描述
        """
        # 获取请求参数
        data = json.loads(request.body)
        name, _type, desc = data["name"], data["type"], data["desc"]

        # 验证标签重复
        labels = LabelModel.objects.filter(name=name, type=_type).all()
        if labels:
            resp = JsonResponse({"code": HttpStatus.BAD_REQUEST.value, "message": "标签已存在"})
            resp.status_code = HttpStatus.BAD_REQUEST.value
            return resp
        
        # 创建标签
        LabelModel(name=name, type=_type, desc=desc).save()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "创建成功"})
    

    def delete(self, request):
        """批量删除标签
        @url: /label
        @param:ids  要删除的标签列表
        """
        # 获取请求参数
        data = json.loads(request.body)
        ids = data.get("ids", list())

        # 删除用户
        LabelModel.objects.filter(id__in=ids).delete()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "批量删除成功"})


class LabelDetailView(View):
    def get(self, request, id):
        """获取单个标签信息
        @url: /label/{id}
        """
        # 获取信息
        labels = LabelModel.objects.filter(id=id).all()

        # 验证非空
        if not labels:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到标签信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 返回
        return JsonResponse(labels[0].to_dict())
    

    def put(self, request, id):
        """修改标签信息
        @url: /label/{id}
        @param:name     标签名称
        @param:type     标签类型
        @param:desc     标签描述
        """
        # 获取请求参数
        data = json.loads(request.body)
        name, _type, desc = data["name"], data["type"], data["desc"]

        # 验证标签重复
        labels = LabelModel.objects.filter(id=id).all()
        if not labels:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未找到目标信息"})
            resp.status_code = HttpStatus.NOT_FOUND.value
            return resp
        
        # 修改信息
        LabelModel.objects.filter(id=id).update(name=name, type=_type, desc=desc)

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "修改标签信息成功"})
    

    def delete(self, request, id):
        """删除指定标签
        @url: /label/{id}
        """
        # 删除标签
        LabelModel.objects.filter(id=id).delete()

        # 返回
        return JsonResponse({"code": HttpStatus.SUCCESS.value, "message": "删除成功"})