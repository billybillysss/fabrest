from ..api.list import ListMixin
from ..api.get import GetMixin
from ..api.create import CreateMixin
from ..api.update import UpdateMixin
from ..api.delete import DeleteMixin
from ..api.url import URL
from ..api.constant import SparkOperation
from .base import BaseOperator
from typing import Dict, List, Optional
import requests
import aiohttp


class SparkOperator(
    BaseOperator,
):
    def __init__(self, workspace_id, item_type="Spark", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = item_type
        self.url = URL.get_item_url(workspace_id=self.workspace_id, item_type=item_type)
        self._cache_operator = {
            "pool": None,
            "livy_session": None,
            "setting": None,
        }

    @property
    def pools(self):
        pool_operator = self._cache_operator["pool"]
        if not pool_operator:
            pool_operator = SparkPoolOperator(
                workspace_id=self.workspace_id, credential=self.credential
            )
            self._cache_operator["pool"] = pool_operator
        return pool_operator

    @property
    def settings(self):
        setting_operator = self._cache_operator["setting"]
        if not setting_operator:
            setting_operator = SparkSettingOperator(
                workspace_id=self.workspace_id, credential=self.credential
            )
            self._cache_operator["setting"] = setting_operator
        return setting_operator

    @property
    def livy_sessions(self):
        livy_session_operator = self._cache_operator["livy_session"]
        if not livy_session_operator:
            livy_session_operator = LivySessionOperator(
                workspace_id=self.workspace_id, credential=self.credential
            )
            self._cache_operator["livy_session"] = livy_session_operator
        return livy_session_operator


class LivySessionOperator(
    ListMixin,
    GetMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, item_id=None, item_type="Spark", credential=None):
        super().__init__(credential=credential)
        self.workspace_id = workspace_id
        self.item_type = None
        self.spark_resource_type = SparkOperation.LivySessions.value
        self.url = (
            URL.get_item_url(
                workspace_id=self.workspace_id, item_type=item_type, item_id=item_id
            )
            + f"/{self.spark_resource_type}"
        )


class SparkPoolOperator(
    CreateMixin,
    ListMixin,
    GetMixin,
    UpdateMixin,
    DeleteMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, config_type="Spark", credential=None):
        super().__init__(credential)
        self.workspace_id = workspace_id
        self.spark_resource_type = SparkOperation.Pool.value
        self.url = (
            URL.get_workspace_config_url(workspace_id=self.workspace_id, config_type=config_type)
            + f"/{self.spark_resource_type}"
        )


class SparkSettingOperator(
    GetMixin,
    UpdateMixin,
    BaseOperator,
):
    def __init__(self, workspace_id, item_type="Spark", credential=None):
        super().__init__(credential)
        self.workspace_id = workspace_id
        self.spark_resource_type = SparkOperation.Setting.value
        self.url = URL.get_item_url(
            workspace_id=self.workspace_id,
            item_type=item_type,
        )

    def get(
        self,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> dict:
        return GetMixin.get(
            self,
            id=self.spark_resource_type,
            session=session,
            headers=headers,
            timeout=timeout,
            throttle_retry_interval=throttle_retry_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            **kwargs,
        )

    def update(
        self,
        payload,
        session=None,
        headers=None,
        timeout=None,
        throttle_retry_interval=None,
        max_retries=0,
        retry_interval=5,
        **kwargs,
    ):
        return UpdateMixin.update(
            self,
            id=self.spark_resource_type,
            payload=payload,
            session=session,
            headers=headers,
            timeout=timeout,
            throttle_retry_interval=throttle_retry_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            **kwargs,
        )

    async def async_get(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> dict:
        return await GetMixin.async_get(
            self,
            id=self.spark_resource_type,
            session=session,
            headers=headers,
            timeout=timeout,
            throttle_retry_interval=throttle_retry_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            **kwargs,
        )

    async def async_update(
        self,
        payload,
        session=None,
        headers=None,
        timeout=None,
        throttle_retry_interval=None,
        max_retries=0,
        retry_interval=5,
        **kwargs,
    ):
        return await UpdateMixin.async_update(
            self,
            id=self.spark_resource_type,
            payload=payload,
            session=session,
            headers=headers,
            timeout=timeout,
            throttle_retry_interval=throttle_retry_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            **kwargs,
        )
