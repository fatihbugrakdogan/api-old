import requests
import json
from app.core.config import settings
from app.core.security import create_access_refresh_tokens


class WorkinoClient:
    def __init__(self, user_id, api_key):
        self.api_key = api_key
        self.url = "http://localhost:80"
        self.tokens = create_access_refresh_tokens(user_id)

    async def _request(self, method, path, params=None, data=None):
        url = self.url + path
        token = self.tokens.get("access_token")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.request(
            method, url, headers=headers, params=params, data=json.dumps(data)
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.text)

    async def get(self, path, params=None):
        return await self._request("get", path, params=params)

    async def post(self, path, data=None):
        print(data, "data")
        return await self._request("post", path, data=data)

    async def put(self, path, data=None):
        return await self._request("put", path, data=data)

    async def delete(self, path, data=None):
        return await self._request("delete", path, data=data)

    async def get_asana_tokens(self, user_id):
        token = await self.get(
            path="/auth/get-asana-token",
            params={"user_id": user_id, "secret": settings.SECRET_KEY},
        )
        return {
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": token.get("expires_at"),
        }
