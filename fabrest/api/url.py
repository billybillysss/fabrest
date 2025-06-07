from .constant import (
    WorkspaceCollection,
    AdminCollection,
    ItemCollection,
    Collection,
    ItemType,
    WorkspaceConfigType,
    JobType,
    JobCollection,
    LakehouseCollection,
    EnvironmentCollection,
)


class URL:
    BASE_URL = "https://api.fabric.microsoft.com"
    API_VERSION = "v1"
    ENDPOINT = f"{BASE_URL}/{API_VERSION}"

    @staticmethod
    def get_admin_url(admin_type: str= None) -> str:
        """Return the admin endpoint URL."""
        url = f"{URL.ENDPOINT}/{Collection.Admin.value}"
        
        if admin_type:
            valid_types = ", ".join([admin_type.name for admin_type in Collection])
            if admin_type not in valid_types:
                raise ValueError(
                    f"Invalid admin_type: {admin_type}, must be one of {valid_types}"
                )
            sub_path = AdminCollection[admin_type].value
            url += f"/{sub_path}"
        return url
    


    @staticmethod
    def get_capacity_url(workspace_id: str = None) -> str:
        """Return the capacity endpoint URL, optionally for a specific workspace."""
        url = f"{URL.ENDPOINT}/{Collection.Capacity.value}"
        if workspace_id:
            url += f"/{workspace_id}"
        return url

    @staticmethod
    def get_workspace_url(workspace_id: str = None) -> str:
        """Return the workspace endpoint URL, optionally for a specific workspace."""
        url = f"{URL.ENDPOINT}/{Collection.Workspace.value}"
        if workspace_id:
            url += f"/{workspace_id}"
        return url

    @staticmethod
    def get_schedule_url(
        workspace_id: str,
        item_id: str,
        item_type: str,
        job_type: str,
        schedule_id: str = None,
    ) -> str:
        """
        Return the schedule URL for a given workspace, item, and item type.
        Raises ValueError if item_type is invalid.
        """
        if item_type not in [attr.name for attr in JobType]:
            valid_types = ", ".join([job_type.name for job_type in JobType])
            raise ValueError(
                f"Invalid item_type: {item_type}, must be one of {valid_types}"
            )

        url = (
            f"{URL.ENDPOINT}/{Collection.Workspace.value}/{workspace_id}/{WorkspaceCollection.Item.value}/"
            f"{item_id}/{ItemCollection.Job.value}/{job_type}/{JobCollection.Schedule.value}"
        )
        if schedule_id:
            url += f"/{schedule_id}"
        return url

    @staticmethod
    def get_job_instance_url(
        workspace_id: str,
        item_id: str,
        job_type: str = None,
        item_type: str = None,
        job_id: str = None,
    ) -> str:
        """
        Construct the URL for a job instance.
        Raises ValueError if job_type and job_id are both provided or if job_type is invalid.
        """
        if job_type and job_id:
            raise ValueError("job_type and job_id are mutually exclusive")

        url = (
            URL.get_item_url(workspace_id, item_type, item_id)
            + f"/{ItemCollection.Job.value}/{JobCollection.Instance.value}"
        )

        if job_type:
            valid_types = ", ".join([job_type.name for job_type in JobType])
            if job_type not in [attr.value for attr in JobType]:
                raise ValueError(
                    f"Invalid Job Type: {job_type}, must be one of {valid_types}"
                )
            url += f"?jobType={job_type}"
        elif job_id:
            url += f"/{job_id}"

        return url

    @staticmethod
    def get_item_url(
        workspace_id: str, item_type: str = None, item_id: str = None
    ) -> str:
        """
        Return the item URL for a given workspace, item type, and item ID.
        Raises ValueError if item_type is invalid.
        """
        if item_type:
            valid_types = ", ".join(
                [item_type.name for item_type in ItemType]
            )
            if item_type not in valid_types:
                raise ValueError(
                    f"Invalid item_type: {item_type}, must be one of {valid_types}"
                )
            item_path = ItemType[item_type].value
        else:
            item_path = "items"

        url = f"{URL.ENDPOINT}/{Collection.Workspace.value}/{workspace_id}/{item_path}"
        if item_id:
            url += f"/{item_id}"
        return url
    
    @staticmethod
    def get_workspace_config_url(workspace_id: str, config_type: str, config_id: str = None) -> str:

        valid_types = ", ".join(
            [config_type.name for config_type in WorkspaceConfigType    ]
        )
        if config_type not in valid_types:
            raise ValueError(
                f"Invalid config_type: {config_type}, must be one of {valid_types}"
            )
        config_path = WorkspaceConfigType[config_type].value
        
        url = f"{URL.ENDPOINT}/{Collection.Workspace.value}/{workspace_id}/{config_path}"
        if config_id:
            url += f"/{config_id}"
        return url


    @staticmethod
    def get_table_url(
        workspace_id: str, lakehouse_id: str, table_name: str = None
    ) -> str:
        """Return the table URL for a given workspace and optional table ID."""
        lakehouse_url = URL.get_item_url(
            workspace_id, WorkspaceCollection.Lakehouse.value, item_id=lakehouse_id
        )
        url = f"{lakehouse_url}/{LakehouseCollection.Table.value}"
        if table_name:
            url += f"/{table_name}/load"
        return url

    @staticmethod
    def get_env_url(
        workspace_id: str,
        environment_id: str,
        env_sub_type: str = None,
        staging: bool = False,
    ) -> str:
        """
        Return the environment URL for a given workspace and environment.
        Raises ValueError if sub_path is invalid.
        """
        env_sub_types = [attr.value for attr in EnvironmentCollection]
        if env_sub_type and env_sub_type not in env_sub_types:
            raise ValueError(
                f"Invalid environment sub type: {env_sub_type}, must be one of {str(env_sub_types)}"
            )

        url = f"{URL.ENDPOINT}/{Collection.Workspace.value}/{workspace_id}/{WorkspaceCollection.Environment.value}/{environment_id}"
        if staging:
            url += "/staging"
        if env_sub_type:
            url += f"/{env_sub_type}"
        return url
