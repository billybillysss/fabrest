from ..api.list import ListMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin
from ..api.delete import DeleteMixin
from ..api.get import GetMixin
from ..api.url import URL
from .item import ItemOperator
from .data_pipeline import DataPipelineOperator
from .folder import FolderOperator
from .lakehouse import LakehouseOperator
from .base import BaseOperator
from .spark_job_definition import SparkJobDefinitionOperator
from .mirrored_database import MirroredDatabaseOperator
from .airflow import AirflowOperator
from .mirrored_warehouse import MirroredWarehouseOperator
from .dashboard import DashboardOperator
from .dataflow import DataflowOperator
from .environment import EnvironmentOperator
from .eventhouse import EventhouseOperator
from .eventstream import EventstreamOperator
from .graphql_api import GraphQLApiOperator
from .kql_dashboard import KQLDashboardOperator
from .kql_database import KQLDatabaseOperator
from .kql_queryset import KQLQuerysetOperator
from .ml_experiment import MLExperimentOperator
from .ml_model import MLModelOperator
from .mounted_data_factory import MountedDataFactoryOperator
from .notebook import NotebookOperator
from .paginated_report import PaginatedReportOperator
from .reflex import ReflexOperator
from .report import ReportOperator
from .sql_database import SQLDatabaseOperator
from .sql_endpoint import SQLEndpointOperator
from .semantic_model import SemanticModelOperator
from .variable_library import VariableLibraryOperator
from .warehouse import WarehouseOperator
from .spark import SparkOperator
from .role_assignment import RoleAssignmentOperator


class WorkspacesOperator(
    CreateMixin, ListMixin, GetMixin, UpdateMixin, DeleteMixin, BaseOperator
):
    def __init__(
        self,
        credential,
    ):
        super().__init__(credential)
        self.url = URL.get_workspace_url()
        self._cache_operator = {
            "workspace": {},
        }

    def workspace(self, workspace_id):
        cached = self._cache_operator["workspace"]
        ws_operator = cached.get(workspace_id)
        if not ws_operator:
            ws_operator = WorkspaceOperator(id=workspace_id, credential=self.credential)
            cached[workspace_id] = ws_operator
        return ws_operator


class WorkspaceOperator(BaseOperator):
    def __init__(self, id, credential, client=None):
        super().__init__(credential, client)
        self.id = id
        self.url = URL.get_workspace_url(self.id)

        # Define mapping of operator names to their classes and caches
        self._item_operator_configs = {
            "items": (ItemOperator, {}),
            "data_pipelines": (DataPipelineOperator, {}),
            "folders": (FolderOperator, {}),
            "lakehouses": (LakehouseOperator, {}),
            "spark_job_definitions": (SparkJobDefinitionOperator, {}),
            "spark": (SparkOperator, {}),
            "mirrored_databases": (MirroredDatabaseOperator, {}),
            "airflow": (AirflowOperator, {}),
            "copy_jobs": (AirflowOperator, {}),
            "dashboards": (DashboardOperator, {}),
            "dataflows": (DataflowOperator, {}),
            "environments": (EnvironmentOperator, {}),
            "eventhouses": (EventhouseOperator, {}),
            "eventstreams": (EventstreamOperator, {}),
            "graphql_apis": (GraphQLApiOperator, {}),
            "kql_dashboards": (KQLDashboardOperator, {}),
            "kql_databases": (KQLDatabaseOperator, {}),
            "kql_querysets": (KQLQuerysetOperator, {}),
            "ml_experiments": (MLExperimentOperator, {}),
            "ml_models": (MLModelOperator, {}),
            "mirrored_warehouses": (MirroredWarehouseOperator, {}),
            "mounted_data_factories": (MountedDataFactoryOperator, {}),
            "notebooks": (NotebookOperator, {}),
            "paginated_reports": (PaginatedReportOperator, {}),
            "reflexes": (ReflexOperator, {}),
            "reports": (ReportOperator, {}),
            "sql_databases": (SQLDatabaseOperator, {}),
            "sql_endpoints": (SQLEndpointOperator, {}),
            "semantic_models": (SemanticModelOperator, {}),
            "variable_libraries": (VariableLibraryOperator, {}),
            "warehouses": (WarehouseOperator, {}),
            "role_assignments": (RoleAssignmentOperator, {}),
        }

    def _get_item_operator(self, key):
        operator_cls, cache = self._item_operator_configs[key]
        if self.id not in cache:
            cache[self.id] = operator_cls(
                workspace_id=self.id, credential=self.credential
            )
        return cache[self.id]

    # Dynamically add properties
    @property
    def items(self):
        return self._get_item_operator("items")

    @property
    def data_pipelines(self) -> DataPipelineOperator:
        return self._get_item_operator("data_pipelines")

    @property
    def folders(self):
        return self._get_item_operator("folders")

    @property
    def lakehouses(self):
        return self._get_item_operator("lakehouses")

    @property
    def spark_job_definitions(self):
        return self._get_item_operator("spark_job_definitions")

    @property
    def spark(self):
        return self._get_item_operator("spark")

    @property
    def mirror_databases(self):
        return self._get_item_operator("mirror_databases")

    @property
    def airflow(self):
        return self._get_item_operator("airflow")

    @property
    def copy_jobs(self):
        return self._get_item_operator("copy_jobs")

    @property
    def dashboards(self):
        return self._get_item_operator("dashboards")

    @property
    def dataflows(self):
        return self._get_item_operator("dataflows")

    @property
    def environments(self):
        return self._get_item_operator("environments")

    @property
    def eventhouses(self):
        return self._get_item_operator("eventhouses")

    @property
    def eventstreams(self):
        return self._get_item_operator("eventstreams")

    @property
    def graphql_apis(self):
        return self._get_item_operator("graphql_apis")

    @property
    def kql_dashboards(self):
        return self._get_item_operator("kql_dashboards")

    @property
    def kql_databases(self):
        return self._get_item_operator("kql_databases")

    @property
    def kql_querysets(self):
        return self._get_item_operator("kql_querysets")

    @property
    def ml_experiments(self):
        return self._get_item_operator("ml_experiments")

    @property
    def ml_models(self):
        return self._get_item_operator("ml_models")

    @property
    def mirrored_databases(self):
        return self._get_item_operator("mirrored_databases")

    @property
    def mirrored_warehouses(self):
        return self._get_item_operator("mirrored_warehouses")

    @property
    def mounted_data_factories(self):
        return self._get_item_operator("mounted_data_factories")

    @property
    def notebooks(self):
        return self._get_item_operator("notebooks")

    @property
    def paginated_reports(self):
        return self._get_item_operator("paginated_reports")

    @property
    def reflexes(self):
        return self._get_item_operator("reflexes")

    @property
    def reports(self):
        return self._get_item_operator("reports")

    @property
    def sql_databases(self):
        return self._get_item_operator("sql_databases")

    @property
    def sql_endpoints(self):
        return self._get_item_operator("sql_endpoints")

    @property
    def semantic_models(self):
        return self._get_item_operator("semantic_models")

    @property
    def variable_libraries(self):
        return self._get_item_operator("variable_libraries")

    @property
    def warehouses(self):
        return self._get_item_operator("warehouses")

    @property
    def role_assignments(self):
        return self._get_item_operator("role_assignments")