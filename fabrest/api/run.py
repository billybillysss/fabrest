import logging
from .url import URL

logger = logging.getLogger(__name__)


def _get_job_run_logger(data, url):
    job_type = data.get("jobType")
    status = data.get("status")
    log_msg = f"'{job_type}' {status.lower()} - URL: {url}"
    logger.info(log_msg)


class RunJobMixin:
    def run(
        self,
        session=None,
        headers=None,
        payload=None,
        timeout=None,
        wait_for_completion=True,
        throttle_retry_interval=10,
        job_check_interval=10,
        max_retries=0,
        retry_interval=5,
        **kwargs,
    ):
        """Runs a job in a workspace."""
        url = kwargs.get("url") or URL.get_job_instance_url(
            workspace_id=self.workspace_id,
            item_id=self.item_id,
            job_type=self.job_type,
            item_type=self.item_type,
        )

        try:
            response = self.client.job_request(
                url=url,
                headers=headers,
                session=session,
                json=payload,
                timeout=timeout,
                wait_for_completion=wait_for_completion,
                throttle_retry_interval=throttle_retry_interval,
                job_check_interval=job_check_interval,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            if wait_for_completion:
                data = response.json()
                _get_job_run_logger(data, url)
                return data
            logger.info(f"Job run request accepted - URL: {url}")
            return response
        except Exception as e:
            logger.error(f"Error running job - URL {url}")
            raise
        finally:
            self.client.close_session_if_owned(session)

    async def async_run(
        self,
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
        """Asynchronously runs a job in a workspace."""
        url = kwargs.get("url") or URL.get_job_instance_url(
            workspace_id=self.workspace_id,
            item_id=self.item_id,
            job_type=self.job_type,
            item_type=self.item_type,
        )

        try:
            if wait_for_completion:
                response = await self.async_client.job_request(
                    url=url,
                    headers=headers,
                    session=session,
                    json=payload,
                    timeout=timeout,
                    wait_for_completion=wait_for_completion,
                    throttle_retry_interval=throttle_retry_interval,
                    status_check_interval=status_check_interval,
                    max_retries=max_retries,
                    retry_interval=retry_interval,
                )
                data = await response.json()
                _get_job_run_logger(data, url)
                return data
            logger.info(f"Job run request accepted - URL: {url}")
            return response
        except Exception:
            logger.error(f"Error running job - URL {url}")
            raise
        finally:
            await self.async_client.close_session_if_owned(session)
