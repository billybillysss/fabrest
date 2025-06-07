import asyncio
import logging
from typing import Any, Dict, Optional, List
import requests
import aiohttp

logger = logging.getLogger(__name__)


def _create_logger(data: dict, status_code: int, url: str):
    display_name = data.get("displayName")
    id = data.get("id")
    status = "accepted" if status_code == 202 else "created"
    log_parts = []

    if display_name:
        log_parts.append(f"'{display_name}'")
    if id:
        log_parts.append(f"(id: {id})")

    if log_parts:
        log_parts.append(f"{status}.")
        log_msg = " ".join(log_parts)
    else:
        log_msg = f"Create request {status} - URL: {url}"
    logger.info(log_msg)


class CreateMixin:
    def create(
        self,
        payload: dict,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        wait_for_completion: bool = True,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ):
        """Creates an item in a workspace."""
        method = "POST"
        display_name = payload.get("displayName")

        url = kwargs.get("url") or self.url

        try:
            response = self.client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                params=params,
                json=payload,
                timeout=timeout,
                wait_for_completion=wait_for_completion,
                throttle_retry_interval=throttle_retry_interval,
                lro_check_interval=lro_check_interval,
                item_name_in_use_max_retries=item_name_in_use_max_retries,
                item_name_in_use_retry_interval=item_name_in_use_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            resp_code = response.status_code
            try:
                data = response.json()
            except Exception:
                data = {}
            _create_logger(data, resp_code, url)
            return response
        except Exception:
            log_part = f"{display_name}" if display_name else "resource"
            logger.error(f"Error creating {log_part} - URL: {url}")
            raise
        finally:
            self.client.close_session_if_owned(session)

    def create_many(
        self,
        payloads: list,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        wait_for_completion: bool = True,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ):
        """Creates multiple items in a workspace."""
        responses = []
        _session = self.client._get_or_create_session(session)
        try:
            for payload in payloads:
                response = self.create(
                    payload=payload,
                    session=_session,
                    headers=headers,
                    params=params,
                    timeout=timeout,
                    wait_for_completion=wait_for_completion,
                    throttle_retry_interval=throttle_retry_interval,
                    lro_check_interval=lro_check_interval,
                    item_name_in_use_max_retries=item_name_in_use_max_retries,
                    item_name_in_use_retry_interval=item_name_in_use_retry_interval,
                    max_retries=max_retries,
                    retry_interval=retry_interval,
                    **kwargs,
                )
                responses.append(response)
        except Exception:
            raise
        finally:
            self.client.close_session_if_owned(session)
        return responses

    async def async_create(
        self,
        payload: Dict[str, Any],
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        wait_for_completion: bool = True,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """Creates an item in a workspace."""
        method = "POST"
        display_name = payload.get("displayName")

        url = kwargs.get("url") or self.url
        try:
            response = await self.async_client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                params=params,
                json=payload,
                timeout=timeout,
                wait_for_completion=wait_for_completion,
                throttle_retry_interval=throttle_retry_interval,
                lro_check_interval=lro_check_interval,
                item_name_in_use_max_retries=item_name_in_use_max_retries,
                item_name_in_use_retry_interval=item_name_in_use_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            resp_code = response.status
            try:
                data = await response.json()
            except Exception:
                data = {}
            _create_logger(data, resp_code, url)
            return response
        except Exception:
            log_part = f"{display_name}" if display_name else "resource"
            logger.error(f"Error creating {log_part} - URL: {url}")
            raise
        finally:
            await self.async_client.close_session_if_owned(session)

    async def async_create_many(
        self,
        payloads: list,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        wait_for_completion: bool = True,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    )-> List[aiohttp.ClientResponse]:
        """Creates multiple items in a workspace."""
        tasks = []
        _session = await self.async_client._get_or_create_session(session)
        for payload in payloads:
            tasks.append(
                self.async_create(
                    payload=payload,
                    session=_session,
                    headers=headers,
                    params=params,
                    timeout=timeout,
                    wait_for_completion=wait_for_completion,
                    throttle_retry_interval=throttle_retry_interval,
                    lro_check_interval=lro_check_interval,
                    item_name_in_use_max_retries=item_name_in_use_max_retries,
                    item_name_in_use_retry_interval=item_name_in_use_retry_interval,
                    max_retries=max_retries,
                    retry_interval=retry_interval,
                    **kwargs,
                )
            )
        try:
            responses = await asyncio.gather(*tasks)
        except Exception:
            raise
        finally:
            await self.async_client.close_session_if_owned(session)
        return responses
