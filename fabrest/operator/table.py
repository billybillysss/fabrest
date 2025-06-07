from ..api.list import ListMixin
from ..api.load_table import LoadTableMixin
from ..api.url import URL
from .base import BaseOperator


class TableOperator(
    ListMixin,
    LoadTableMixin,
    BaseOperator,
):
    def __init__(
        self, workspace_id, lakehouse_id, item_type="Lakehouse", credential=None
    ):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.lakehouse_id = lakehouse_id
        self.item_type = item_type
        self.url = URL.get_table_url(
            workspace_id=self.workspace_id,
            lakehouse_id=lakehouse_id,
        )
