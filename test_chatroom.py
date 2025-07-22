#!/usr/bin/env python3
"""
WebSocket 聊天室测试脚本
自动启动服务器和多个客户端进行测试
"""
import subprocess
import time
import asyncio
import sys
import json
from core.chat_client import ChatClient

class TestClient(ChatClient):
    def __init__(self, server_host='localhost', server_port=12345):
        super().__init__(server_host=server_host, server_port=server_port)
        self.messages_received = []
        self.running = False

    async def start_listening(self):
        """开始监听服务器消息"""
        self.running = True
        try:
            await self.listen_for_messages(self.handle_server_message)
        except asyncio.CancelledError:
            print(f"[{self.username}] 消息监听已取消")
        finally:
            self.running = False

    async def handle_server_message(self, raw_message):
        """处理服务器消息"""
        try:
            message_data = json.loads(raw_message)
            message_type = message_data.get('type')

            # 只处理 join、message 和 leave 类型
            if message_type in ['join', 'message', 'leave']:
                self.messages_received.append(message_data)

                if message_type == 'join':
                    username = message_data.get('username')
                    print(f"[{self.username}] 🟢 {username} 加入了聊天室")
                elif message_type == 'message':
                    username = message_data.get('username')
                    content = message_data.get('content')
                    timestamp = message_data.get('timestamp')
                    print(f"[{self.username}] 收到聊天: [{timestamp}] {username}: {content}")
                elif message_type == 'leave':
                    username = message_data.get('username')
                    print(f"[{self.username}] 🔴 {username} 离开了聊天室")
            else:
                # 忽略未处理的消息类型
                print(f"[{self.username}] ⚠️ 未知消息类型: {message_type}")
        except json.JSONDecodeError:
            print(f"[{self.username}] 收到非JSON消息: {raw_message}")
        except Exception as e:
            print(f"[{self.username}] 处理消息时出错: {e}")

    async def disconnect(self):
        """断开连接"""
        if self.running:
            self.running = False
            await asyncio.sleep(0.1)
        await self.close()
        print(f"[{self.username}] 已断开连接")

def start_server():
    """启动服务器进程"""
    print("启动 WebSocket 聊天室服务器...")
    try:
        server_process = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd="/Users/wanchongyu/workspace/chatroom",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(5)  # 延长等待时间，确保服务器完全启动
        print("✅ 服务器启动完成")
        return server_process
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        print("请检查 server.py 是否存在或是否有权限运行")
        return None

async def test_basic_chat():
    """基本聊天功能测试"""
    print("\n开始基本聊天功能测试")
    alice = TestClient()
    bob = TestClient()
    charlie = TestClient()

    try:
        if not await alice.connect_to_server("alice"):
            print("❌ Alice 连接失败")
            return False
        if not await bob.connect_to_server("bob"):
            print("❌ Bob 连接失败")
            return False
        if not await charlie.connect_to_server("charlie"):
            print("❌ Charlie 连接失败")
            return False

        listen_tasks = [
            asyncio.create_task(alice.start_listening()),
            asyncio.create_task(bob.start_listening()),
            asyncio.create_task(charlie.start_listening())
        ]

        await alice.send_chat_message("大家好！我是Alice")
        await bob.send_chat_message("你好Alice！我是Bob")
        await charlie.send_chat_message("嗨！我是Charlie，很高兴见到大家")

        # 等待一段时间以确保消息被处理
        await asyncio.sleep(1)

        # 停止监听任务
        for task in listen_tasks:
            task.cancel()
        await asyncio.gather(*listen_tasks, return_exceptions=True)

        # 检查消息接收情况
        print(f"Alice 收到 {len(alice.messages_received)} 条消息")
        print(f"Bob 收到 {len(bob.messages_received)} 条消息")
        print(f"Charlie 收到 {len(charlie.messages_received)} 条消息")

        # 验证消息传递
        success = True
        expected_min_messages = 2  # 每个客户端至少应该收到2条消息（如果服务端不广播给自己）

        if len(alice.messages_received) < expected_min_messages:
            print(f"❌ Alice 只收到 {len(alice.messages_received)} 条消息，期望至少 {expected_min_messages} 条")
            success = False
        if len(bob.messages_received) < expected_min_messages:
            print(f"❌ Bob 只收到 {len(bob.messages_received)} 条消息，期望至少 {expected_min_messages} 条")
            success = False
        if len(charlie.messages_received) < expected_min_messages:
            print(f"❌ Charlie 只收到 {len(charlie.messages_received)} 条消息，期望至少 {expected_min_messages} 条")
            success = False

        if success:
            print("✅ 基本聊天功能测试通过！")
        else:
            print("❌ 基本聊天功能测试失败！")
        return success
    finally:
        await alice.disconnect()
        await bob.disconnect()
        await charlie.disconnect()

async def main():
    server_process = start_server()
    if not server_process:
        return
    try:
        await test_basic_chat()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    asyncio.run(main())