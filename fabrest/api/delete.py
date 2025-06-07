import asyncio
import logging
from typing import Dict, Optional, List
import requests
import aiohttp

logger = logging.getLogger(__name__)


class DeleteMixin:
    def delete(
        self,
        id: str,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> requests.Response:
        """Deletes an item in a workspace."""
        method = "DELETE"
        url = kwargs.get("url") or f"{self.url}/{id}"
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
            logger.info(f"(id: {id}) deleted.")
            return response
        except Exception:
            logger.error(f"Error deleting (id: {id}) - URL: {url}")
            raise
        finally:
            self.client.close_session_if_owned(session)

    def delete_many(
        self,
        ids: list,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> List[requests.Response]:
        """Deletes multiple items in a workspace."""

        responses = []
        _session = self.client._get_or_create_session(session)
        try:
            for id in ids:
                response = self.delete(
                    id=id,
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
            self.client.close_session_if_owned(_session)
        return responses

    async def async_delete(
        self,
        id: str,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """Deletes an item in a workspace."""
        method = "DELETE"
        url = kwargs.get("url") or f"{self.url}/{id}"
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
            logger.info(f"(id: {id}) deleted.")
            return response
        except Exception as e:
            logger.error(f"Error deleting (id: {id}) - URL: {url}")
            raise
        finally:
            await self.async_client.close_session_if_owned(session)

    async def async_delete_many(
        self,
        ids: list,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> List[aiohttp.ClientResponse]:
        """Deletes multiple items in a workspace."""
        tasks = []
        _session = await self.async_client._get_or_create_session(session)
        for id in ids:
            tasks.append(
                self.async_delete(
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
            responses = await asyncio.gather(*tasks)
        except Exception:
            raise
        finally:
            await self.async_client.close_session_if_owned(session)
        return responses
