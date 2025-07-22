import socket

class SocketBase:
    def __init__(self,host='localhost',port=12345):
        self.addr = (host,port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send(self, data: str,target_addr):
        self.socket.sendto(data.encode(),target_addr)

    def receive(self, bufsize=1024):
        data, addr = self.socket.recvfrom(bufsize)
        return data.decode(), addr
    
    def close(self):
        self.socket.close()
        
