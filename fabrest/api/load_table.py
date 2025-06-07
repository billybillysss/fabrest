from typing import Any, Dict, Optional
import asyncio
import logging
import requests
import aiohttp

logger = logging.getLogger(__name__)


class LoadTableMixin:
    def load(
        self,
        table_name: str,
        payload: Dict[str, Any],
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ):
        """updates an item in a workspace."""
        method = "POST"
        rel_path = payload.get("relativePath")
        url = self.url + f"/{table_name}/load"
        url = kwargs.get("url") or url
        try:
            response = self.client.request(
                method=method,
                url=url,
                session=session,
                headers=headers,
                params=params,
                json=payload,
                timeout=timeout,
                throttle_retry_interval=throttle_retry_interval,
                lro_check_interval=lro_check_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            logger.info(f"'{rel_path}' loaded.")
            return response
        except Exception:
            except_msg = f"Error loading '{rel_path}' - URL: {url}"
            logger.error(except_msg)
            raise
        finally:
            self.client.close_session_if_owned(session)

    def load_many(
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
    ):
        """updates items in a workspace."""
        responses = []
        _session = self.client._get_or_create_session(session)
        try:
            for table_name, payload in payloads.items():
                response = self.load(
                    table_name=table_name,
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

    async def async_load(
        self,
        table_name: str,
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
    ):
        """updates an item in a workspace."""
        method = "POST"
        rel_path = payload.get("relativePath")
        url = self.url + f"/{table_name}/load"
        url = kwargs.get("url") or url

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

            logger.info(f"'{rel_path}' loaded.")
            return response
        except Exception:
            except_msg = f"Error loading '{rel_path}' - URL: {url}"
            logger.error(except_msg)
            raise
        finally:
            await self.async_client.close_session_if_owned(session)

    async def async_load_many(
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
    ):
        """updates items in a workspace."""
        tasks = []
        _session = await self.async_client._get_or_create_session(session)

        for table_name, payload in payloads.items():
            tasks.append(
                self.async_load(
                    table_name=table_name,
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
