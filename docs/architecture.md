# Architecture

This document describes the target SDK architecture for FabRest.

```mermaid
graph TD
  %% Public SDK Surface
  A[FabricClient] --> B[WorkspacesResource]
  A --> C[ItemsResource]
  A --> D[AdminResource]
  A --> E[CapacityResource]
  A --> F[JobsResource]
  A --> G[AsyncFabricClient]

  %% Workspace-scoped resources
  B --> B1[WorkspaceResource]
  B1 --> B2["ItemsResource (workspace)"]
  B1 --> B3[LakehousesResource]
  B1 --> B4[WarehousesResource]
  B1 --> B5[SQLEndpointsResource]
  B1 --> B6[Other item resources...]
  B3 --> B7[Lakehouse actions]
  B4 --> B8[Warehouse actions]
  B5 --> B9[SQL endpoint actions]

  %% Resource base + pipeline
  B1 --> H[ResourceBase]
  C --> H
  D --> H
  E --> H
  F --> H

  %% Request pipeline
  H --> I[RequestOptions]
  H --> J[Routes]
  H --> K[Transport]
  K --> K1[RequestsTransport]
  K --> K2[AiohttpTransport]

  %% Cross-cutting
  K --> L[Errors]
  K --> M[Pager]
  K --> N[Poller]
  H --> O[LoggingAdapter]

  %% Models
  H --> P[Models]
  P --> P1[Workspace]
  P --> P2[Item]
  P --> P3[JobRun]
  P --> P4[Capacity]

  %% Auth
  A --> Q[AuthProvider]
  Q --> Q1[Azure Identity Credentials]
  Q --> Q2[ROPC Credential]

```

## Public SDK Surface
- `FabricClient` and `AsyncFabricClient` are the main entry points.
- Top-level resources are exposed as properties (workspaces, items, admin, capacity, jobs).
- Workspace-scoped resources are accessed via `client.workspace(id)`.

## Resources
- Each resource class exposes CRUD and action methods with sync/async parity.
- Workspace resources provide access to item-specific sub-resources.
- Item resources may expose action methods and sub-collections (e.g., tables, restore points, schedules, sessions).
- Preview/beta endpoints are exposed explicitly (either via named methods or flags) and documented in the method docstrings.

## Routing
- `Routes` centralizes endpoint construction and validation.
- Existing URL helpers can remain as a compatibility layer that calls `Routes`.

## Transport
- `Transport` owns sessions, timeouts, and retry/throttling behavior.
- Requests and aiohttp are isolated behind transport implementations.

## Errors
- A single error hierarchy maps HTTP responses to SDK exceptions.
- Error parsing is centralized and consistent for sync/async.

## Pagination and LRO
- `Pager` provides lazy iteration and aggregated list helpers.
- `Poller` manages long-running operations with `wait` and `result` APIs.
- Long-running behavior is controlled via `RequestOptions` on resource methods rather than per-resource polling logic.

## Models
- Lightweight TypedDict models (no new dependencies) for payload interfaces and parsed responses.
- Default return type is parsed data; `raw_response=True` returns the transport response.
- Payload interfaces are generated from Fabric Swagger specs and exposed under `fabrest/models`.

## Auth
- Token handling lives in `AuthProvider`.
- Scopes are derived centrally based on credential type.
