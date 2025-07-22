from core.chat_client import Chatclient

if __name__ == '__main__':
    nickname = input("please choose your nickname: ")
    client = Chatclient(nickname,server_host='localhost',server_port=12345)
    client.start()