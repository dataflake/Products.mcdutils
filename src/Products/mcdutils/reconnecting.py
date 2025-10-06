"""
Reconnecting wrapper for python-memcached's Client with metrics, logging,
and parametrizable backoff.

Env vars (all optional):
- MCDUTILS_DISABLE_RECONNECT=1        -> disables the monkey-patch
- MCDUTILS_LOG_LEVEL=DEBUG|INFO|...   -> logging level (default: WARNING)
- MCDUTILS_LOG=1                      -> enable logging of reconnect events
- MCDUTILS_METRICS=1                  -> enable in-process metrics counters
- MCDUTILS_BACKOFF_MIN_MS=50          -> min backoff before retry (ms)
- MCDUTILS_BACKOFF_MAX_MS=200         -> max backoff before retry (ms)
                                      -> set both to 0 to disable backoff
Optionally, you can export Prometheus-format metrics by calling
`export_prometheus_textfile(path)` from your app.
"""

from __future__ import annotations

from collections.abc import Iterable
from functools import wraps
from typing import Any

import contextlib
import logging
import memcache
import os
import random
import socket
import threading
import time


_OriginalClient = memcache.Client
_system_random = random.SystemRandom()

log = logging.getLogger("Products.mcdutils.reconnecting")
_level = os.environ.get("MCDUTILS_LOG_LEVEL")
if _level:
    try:
        log.setLevel(getattr(logging, _level.upper(), logging.WARNING))
    except Exception:
        log.setLevel(logging.WARNING)
else:
    log.setLevel(logging.WARNING)
if not log.handlers:
    # Defer to root configuration, but ensure at least a NullHandler present
    log.addHandler(logging.NullHandler())

_ENABLE_LOG = os.environ.get("MCDUTILS_LOG") == "1"
_ENABLE_METRICS = os.environ.get("MCDUTILS_METRICS") == "1"


def _env_ms(name: str, default: int) -> int:
    try:
        v = int(os.environ.get(name, default))
        return max(0, v)
    except Exception:
        return default


_BACKOFF_MIN_MS = _env_ms("MCDUTILS_BACKOFF_MIN_MS", 50)
_BACKOFF_MAX_MS = _env_ms("MCDUTILS_BACKOFF_MAX_MS", 200)
if _BACKOFF_MAX_MS < _BACKOFF_MIN_MS:
    _BACKOFF_MAX_MS = _BACKOFF_MIN_MS

# -------------------- metrics (in-process) --------------------
_metrics = {
    # tpc_vote-level metrics
    "tpc_retry_attempts_total": 0,
    "tpc_retry_success_total": 0,
    "tpc_retry_fail_total": 0,
    "tpc_retry_backoff_seconds_sum": 0.0,
    "tpc_retry_backoff_seconds_count": 0,
    "reconnect_attempts_total": 0,
    "reconnect_success_total": 0,
    "reconnect_fail_total": 0,
    "retry_calls_total": 0,
    "retry_duration_seconds_sum": 0.0,
    "retry_duration_seconds_count": 0,
}


def get_metrics() -> dict[str, float]:
    """Return a copy of metrics counters (always available)."""
    return dict(_metrics)


def incr_metric(name: str, inc: float = 1.0) -> None:
    try:
        if name in _metrics:
            _metrics[name] += inc
        else:
            _metrics[name] = inc
    except Exception:  # noqa: S110
        pass


def export_prometheus_textfile(path: str) -> None:
    """Write metrics in Prometheus textfile format to `path` (atomic write)."""
    lines = [
        "# TYPE mcdutils_reconnect_attempts_total counter",
        f"mcdutils_reconnect_attempts_total {_metrics['reconnect_attempts_total']}",  # noqa: E501
        "# TYPE mcdutils_reconnect_success_total counter",
        f"mcdutils_reconnect_success_total {_metrics['reconnect_success_total']}",  # noqa: E501
        "# TYPE mcdutils_reconnect_fail_total counter",
        f"mcdutils_reconnect_fail_total {_metrics['reconnect_fail_total']}",
        "# TYPE mcdutils_retry_calls_total counter",
        f"mcdutils_retry_calls_total {_metrics['retry_calls_total']}",
        "# TYPE mcdutils_retry_duration_seconds summary",
        f"mcdutils_retry_duration_seconds_sum {_metrics['retry_duration_seconds_sum']}",  # noqa: E501
        f"mcdutils_retry_duration_seconds_count {_metrics['retry_duration_seconds_count']}",  # noqa: E501
    ]
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    os.replace(tmp, path)


