from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin
from ..api.url import URL
from .base import BaseOperator


class FolderOperator(
    CreateMixin, ListMixin, GetMixin, UpdateMixin, DeleteMixin, BaseOperator
):
    def __init__(self, workspace_id, credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.url = URL.get_workspace_config_url(
            workspace_id=self.workspace_id,
            config_type="Folder",
        )
