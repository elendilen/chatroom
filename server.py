from core.chat_server import ChatServer

if __name__ == '__main__':
    server = ChatServer(host='localhost',port=12345)
    server.start()
