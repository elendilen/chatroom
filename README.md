# 聊天室项目测试指南

## 项目结构
```
chatroom/
├── server.py              # 服务器启动脚本
├── client.py              # 客户端启动脚本
├── core/
│   ├── socket_base.py     # 基础Socket类
│   ├── chat_server.py     # 聊天服务器实现
│   └── chat_client.py     # 聊天客户端实现
├── test_chatroom.py       # 自动化测试脚本
├── quick_test.py          # 快速功能测试
├── start_test.py          # 手动测试启动器
└── README.md              # 本文件
```


## 测试方法

### 1. 手动测试（推荐新手）
```bash
# 方法1: 使用启动器
python start_test.py

# 方法2: 手动启动
# 终端1: 启动服务器
python server.py

# 终端2: 启动客户端1
python client.py

# 终端3: 启动客户端2  
python client.py
```


### 2. 完整自动化测试
```bash
# 这会自动启动服务器并运行所有测试
python test_chatroom.py
```

## 测试脚本说明


### `test_chatroom.py` - 完整自动化测试
- 自动启动服务器
- 包含多个测试场景：基本聊天、客户端断连等
- 提供详细的测试报告
- 支持交互式测试模式

## 验证聊天室是否正常工作

### 正常现象
1. 服务器启动后显示监听地址
2. 客户端加入时服务器显示新连接
3. 一个客户端发送的消息能被其他客户端看到
4. 客户端退出时不影响其他客户端

### 常见问题
1. **看不到其他人消息** - 已修复方法名拼写错误
2. **连接失败** - 检查服务器是否启动
3. **端口占用** - 更改server.py和client.py中的端口号

## 技术细节

### 协议说明
- 使用UDP协议进行通信
- 服务器维护客户端地址列表
- 采用广播机制转发消息（发送者除外）

### 架构说明
- `SocketBase`: 基础UDP通信类
- `ChatServer`: 服务器实现，负责消息转发
- `ChatClient`: 客户端实现，支持多线程收发消息

## 下一步改进建议
1. 添加消息持久化
2. 实现私聊功能
3. 添加用户认证
4. 支持文件传输
5. 改用TCP协议保证消息可靠性
