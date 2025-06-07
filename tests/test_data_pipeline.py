#!/usr/bin/env python3
"""
Test script for fabrest Data Pipeline operations.
Tests CRUD operations and definition management for data pipelines.
Supports both synchronous and asynchronous operations.
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

import pytest

# Add parent directories to sys.path for local imports
src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

from fabrest.operator.workspace import WorkspaceOperator
from fabrest.api.auth import ClientSecretCredential
from fabrest.operator.data_pipeline import DataPipelineOperator
from fabrest.utils.functions import encode_base64, decode_base64
from fabrest.logger import logger


class DataPipelineTestSuite:
    """Test suite for Data Pipeline operations (synchronous)."""
    
    def __init__(self, test_item_name: str):
        """Initialize test suite with credentials and operators."""
        self.workspace_id = self._get_env_var("TEST_WORKSPACE_ID")
        self.client_id = self._get_env_var("CLIENT_ID")
        self.client_secret = self._get_env_var("CLIENT_SECRET")
        self.tenant_id = self._get_env_var("TENANT_ID")
        
        self.credential = ClientSecretCredential(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )
        
        self.operator = WorkspaceOperator(
            id=self.workspace_id, 
            credential=self.credential
        )
        
        self.success_codes = {200, 201, 202, 204}  # Added 204 for delete
        self.test_item_name = test_item_name
        self.updated_item_name = test_item_name + "_update"
        self.pipeline_id: Optional[str] = None
    
    @staticmethod
    def _get_env_var(var_name: str) -> str:
        """Get environment variable with error handling."""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Environment variable {var_name} is not set")
        return value
    
    def test_create_pipeline(self) -> Dict[str, Any]:
        """Test creating a new data pipeline."""
        logger.info(f"Creating pipeline: {self.test_item_name}")
        
        payload = {"displayName": self.test_item_name}
        response = self.operator.data_pipelines.create(payload=payload)
        
        assert response.status_code in self.success_codes, \
            f"Create failed with status: {response.status_code}"
        
        data = response.json()
        assert data["displayName"] == self.test_item_name, \
            f"Expected name {self.test_item_name}, got {data['displayName']}"
        
        self.pipeline_id = data["id"]
        logger.info(f"Pipeline created successfully with ID: {self.pipeline_id}")
        return data
    
    def test_list_pipelines(self) -> Dict[str, Any]:
        """Test listing pipelines and finding the created one."""
        logger.info("Listing pipelines")
        
        pipelines = self.operator.data_pipelines.list()
        assert isinstance(pipelines, list), "Expected list of pipelines"
        
        # Find our test pipeline
        test_pipeline = next(
            (item for item in pipelines if item["displayName"] == self.test_item_name),
            None
        )
        
        assert test_pipeline is not None, \
            f"Pipeline {self.test_item_name} not found in list"
        
        logger.info(f"Pipeline found in list: {test_pipeline['id']}")
        return test_pipeline
    
    def test_get_pipeline(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test getting a specific pipeline by ID."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Getting pipeline: {pipeline_id}")
        
        data = self.operator.data_pipelines.get(id=pipeline_id)
        assert data["displayName"] == self.test_item_name, \
            f"Expected name {self.test_item_name}, got {data['displayName']}"
        
        logger.info("Pipeline retrieved successfully")
        return data
    
    def test_update_pipeline(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test updating pipeline display name."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Updating pipeline {pipeline_id} to {self.updated_item_name}")
        
        payload = {"displayName": self.updated_item_name}
        response = self.operator.data_pipelines.update(
            id=pipeline_id, 
            payload=payload
        )
        
        assert response.status_code in self.success_codes, \
            f"Update failed with status: {response.status_code}"
        
        data = response.json()
        assert data["displayName"] == self.updated_item_name, \
            f"Expected updated name {self.updated_item_name}, got {data['displayName']}"
        
        logger.info("Pipeline updated successfully")
        return data
    
    def test_update_pipeline_definition(self, pipeline_data: Dict[str, Any]) -> None:
        """Test updating pipeline definition with new activities."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Updating pipeline definition for {pipeline_id}")
        
        # Define new pipeline content
        update_def_payload = {
            "properties": {
                "activities": [
                    {
                        "name": "Updated_Wait",
                        "type": "Wait",
                        "dependsOn": [],
                        "typeProperties": {"waitTimeInSeconds": 15},
                    }
                ]
            }
        }
        
        # Get current definition
        current_definition = self.operator.data_pipelines.get_definition(id=pipeline_id)
        parts = current_definition["definition"]["parts"]
        
        # Update pipeline content
        pipeline_content = json.dumps(update_def_payload)
        pipeline_part = next(
            (p for p in parts if p["path"] == "pipeline-content.json"),
            None
        )
        
        if pipeline_part:
            pipeline_part["payload"] = encode_base64(pipeline_content)
        else:
            # Add new pipeline content part if it doesn't exist
            parts.append({
                "path": "pipeline-content.json",
                "payload": encode_base64(pipeline_content)
            })
        
        # Update definition
        response = self.operator.data_pipelines.update_definition(
            id=pipeline_id, 
            payload=current_definition
        )
        
        assert response.status_code in self.success_codes, \
            f"Definition update failed with status: {response.status_code}"
        
        logger.info("Pipeline definition updated successfully")
    
    def test_get_pipeline_definition(self, pipeline_data: Dict[str, Any]) -> None:
        """Test retrieving and validating pipeline definition."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Getting pipeline definition for {pipeline_id}")
        
        data = self.operator.data_pipelines.get_definition(id=pipeline_id)
        parts = data["definition"]["parts"]
        
        # Validate platform metadata
        encoded_platform = next(
            (p["payload"] for p in parts if p["path"] == ".platform"),
            None
        )
        
        if encoded_platform:
            decoded_platform = json.loads(decode_base64(encoded_platform))
            metadata = decoded_platform.get("metadata", {})
            display_name = metadata.get("displayName")
            logger.info(f"Platform metadata display name: {display_name}")
        
        # Validate pipeline content
        encoded_pipeline = next(
            (p["payload"] for p in parts if p["path"] == "pipeline-content.json"),
            None
        )
        
        assert encoded_pipeline is not None, "Pipeline content not found"
        
        decoded_pipeline = json.loads(decode_base64(encoded_pipeline))
        activities = decoded_pipeline.get("properties", {}).get("activities", [])
        
        assert len(activities) > 0, "No activities found in pipeline"
        assert activities[0]["name"] == "Updated_Wait", \
            f"Expected activity name 'Updated_Wait', got {activities[0]['name']}"
        
        logger.info("Pipeline definition validated successfully")
    
    def test_delete_pipeline(self, pipeline_data: Dict[str, Any]) -> None:
        """Test deleting a pipeline."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Deleting pipeline: {pipeline_id}")
        
        response = self.operator.data_pipelines.delete(id=pipeline_id)
        
        assert response.status_code in self.success_codes, \
            f"Delete failed with status: {response.status_code}"
        
        logger.info("Pipeline deleted successfully")
        
        # Verify deletion by trying to get the pipeline (should fail)
        try:
            self.operator.data_pipelines.get(id=pipeline_id)
            assert False, "Pipeline still exists after deletion"
        except Exception as e:
            logger.info(f"Confirmed pipeline deletion: {e}")
    
    def run_all_tests(self) -> None:
        """Run all tests in sequence."""
        try:
            logger.info("Starting Data Pipeline test suite (sync)")
            
            # Test create
            pipeline_data = self.test_create_pipeline()
            
            # Test list
            listed_pipeline = self.test_list_pipelines()
            
            # Test get
            retrieved_pipeline = self.test_get_pipeline(listed_pipeline)
            
            # Test update
            updated_pipeline = self.test_update_pipeline(retrieved_pipeline)
            
            # Test update definition
            self.test_update_pipeline_definition(updated_pipeline)
            
            # Test get definition
            self.test_get_pipeline_definition(updated_pipeline)
            
            # Test delete
            self.test_delete_pipeline(updated_pipeline)
            
            logger.info("All synchronous tests completed successfully!")
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise


