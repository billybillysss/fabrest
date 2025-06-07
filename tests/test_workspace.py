import pytest
from unittest.mock import patch, MagicMock

from fabric.operator.workspace import WorkspacesOperator, WorkspaceOperator

@pytest.fixture
def credential():
    return "dummy_credential"

def test_workspaces_operator_creates_workspace_operator(credential):
    ws_operator = WorkspacesOperator(credential)
    workspace_id = "ws1"
    with patch("fabric.operator.workspace.WorkspaceOperator") as MockWorkspaceOperator:
        instance = MockWorkspaceOperator.return_value
        result = ws_operator.workspace(workspace_id)
        assert result == instance
        # Should be cached
        assert ws_operator._WorkspacesOperator__cached_operators[workspace_id] == instance

def test_workspace_operator_items_property(credential):
    workspace_id = "ws2"
    operator = WorkspaceOperator(id=workspace_id, credential=credential)
    with patch("fabric.operator.workspace.ItemOperator") as MockItemOperator:
        instance = MockItemOperator.return_value
        result = operator.items
        assert result == instance
        # Should be cached
        assert operator._WorkspaceOperator__cached_item_operators[workspace_id] == instance

def test_workspace_operator_data_pipelines_property(credential):
    workspace_id = "ws3"
    operator = WorkspaceOperator(id=workspace_id, credential=credential)
    with patch("fabric.operator.workspace.DataPipelineOperator") as MockPipelineOperator:
        instance = MockPipelineOperator.return_value
        result = operator.data_pipelines
        assert result == instance
        assert operator._WorkspaceOperator__cached_data_pipeline_operators[workspace_id] == instance

def test_workspace_operator_folders_property(credential):
    workspace_id = "ws4"
    operator = WorkspaceOperator(id=workspace_id, credential=credential)
    with patch("fabric.operator.workspace.FolderOperator") as MockFolderOperator:
        instance = MockFolderOperator.return_value
        result = operator.folders
        assert result == instance
        assert operator._WorkspaceOperator__cached_folder_operators[workspace_id] == instance

def test_workspace_operator_lakehouses_property(credential):
    workspace_id = "ws5"
    operator = WorkspaceOperator(id=workspace_id, credential=credential)
    with patch("fabric.operator.workspace.LakehouseOperator") as MockLakehouseOperator:
        instance = MockLakehouseOperator.return_value
        result = operator.lakehouses
        assert result == instance
        assert operator._WorkspaceOperator__cached_lakehouse_operators[workspace_id] == instance

def test_workspace_operator_spark_job_definitions_property(credential):
    workspace_id = "ws6"
    operator = WorkspaceOperator(id=workspace_id, credential=credential)
    with patch("fabric.operator.workspace.SparkJobDefinitionOperator") as MockSparkJobDefOperator:
        instance = MockSparkJobDefOperator.return_value
        result = operator.spark_job_definitions
        assert result == instance
        assert operator._WorkspaceOperator__cached_spark_job_definition_operators[workspace_id] == instance