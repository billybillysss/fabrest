import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.storage.filedatalake import DataLakeDirectoryClient
from azure.storage.filedatalake.aio import (
    DataLakeDirectoryClient as AsyncDataLakeDirectoryClient,
)
from azure.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class DataLakeOperator:
    def __init__(
        self,
        workspace_id: str,
        lakehouse_id: str,
        credential: Any,
        working_directory: Optional[str] = None,
    ):
        """
        Initialize the DataLakeOperator.

        :param workspace_id: The workspace ID.
        :param lakehouse_id: The lakehouse ID.
        :param credential: The credential for authentication.
        :param working_directory: Optional working directory within the lakehouse.
        """
        self.workspace_id = workspace_id
        self.lakehouse_id = lakehouse_id
        self.account_url = "https://onelake.dfs.fabric.microsoft.com"
        self.credential = credential
        self._base_directory = (
            Path(f"{self.lakehouse_id}/Files") / working_directory
            if working_directory else Path(f"{self.lakehouse_id}/Files")
        ).as_posix()
        self._directory_client = None

    @property
    def directory_client(self) -> DataLakeDirectoryClient:
        if not self._directory_client:
            self._directory_client = DataLakeDirectoryClient(
                account_url=self.account_url,
                credential=self.credential,
                file_system_name=self.workspace_id,
                directory_name=self._base_directory,
            )
        return self._directory_client

    def get_paths(self):
        """Get paths in the directory."""
        return self.directory_client.get_paths()

    def upload(self, file_path: str, file_content: Any, overwrite: bool = True):
        """Upload a file to the data lake."""
        file_client = self.directory_client.get_file_client(file_path)
        file_client.upload_data(file_content, overwrite=overwrite)
        logger.info(f"Uploaded to ({file_path})")

    def upload_many(self, payloads: List[Dict[str, Any]]):
        """Upload multiple files to the data lake."""
        for payload in payloads:
            self.upload(
                payload["path"],
                payload["content"],
                payload.get("overwrite", True),
            )
        logger.info("Upload completed.")

    def delete_many(self, payloads: List[Dict[str, Any]]):
        """Delete multiple files or directories from the data lake."""
        for payload in payloads:
            self.delete(payload["path"], payload["is_directory"])
        logger.info("Deletion completed.")

    def delete(self, path: str, is_directory: bool):
        """Delete a file or directory from the data lake."""
        if is_directory:
            try:
                self.directory_client.delete_sub_directory(path)
                logger.info(f"Folder {path} deleted")
            except ResourceNotFoundError:
                logger.warning(
                    f"Directory not found during deletion (possibly already deleted) - Path: {path}"
                )
            except Exception as e:
                logger.error(f"Unexpected error deleting directory {path}: {e}")
        else:
            try:
                self.directory_client.get_file_client(path).delete_file()
                logger.info(f"File {path} deleted")
            except ResourceNotFoundError:
                logger.warning(
                    f"File not found during deletion (possibly already deleted) - Path: {path}"
                )
            except Exception as e:
                logger.error(f"Unexpected error deleting file {path}: {e}")

    async def async_get_paths(self):
        """Asynchronously get paths in the directory."""
        async with AsyncDataLakeDirectoryClient(
            account_url=self.account_url,
            credential=self.credential,
            file_system_name=self.workspace_id,
            directory_name=self._base_directory,
        ) as directory_client:
            async for path in directory_client.get_paths():
                yield path

    async def async_upload(
        self,
        file_path: str,
        file_content: Any,
        overwrite: bool = True,
        directory_client: Optional[AsyncDataLakeDirectoryClient] = None,
    ):
        """Asynchronously upload a file to the data lake."""
        own_client = directory_client is None

        if not directory_client:
            directory_client = AsyncDataLakeDirectoryClient(
                account_url=self.account_url,
                credential=self.credential,
                file_system_name=self.workspace_id,
                directory_name=self._base_directory,
            )

        file_client = directory_client.get_file_client(file_path)
        await file_client.upload_data(file_content, overwrite=overwrite)
        logger.info(f"Uploaded to ({file_path})")

        if own_client:
            await directory_client.close()

    async def async_upload_many(self, payloads: List[Dict[str, Any]]):
        """Asynchronously upload multiple files to the data lake."""
        async with AsyncDataLakeDirectoryClient(
            account_url=self.account_url,
            credential=self.credential,
            file_system_name=self.workspace_id,
            directory_name=self._base_directory,
        ) as directory_client:
            tasks = []
            for payload in payloads:
                tasks.append(
                    self.async_upload(
                        payload["path"],
                        payload["content"],
                        payload.get("overwrite", True),
                        directory_client,
                    )
                )
            await asyncio.gather(*tasks)
        logger.info("Files uploaded.")

    async def async_delete(
        self,
        path: str,
        is_directory: bool = False,
        directory_client: Optional[AsyncDataLakeDirectoryClient] = None,
    ):
        """Asynchronously delete a file or directory from the data lake."""
        own_client = directory_client is None

        if not directory_client:
            directory_client = AsyncDataLakeDirectoryClient(
                account_url=self.account_url,
                credential=self.credential,
                file_system_name=self.workspace_id,
                directory_name=self._base_directory,
            )

        if is_directory:
            try:
                await directory_client.delete_sub_directory(path)
                logger.info(f"Folder ({path}) deleted")
            except ResourceNotFoundError:
                logger.warning(
                    f"Directory not found during deletion (possibly already deleted) - Path: '{path}'"
                )
            except Exception as e:
                logger.error(f"Unexpected error deleting directory {path}: {e}")
        else:
            try:
                await directory_client.get_file_client(path).delete_file()
                logger.info(f"File ({path}) deleted")
            except ResourceNotFoundError:
                logger.warning(
                    f"File not found during deletion (possibly already deleted) - Path: '{path}'"
                )
            except Exception as e:
                logger.error(f"Unexpected error deleting file {path}: {e}")
        if own_client:
            await directory_client.close()

    async def async_delete_many(self, payloads: List[Dict[str, Any]]):
        """Asynchronously delete multiple files or directories from the data lake."""
        async with AsyncDataLakeDirectoryClient(
            account_url=self.account_url,
            credential=self.credential,
            file_system_name=self.workspace_id,
            directory_name=self._base_directory,
        ) as directory_client:
            tasks = []
            for payload in payloads:
                tasks.append(
                    self.async_delete(
                        payload["path"], payload["is_directory"], directory_client
                    )
                )
            await asyncio.gather(*tasks)
            logger.info("Deletion completed.")
