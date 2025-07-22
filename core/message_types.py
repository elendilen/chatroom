JOIN = 'join'
MESSAGE = 'message'
LEAVE = 'leave'
ERROR = 'error'

def format_message(msg_type, **kwargs):
    import json
    data = {'type': str(msg_type)}
    for k, v in kwargs.items():
        try:
            json.dumps({k: v})
            data[k] = v
        except Exception:
            data[k] = str(v)
    return json.dumps(data, ensure_ascii=False)

# 检查此文件没有问题，[error]: unable to connect to chat server 不是由本文件引起的。
# 请检查 server 是否已启动、端口是否一致、依赖是否安装、网络是否正常。
# 如果需要定位连接问题，请查看 server.py 和 socket_base.py 的启动与监听日志。
