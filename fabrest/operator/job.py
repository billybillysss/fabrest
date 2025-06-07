from ..api.list import ListMixin
from ..api.get import GetMixin
from ..api.run import RunJobMixin
from ..api.cancel import CancelJobMixin
from ..api.url import URL
from .base import BaseOperator


class JobInstanceOperator(
    ListMixin, GetMixin, RunJobMixin, CancelJobMixin, BaseOperator
):
    def __init__(
        self,
        workspace_id,
        job_type,
        item_id,
        item_type=None,
        credential=None,
    ):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_id = item_id
        self.item_type = item_type
        self.job_type = job_type
        self.url = URL.get_job_instance_url(
            workspace_id=self.workspace_id, item_id=item_id, item_type=item_type
        )
