from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin
from ..api.url import URL
from ..api.constant import AdminCollection
from .base import BaseOperator


class AdminOperator(
    BaseOperator,
):
    def __init__(
        self,
        credential,
    ):
        super().__init__(credential)
        self.credential = credential
        self.url = URL.get_admin_url()
        self._cache_operator = {
            "workspace": None,
        }

    @property
    def workspaces(self):
        ws_operator = self._cache_operator["workspace"]
        if not ws_operator:
            ws_operator = AdminWorkspaceOperator(credential=self.credential)
            self._cache_operator["workspace"] = ws_operator
        return ws_operator


class AdminWorkspaceOperator(
    GetMixin,
    ListMixin,
    BaseOperator,
):
    def __init__(
        self,
        credential,
    ):
        super().__init__(credential)
        self.admin_type = "Workspace"
        self.credential = credential
        self.url = URL.get_admin_url(self.admin_type)

        self._cache_operator = {
            "git_connections": None,
            "workspace": {},
        }

    @property
    def git_connections(self):
        git_conn_operator = self._cache_operator["git_connections"]
        if not git_conn_operator:
            git_conn_operator = AdminWorkspaceGitConnectionOperator(
                credential=self.credential
            )
            self._cache_operator["git_connections"] = git_conn_operator
        return git_conn_operator

    def access_details(self, workspace_id):
        cached = self._cache_operator["workspace"]
        access_operator = cached.get(workspace_id)
        if not access_operator:
            access_operator = AdminWorkspaceAccessOperator(
                workspace_id=workspace_id, credential=self.credential
            )
            cached[workspace_id] = access_operator
        return access_operator


class AdminWorkspaceGitConnectionOperator(
    ListMixin,
    BaseOperator,
):
    def __init__(
        self,
        credential,
    ):
        super().__init__(credential)
        self.credential = credential
        self.admin_type = "Workspace"
        self.url = URL.get_admin_url(self.admin_type) + "/discoverGitConnections"


class AdminWorkspaceAccessOperator(
    GetMixin,
    ListMixin,
    BaseOperator,
):
    def __init__(
        self,
        workspace_id,
        credential,
    ):
        super().__init__(credential)
        self.workspace_id = workspace_id
        self.credential = credential
        self.admin_type = "Workspace"
        self.url = URL.get_admin_url(self.admin_type) + f"/{self.workspace_id}/users"
