from choicesenum import ChoicesEnum


# http响应状态码
class HttpStatus(ChoicesEnum):
    SUCCESS = 200,              "请求成功"
    UNAUTHORIZED = 401,         "验证未通过"
    BAD_REQUEST = 400,          "请求错误"
    FORBIDDEN = 403,            "无权执行"
    NOT_FOUND = 404,            "资源未找到"
    INTERNAL_SERVER_ERROR = 500,    "服务器错误"