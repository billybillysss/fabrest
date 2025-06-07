from typing import Dict, Optional

import logging
import aiohttp
import requests

logger = logging.getLogger(__name__)


def _list_logger(data, url):
    """
    Log the number of records fetched from a list operation.
    """
    records = data.get("value")
    if records:
        record_count = len(records)
        log_part = str(record_count) + " records "
    else:
        log_part = "No records "

    logger.debug(f"Fetched {log_part} - URL: {url}")


class ListMixin:
    def list(
        self,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> Optional[list]:
        """Lists resources."""
        method = "GET"
        url = kwargs.get("url") or self.url
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
            _list_logger(data, url)

            return data.get("value")
        except Exception:
            logger.error(f"Error listing - URL: {url}")
            raise
        finally:
            self.client.close_session_if_owned(session)

    async def async_list(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        throttle_retry_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs,
    ) -> Optional[list]:
        """Asynchronously lists resources."""
        method = "GET"
        url = kwargs.get("url") or self.url
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
            _list_logger(data, url)
            return data.get("value")
        except Exception:
            logger.error(f"Error listing - URL: {url}")
            raise
        finally:
            await self.async_client.close_session_if_owned(session)
