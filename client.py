import asyncio
from core.chat_client import ChatClient

async def main():
    client = ChatClient(server_host='localhost', server_port=12345)
    await client.run()
        
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n客户端已退出")