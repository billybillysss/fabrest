from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin, UpdateDefinitionMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin, GetDefinitionMixin
from ..api.url import URL
from ..api.constant import JobType
from .base import BaseOperator
from .schedule import ScheduleOperator


class CopyJobOperator(
    ListMixin,
    CreateMixin,
    UpdateMixin,
    UpdateDefinitionMixin,
    DeleteMixin,
    GetMixin,
    GetDefinitionMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, item_type="CopyJob", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = item_type
        self.url = URL.get_item_url(workspace_id=self.workspace_id, item_type=item_type)
        self._cache_operator = {
            "schedule": {},
        }

    def schedule(self, item_id):
        cached = self._cache_operator["schedule"]
        sched_operator = cached.get(item_id)
        if not sched_operator:
            sched_operator = ScheduleOperator(
                workspace_id=self.workspace_id,
                item_id=item_id,
                item_type=self.item_type,
                job_type=JobType.CopyJob.value,
                credential=self.credential,
            )
            cached[item_id] = sched_operator
        return sched_operator
