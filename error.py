from functools import wraps


class RequestError(Exception):
    def __init__(self, url, status_code, content):
        self.url = url
        self.status_code = status_code
        self.content = content
        Exception.__init__(self, content)


def request_errorhandler(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssertionError as e:
            req = e.args[0]
            raise RequestError(
                    req.url, req.status_code, req.content
                )
    return decorator

"""
_policy_fields = set([
    'callbackUrl',       # 回调URL
    'callbackBody',      # 回调Body
    'callbackHost',      # 回调URL指定的Host
    'callbackBodyType',  # 回调Body的Content-Type
    'callbackFetchKey',  # 回调FetchKey模式开关

    'returnUrl',         # 上传端的303跳转URL
    'returnBody',        # 上传端简单反馈获取的Body

    'endUser',           # 回调时上传端标识
    'saveKey',           # 自定义资源名
    'insertOnly',        # 插入模式开关

    'detectMime',        # MimeType侦测开关
    'mimeLimit',         # MimeType限制
    'fsizeLimit',        # 上传文件大小限制
    'fsizeMin',          # 上传文件最少字节数

    'persistentOps',        # 持久化处理操作
    'persistentNotifyUrl',  # 持久化处理结果通知URL
    'persistentPipeline',   # 持久化处理独享队列
    'deleteAfterDays',      # 文件多少天后自动删除
    'fileType',             # 文件的存储类型，0为普通存储，1为低频存储
    'isPrefixalScope'       # 指定上传文件必须使用的前缀
])
"""
