import asyncio
import json
from datetime import datetime
from core.socket_base import SocketBase

class ChatServer(SocketBase):
    def __init__(self, host='localhost', port=12345):
        super().__init__(host, port)
        # 修正注释，明确结构：{websocket: {'username': str, 'join_time': str}}
        self.clients = {}

    async def handle_message(self, raw_message, websocket):
        try:
            message_data = json.loads(raw_message)
            message_type = message_data.get('type')

            if message_type == 'message':
                try:
                    await self.handle_chat_message(message_data, websocket)
                except Exception as e:
                    print(f"[handle_chat_message error]: {e}, message_data: {message_data}, websocket: {websocket}")
            elif message_type == 'join':
                try:
                    await self.handle_join(message_data, websocket)
                except Exception as e:
                    print(f"[handle_join error]: {e}")
            elif message_type == 'leave':
                try:
                    await self.handle_leave(message_data, websocket)
                except Exception as e:
                    print(f"[handle_leave error]: {e}")
            elif message_type == 'error':
                pass
            else:
                print(f"[unknown message type]: {message_type}")
        except json.JSONDecodeError:
            print(f"[invalid message format]: {raw_message}")
            await self.send_error("Invalid message format", websocket)
        except Exception as e:
            print(f"[handle_message error]: {e}")

    async def handle_chat_message(self, message_data, websocket):
        # 必须先 join 才能发消息
        if websocket not in self.connected_clients or websocket not in self.clients:
            print(f"[client not joined]: {websocket.remote_address}")
            await self.send_error("You must join before sending messages", websocket)
            return
        # 直接安全获取 username
        username = self.clients[websocket]['username']
        content = message_data.get('content','')

        if not content.strip():
            await self.send_error("Message content cannot be empty", websocket)
            return

        broadcast_message = json.dumps({
            'type': 'message',
            'username': username,
            'content': content,
            'timestamp': datetime.now().isoformat(),
        })
        await self.broadcast(broadcast_message)
        print(f"[message from {username}]: {content}")

    async def handle_join(self, message_data, websocket):
        print("handle join")
        # 不要重复添加，socket_base已添加
        if websocket in self.clients:
            print(f"[client already joined]: {websocket.remote_address}")
            return
        username = message_data.get('username', "unknown_user")
        self.clients[websocket] = {
            'username': username,
            'join_time': datetime.now().isoformat()
        }
        # 不再添加到 self.connected_clients，这一步已由 socket_base 处理
        join_message = json.dumps({
            'type': 'join',
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'online_count': len(self.connected_clients)
        })
        await self.broadcast(join_message)
        print(f"[{username} joined] {len(self.connected_clients)} person in the chat room")

    async def handle_leave(self, message_data, websocket):
        if websocket not in self.connected_clients:
            print(f"[client not connected]: {websocket.remote_address}")
            return
        # 离开时安全获取 username
        username = self.clients[websocket]['username'] if websocket in self.clients else "unknown"
        leave_message = json.dumps({
            'type': 'leave',
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'online_count': len(self.connected_clients) - 1
        })
        await self.broadcast(leave_message)
        self.connected_clients.discard(websocket)
        if websocket in self.clients:
            del self.clients[websocket]
        print(f"[{username} left] {len(self.connected_clients)} person in the chat room")

    async def send_error(self, error_message, websocket):
        error_data = json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()  # 同时修复时间序列化
        })
        if websocket and not websocket.closed:
            await websocket.send(error_data)  # 移除多余的 websocket 参数
        else:
            print(f"[error sending to {websocket.remote_address}]: {error_message}")

    async def start(self):
        #start the server
        await self.start_server(self.handle_message)

        try:
            await asyncio.Future()  # run forever
        except KeyboardInterrupt:
            print("[server stopped by user]")
            await self.close()

async def main():
    # main entry point
    chat_server = ChatServer('localhost', 12345)
    await chat_server.start()

if __name__ == "__main__":
    asyncio.run(main())

