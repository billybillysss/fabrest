from ..api.list import ListMixin
from ..api.url import URL
from .base import BaseOperator


class DashboardOperator(
    ListMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, item_type="Dashboard", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = item_type
        self.url = URL.get_item_url(workspace_id=self.workspace_id, item_type=item_type)
