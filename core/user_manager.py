class UserManager:
    def __init__(self):
        self.clients = {}  # {websocket: {'username': ..., 'join_time': ...}}

    def add_user(self, websocket, username, join_time):
        self.clients[websocket] = {'username': username, 'join_time': join_time}

    def remove_user(self, websocket):
        if websocket in self.clients:
            del self.clients[websocket]

    def get_username(self, websocket):
        return self.clients.get(websocket, {}).get('username', 'unknown')

    def has_user(self, websocket):
        return websocket in self.clients
