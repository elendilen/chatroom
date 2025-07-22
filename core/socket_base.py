import asyncio
import websockets
import json
from typing import Optional, Set, Callable

class SocketBase:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server = None
        self.client_websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.message_handler: Optional[Callable] = None
        
    async def start_server(self, message_handler: Callable = None):
        print(f"[WebSocket server starting]: ws://{self.host}:{self.port}")
        self.message_handler = message_handler

        async def handle_client(websocket, path):
            self.connected_clients.add(websocket)
            print(f"[client connection]: {websocket.remote_address}")
            try:
                async for message in websocket:
                    if self.message_handler:
                        await self.message_handler(message, websocket)
                    else:
                        await self.broadcast(message, exclude=websocket)
            except websockets.exceptions.ConnectionClosed:
                print(f"[client disconnected]: {websocket.remote_address}")
            finally:
                self.connected_clients.discard(websocket)

        self.server = await websockets.serve(handle_client, self.host, self.port)
        print(f"[WebSocket server started]: ws://{self.host}:{self.port}")
        
    async def connect_as_client(self, uri: str = None):
        # connect to a WebSocket server as a client
        if uri is None:
            uri = f"ws://{self.host}:{self.port}"
        
        try:
            self.client_websocket = await websockets.connect(uri)
            print(f"[client connected]: {uri}")
            return True
        except Exception as e:
            print(f"[connection failed]: {e}")
            return False
            
    async def send(self, data: str, target_websocket: websockets.WebSocketServerProtocol = None):
        # send message
        target = target_websocket or self.client_websocket
        if target:
            try:
                await target.send(data)
                return True
            except websockets.exceptions.ConnectionClosed:
                print("[connection failed]: unable to send message")
                return False
            except Exception as e:
                print(f"[send error]: {e}")
                return False
        else:
            print("[no websocket available]: unable to send message")
            return False
    
    async def broadcast(self, message: str, exclude: websockets.WebSocketServerProtocol = None):
        # broadcast message to all connected clients
        if not self.connected_clients:
            return
            
        targets = self.connected_clients.copy()
        if exclude:
            targets.discard(exclude)
            
        tasks = []
        for client in targets:
            tasks.append(self._safe_send(client,message))
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_send(self, websocket, message):
        """安全发送消息"""
        try:
            await websocket.send(message)
        except Exception as e:
            print(f"[safe_send error]: {e}")
            self.connected_clients.discard(websocket)

    async def receive(self):
        # receive message (client mode)
        if self.client_websocket:
            try:
                message = await self.client_websocket.recv()
                return message, f"{self.host}:{self.port}"
            except websockets.exceptions.ConnectionClosed:
                print("[connection closed]: unable to receive message")
                return None, None
            except Exception as e:  
                print(f"[receive error]: {e}")
                return None, None
        else:
            print("[no available client connection]")
            return None, None
    
    async def listen_for_messages(self, message_callback: Callable = None):
        # listen for messages from the server (client mode)
        while self.client_websocket:
            try:
                message = await self.client_websocket.recv()
                if message_callback:
                    await message_callback(message)
                else:
                    print(f"[message received]: {message}")
            except websockets.exceptions.ConnectionClosed:
                print("[connection closed]: unable to receive message")
                break
            except Exception as e:
                print(f"[listen error]: {e}")
                break
    
    async def close(self):
        # close all connections
        # close client connection
        if self.client_websocket:
            await self.client_websocket.close()

        # close all server client connections
        for client in self.connected_clients.copy():
            await client.close()
        self.connected_clients.clear()

        # close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
    def get_connected_count(self):
        # return the number of connected clients
        return len(self.connected_clients)