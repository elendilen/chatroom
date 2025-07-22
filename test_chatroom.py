#!/usr/bin/env python3
"""
聊天室测试脚本
自动启动服务器和多个客户端进行测试
"""
import subprocess
import time
import threading
import signal
import sys
import os
from core.chat_client import Chatclient

class TestClient:
    def __init__(self, nickname, server_host='localhost', server_port=12345):
        self.nickname = nickname
        self.client = Chatclient(nickname, server_host, server_port)
        self.messages_received = []
        self.running = False
        
    def start_test_client(self):
        """启动测试客户端"""
        self.running = True
        # 启动接收消息线程
        threading.Thread(target=self._receive_messages, daemon=True).start()
        
        # 发送加入消息
        self.client.send(f"{self.nickname} 加入了聊天室。", self.client.server_addr)
        print(f"[{self.nickname}] 已加入聊天室")
        
    def send_message(self, message):
        """发送消息"""
        full_msg = f"{self.nickname}: {message}"
        self.client.send(full_msg, self.client.server_addr)
        print(f"[{self.nickname}] 发送: {message}")
        
    def _receive_messages(self):
        """接收消息线程"""
        while self.running:
            try:
                msg, _ = self.client.receive()
                self.messages_received.append(msg)
                print(f"[{self.nickname}] 收到: {msg}")
            except:
                break
                
    def stop(self):
        """停止客户端"""
        self.running = False
        self.client.send(f"{self.nickname} 退出了聊天室。", self.client.server_addr)
        self.client.close()

def start_server():
    """启动服务器进程"""
    print("启动聊天室服务器...")
    server_process = subprocess.Popen([sys.executable, "server.py"], 
                                    cwd="/Users/wanchongyu/workspace/chatroom")
    time.sleep(2)  # 等待服务器启动
    return server_process

def test_basic_chat():
    """基本聊天功能测试"""
    print("\n=== 开始基本聊天功能测试 ===")
    
    # 创建测试客户端
    client1 = TestClient("Alice")
    client2 = TestClient("Bob")
    client3 = TestClient("Charlie")
    
    try:
        # 启动客户端
        client1.start_test_client()
        time.sleep(0.5)
        
        client2.start_test_client()
        time.sleep(0.5)
        
        client3.start_test_client()
        time.sleep(1)
        
        # 测试消息发送
        print("\n--- 开始消息测试 ---")
        client1.send_message("大家好！")
        time.sleep(0.5)
        
        client2.send_message("你好 Alice！")
        time.sleep(0.5)
        
        client3.send_message("我也来了！")
        time.sleep(0.5)
        
        client1.send_message("欢迎 Charlie！")
        time.sleep(1)
        
        # 检查消息接收情况
        print("\n--- 消息接收统计 ---")
        print(f"Alice 收到 {len(client1.messages_received)} 条消息: {client1.messages_received}")
        print(f"Bob 收到 {len(client2.messages_received)} 条消息: {client2.messages_received}")
        print(f"Charlie 收到 {len(client3.messages_received)} 条消息: {client3.messages_received}")
        
        # 验证消息传递
        success = True
        if len(client1.messages_received) < 3:  # Alice应该收到Bob和Charlie的消息
            print("❌ Alice 没有收到足够的消息")
            success = False
            
        if len(client2.messages_received) < 3:  # Bob应该收到Alice和Charlie的消息
            print("❌ Bob 没有收到足够的消息")
            success = False
            
        if len(client3.messages_received) < 3:  # Charlie应该收到Alice和Bob的消息
            print("❌ Charlie 没有收到足够的消息")
            success = False
            
        if success:
            print("✅ 基本聊天功能测试通过！")
        else:
            print("❌ 基本聊天功能测试失败！")
            
    finally:
        # 清理客户端
        client1.stop()
        client2.stop()
        client3.stop()
        time.sleep(1)

def test_client_disconnect():
    """客户端断开连接测试"""
    print("\n=== 开始客户端断开连接测试 ===")
    
    client1 = TestClient("David")
    client2 = TestClient("Eve")
    
    try:
        client1.start_test_client()
        client2.start_test_client()
        time.sleep(1)
        
        # 发送一些消息
        client1.send_message("我要测试断开连接")
        time.sleep(0.5)
        
        # 断开client1
        print("断开 David 的连接...")
        client1.stop()
        time.sleep(1)
        
        # client2继续发送消息
        client2.send_message("David 还在吗？")
        time.sleep(0.5)
        
        print("✅ 客户端断开连接测试完成")
        
    finally:
        client2.stop()
        time.sleep(1)

def interactive_test():
    """交互式测试模式"""
    print("\n=== 交互式测试模式 ===")
    print("你可以手动测试聊天室功能")
    print("请在另一个终端运行: python client.py")
    print("按 Ctrl+C 结束测试")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n退出交互式测试模式")

def main():
    print("聊天室测试脚本")
    print("=" * 50)
    
    # 启动服务器
    server_process = None
    try:
        server_process = start_server()
        
        print("\n选择测试模式:")
        print("1. 自动化测试")
        print("2. 交互式测试")
        choice = input("请选择 (1 或 2): ").strip()
        
        if choice == "1":
            # 运行自动化测试
            test_basic_chat()
            test_client_disconnect()
            print("\n🎉 所有自动化测试完成！")
            
        elif choice == "2":
            interactive_test()
            
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        
    finally:
        # 清理服务器进程
        if server_process:
            print("关闭服务器...")
            server_process.terminate()
            server_process.wait()
            print("服务器已关闭")

if __name__ == "__main__":
    main()
