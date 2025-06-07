import logging
from typing import Dict, Optional, Any
import requests
import asyncio
import aiohttp
from ..utils.functions import decode_base64
import json

logger = logging.getLogger(__name__)


def _get_payload_logger(data):
    """
    Log retrieval of an item, including display name and id if present.
    """
    display_name = data.get("displayName")
    id = data.get("id")
    log_parts = []
    if display_name:
        log_parts.append(f"'{display_name}'")
    if id:
        log_parts.append(f"(id: {id})")
    if display_name or id:
        log_parts.append("retrieved.")
        log_msg = " ".join(log_parts)
    else:
        log_msg = "Resource retrieved."
    logger.info(log_msg)


def _get_def_payload_logger(data):
    """
    Log retrieval of an item, including display name and id if present.
    """
    parts = data["definition"]["parts"]

    encoded_platform = next(
        (p["payload"] for p in parts if p["path"] == ".platform"), {}
    )
    decoded_platform = json.loads(decode_base64(encoded_platform))
    metadata = decoded_platform.get("metadata")
    display_name = metadata.get("displayName")
    item_type = metadata.get("type")

    log_parts = []
    if item_type:
        log_parts.append(item_type)
    if display_name:
        log_parts.append(f"'{display_name}'")

    if display_name or id:
        log_parts.append("retrieved.")
        log_msg = " ".join(log_parts)
    else:
        log_msg = "Resource retrieved."
    logger.info(log_msg)


class GetMixin:
    def get(
        self,
        id: str,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> dict:
        """Gets an item in a workspace."""
        method = "GET"
        url = kwargs.get("url") or self.url
        if id:
            url += f"/{id}"
        try:
            response = self.client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                timeout=timeout,
                throttle_retry_interval=throttle_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            data = response.json()
            _get_payload_logger(data)
            return data
        except Exception:
            logger.error(f"Error retrieving  - URL {url}")
            raise
        finally:
            self.client.close_session_if_owned(session)

    async def async_get(
        self,
        id: str,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> dict:
        """Gets an item in a workspace."""
        method = "GET"
        url = kwargs.get("url") or self.url
        if id:
            url += f"/{id}"
        try:
            response = await self.async_client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                timeout=timeout,
                throttle_retry_interval=throttle_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            data = await response.json()
            _get_payload_logger(data)
            return data
        except Exception:
            logger.error(f"Error retrieving  - URL {url}")
            raise
        finally:
            await self.async_client.close_session_if_owned(session)


class GetDefinitionMixin:
    def get_definition(
        self,
        id: str,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> dict:
        """gets an item in a workspace."""
        method = "POST"
        url = self.url + f"/{id}" + "/getDefinition"
        url = kwargs.get("url") or url
        try:
            response = self.client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                timeout=timeout,
                throttle_retry_interval=throttle_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            data = response.json()
            _get_def_payload_logger(data)
            return data
        except Exception:
            logger.error(f"Error retrieving  - URL {url}")
            raise
        finally:
            self.client.close_session_if_owned(session)

    def get_definition_many(
        self,
        ids: list,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> list:
        """gets items in a workspace."""
        results = []
        _session = self.client._get_or_create_session(session)
        try:
            for id in ids:
                data = self.get_definition(
                    id=id,
                    session=_session,
                    headers=headers,
                    timeout=timeout,
                    throttle_retry_interval=throttle_retry_interval,
                    max_retries=max_retries,
                    retry_interval=retry_interval,
                    **kwargs,
                )
                results.append(data)
        except Exception:
            raise
        finally:
            self.client.close_session_if_owned(session=session)
        return results

    async def async_get_definition(
        self,
        id: str,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> dict:
        """gets an item in a workspace."""
        method = "POST"
        url = self.url + f"/{id}" + "/getDefinition"
        url = kwargs.get("url") or url

        try:
            response = await self.async_client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                timeout=timeout,
                throttle_retry_interval=throttle_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )

            data = await response.json()
            _get_def_payload_logger(data)
            return data
        except Exception:
            logger.error(f"Error retrieving  - URL {url}")
            raise
        finally:
            await self.async_client.close_session_if_owned(session)

    async def async_get_definition_many(
        self,
        ids: list,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> list:
        """gets items in a workspace."""
        tasks = []
        results = []
        _session = await self.async_client._get_or_create_session(session)

        for id in ids:
            tasks.append(
                self.async_get_definition(
                    id=id,
                    session=_session,
                    headers=headers,
                    timeout=timeout,
                    throttle_retry_interval=throttle_retry_interval,
                    max_retries=max_retries,
                    retry_interval=retry_interval,
                    **kwargs,
                )
            )
        try:
            results = await asyncio.gather(*tasks)
        except Exception:
            raise
        finally:
            await self.async_client.close_session_if_owned(session)
        return results
