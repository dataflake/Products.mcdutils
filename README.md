# Products.mcdutils

`Products.mcdutils` provides an alternative to the ZODB-based session container (the `Transience` product) by using **memcached** as the _backing store_. It brings components for Zope/Plone that enable:

- **MemCacheSessionDataContainer** (`sessiondata.py`): A session data container persisted in one or more **memcached** servers instead of the ZODB.
- **MemCacheMapping** (`mapping.py`): A transactional mapping (compatible with `IDataManager` / savepoints) that represents the session. Integrates with Zope's/`transaction`'s transaction mechanism.
- **MemCacheProxy** (`proxy.py`): A _proxy_ that manages the memcached client, servers, and serialization of session objects.
- **ZCache / ZCacheManager (work-alike)** (`zcache.py`): An in-memory cache implementation based on memcached with an API compatible with `RAMCacheManager` for use in Zope views/objects.
- **ZMI Views and Screens** (`www/*.pt`): Helpers for creating/configuring containers, proxies, and adding items for testing/diagnostics.
- **Transaction Integration**: Session objects participate in the `tpc_vote / tpc_finish` cycle, with safe writing only at the end of the transaction.

> In practical terms: you get fast, distributed sessions, backed by memcached, while maintaining the transactional semantics expected by Zope/Plone.

## What's New in Version 5.0.0

The new `5.0.0` version includes significant improvements in **resilience**, **observability**, and **code modernization**, while maintaining API compatibility.

### 1) Resilient Memcached Client (New `reconnecting.py` Module)

- **ReconnectingClient**: A _wrapper_ for `python-memcached` that attempts to **reconnect** and **reactivate** the client on network/server failures.
- **Automatic Monkey-patch** (by default): `memcache.Client` is replaced by `ReconnectingClient` during package import.
- **How to Disable**: Export `MCDUTILS_DISABLE_RECONNECT=1` to revert to the original client.
- **Configurable Backoff**: `MCDUTILS_BACKOFF_MIN_MS` and `MCDUTILS_BACKOFF_MAX_MS` (set both to `0` to disable waiting).
- **Optional Logs**: Enable with `MCDUTILS_LOG=1` and adjust the level with `MCDUTILS_LOG_LEVEL` (e.g., `INFO`, `DEBUG`).
- **Built-in Metrics** (in-process): Enable with `MCDUTILS_METRICS=1`. Exposed counters include, among others:
  `mcdutils_reconnect_attempts_total`, `mcdutils_reconnect_success_total`, `mcdutils_reconnect_fail_total`,
  `mcdutils_retry_calls_total`, `mcdutils_retry_duration_seconds_sum`, `mcdutils_retry_duration_seconds_count`.
- **Prometheus (Textfile) Export**: Available via `reconnecting.export_prometheus_textfile(path)` when desired.

### 2) Retry in `tpc_vote` with Metrics and Structured Logs

- The `MemCacheMapping.tpc_vote` function receives a **wrapper with retry attempts** when a `MemCacheError` occurs during the _vote_.
- **Environment Parameters**:

  - `MCDUTILS_DISABLE_TPC_RETRY=1` → Disables the _retry_ in `tpc_vote`.
  - `MCDUTILS_TPC_RETRY_ATTEMPTS` → Number of additional attempts (default: `1`).
  - `MCDUTILS_TPC_RETRY_BACKOFF_MS` → _Backoff_ between attempts (ms, default: `100`).
  - `MCDUTILS_LOG=1` / `MCDUTILS_LOG_LEVEL` → Enables logs and adjusts verbosity.
  - Additional metrics: `tpc_retry_attempts_total`, `tpc_retry_success_total`, `tpc_retry_fail_total`, `tpc_retry_backoff_seconds_sum|count`.

- **"Forced" Reconnection Path**: Before retrying, the wrapper attempts to invalidate connections (`disconnect_all` / `force_reconnect`) and executes a short _probe_ operation to warm up the client.
- **Motivation**: To mitigate intermittent failures at critical moments in the transaction cycle (e.g., network errors during _vote_).

### 3) Robustness and Readability Improvements

- Consistent use of `contextlib.suppress(...)` instead of empty `try/except` blocks for idempotent operations (e.g., invalidating caches/volatile attributes).
- Adoption of _f-strings_, typing, and the `py.typed` marker → better support for _type checkers_.
- _Style_ adjustments and compatibility (strings, imports with `from __future__ import annotations`, minor _cleanups_ in views and ZCache).

### 4) Compatibility and API

- **No Declared API Breaks** for the core components (Proxy, Mapping, SessionDataContainer, and ZCache).
- Default behavior is **more resilient** due to _reconnecting_ and _retry_ in `tpc_vote` — both can be **disabled by environment variable** if necessary.