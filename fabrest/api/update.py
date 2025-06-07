from typing import Any, Dict, List, Optional
import asyncio
import logging
import requests
import aiohttp

logger = logging.getLogger(__name__)


def _update_logger(data: dict, url: str):
    display_name = data.get("displayName")
    id = data.get("id")
    log_parts = []

    if display_name:
        log_parts.append(f"'{display_name}'")
    if id:
        log_parts.append(f"(id: {id})")

    if log_parts:
        log_parts.append("updated.")
        log_msg = " ".join(log_parts)
    else:
        log_msg = f"Update request completed - URL: {url}"
    logger.info(log_msg)


def _update_def_logger(payload: dict, status_code: int, url: str):
    display_name = payload.get("displayName")
    id = payload.get("id")
    status = "accepted" if status_code == 202 else "completed"
    log_parts = []

    if display_name:
        log_parts.append(f"'{display_name}'")
    if id:
        log_parts.append(f"(id: {id})")
    if log_parts:
        log_parts.append(f"definition update request {status}.")
        log_msg = " ".join(log_parts)
    else:
        log_msg = f"UpdateDefinition request {status} - URL: {url}"

    logger.info(log_msg)


def _get_exception_message(display_name):
    log_part = f"'{display_name}'" if display_name else "resource"
    return f"Error updating {log_part}"


class UpdateMixin:
    def update(
        self,
        id: str,
        payload: dict,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> requests.Response:
        """Updates an item in a workspace."""
        method = "PATCH"
        display_name = payload.get("displayName")
        url = self.url + f"/{id}"
        url = kwargs.get("url") or url
        try:
            response = self.client.request(
                method=method,
                json=payload,
                url=url,
                session=session,
                headers=headers,
                timeout=timeout,
                throttle_retry_interval=throttle_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            data = response.json()
            _update_logger(data, url)
            return response
        except Exception:
            except_msg = _get_exception_message(display_name)
            logger.error(except_msg)
            raise
        finally:
            self.client.close_session_if_owned(session)

    def update_many(
        self,
        payloads: dict,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> List[requests.Response]:
        """Updates items in a workspace."""

        responses = []
        _session = self.client._get_or_create_session(session)
        try:
            for id, payload in payloads.items():
                response = self.update(
                    id=id,
                    payload=payload,
                    session=_session,
                    headers=headers,
                    timeout=timeout,
                    throttle_retry_interval=throttle_retry_interval,
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

    async def async_update(
        self,
        id: str,
        payload: dict,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """Updates an item in a workspace."""
        method = "PATCH"
        display_name = payload.get("displayName")
        url = self.url + f"/{id}"
        url = kwargs.get("url") or url
        try:
            response = await self.async_client.request(
                method=method,
                json=payload,
                url=url,
                session=session,
                headers=headers,
                timeout=timeout,
                throttle_retry_interval=throttle_retry_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            data = await response.json()
            _update_logger(data, url)
            return response
        except Exception:
            except_msg = _get_exception_message(display_name)
            logger.error(except_msg)
            raise
        finally:
            await self.async_client.close_session_if_owned(session)

    async def async_update_many(
        self,
        payloads: dict,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> List[aiohttp.ClientResponse]:
        """Updates items in a workspace."""
        tasks = []
        _session = await self.async_client._get_or_create_session(session)
        for id, payload in payloads.items():
            tasks.append(
                self.async_update(
                    id=id,
                    payload=payload,
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
            return await asyncio.gather(*tasks)
        except Exception:
            raise
        finally:
            await self.async_client.close_session_if_owned(session)

class UpdateDefinitionMixin:
    def update_definition(
        self,
        id: str,
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
    ) -> requests.Response:
        """updates an item in a workspace."""
        method = "POST"
        display_name = payload.get("displayName")
        url = self.url + f"/{id}" + "/updateDefinition?updateMetadata=True"
        url = kwargs.get("url") or url
        def_payload = {"definition": payload.get("definition")}
        try:
            response = self.client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                params=params,
                json=def_payload,
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
            _update_def_logger(payload, resp_code, url)
            return response
        except Exception:
            except_msg = _get_exception_message(display_name)
            logger.error(f"{except_msg} - URL: {url}")
            raise
        finally:
            self.client.close_session_if_owned(session)

    def update_definition_many(
        self,
        payloads: dict,
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
    ) -> List[requests.Response]:
        """updates items in a workspace."""
        responses = []
        _session = self.client._get_or_create_session(session)
        try:
            for id, payload in payloads.items():
                response = self.update_definition(
                    id=id,
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
            self.client.close_session_if_owned(session=session)
        return responses

    async def async_update_definition(
        self,
        id: str,
        payload: dict,
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
        """updates an item in a workspace."""
        method = "POST"
        display_name = payload.get("displayName")
        url = self.url + f"/{id}" + "/updateDefinition?updateMetadata=True"
        url = kwargs.get("url") or url
        def_payload = {"definition": payload.get("definition")}

        try:
            response = await self.async_client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                params=params,
                json=def_payload,
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
            _update_def_logger(payload, resp_code, url)
            return response
        except Exception:
            except_msg = _get_exception_message(display_name)
            logger.error(f"{except_msg} - URL: {url}")
            raise
        finally:
            await self.async_client.close_session_if_owned(session)

    async def async_update_definition_many(
        self,
        payloads: dict,
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
    ) -> List[aiohttp.ClientResponse]:
        """updates items in a workspace."""
        tasks = []
        _session = await self.async_client._get_or_create_session(session)

        for id, payload in payloads.items():
            tasks.append(
                self.async_update_definition(
                    id=id,
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
