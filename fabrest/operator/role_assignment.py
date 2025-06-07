from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin, UpdateDefinitionMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin, GetDefinitionMixin
from ..api.url import URL
from .base import BaseOperator

class RoleAssignmentOperator(
    ListMixin,
    CreateMixin,
    UpdateMixin,
    UpdateDefinitionMixin,
    DeleteMixin,
    GetMixin,
    GetDefinitionMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, config_type="RoleAssignment", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.config_type = config_type
        self.url = URL.get_workspace_config_url(workspace_id=self.workspace_id, config_type=config_type)
