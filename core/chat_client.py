from core.socket_base import SocketBase
import threading

class Chatclient(SocketBase):
    def __init__(self,nickname, server_host='localhost', server_port=12345):
        super().__init__()
        self.nickname = nickname
        self.server_addr = (server_host,server_port)
        self.running = True

    def start(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        print(f"[{self.nickname}] 你可以开始聊天了，输入 exit 退出。")
        self.send(f"{self.nickname} 加入了聊天室。", self.server_addr)

        while self.running:
            msg = input()
            if msg.lower() == 'exit':
                self.send(f"{self.nickname} 退出了聊天室。", self.server_addr)
                self.running = False
                break
            full_msg = f"{self.nickname}: {msg}"
            self.send(full_msg, self.server_addr)

        self.close()
        
    def receive_messages(self):
        while self.running:
            try:
                msg, _ = self.receive()
                print(msg)
            except:
                break