import asyncio
import json
from datetime import datetime
from core.socket_base import SocketBase
from core.user_manager import UserManager
from core.message_types import JOIN, MESSAGE, LEAVE, ERROR, format_message
from core.utils import now_iso

class ChatServer(SocketBase):
    def __init__(self, host='localhost', port=12345):
        super().__init__(host, port)
        # 使用UserManager管理用户
        self.user_manager = UserManager()

    async def handle_message(self, raw_message, websocket):
        try:
            message_data = json.loads(raw_message)
            message_type = message_data.get('type')

            if message_type == MESSAGE:
                try:
                    await self.handle_chat_message(message_data, websocket)
                except Exception as e:
                    print(f"[handle_chat_message error]: {e}, message_data: {message_data}, websocket: {websocket}")
            elif message_type == JOIN:
                try:
                    await self.handle_join(message_data, websocket)
                except Exception as e:
                    print(f"[handle_join error]: {e}")
            elif message_type == LEAVE:
                try:
                    await self.handle_leave(message_data, websocket)
                except Exception as e:
                    print(f"[handle_leave error]: {e}")
            elif message_type == ERROR:
                pass
            else:
                print(f"[unknown message type]: {message_type}")
        except json.JSONDecodeError:
            print(f"[invalid message format]: {raw_message}")
            await self.send_error("Invalid message format", websocket)
        except Exception as e:
            print(f"[handle_message error]: {e}")

    async def handle_chat_message(self, message_data, websocket):
        if websocket not in self.connected_clients or not self.user_manager.has_user(websocket):
            print(f"[client not joined]: {websocket.remote_address}")
            await self.send_error("You must join before sending messages", websocket)
            return
        username = self.user_manager.get_username(websocket)
        content = message_data.get('content','')

        if not content.strip():
            await self.send_error("Message content cannot be empty", websocket)
            return

        broadcast_message = format_message(MESSAGE,
            username=username,
            content=content,
            timestamp=now_iso()
        )
        await self.broadcast(broadcast_message)
        print(f"[message from {username}]: {content}")

    async def handle_join(self, message_data, websocket):
        print("handle join")
        if self.user_manager.has_user(websocket):
            print(f"[client already joined]: {websocket.remote_address}")
            return
        username = message_data.get('username', "unknown_user")
        self.user_manager.add_user(websocket, username, now_iso())
        join_message = format_message(JOIN,
            username=username,
            timestamp=now_iso(),
            online_count=len(self.connected_clients)
        )
        await self.broadcast(join_message)
        print(f"[{username} joined] {len(self.connected_clients)} person in the chat room")

    async def handle_leave(self, message_data, websocket):
        if websocket not in self.connected_clients:
            print(f"[client not connected]: {websocket.remote_address}")
            return
        username = self.user_manager.get_username(websocket)
        leave_message = format_message(LEAVE,
            username=username,
            timestamp=now_iso(),
            online_count=len(self.connected_clients) - 1
        )
        await self.broadcast(leave_message)
        self.connected_clients.discard(websocket)
        self.user_manager.remove_user(websocket)
        print(f"[{username} left] {len(self.connected_clients)} person in the chat room")

    async def send_error(self, error_message, websocket):
        error_data = format_message(ERROR,
            message=error_message,
            timestamp=now_iso()
        )
        if websocket and not websocket.closed:
            await websocket.send(error_data)
        else:
            print(f"[error sending to {websocket.remote_address}]: {error_message}")

    async def start(self):
        await self.start_server(self.handle_message)
        try:
            await asyncio.Future()
        except KeyboardInterrupt:
            print("[server stopped by user]")
            await self.close()

# 只保留一份 main 和入口
async def main():
    chat_server = ChatServer('localhost', 12345)
    await chat_server.start()

if __name__ == "__main__":
    asyncio.run(main())

