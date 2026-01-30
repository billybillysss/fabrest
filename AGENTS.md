# AGENTS.md
# Guidance for agentic coding in this repository.

## Project snapshot
- Package: `fabrest`
- Language/runtime: Python 3.11 (see `.python-version`)
- Test framework: pytest
- Async stack: `aiohttp` with async client variants
- Sync stack: `requests` for sync client variants
- Dependency management: `pyproject.toml` + `uv.lock` (uv is optional)

## Build, lint, test commands
### Environment setup
- Create venv: `python -m venv .venv`
- Activate (Windows PowerShell): `.venv\Scripts\Activate.ps1`
- Install package in editable mode: `python -m pip install -e .`
- Install dev deps (pytest): `python -m pip install -e .[dev]`

### Tests
- Run all tests: `python -m pytest`
- Run a single file: `python -m pytest tests\test_auth.py`
- Run a single test: `python -m pytest tests\test_auth.py::test_get_token_refreshes_when_expired`
- Run a single test by keyword: `python -m pytest -k "get_token"`

### Lint/format
- No lint or formatter config is present in this repo.
- If you introduce a tool, update this file with exact commands.

### Build/package
- No dedicated build script is configured.
- Editable install is the standard local workflow: `python -m pip install -e .`
- If you need sdist/wheel: `python -m pip install build` then `python -m build`

### Optional: uv workflow
- Sync deps: `uv sync`
- Run tests via uv: `uv run pytest`

## Repo layout
- `fabrest/`: library source
- `fabrest/api/`: HTTP request mixins and client logic
- `fabrest/utils/`: shared helpers
- `tests/`: pytest suite

## Code style and conventions
### General formatting
- Use 4-space indentation.
- Match existing line wrapping; keep lines readable over strict limits.
- Prefer explicit names over brevity in public APIs.
- Avoid adding comments unless clarifying non-obvious logic.

### Imports
- Group imports in this order when editing files:
  1) standard library
  2) third-party
  3) local package imports
- Keep imports minimal and module-scoped; avoid heavy imports inside functions.

### Naming
- Classes: `PascalCase` (e.g., `WorkspaceResource`).
- Functions/methods/vars: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Async variants: prefix with `async_` (e.g., `async_create`).
- Operator collections are plural (e.g., `WorkspacesOperator`).

### Types
- Use `typing` hints for public functions and methods.
- Favor `Optional[T]` when `None` is a valid input.
- Use `Dict[str, Any]`, `List[T]`, etc. consistent with existing code.
- Keep return types explicit for async methods (`aiohttp.ClientResponse`).

### HTTP client patterns
- Use `Client` and `AsyncClient` for request sending; do not reimplement.
- Sync methods accept optional `requests.Session` and close only if owned.
- Async methods accept optional `aiohttp.ClientSession` and close only if owned.
- For new operations, route through `_send_request` and existing handlers.
- Preserve retry, throttling, LRO, and pagination behaviors.
- Pass through `headers`, `params`, `timeout`, and retry settings untouched unless required.
- Prefer `client.request(...)` or `async_client.request(...)` over raw `requests`/`aiohttp` usage.

### Auth and scopes
- The client decides scopes based on credential type; avoid hard-coding scopes in resources.
- ROPC-specific flows live in `fabrest/api/auth.py`; keep them isolated.
- Do not log secrets or tokens; log identifiers and URLs only.

### Error handling and logging
- Wrap network calls with `try/except`, log failures, then re-raise.
- When parsing response JSON, handle failures with a safe fallback `{}`.
- Prefer structured, contextual log messages (URL, item id, display name).
- For request failures, include method and URL in logs when available.
- For retries, preserve the retry counters and intervals from caller inputs.

### Mixins
- Mixins implement CRUD and action methods (create/get/list/update/delete/run).
- Keep method signatures consistent across sync/async variants.
- Ensure keyword args are passed through to the client request layer.
- Keep the sync/async method docstrings aligned.
- Avoid changing mixin behavior in one path without mirroring the other.

### Response handling
- Methods typically return raw response objects for create/update/run flows.
- For list/get helpers that return data, keep JSON parsing guarded with try/except.
- Do not mutate response objects except where pagination/LRO logic requires it.

### Async and sync parity
- If you add a sync method, add the async counterpart (and vice versa).
- Preserve parameter order and defaults across sync/async versions.
- Use `asyncio` helpers (`asyncio.sleep`, `asyncio.gather`) for async flows.

### Tests
- Use pytest fixtures for shared setup.
- Use `unittest.mock` for network calls.
- Keep tests focused on behavior and error cases.
- Prefer descriptive test names starting with `test_`.
- Keep tests deterministic; avoid real network calls.
- When asserting logs, prefer explicit error messages or exception types.

## Documentation and public API
- Update README examples only if behavior changes or new features are added.
- Avoid breaking public method signatures unless explicitly requested.
- Keep module exports consistent in `fabrest/__init__.py` if you add new public types.

## Security and secrets
- Never add secrets (tokens, passwords, client secrets) to source or tests.
- If sample values are needed, use placeholders like `your-client-id`.

## Behavioral notes for agents
- Do not assume a formatter or linter; keep formatting consistent with the file.
- Avoid adding new dependencies without updating `pyproject.toml`.
- Prefer minimal edits over sweeping refactors.
- When touching API or resource logic, ensure both sync and async paths remain aligned.
- Keep public method names and signatures stable unless explicitly requested.

## Cursor/Copilot rules
- No Cursor rules found in `.cursor/rules/` or `.cursorrules`.
- No Copilot instructions found in `.github/copilot-instructions.md`.
