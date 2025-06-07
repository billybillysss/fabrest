from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin, UpdateDefinitionMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin, GetDefinitionMixin
from ..api.url import URL
from ..operator.spark import LivySessionOperator
from .base import BaseOperator


class NotebookOperator(
    CreateMixin,
    ListMixin,
    GetMixin,
    GetDefinitionMixin,
    UpdateMixin,
    UpdateDefinitionMixin,
    DeleteMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, item_type="Notebook", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.credential = credential
        self.item_type = None
        self.url = URL.get_item_url(workspace_id=self.workspace_id, item_type=item_type)
        self._cache_operator = {
            "livy": {},
        }

    def livy_session(self, item_id):
        cached = self._cache_operator["livy"]
        livy_operator = cached.get(item_id)
        if not livy_operator:
            livy_operator = LivySessionOperator(
                workspace_id=self.workspace_id,
                item_id=item_id,
                item_type=self.item_type,
                credential=self.credential,
            )
            cached[item_id] = livy_operator
        return livy_operator
