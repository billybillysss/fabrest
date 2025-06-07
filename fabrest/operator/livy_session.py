from ..api.list import ListMixin
from ..api.get import GetMixin
from ..api.url import URL
from ..api.constant import SparkOperation
from .base import BaseOperator


class LivySessionOperator(ListMixin, GetMixin, BaseOperator):
    def __init__(self, workspace_id, id, item_type="Notebook", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = None
        sub_path = SparkOperation.LivySessions.value
        self.url = (
            URL.get_item_url(
                workspace_id=self.workspace_id, item_type=item_type, item_id=id
            )
            + f"/{sub_path}"
        )