class AsyncDataPipelineTestSuite:
    """Test suite for Data Pipeline operations (asynchronous)."""
    
    def __init__(self, test_item_name: str):
        """Initialize async test suite with credentials and operators."""
        self.workspace_id = self._get_env_var("TEST_WORKSPACE_ID")
        self.client_id = self._get_env_var("CLIENT_ID")
        self.client_secret = self._get_env_var("CLIENT_SECRET")
        self.tenant_id = self._get_env_var("TENANT_ID")
        
        self.credential = ClientSecretCredential(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )
        
        self.operator = WorkspaceOperator(
            id=self.workspace_id, 
            credential=self.credential
        )
        
        self.success_codes = {200, 201, 202, 204}
        self.test_item_name = test_item_name+"_async"
        self.updated_item_name = test_item_name + "_async_update"
        self.pipeline_id: Optional[str] = None
    
    @staticmethod
    def _get_env_var(var_name: str) -> str:
        """Get environment variable with error handling."""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Environment variable {var_name} is not set")
        return value
    
    async def test_create_pipeline_async(self) -> Dict[str, Any]:
        """Test creating a new data pipeline (async)."""
        logger.info(f"Creating pipeline (async): {self.test_item_name}")
        
        payload = {"displayName": self.test_item_name}
        response = await self.operator.data_pipelines.async_create(payload=payload)
        
        assert response.status in self.success_codes, \
            f"Async create failed with status: {response.status}"
        
        data = await response.json()
        assert data["displayName"] == self.test_item_name, \
            f"Expected name {self.test_item_name}, got {data['displayName']}"
        
        self.pipeline_id = data["id"]
        logger.info(f"Pipeline created successfully (async) with ID: {self.pipeline_id}")
        return data
    
    async def test_list_pipelines_async(self) -> Dict[str, Any]:
        """Test listing pipelines and finding the created one (async)."""
        logger.info("Listing pipelines (async)")
        
        pipelines = await self.operator.data_pipelines.async_list()
        assert isinstance(pipelines, list), "Expected list of pipelines"
        
        # Find our test pipeline
        test_pipeline = next(
            (item for item in pipelines if item["displayName"] == self.test_item_name),
            None
        )
        
        assert test_pipeline is not None, \
            f"Pipeline {self.test_item_name} not found in list"
        
        logger.info(f"Pipeline found in list (async): {test_pipeline['id']}")
        return test_pipeline
    
    async def test_get_pipeline_async(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test getting a specific pipeline by ID (async)."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Getting pipeline (async): {pipeline_id}")
        
        data = await self.operator.data_pipelines.async_get(id=pipeline_id)
        assert data["displayName"] == self.test_item_name, \
            f"Expected name {self.test_item_name}, got {data['displayName']}"
        
        logger.info("Pipeline retrieved successfully (async)")
        return data
    
    async def test_update_pipeline_async(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test updating pipeline display name (async)."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Updating pipeline (async) {pipeline_id} to {self.updated_item_name}")
        
        payload = {"displayName": self.updated_item_name}
        response = await self.operator.data_pipelines.async_update(
            id=pipeline_id, 
            payload=payload
        )
        
        assert response.status in self.success_codes, \
            f"Async update failed with status: {response.status}"
        
        data = await self.operator.data_pipelines.async_get(id=pipeline_id)
        assert data["displayName"] == self.updated_item_name, \
            f"Expected updated name {self.updated_item_name}, got {data['displayName']}"
        
        logger.info("Pipeline updated successfully (async)")
        return data
    
    async def test_update_pipeline_definition_async(self, pipeline_data: Dict[str, Any]) -> None:
        """Test updating pipeline definition with new activities (async)."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Updating pipeline definition (async) for {pipeline_id}")
        
        # Define new pipeline content
        update_def_payload = {
            "properties": {
                "activities": [
                    {
                        "name": "Async_Updated_Wait",
                        "type": "Wait",
                        "dependsOn": [],
                        "typeProperties": {"waitTimeInSeconds": 20},
                    }
                ]
            }
        }
        
        # Get current definition
        current_definition = await self.operator.data_pipelines.async_get_definition(id=pipeline_id)
        parts = current_definition["definition"]["parts"]
        
        # Update pipeline content
        pipeline_content = json.dumps(update_def_payload)
        pipeline_part = next(
            (p for p in parts if p["path"] == "pipeline-content.json"),
            None
        )
        
        if pipeline_part:
            pipeline_part["payload"] = encode_base64(pipeline_content)
        else:
            # Add new pipeline content part if it doesn't exist
            parts.append({
                "path": "pipeline-content.json",
                "payload": encode_base64(pipeline_content)
            })
        
        # Update definition
        response = await self.operator.data_pipelines.async_update_definition(
            id=pipeline_id, 
            payload=current_definition
        )
        
        assert response.status in self.success_codes, \
            f"Async definition update failed with status: {response.status}"
        
        logger.info("Pipeline definition updated successfully (async)")
    
    async def test_get_pipeline_definition_async(self, pipeline_data: Dict[str, Any]) -> None:
        """Test retrieving and validating pipeline definition (async)."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Getting pipeline definition (async) for {pipeline_id}")
        
        data = await self.operator.data_pipelines.async_get_definition(id=pipeline_id)
        parts = data["definition"]["parts"]
        
        # Validate platform metadata
        encoded_platform = next(
            (p["payload"] for p in parts if p["path"] == ".platform"),
            None
        )
        
        if encoded_platform:
            decoded_platform = json.loads(decode_base64(encoded_platform))
            metadata = decoded_platform.get("metadata", {})
            display_name = metadata.get("displayName")
            logger.info(f"Platform metadata display name (async): {display_name}")
        
        # Validate pipeline content
        encoded_pipeline = next(
            (p["payload"] for p in parts if p["path"] == "pipeline-content.json"),
            None
        )
        
        assert encoded_pipeline is not None, "Pipeline content not found"
        
        decoded_pipeline = json.loads(decode_base64(encoded_pipeline))
        activities = decoded_pipeline.get("properties", {}).get("activities", [])
        
        assert len(activities) > 0, "No activities found in pipeline"
        assert activities[0]["name"] == "Async_Updated_Wait", \
            f"Expected activity name 'Async_Updated_Wait', got {activities[0]['name']}"
        
        logger.info("Pipeline definition validated successfully (async)")
    
    async def test_delete_pipeline_async(self, pipeline_data: Dict[str, Any]) -> None:
        """Test deleting a pipeline (async)."""
        pipeline_id = pipeline_data["id"]
        logger.info(f"Deleting pipeline (async): {pipeline_id}")
        
        response = await self.operator.data_pipelines.async_delete(id=pipeline_id)
        
        assert response.status in self.success_codes, \
            f"Async delete failed with status: {response.status}"
        
        logger.info("Pipeline deleted successfully (async)")
        
        # Verify deletion by trying to get the pipeline (should fail)
        try:
            await self.operator.data_pipelines.async_get(id=pipeline_id)
            assert False, "Pipeline still exists after deletion"
        except Exception as e:
            logger.info(f"Confirmed pipeline deletion (async): {e}")
    
    async def run_all_tests_async(self) -> None:
        """Run all async tests in sequence."""
        try:
            logger.info("Starting Data Pipeline test suite (async)")
            
            # Test create
            pipeline_data = await self.test_create_pipeline_async()
            
            # Test list
            listed_pipeline = await self.test_list_pipelines_async()
            
            # Test get
            retrieved_pipeline = await self.test_get_pipeline_async(listed_pipeline)
            
            # Test update
            updated_pipeline = await self.test_update_pipeline_async(retrieved_pipeline)
            
            # Test update definition
            await self.test_update_pipeline_definition_async(updated_pipeline)
            
            # Test get definition
            await self.test_get_pipeline_definition_async(updated_pipeline)
            
            # Test delete
            await self.test_delete_pipeline_async(updated_pipeline)
            
            logger.info("All asynchronous tests completed successfully!")
            
        except Exception as e:
            logger.error(f"Async test suite failed: {e}")
            raise
    async def cleanup_pipeline(self, pipeline_name_prefix: str) -> None:
        """Delete all pipelines with the given name prefix."""
        pipelines = await self.operator.data_pipelines.async_list()
        ids = [pipeline["id"] for pipeline in pipelines]
        await self.operator.data_pipelines.async_delete_many(ids=ids)

def main():
    """Main entry point for running tests."""
    test_item_prefix = "pl_test_"
    test_number = 7
    test_item_name = test_item_prefix + str(test_number)

    try:
        # Run synchronous tests
        print("=" * 60)
        print("RUNNING SYNCHRONOUS TESTS")
        print("=" * 60)
        sync_test_suite = DataPipelineTestSuite(test_item_name)
        sync_test_suite.run_all_tests()
        
        # Run asynchronous tests
        print("\n" + "=" * 60)
        print("RUNNING ASYNCHRONOUS TESTS")
        print("=" * 60)
        async_test_suite = AsyncDataPipelineTestSuite(test_item_name)
        asyncio.run(async_test_suite.run_all_tests_async())

    finally:
        print("\n" + "=" * 60)
        print("Cleaning up")
        print("=" * 60)
        asyncio.run(async_test_suite.cleanup_pipeline(test_item_prefix))

if __name__ == "__main__":
    main()