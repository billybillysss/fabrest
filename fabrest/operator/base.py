from ..api.client import Client, AsyncClient


class BaseOperator:
    def __init__(self, credential, scopes=None):
        self.credential = credential
        self.scopes = scopes
        self._client = None
        self._async_client = None

    @property
    def client(self):
        if not self._client:
            self._client = Client(self.credential, self.scopes)
        return self._client
    
    @property
    def async_client(self):
        if not self._async_client:
            self._async_client = AsyncClient(self.credential, self.scopes)
        return self._async_client
