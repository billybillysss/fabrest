from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin, UpdateDefinitionMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin
from ..api.run import RunJobMixin
from ..api.constant import JobType
from .job import JobInstanceOperator
from ..api.url import URL
from .base import BaseOperator
from .schedule import ScheduleOperator
from ..api.constant import JobType


class SparkJobDefinitionOperator(
    CreateMixin,
    ListMixin,
    GetMixin,
    UpdateMixin,
    UpdateDefinitionMixin,
    DeleteMixin,
    BaseOperator,
    RunJobMixin,
):
    def __init__(self, workspace_id, item_type="SparkJobDefinition", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = item_type
        self.url = URL.get_item_url(workspace_id=self.workspace_id, item_type=item_type)
        self._cache_operator = {
            "schedule": {},
            "job_instance": {},
        }
        self.__cache_schedule_operator = {}
        self.__cache_job_instance_operator = {}

    def schedule(self, item_id):
        cached = self._cache_operator["schedule"]
        sched_operator = cached.get(item_id)

        if not sched_operator:
            sched_operator = ScheduleOperator(
                workspace_id=self.workspace_id,
                item_id=item_id,
                item_type=self.item_type,
                job_type=JobType.SparkJobDefinition.value,
                credential=self.credential,
            )
            cached[item_id] = sched_operator
        return sched_operator

    def job_instance(
        self,
        item_id,
    ):
        cached = self._cache_operator["job_instance"]
        job_instance_operator = cached.get(item_id)

        if not job_instance_operator:
            job_instance_operator = JobInstanceOperator(
                workspace_id=self.workspace_id,
                item_id=item_id,
                item_type=self.item_type,
                job_type=JobType.SparkJobDefinition.value,
                credential=self.credential,
            )
            cached[item_id] = job_instance_operator
        return job_instance_operator
