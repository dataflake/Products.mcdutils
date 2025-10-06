import contextlib
import os


##############################################################################
#
# Copyright (c) 2008-2023 Tres Seaver and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################
""" Product:  mcdutils

Implement Zope sessions using memcached as the backing store.
"""


__version__ = "5.0.0"


class MemCacheError(IOError):
    pass


def initialize(context):
    from .proxy import addMemCacheProxy
    from .proxy import addMemCacheProxyForm
    from .proxy import MemCacheProxy

    context.registerClass(
        MemCacheProxy, constructors=(addMemCacheProxyForm, addMemCacheProxy)
    )

    from .sessiondata import addMemCacheSessionDataContainer
    from .sessiondata import addMemCacheSessionDataContainerForm
    from .sessiondata import MemCacheSessionDataContainer

    context.registerClass(
        MemCacheSessionDataContainer,
        constructors=(
            addMemCacheSessionDataContainerForm,
            addMemCacheSessionDataContainer,
        ),
    )

    from .zcache import addMemCacheZCacheManager
    from .zcache import addMemCacheZCacheManagerForm
    from .zcache import MemCacheZCacheManager

    context.registerClass(
        MemCacheZCacheManager,
        constructors=(addMemCacheZCacheManagerForm, addMemCacheZCacheManager),
    )


# --- mcdutils: enable resilient memcache client by default -------------------
try:  # patch python-memcached Client with a reconnecting wrapper
    from .reconnecting import patch_memcache as _mcdutils_patch_memcache

    _mcdutils_patch_memcache()
except Exception:  # pragma: no cover - safe import guard # noqa: S110
    pass
# -----------------------------------------------------------------------------

# --- mcdutils: add retry at tpc_vote with metrics & structured logs
try:
    from .mapping import MemCacheMapping

    import logging
    import os
    import time

    if not os.environ.get("MCDUTILS_DISABLE_TPC_RETRY"):
        from . import MemCacheError as _MCD_Err
        from .reconnecting import incr_metric as _mcd_incr_metric  # metrics

        log = logging.getLogger("Products.mcdutils.tpc")
        _orig_tpc_vote = getattr(MemCacheMapping, "tpc_vote", None)

        if _orig_tpc_vote is not None and not getattr(
            _orig_tpc_vote, "_mcdutils_patched", False
        ):

            def _tpc_vote_with_retry(self, txn):  # noqa: C901
                attempts = 1
                try:
                    attempts = int(
                        os.environ.get("MCDUTILS_TPC_RETRY_ATTEMPTS", "1")
                    )
                except Exception:
                    attempts = 1
                backoff_ms = 0
                try:
                    backoff_ms = int(
                        os.environ.get("MCDUTILS_TPC_RETRY_BACKOFF_MS", "100")
                    )
                except Exception:
                    backoff_ms = 0

                # First attempt (original behavior)
                try:
                    return _orig_tpc_vote(self, txn)
                except _MCD_Err as first_exc:
                    last_exc = first_exc
                    if os.environ.get("MCDUTILS_LOG") == "1":
                        log.warning(
                            "tpc_vote failed on first try; will retry",
                            extra={
                                "event": "tpc_vote_fail_first",
                                "retries": attempts,
                                "backoff_ms": backoff_ms,
                            },
                        )

                # Retry loop
                for i in range(1, attempts + 1):
                    t0 = time.time()
                    # Metrics: count attempt
                    with contextlib.suppress(Exception):
                        _mcd_incr_metric("tpc_retry_attempts_total", 1)
                    try:
                        # Hard reconnect path
                        # Accept both _p_proxy (observed) and _proxy (older)
                        _proxy_obj = getattr(self, "_p_proxy", None)
                        if _proxy_obj is None:
                            _proxy_obj = getattr(self, "_proxy", None)
                        if _proxy_obj is None:
                            _proxy_obj = getattr(self, "proxy", None)
                        _client = getattr(_proxy_obj, "client", None)
                        if _client is not None:
                            disc = getattr(_client, "disconnect_all", None)
                            if callable(disc):
                                with contextlib.suppress(Exception):
                                    disc()
                            frc = getattr(_client, "force_reconnect", None)
                            if callable(frc):
                                with contextlib.suppress(Exception):
                                    frc()
                            # Dummy op to warm/validate
                            try:
                                setter = getattr(_client, "set", None)
                                if callable(setter):
                                    setter("mcdutils:tpc_probe", 1, time=2)
                            except Exception:  # noqa: S110
                                pass

                        # Optional backoff
                        if backoff_ms > 0:
                            time.sleep(backoff_ms / 1000.0)
                            try:
                                _mcd_incr_metric(
                                    "tpc_retry_backoff_seconds_sum",
                                    backoff_ms / 1000.0,
                                )
                                _mcd_incr_metric(
                                    "tpc_retry_backoff_seconds_count", 1
                                )
                            except Exception:  # noqa: S110
                                pass

                        # Attempt vote again
                        result = _orig_tpc_vote(self, txn)
                        # Success metrics
                        with contextlib.suppress(Exception):
                            _mcd_incr_metric("tpc_retry_success_total", 1)
                        if os.environ.get("MCDUTILS_LOG") == "1":
                            log.info(
                                "tpc_vote retry succeeded",
                                extra={
                                    "event": "tpc_vote_retry_ok",
                                    "attempt": i,
                                    "elapsed_ms": int(
                                        (time.time() - t0) * 1000
                                    ),
                                },
                            )
                        return result
                    except _MCD_Err as exc:
                        last_exc = exc
                        # Failure metrics
                        with contextlib.suppress(Exception):
                            _mcd_incr_metric("tpc_retry_fail_total", 1)
                        if os.environ.get("MCDUTILS_LOG") == "1":
                            log.error(
                                "tpc_vote retry failed",
                                extra={
                                    "event": "tpc_vote_retry_fail",
                                    "attempt": i,
                                    "elapsed_ms": int(
                                        (time.time() - t0) * 1000
                                    ),
                                },
                            )
                        continue

                # If still failing, re-raise last MemCacheError
                raise last_exc

            _tpc_vote_with_retry._mcdutils_patched = True
            MemCacheMapping.tpc_vote = _tpc_vote_with_retry
except Exception:  # noqa: S110
    # Safe guard: don't break import if anything goes wrong here
    pass
# -----------------------------------------------------------------------------