# --------------------------------------------------------------

_RECOVERABLE = (
    socket.timeout,
    ConnectionError,
    BrokenPipeError,
    ConnectionResetError,
    OSError,  # covers "Bad file descriptor", "Transport endpoint not connected", etc. # noqa: E501
)


def _should_reconnect(exc: BaseException) -> bool:
    # Conservative: reconnect on any socket-ish error.
    if isinstance(exc, _RECOVERABLE):
        return True
    # python-memcached raises generic Exception for some network issues;
    # string-match some common cases without being too specific.
    msg = str(exc).lower()
    network_markers = (
        "socket",
        "timed out",
        "reset",
        "broken pipe",
        "bad file descriptor",
        "transport",
    )
    return any(m in msg for m in network_markers)


class ReconnectingClient:
    """
    Drop-in replacement for memcache.Client with automatic
    reconnect+retry-once. Includes optional logging,
    metrics, and jittered backoff.
    """

    def __init__(self, servers: Iterable[str], **kwargs: Any) -> None:
        self._servers = list(servers)
        self._kwargs = dict(kwargs)
        self._lock = threading.RLock()
        self._client = _OriginalClient(self._servers, **self._kwargs)

    def _reconnect(self) -> None:
        if _ENABLE_METRICS:
            _metrics["reconnect_attempts_total"] += 1
        if _ENABLE_LOG:
            log.info(
                "mcdutils: reconnecting memcache client to %r", self._servers
            )
        with self._lock:
            self._client = _OriginalClient(self._servers, **self._kwargs)
        if _ENABLE_METRICS:
            _metrics["reconnect_success_total"] += 1

    def _backoff_sleep(self) -> None:
        if _BACKOFF_MAX_MS == 0 and _BACKOFF_MIN_MS == 0:
            return  # disabled
        delay_ms = _system_random.uniform(_BACKOFF_MIN_MS, _BACKOFF_MAX_MS)
        time.sleep(delay_ms / 1000.0)

    def __getattr__(self, name: str) -> Any:
        # Forward attributes; wrap callables with retry-once logic.
        attr = getattr(self._client, name)
        if not callable(attr):
            return attr

        @wraps(attr)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                return attr(*args, **kwargs)
            except BaseException as exc:
                if not _should_reconnect(exc):
                    # Non-network problem: bubble up.
                    raise
                start = time.time()
                try:
                    self._reconnect()
                except Exception as rex:
                    if _ENABLE_METRICS:
                        _metrics["reconnect_fail_total"] += 1
                    if _ENABLE_LOG:
                        log.error(
                            "mcdutils: reconnect attempt failed: %s", rex
                        )
                    raise
                self._backoff_sleep()
                # retry once
                if _ENABLE_METRICS:
                    _metrics["retry_calls_total"] += 1
                new_attr = getattr(self._client, name)
                try:
                    return new_attr(*args, **kwargs)
                finally:
                    if _ENABLE_METRICS:
                        _metrics["retry_duration_seconds_sum"] += (
                            time.time() - start
                        )
                        _metrics["retry_duration_seconds_count"] += 1

        return _wrapped

    # Explicitly expose close so app code can forcefully reset if desired.
    def force_reconnect(self) -> None:
        """Force a full reconnect by rebuilding underlying client."""
        self._reconnect()

    def close(self) -> None:
        try:
            c = self._client
        except Exception:
            return
        close = getattr(c, "disconnect_all", None) or getattr(c, "close", None)
        if callable(close):
            with contextlib.suppress(Exception):
                close()


# Copy class-level constants (e.g., _SERVER_RETRIES, timeouts) so that any
# external code referencing memcache.Client.<CONST> keeps working after
# monkey-patch. python-memcached expects some of these to exist at class-level.
for _k, _v in _OriginalClient.__dict__.items():
    try:
        if (
            isinstance(_k, str)
            and _k.isupper()
            and not hasattr(ReconnectingClient, _k)
        ):
            setattr(ReconnectingClient, _k, _v)
    except Exception:  # noqa: S110
        pass


def patch_memcache() -> None:
    """
    Monkey-patch memcache.Client globally to use ReconnectingClient.
    Controlled by env var MCDUTILS_DISABLE_RECONNECT to opt-out.
    """
    if os.environ.get("MCDUTILS_DISABLE_RECONNECT"):
        return
    memcache.Client = ReconnectingClient
