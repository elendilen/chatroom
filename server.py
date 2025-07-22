import asyncio
from core.chat_server import ChatServer

if __name__ == '__main__':
    server = ChatServer(host='localhost', port=12345)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n服务器已关闭")