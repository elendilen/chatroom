from core.socket_base import SocketBase

class ChatServer(SocketBase):
    def __init__(self, host='localhost', port=12345):
        super().__init__(host, port)
        self.clients = set()
        self.socket.bind(self.addr)
        print(f"[server] initializing , listening to {self.addr}")

    def start(self):
        while True:
            try:
                message, addr = self.receive()
                if addr not in self.clients:
                    self.clients.add(addr)
                    print(f"[new connection] {addr}")
                self.broadcast(message,addr)
            except Exception as e:
                print(f"[error] {e}")
    
    def broadcast(self, message, sender):
        for client in self.clients:
            if client != sender:
                self.send(message,client)
    
