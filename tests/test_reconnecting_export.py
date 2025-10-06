##############################################################################
# Complementary tests for reconnecting metrics export.
###############################################################################
import contextlib
import os
import tempfile


def test_export_prometheus_textfile_creates_file():
    from Products.mcdutils import reconnecting as r

    # ensure counters change a bit
    r._metrics["reconnect_attempts_total"] += 1
    fd, path = tempfile.mkstemp(prefix="mcdutils_metrics_", suffix=".prom")
    os.close(fd)
    try:
        r.export_prometheus_textfile(path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "mcdutils_reconnect_attempts_total" in content
        assert "mcdutils_retry_calls_total" in content
    finally:
        with contextlib.suppress(OSError):
            os.remove(path)
