import asyncio
import json
import sys
from datetime import datetime
from core.socket_base import SocketBase

class ChatClient(SocketBase):
    def __init__(self, server_host='localhost', server_port=12345):
        super().__init__(server_host, server_port)
        self.username = None
        self.connected = False
        self.chatroom_num = 0
        self.chatroom_name = f"Chatroom {self.chatroom_num}"

    async def connect_to_server(self, username: str):
        if self.connected:
            print("[error]: already connected to chatroom")
            return  

        if not username.strip():
            print("[error]: username cannot be empty")
            return
        self.username = username

        # 正确调用 connect_as_client，不赋值
        if not await self.connect_as_client():
            print("[error]: unable to connect to chat server")
            return

        join_message = json.dumps({
            'type': 'join',
            'username': self.username
        })
        if await self.send(join_message, target_websocket=self.client_websocket):
            print(f"[joining chatroom]: {self.username}")
            self.connected = True
            return True
        return False

    async def send_chat_message(self, content: str):
        if not self.connected:
            print("[error]: join chatroom first")
            return
        
        message_data = {
            'type': 'message',
            'username': self.username,
            'content': content
        }
        message = json.dumps(message_data)
        # 指定 target_websocket
        await self.send(message, target_websocket=self.client_websocket)
    
    async def handle_server_message(self, raw_message):
        """处理服务器消息"""
        try:
            message_data = json.loads(raw_message)
            message_type = message_data.get('type')
            
            if message_type == 'join':
                username = message_data.get('username')
                timestamp = message_data.get('timestamp')
                print(f"✅ [{timestamp}] {username} 加入聊天室")
                online_count = message_data.get('online_count')
                print(f"📊 在线人数: {online_count}")
                
            elif message_type == 'message':
                username = message_data.get('username')
                content = message_data.get('content')
                timestamp = message_data.get('timestamp')
                print(f"[{timestamp}] {username}: {content}")
                
            elif message_type == 'leave':
                username = message_data.get('username')
                timestamp = message_data.get('timestamp')
                online_count = message_data.get('online_count') or message_data.get('online count')
                print(f"🔴 [{timestamp}] {username} 离开了聊天室 (在线: {online_count})")
                
            elif message_type == 'error':
                print(f"❌ 错误: {message_data.get('message')}")
                
        except json.JSONDecodeError:
            print(f"收到消息: {raw_message}")
        except Exception as e:
            print(f"处理消息时出错: {e}")
            
    async def disconnect(self):
        if self.connected:
            leave_message = json.dumps({
                'type': 'leave'
            })
            await self.send(leave_message, target_websocket=self.client_websocket)
            print(f"[leaving chatroom]: {self.username}")
            self.connected = False
        await self.close()
    
    async def run(self):
        # run the client
        print("=== welcome to chatroom ===")
        
        # aquiring username
        while True:
            self.username = input("please input username: ").strip()
            if self.username:
                break
            print("invalid username")
            
        # connect to server
        print("connecting to server...")
        if not await self.connect_to_server(self.username):
            print("❌ error: unable to connect to chat server")
            return
            
        print("✅ connected to chat server,type 'exit' to leave")
        print("-" * 50)
        
        # start listening for messages
        listen_task = asyncio.create_task(
            self.listen_for_messages(self.handle_server_message)
        )

        # start handling user input
        input_task = asyncio.create_task(self.handle_user_input())
        
        try:
            # wait for any task to complete
            done, pending = await asyncio.wait(
                [listen_task, input_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # cancel pending tasks
            for task in pending:
                task.cancel()
                
        except KeyboardInterrupt:
            print("\nclosing chat client...")
        finally:
            await self.disconnect()

    async def handle_user_input(self):
        """处理用户输入"""
        loop = asyncio.get_event_loop()
        
        while self.connected:
            try:
                # get user input
                message = await loop.run_in_executor(None, input)
                
                if message.strip() == 'exit':
                    break
                elif message.strip():
                    await self.send_chat_message(message.strip())
                    
            except EOFError:
                break
            except Exception as e:
                print(f"输入处理错误: {e}")
                break

async def main():
    # username 会在 run() 里输入
    client = ChatClient(server_host='localhost', server_port=12345)
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
