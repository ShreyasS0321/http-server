import socket
import subprocess
import sys
import time

import pytest


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_until_up(port, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"server on port {port} did not start within {timeout}s")


@pytest.fixture(params=["threaded", "async"])
def base_url(request):
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "tests._server_app", request.param, str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_until_up(port)
        yield f"http://127.0.0.1:{port}"
    finally:
        proc.terminate()
        proc.wait(timeout=5)
