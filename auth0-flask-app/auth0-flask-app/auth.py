
import os
from dotenv import load_dotenv
from auth0_server_python.auth_server.server_client import ServerClient

load_dotenv()


class MemoryStateStore:
    def __init__(self):
        self.data = {}

    async def get(self, key, options=None):
        return self.data.get(key)

    async def set(self, key, value, options=None):
        self.data[key] = value

    async def delete(self, key, options=None):
        self.data.pop(key, None)

    async def delete_by_logout_token(self, claims, options=None):
        pass


class MemoryTransactionStore:
    def __init__(self):
        self.data = {}

    async def get(self, key, options=None):
        return self.data.get(key)

    async def set(self, key, value, options=None):
        self.data[key] = value

    async def delete(self, key, options=None):
        self.data.pop(key, None)


state_store = MemoryStateStore()
transaction_store = MemoryTransactionStore()

auth0 = ServerClient(
    domain=os.getenv("AUTH0_DOMAIN"),
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    secret=os.getenv("AUTH0_SECRET"),
    redirect_uri=os.getenv("AUTH0_REDIRECT_URI"),
    state_store=state_store,
    transaction_store=transaction_store,
    authorization_params={
        "scope": "openid profile email"
    }
)
