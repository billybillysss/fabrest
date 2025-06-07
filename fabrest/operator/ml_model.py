from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin
from ..api.url import URL
from .base import BaseOperator


class MLModelOperator(
    ListMixin,
    CreateMixin,
    UpdateMixin,
    DeleteMixin,
    GetMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, item_type="MLModel", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = item_type
        self.url = URL.get_item_url(workspace_id=self.workspace_id, item_type=item_type)
