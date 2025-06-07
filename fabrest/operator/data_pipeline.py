from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin, UpdateDefinitionMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin, GetDefinitionMixin
from ..api.url import URL
from ..api.constant import JobType
from .base import BaseOperator
from .schedule import ScheduleOperator


class DataPipelineOperator(
    ListMixin,
    CreateMixin,
    UpdateMixin,
    UpdateDefinitionMixin,
    DeleteMixin,
    GetMixin,
    GetDefinitionMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, item_type="DataPipeline", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = item_type
        self.url = URL.get_item_url(workspace_id=self.workspace_id, item_type=item_type)
        self.__cache_operator = {}

    def schedule(self, item_id):
        sched_operator = self.__cache_operator.get(item_id)

        if not sched_operator:
            sched_operator = ScheduleOperator(
                workspace_id=self.workspace_id,
                item_id=item_id,
                item_type=self.item_type,
                job_type=JobType.DataPipeline.value,
                credential=self.credential,
            )
            self.__cache_operator[item_id] = sched_operator
        return self.__cache_operator[item_id]
