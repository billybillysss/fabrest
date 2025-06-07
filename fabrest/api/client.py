import requests
import logging
import time
from typing import Any, Dict, List, Optional
from .constant import LongRunningOperationStatus, JobStatus
import json
import aiohttp
import asyncio


logger = logging.getLogger(__name__)


class BaseClient:
    """Base Client for both sync and async clients."""

    DEFAULT_SCOPES_SPN = ["https://api.fabric.microsoft.com/.default"]
    DEFAULT_SCOPES_ROPC = [
        "https://api.fabric.microsoft.com/Workspace.Read.All",
        "https://api.fabric.microsoft.com/Item.Execute.All",
        "https://api.fabric.microsoft.com/Item.ReadWrite.All",
    ]
    DEFAULT_LRO_INTERVAL = 10
    DEFAULT_THROTTLE_INTERVAL = 60

    def __init__(
        self,
        credential: Any,
        scopes: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        self.credential = credential
        self.kwargs = kwargs

        if scopes:
            self._scopes = scopes
        elif (
            getattr(credential, "__class__", None).__name__
            == "ResourceOwnerPasswordCredential"
        ):
            self._scopes = self.DEFAULT_SCOPES_ROPC
        else:
            self._scopes = self.DEFAULT_SCOPES_SPN

    def get_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers with auth token."""
        merged = headers.copy() if headers else {}
        if "Authorization" not in merged:
            token = self.credential.get_token(*self._scopes).token
            merged["Authorization"] = f"Bearer {token}"
        merged.setdefault("Content-Type", "application/json")
        return merged

    def _error_response_handler(
        self,
        payload: Dict[str, Any],
        context: str = "",
        prefix: str = "",
        suffix: str = "",
    ) -> str:
        """
        Parse error payload and log a structured message.
        Assumes payload is already a dict parsed from JSON.
        """
        code = payload.get("errorCode", "<no errorCode>")
        msg = payload.get("message", "<no message>")
        related = payload.get("relatedResource") or {}
        if related and isinstance(related, dict):
            related_str = ", ".join(f"{k}={v}" for k, v in related.items())
            related = f"{{{related_str}}}"
        else:
            related = ""

        details = payload.get("moreDetails", [])
        detail_parts = []
        for idx, d in enumerate(details, 1):
            d_code = d.get("errorCode", "<no errorCode>")
            d_msg = d.get("message", "<no message>")
            rel = d.get("relatedResource", {})
            if rel and isinstance(rel, dict):
                rel_str = ", ".join(f"{k}={v}" for k, v in rel.items())
                rel = f"{{{rel_str}}}"
            else:
                rel = ""
            rel_part = f", relatedResource: {rel}" if rel else ""
            detail_parts.append(f"[{idx}] {d_code}: {d_msg}{rel_part}")
        details_str = "; ".join(detail_parts)

        parts = []
        if context:
            parts.append(f"[{context}]")
        if prefix:
            parts.append(prefix)
        parts.append(f"{code}: {msg}")
        if related:
            parts.append(f"RelatedResource: {related}")
        if details_str:
            parts.append(f"MoreDetails: {details_str}")
        if suffix:
            parts.append(suffix)

        log_msg = ". ".join(parts)
        logger.error(log_msg)
        return log_msg


class Client(BaseClient):
    """Synchronous Client for Microsoft Fabric REST API."""

    def __init__(
        self,
        credential: Any,
        scopes: Optional[List[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(credential, scopes, **kwargs)
        self._session: Optional[requests.Session] = None

    def _get_or_create_session(
        self, session: Optional[requests.Session] = None
    ) -> requests.Session:
        if session:
            return session
        elif not self._session:
            self._session = requests.Session()
        return self._session

    def _throttling_handler(
        self,
        response: requests.Response,
        headers: dict,
        session: requests.Session,
        payload: dict,
        interval: Optional[int] = None,
        timeout: int = 120,
    ) -> requests.Response:
        """Handle 429 responses by waiting and retrying."""
        while True:
            wait = interval or int(
                response.headers.get("Retry-After", self.DEFAULT_THROTTLE_INTERVAL)
            )
            try:
                data = response.json()
            except Exception:
                data = {}
            self._error_response_handler(
                data,
                prefix="Throttled.",
                suffix=f"Retry in {wait}s",
            )
            time.sleep(wait)
            req = response.request
            try:
                response = session.request(
                    req.method,
                    req.url,
                    headers=self.get_headers(headers),
                    json=payload,
                    timeout=timeout,
                )
            except requests.Timeout:
                logger.error(
                    f"Throttling handler timed out after {timeout}s: {req.method} {req.url}"
                )
                raise
            if response.status_code != 429:
                return response

    def _pagination_handler(
        self,
        response: requests.Response,
        headers: dict,
        session: requests.Session,
        timeout: int = 120,
    ) -> requests.Response:
        """Aggregate paginated responses into one."""
        if "application/json" not in response.headers.get("Content-Type", ""):
            return response

        data = response.json()
        items = data.get("value", [])
        continue_url = data.get("continuationUri")
        while continue_url:
            try:
                resp = session.get(
                    continue_url, headers=self.get_headers(headers), timeout=timeout
                )
            except requests.Timeout:
                logger.error(
                    f"Pagination handler timed out after {timeout}s: {continue_url}"
                )
                raise
            page = resp.json()
            items.extend(page.get("value", []))
            continue_url = page.get("continuationUri")

        data["value"] = items
        response._content = json.dumps(data).encode("utf-8")
        return response

    def _item_name_in_use_handler(
        self,
        response: requests.Response,
        headers: dict,
        session: requests.Session,
        max_retries: int = 6,
        retry_interval: int = 60,
        timeout: int = 120,
    ) -> requests.Response:
        """Retry if item name conflict occurs."""
        if max_retries == 0 or not max_retries:
            return response
        for attempt in range(1, max_retries + 1):
            time.sleep(retry_interval)
            req = response.request
            try:
                resp = session.request(
                    req.method,
                    req.url,
                    headers=self.get_headers(headers),
                    json=json.loads(req.body) if req.body else None,
                    timeout=timeout,
                )
            except requests.Timeout:
                logger.error(
                    f"Item name in use handler timed out after {timeout}s: {req.method} {req.url}"
                )
                raise
            if not (
                resp.status_code == 400
                and resp.headers.get("x-ms-public-api-error-code")
                == "ItemDisplayNameAlreadyInUse"
            ):
                return resp
            try:
                err_payload = resp.json()
            except Exception:
                err_payload = {}
            self._error_response_handler(
                err_payload, suffix=f"Retry after {retry_interval}s - {attempt}/{max_retries}"
            )
        resp.raise_for_status()
        return resp

    def _lro_handler(
        self,
        response: requests.Response,
        headers: dict,
        session: requests.Session,
        interval: Optional[int] = None,
        timeout: int = 120,
    ) -> requests.Response:
        """Poll long-running operations until completion."""
        wait = interval or int(
            response.headers.get("Retry-After", self.DEFAULT_LRO_INTERVAL)
        )
        url = response.headers.get("Location")
        logger.info(f"Long Running Operation started, checking in {wait}s at {url}")
        time.sleep(wait)

        terminate_codes = {
            LongRunningOperationStatus.FAILED.value,
            LongRunningOperationStatus.UNDEFINED.value,
        }
        while True:
            try:
                resp = session.get(
                    url, headers=self.get_headers(headers), timeout=timeout
                )
            except requests.Timeout:
                logger.error(f"LRO handler timed out after {timeout}s: {url}")
                raise
            if resp.status_code >= 300:
                return resp

            wait = int(
                resp.headers.get("Retry-After", interval or self.DEFAULT_LRO_INTERVAL)
            )
            data = resp.json()
            status = data.get("status")
            if status in terminate_codes:
                error = data.get("error", {})
                msg = self._error_response_handler(
                    error,
                    prefix="Long running operation error. ",
                    suffix=f"URL: {url}",
                )
                raise Exception(msg)
            logger.info(
                f"Long Running Operation: {status}, progress {data.get('percentComplete')}%. Checking in {wait}s at {url}"
            )
            if url.endswith("results"):
                break
            time.sleep(wait)
            url = resp.headers.get("Location")

        try:
            final_resp = session.get(
                url, headers=self.get_headers(headers), timeout=timeout
            )
        except requests.Timeout:
            logger.error(f"LRO handler final get timed out after {timeout}s: {url}")
            raise
        return final_resp

    def _job_run_handler(
        self,
        response: requests.Response,
        headers: dict,
        session: requests.Session,
        interval: int,
        timeout: int = 120,
    ) -> requests.Response:
        wait = int(response.headers.get("Retry-After", interval))
        url = response.headers.get("Location")
        logger.info(f"Job started, checking in {wait}s at {url}")
        time.sleep(wait)
        while True:
            try:
                resp = session.get(
                    url, headers=self.get_headers(headers), timeout=timeout
                )
            except requests.Timeout:
                logger.error(f"Job run handler timed out after {timeout}s: {url}")
                raise
            if resp.status_code >= 300:
                return resp
            wait = int(resp.headers.get("Retry-After", interval))
            data = resp.json()
            status = data.get("status")
            if status in {JobStatus.FAILED.value, JobStatus.DEDUPE.value}:
                error = data.get("failureReason", {})
                msg = self._error_response_handler(
                    error,
                    prefix="Job terminated. ",
                    suffix=f"URL: {url}",
                )
                raise Exception(msg)
            elif status in {JobStatus.COMPLETED.value, JobStatus.CANCELLED.value}:
                return resp

            logger.info(f"Job status: {status}. Checking in {wait}s at {url}")
            time.sleep(wait)

    def _send_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        session: Optional[requests.Session],
        params: Optional[Dict[str, Any]],
        json: Optional[Dict[str, Any]],
        timeout: int = 120,
        wait_for_completion: bool = True,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        job_check_interval: Optional[int] = None,
        handle_long_running_operation: bool = False,
        handle_long_running_job: bool = False,
        handle_pagination: bool = False,
    ) -> requests.Response:
        """Generic retry/error handler for both normal and job requests."""
        session = self._get_or_create_session(session)
        try:
            resp = session.request(
                method=method,
                url=url,
                headers=self.get_headers(headers),
                params=params,
                json=json,
                timeout=timeout,
            )
        except requests.Timeout:
            logger.error(f"Request timed out after {timeout}s: {method} {url}")
            raise

        retries = 0
        while retries <= max_retries:
            try:
                code = resp.status_code
                if code == 429:
                    resp = self._throttling_handler(
                        resp,
                        headers,
                        session,
                        payload=json,
                        interval=throttle_retry_interval,
                        timeout=timeout,
                    )
                elif (
                    code == 400
                    and resp.headers.get("x-ms-public-api-error-code")
                    == "ItemDisplayNameAlreadyInUse"
                    and handle_long_running_operation is True
                ):
                    try:
                        used_name_payload = resp.json()
                    except Exception:
                        used_name_payload = {}

                    if item_name_in_use_max_retries > 0:
                        used_name_log_suffix = f"Retry after {item_name_in_use_retry_interval}s"
                    else:
                        used_name_log_suffix = ""

                    self._error_response_handler(used_name_payload, suffix=used_name_log_suffix)
                    resp = self._item_name_in_use_handler(
                        resp,
                        headers,
                        session,
                        max_retries=item_name_in_use_max_retries,
                        retry_interval=item_name_in_use_retry_interval,
                        timeout=timeout,
                    )
                    continue
                elif code == 202 and wait_for_completion:
                    if handle_long_running_operation:
                        resp = self._lro_handler(
                            resp,
                            headers,
                            session,
                            interval=lro_check_interval,
                            timeout=timeout,
                        )
                    elif handle_long_running_job:
                        resp = self._job_run_handler(
                            resp,
                            headers,
                            session,
                            interval=job_check_interval,
                            timeout=timeout,
                        )
                    continue
                if 200 <= resp.status_code < 300:
                    if handle_pagination:
                        resp = self._pagination_handler(
                            resp, headers, session, timeout=timeout
                        )
                    return resp
                # If not successful, log and possibly raise
                try:
                    payload = resp.json()
                except Exception:
                    payload = {}
                self._error_response_handler(payload)
                resp.raise_for_status()

            except Exception as e:
                retries += 1
                if retries > max_retries:
                    raise e
                time.sleep(retry_interval)
                logger.info(
                    f"Request failed. Retrying after {retry_interval}s. {retries}/{max_retries}"
                )
        return resp

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 120,
        wait_for_completion: bool = True,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
    ) -> requests.Response:
        """Send HTTP request with retry, pagination, and LRO handling."""
        return self._send_request(
            method,
            url,
            headers=headers,
            session=session,
            params=params,
            json=json,
            timeout=timeout,
            wait_for_completion=wait_for_completion,
            throttle_retry_interval=throttle_retry_interval,
            lro_check_interval=lro_check_interval,
            item_name_in_use_max_retries=item_name_in_use_max_retries,
            item_name_in_use_retry_interval=item_name_in_use_retry_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            handle_long_running_operation=True,
            handle_pagination=True,
        )

    def job_request(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 120,
        wait_for_completion: bool = True,
        throttle_retry_interval: Optional[int] = None,
        job_check_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
    ):
        method = "POST"
        return self._send_request(
            method=method,
            url=url,
            headers=headers,
            session=session,
            params=params,
            json=json,
            timeout=timeout,
            wait_for_completion=wait_for_completion,
            throttle_retry_interval=throttle_retry_interval,
            job_check_interval=job_check_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            handle_long_running_job=True,
        )

    def close(self):
        if self._session:
            self._session.close()
            self._session = None

    def close_session_if_owned(self, session: requests.Session) -> bool:
        """Closes the session if it is owned by this client."""
        if session is None:
            if self._session:
                self._session.close()
                self._session = None
            return True
        return False


class AsyncClient(BaseClient):
    """Asynchronous Client for Microsoft Fabric REST API."""

    def __init__(
        self, credential: Any, scopes: Optional[List[str]] = None, **kwargs: Any
    ):
        super().__init__(credential, scopes, **kwargs)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_or_create_session(
        self, session: Optional[aiohttp.ClientSession] = None
    ) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if session:
            return session
        elif self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _throttling_handler(
        self,
        response: aiohttp.ClientResponse,
        headers: dict,
        payload: dict,
        interval: Optional[int] = None,
        timeout: int = 120,
    ) -> aiohttp.ClientResponse:
        while True:
            wait = interval or int(
                response.headers.get("Retry-After", self.DEFAULT_THROTTLE_INTERVAL)
            )
            try:
                err_payload = await response.json()
            except Exception:
                err_payload = {}
            self._error_response_handler(
                err_payload, prefix="Throttled.", suffix=f"Retry in {wait}s"
            )
            await asyncio.sleep(wait)
            req = response.request_info
            session = await self._get_or_create_session()
            try:
                async with asyncio.timeout(timeout):
                    async with session.request(
                        req.method,
                        req.url,
                        headers=self.get_headers(headers),
                        json=payload,
                    ) as resp:
                        if resp.status != 429:
                            return resp
                        response = resp  # Keep retrying if 429
            except asyncio.TimeoutError:
                logger.error(f"Throttling handler timed out after {timeout}s")
                raise

    async def _pagination_handler(
        self,
        response: aiohttp.ClientResponse,
        headers: dict,
        session: aiohttp.ClientSession,
        timeout: int = 120,
    ) -> aiohttp.ClientResponse:
        """Aggregate paginated responses into one."""
        if "application/json" not in response.headers.get("Content-Type", ""):
            return response
        data = await response.json()
        items = data.get("value", [])
        continue_url = data.get("continuationUri")
        session = await self._get_or_create_session(session)

        while continue_url:
            try:
                async with asyncio.timeout(timeout):
                    async with session.get(
                        continue_url, headers=self.get_headers(headers)
                    ) as resp:
                        page = await resp.json()
                        items.extend(page.get("value", []))
                        continue_url = page.get("continuationUri")
            except asyncio.TimeoutError:
                logger.error(f"Pagination handler timed out after {timeout}s")
                raise

        data["value"] = items
        response._body = json.dumps(data).encode("utf-8")
        return response

    async def _item_name_in_use_handler(
        self,
        response: aiohttp.ClientResponse,
        headers: dict,
        session: aiohttp.ClientSession,
        max_retries: int = 6,
        retry_interval: int = 60,
        timeout: int = 120,
    ) -> aiohttp.ClientResponse:
        if max_retries == 0 or not max_retries:
            return response
        req = response.request_info
        body = await response.read()
        for attempt in range(1, max_retries + 1):
            await asyncio.sleep(retry_interval)
            try:
                async with asyncio.timeout(timeout):
                    async with session.request(
                        req.method,
                        req.url,
                        headers=self.get_headers(headers),
                        data=body,
                    ) as resp:
                        if not (
                            resp.status == 400
                            and resp.headers.get("x-ms-public-api-error-code")
                            == "ItemDisplayNameAlreadyInUse"
                        ):
                            return resp
                        try:
                            payload = await resp.json()
                        except Exception:
                            payload = {}
                        self._error_response_handler(
                            payload, suffix=f"Retry after {retry_interval}s - {attempt}/{max_retries}"
                        )
            except asyncio.TimeoutError:
                logger.error(f"Item name in use handler timed out after {timeout}s")
                raise
        resp.raise_for_status()
        return resp

    async def _lro_handler(
        self,
        response: aiohttp.ClientResponse,
        headers: dict,
        interval: Optional[int] = None,
        timeout: int = 120,
    ) -> aiohttp.ClientResponse:
        wait = interval or int(
            response.headers.get("Retry-After", self.DEFAULT_LRO_INTERVAL)
        )
        url = response.headers.get("Location")
        logger.info(f"Long Running Operation started, checking in {wait}s at {url}")
        await asyncio.sleep(wait)

        session = await self._get_or_create_session()

        while True:
            try:
                async with asyncio.timeout(timeout):
                    async with session.get(
                        url, headers=self.get_headers(headers)
                    ) as resp:
                        if resp.status >= 300:
                            return resp
                        data = await resp.json()
                        status = data.get("status")
                        if status in {
                            LongRunningOperationStatus.FAILED.value,
                            LongRunningOperationStatus.UNDEFINED.value,
                        }:
                            msg = self._error_response_handler(
                                data.get("error", {}),
                                prefix="Long running operation error. ",
                                suffix=f"URL: {url}",
                            )
                            raise Exception(msg)

                        logger.info(
                            f"Long Running Operation: {status}, progress {data.get('percentComplete')}%"
                        )

                        if url.endswith("results"):
                            break

                        await asyncio.sleep(wait)
                        url = resp.headers.get("Location")
            except asyncio.TimeoutError:
                logger.error(f"LRO handler timed out after {timeout}s")
                raise

        try:
            async with asyncio.timeout(timeout):
                async with session.get(url, headers=self.get_headers(headers)) as resp:
                    return resp
        except asyncio.TimeoutError:
            logger.error(f"LRO handler final get timed out after {timeout}s")
            raise

    async def _job_run_handler(
        self,
        response: aiohttp.ClientResponse,
        headers: dict,
        session: aiohttp.ClientSession,
        interval: int,
        timeout: int = 120,
    ) -> aiohttp.ClientResponse:
        wait = int(response.headers.get("Retry-After", interval))
        url = response.headers.get("Location")
        logger.info(f"Job started, checking in {wait}s at {url}")
        await asyncio.sleep(wait)
        while True:
            try:
                async with asyncio.timeout(timeout):
                    resp = await session.get(url, headers=self.get_headers(headers))
                    if resp.status >= 300:
                        return resp
                    data = await resp.json()
                    status = data.get("status")
                    if status in {JobStatus.FAILED.value, JobStatus.DEDUPE.value}:
                        error = data.get("failureReason", {})
                        msg = self._error_response_handler(
                            error,
                            prefix="Job terminated. ",
                            suffix=f"URL: {url}",
                        )
                        raise Exception(msg)
                    elif status in {
                        JobStatus.COMPLETED.value,
                        JobStatus.CANCELLED.value,
                    }:
                        return resp

                    logger.info(f"Job status: {status}. Checking in {wait}s at {url}")
                    await asyncio.sleep(wait)
            except asyncio.TimeoutError:
                logger.error(f"Job run handler timed out after {timeout}s")
                raise

    async def _send_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        session: Optional[aiohttp.ClientSession],
        params: Optional[Dict[str, Any]],
        json: Optional[Dict[str, Any]],
        timeout: int = 120,
        wait_for_completion: bool = True,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
        throttle_retry_interval: Optional[int] = None,
        lro_check_interval: Optional[int] = None,
        job_check_interval: Optional[int] = None,
        handle_long_running_operation: bool = False,
        handle_long_running_job: bool = False,
        handle_pagination: bool = False,
    ) -> aiohttp.ClientResponse:
        """Generic retry/error handler for both normal and job requests."""
        session = await self._get_or_create_session(session)
        retries = 0
        while retries <= max_retries:
            try:
                try:
                    async with asyncio.timeout(timeout):
                        resp = await session.request(
                            method=method,
                            url=url,
                            headers=self.get_headers(headers),
                            params=params,
                            json=json,
                        )
                except asyncio.TimeoutError:
                    logger.error(f"Request timed out after {timeout}s: {method} {url}")
                    raise

                code = resp.status
                if code == 429:
                    resp = await self._throttling_handler(
                        resp,
                        headers,
                        session,
                        payload=json,
                        interval=throttle_retry_interval,
                        timeout=timeout,
                    )
                elif (
                    code == 400
                    and resp.headers.get("x-ms-public-api-error-code")
                    == "ItemDisplayNameAlreadyInUse"
                    and handle_long_running_operation is True
                ):
                    try:
                        used_name_payload = await resp.json()
                    except Exception:
                        used_name_payload = {}
                        
                    if item_name_in_use_max_retries > 0:
                        used_name_log_suffix = f"Retry after {item_name_in_use_retry_interval}s"
                    else:
                        used_name_log_suffix = ""

                    self._error_response_handler(used_name_payload, suffix=used_name_log_suffix)
                    resp = await self._item_name_in_use_handler(
                        resp,
                        headers,
                        session,
                        max_retries=item_name_in_use_max_retries,
                        retry_interval=item_name_in_use_retry_interval,
                        timeout=timeout,
                    )
                    continue
                elif code == 202 and wait_for_completion:
                    if handle_long_running_operation:
                        resp = await self._lro_handler(
                            resp, headers, interval=lro_check_interval, timeout=timeout
                        )
                    elif handle_long_running_job:
                        resp = await self._job_run_handler(
                            resp,
                            headers,
                            session,
                            interval=job_check_interval,
                            timeout=timeout,
                        )
                    continue
                if 200 <= resp.status < 300:
                    if handle_pagination:
                        resp = await self._pagination_handler(
                            resp, headers, session, timeout=timeout
                        )
                    return resp

                # If not successful, log and possibly raise
                try:
                    payload = await resp.json()
                except Exception:
                    payload = {}
                self._error_response_handler(payload)
                resp.raise_for_status()

            except Exception as e:
                retries += 1
                if retries > max_retries:
                    raise e
                await asyncio.sleep(retry_interval)
                logger.info(
                    f"Request failed. Retrying after {retry_interval}s. {retries}/{max_retries}"
                )
        return resp

    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[aiohttp.ClientSession] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 120,
        wait_for_completion: bool = True,
        throttle_retry_interval: int = 10,
        lro_check_interval: int = 10,
        item_name_in_use_max_retries: int = 6,
        item_name_in_use_retry_interval: int = 60,
        max_retries: int = 0,
        retry_interval: int = 5,
    ) -> aiohttp.ClientResponse:
        """Send async HTTP request with retry, pagination, and LRO handling."""
        return await self._send_request(
            method,
            url,
            headers=headers,
            session=session,
            params=params,
            json=json,
            timeout=timeout,
            wait_for_completion=wait_for_completion,
            throttle_retry_interval=throttle_retry_interval,
            lro_check_interval=lro_check_interval,
            item_name_in_use_max_retries=item_name_in_use_max_retries,
            item_name_in_use_retry_interval=item_name_in_use_retry_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            handle_long_running_operation=True,
            handle_pagination=True,
        )

    async def job_request(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[aiohttp.ClientSession] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 120,
        wait_for_completion: bool = True,
        throttle_retry_interval: Optional[int] = None,
        job_check_interval: Optional[int] = None,
        max_retries: int = 0,
        retry_interval: int = 5,
    ):
        method = "POST"
        return await self._send_request(
            method=method,
            url=url,
            headers=headers,
            session=session,
            params=params,
            json=json,
            timeout=timeout,
            wait_for_completion=wait_for_completion,
            throttle_retry_interval=throttle_retry_interval,
            job_check_interval=job_check_interval,
            max_retries=max_retries,
            retry_interval=retry_interval,
            handle_long_running_job=True,
        )

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def close_session_if_owned(self, session: aiohttp.ClientSession) -> bool:
        """Closes the session if it is owned by this client."""
        if session is None:
            if self._session:
                await self._session.close()
                self._session = None
            return True
        return False
