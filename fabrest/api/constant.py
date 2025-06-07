from enum import Enum


class Collection(Enum):
    Workspace = "workspaces"
    Admin = "admin"
    Capacity = "capacities"
    Connection = "connections"
    DeploymentPipeline = "deploymentPipelines"
    ExternalDataShare = "externalDataShares"
    Gateway = "gateways"
    Operation = "operations"


class AdminCollection(Enum):
    Workspace = "workspaces"
    Domain = "domains"
    Item = "items"
    Capacity = "capacities"
    Tag = "tags"
    User = "users"


class WorkspaceConfigType(Enum):
    Spark = "spark"
    ManagedPrivateEndpoint = "managedPrivateEndpoints"
    RoleAssignment = "roleAssignments"
    Folder = "folders"
    Git = "git"


class ItemType(Enum):
    Item = "items"
    ApacheAirflowJob = "ApacheAirflowJobs"
    CopyJob = "copyJobs"
    Dashboard = "dashboards"
    Dataflow = "dataflows"
    DataPipeline = "dataPipelines"
    Datamart = "datamarts"
    Environment = "environments"
    Eventhouse = "eventhouses"
    Eventstream = "eventstreams"
    GraphQLApi = "GraphQLApis"
    KQLDashboard = "kqlDashboards"
    KQLDatabase = "kqlDatabases"
    KQLQueryset = "kqlQuerysets"
    Lakehouse = "lakehouses"
    MLExperiment = "mlExperiments"
    MLModel = "mlModels"
    MirroredDatabase = "mirroredDatabases"
    MirroredWarehouse = "mirroredWarehouses"
    MountedDataFactory = "mountedDataFactories"
    Notebook = "notebooks"
    PaginatedReport = "paginatedReports"
    Reflex = "reflexes"
    Report = "reports"
    SQLDatabase = "SQLDatabases"
    SQLEndpoint = "sqlEndpoints"
    SemanticModel = "semanticModels"
    SparkJobDefinition = "sparkJobDefinitions"
    VariableLibrary = "VariableLibraries"
    Warehouse = "warehouses"


# Dynamic Workspace Collection
WorkspaceCollection: WorkspaceConfigType | ItemType = Enum(
    "WorkspaceCollection",
    {
        **{attr.name: attr.value for attr in WorkspaceConfigType},
        **{attr.name: attr.value for attr in ItemType},
    },
)


class WorksapceOperation(Enum):
    AssignToCapacity = "assignToCapacity"
    UnassignFromCapacity = "unassignFromCapacity"
    ProvisionIdentity = "provisionIdentity"


class GitOperation(Enum):
    UnboundLocalErrorpdateFromGit = "updateFromGit"
    InitializeConnection = "initializeConnection"
    MyGitCredentials = "myGitCredentials"
    Status = "status"
    Connection = "connection"
    Disconnect  = "disconnect"
    Connect = "connect"
    CommitToGit = "commitToGit"

class ItemCollection(Enum):
    Job = "jobs"
    Shortcut = "shortcuts"
    DataAccessRole = "dataAccessRoles"
    ExternalDataShare = "externalDataShares"


class ExternalDataShareOperation(Enum):
    Revoke = "revoke"


class TagOperation(Enum):
    ApplyTag = "applyTags"
    UnapplyTag = "unapplyTags"


class LakehouseCollection(Enum):
    Table = "tables"


class SparkOperation(Enum):
    LivySessions = "livySessions"
    Setting = "settings"
    Pool = "pools"


class EnvironmentCollection(Enum):
    Library = "libraries"
    SparkCompute = "sparkcompute"


class JobCollection(Enum):
    Schedule = "schedules"
    Instance = "instances"


class JobType(Enum):
    Notebook = "RunNotebook"
    DataPipeline = "Pipeline"
    SparkJobDefinition = "sparkjob"
    CopyJob = "CopyJob"
    TableMaintenance = "TableMaintenance"
    ApplyChange = "ApplyChanges"
    Execute = "Execute"


class JobStatus(Enum):
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    DEDUPE = "Deduped"
    FAILED = "Failed"
    IN_PROGRESS = "InProgress"
    NOT_STARTED = "NotStarted"


class LongRunningOperationStatus(Enum):
    FAILED = "Failed"
    NOTSTARTED = "NotStarted"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    UNDEFINED = "Undefined"
