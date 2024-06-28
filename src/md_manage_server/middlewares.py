import re
import json
from django.http import JsonResponse

from md_manage_server.response_status import HttpStatus


# 所有人都可以访问的普通接口
normal_urls = [
    (r"/user/login", ["POST"], "用户登录"),
    (r"/user/register", ["POST"], "用户注册"),
    (r"/label", ["GET"], "获取标签列表"),
    (r"/label/\d{1,}", ["GET"], "获取单个标签信息"),
    (r"/audio/singer", ["GET"], "搜索歌手信息"),
    (r"/audio/singer/\d{1,}", ["GET"], "获取单个歌手信息"),
    (r"/audio/singer/avatar/\d{1,}", ["GET"], "获取指定歌手头像"),
    (r"/audio/album", ["GET"], "搜索专辑"),
    (r"/audio/album/\d{1,}", ["GET"], "获取单个专辑信息"),
    (r"/audio/album/theme/\d{1,}", ["GET"], "获取指定专辑头像"),
    (r"/audio/group", ["GET"], "搜索分组"),
    (r"/audio/group/\d{1,}", ["GET"], "获取指定分组信息"),
    (r"/audio/group/theme/\d{1,}", ["GET"], "获取分组主题图片"),
    (r"/audio", ["GET"], "搜索音频"),
    (r"/audio/\d{1,}", ["GET"], "获取指定音频信息"),
    (r"/audio/download/\d{1,}", ["GET"], "下载音频"),

]

# 需要登录才能访问的接口
login_urls = [
    (r"/user/logout", ["GET", "DELETE"], "用户登出与注销"),
    (r"/user/self", ["GET", "PUT", "DELETE"], "修改个人信息"),
    (r"/user/self/avatar", ["GET", "POST", "PUT"], "个人头像管理"),
    (r"/audio/group", ["POST", "DELETE"], "新建音频分组"),
    (r"/audio/group/\d{1,}", ["PUT", "DELETE"], "音频分组管理"),
    (r"/audio/group/theme/\d{1,}", ["POST", "PUT"], "音频分组主题图片管理"),
    (r"/audio/group/audio/\d{1,}", ["PUT", "DELETE"], "音频分组内音频管理"),
]

# 仅管理员可访问的接口
admin_urls = [
    (r"/user/manage", ["GET", "POST", "DELETE"], "用户信息管理"),
    (r"/user/manage/\d{1,}", ["GET", "PUT", "DELETE"], "单个用户管理"),
    (r"/user/avatar/\d{1,}", ["GET", "POST", "PUT", "DELETE"], "用户头像管理"),
    (r"/label", ["POST", "DELETE"], "标签管理"),
    (r"/label/\d{1,}", ["PUT", "DELETE"], "单个标签信息管理"),
    (r"/audio/singer", ["POST", "DELETE"], "歌手信息管理"),
    (r"/audio/singer/\d{1,}", ["PUT", "DELETE"], "单个歌手信息管理"),
    (r"/audio/singer/avatar/\d{1,}", ["POST", "PUT"], "歌手头像管理"),
    (r"/audio/album", ["POST", "DELETE"], "专辑管理"),
    (r"/audio/album/\d{1,}", ["PUT", "DELETE"], "单个专辑管理"),
    (r"/audio/album/theme/\d{1,}", ["POST", "PUT"], "专辑主题图片管理"),
    (r"/audio", ["POST", "DELETE"], "音频管理"),
    (r"/audio/\d{1,}", ["PUT", "DELETE"], "单个音频管理"),
    (r"/audio/upload/\d{1,}", ["POST", "PUT"], "音频文件上传"),

]



class ApiPermissionVerify:
    """接口权限验证"""
    def __init__(self, get_response) -> None:
        self.get_response = get_response
    

    def __call__(self, request):
        # 获取接口信息
        url, method, user = request.path, request.method, request.session.get("user", None)

        # 匹配接口等级
        # 管理员接口
        if self.__url_match__(url, method, admin_urls):
            if not user:
                resp = JsonResponse({"code": HttpStatus.UNAUTHORIZED.value, "message": "请登陆后访问"})
            elif not user["is_admin"]:
                resp = JsonResponse({"code": HttpStatus.FORBIDDEN.value, "message": "权限不足"})
            else:
                resp = self.get_response(request)
        elif self.__url_match__(url, method, login_urls):
            if not user:
                resp = JsonResponse({"code": HttpStatus.UNAUTHORIZED.value, "message": "请登陆后访问"})
            else:
                resp = self.get_response(request)
        elif self.__url_match__(url, method, normal_urls):
            resp = self.get_response(request)
        else:
            resp = JsonResponse({"code": HttpStatus.NOT_FOUND.value, "message": "未知的网址"})

        # 响应处理
        if isinstance(resp, JsonResponse):
            resp.status_code = json.loads(resp.getvalue()).get("code", 200)
        resp['X-Frame-Options'] = 'SAMEORIGIN'

        return resp
        


    def __url_match__(self, url, method, urls) -> bool:
        """匹配接口是否在权限列表内
        @param:url  此次请求url
        @param:url  此次请求方法
        @param:urls 某一权限接口列表，即上面的normal_urls、login_urls、admin_urls之一
        """
        for u, m, d in urls:
            res = re.match("^" + u + "$", url)
            if res is None:
                continue
            if method in m:
                return True
        return False