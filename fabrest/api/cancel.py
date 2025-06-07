from .client import Client
from typing import Any, Dict, Optional
import requests
import logging

logger = logging.getLogger(__name__)


def _cancel_job_run_logger(data, url):
    job_type = data.get("jobType")
    status = data.get("status")
    log_msg = f"'{job_type}' {status.lower()} - URL: {url}"
    logger.info(log_msg)


class CancelJobMixin:
    def cancel(
        self,
        id: str,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        wait_for_completion: bool = True,
        throttle_retry_interval: int = 10,
        status_check_interval: int = 10,
        max_retries: int = 0,
        retry_interval: int = 5,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Cancels a job in a workspace.
        """
        url = kwargs.get("url") or self.url
        if id:
            url += f"/{id}/cancel"
        try:
            response = self.client.job_request(
                url=url,
                session=session,
                headers=headers,
                json=payload,
                timeout=timeout,
                wait_for_completion=wait_for_completion,
                throttle_retry_interval=throttle_retry_interval,
                status_check_interval=status_check_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            data = response.json()
            _cancel_job_run_logger(data, url)
            return data
        except Exception as e:
            logger.error(f"Error canceling  - URL {url}")
            raise e
        finally:
            self.client.close_session_if_owned(session)

    async def async_cancel(
        self,
        id: str,
        session=None,
        headers=None,
        payload=None,
        timeout=None,
        wait_for_completion=True,
        throttle_retry_interval=10,
        status_check_interval=10,
        max_retries=0,
        retry_interval=5,
        **kwargs,
    ):
        """Cancel a job in a workspace."""
        url = kwargs.get("url") or self.url
        if id:
            url += f"/{id}/cancel"
        try:
            response = await self.async_client.job_request(
                url=url,
                session=session,
                headers=headers,
                json=payload,
                timeout=timeout,
                wait_for_completion=wait_for_completion,
                throttle_retry_interval=throttle_retry_interval,
                status_check_interval=status_check_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            data = await response.json()
            _cancel_job_run_logger(data, url)
            return data
        except Exception as e:
            logger.error(f"Error canceling  - URL {url}")
            raise e
        finally:
            await self.async_client.close_session_if_owned(session)
