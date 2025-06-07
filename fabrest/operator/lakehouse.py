from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin, UpdateDefinitionMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin
from ..api.url import URL
from ..api.constant import JobType
from .base import BaseOperator
from .job import JobInstanceOperator
from .datalake import DataLakeOperator
from .table import TableOperator


class LakehouseOperator(
    CreateMixin,
    ListMixin,
    GetMixin,
    UpdateMixin,
    UpdateDefinitionMixin,
    DeleteMixin,
    BaseOperator,
):
    def __init__(
        self, workspace_id, item_type="Lakehouse", credential=None, client=None
    ):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = item_type
        self.url = URL.get_item_url(
            workspace_id=self.workspace_id,
            item_type=item_type,
        )
        self._cache_operator = {
            "datalake": {},
            "table": {},
            "table_maintenance": {},
        }

    def files(self, lakehouse_id, working_directory: str = "."):
        cache_key = lakehouse_id + working_directory
        cached = self._cache_operator["datalake"]
        datalake_operator = cached.get(cache_key)
        if not datalake_operator:
            datalake_operator = DataLakeOperator(
                workspace_id=self.workspace_id,
                lakehouse_id=lakehouse_id,
                credential=self.credential,
                working_directory=working_directory,
            )

            cached[cache_key] = datalake_operator

        return datalake_operator

    def tables(self, lakehouse_id: str):
        """Return the table operator for a given lakehouse ID."""
        cached = self._cache_operator["table"]
        table_operator = cached.get(lakehouse_id)
        if not table_operator:
            table_operator = TableOperator(
                workspace_id=self.workspace_id,
                lakehouse_id=lakehouse_id,
                credential=self.credential,
            )
            cached[lakehouse_id] = table_operator
        return table_operator

    def table_maintenance(
        self,
        lakehouse_id: str,
    ):
        cached = self._cache_operator["table_maintenance"]
        job_instance_operator = cached.get(lakehouse_id)

        if not job_instance_operator:
            job_instance_operator = JobInstanceOperator(
                workspace_id=self.workspace_id,
                item_id=lakehouse_id,
                item_type=self.item_type,
                job_type=JobType.TableMaintenance.value,
                credential=self.credential,
            )
            cached[lakehouse_id] = job_instance_operator
        return cached[lakehouse_id]
