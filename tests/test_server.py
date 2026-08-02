import socket
import urllib.error
import urllib.request


def http_get(base_url, path, method="GET", headers=None):
    req = urllib.request.Request(base_url + path, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("latin-1")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("latin-1")


def test_home_returns_200(base_url):
    status, body = http_get(base_url, "/")
    assert status == 200
    assert "Home" in body


def test_query_param_is_used(base_url):
    status, body = http_get(base_url, "/hello?name=shreyas")
    assert status == 200
    assert body == "Hello shreyas"


def test_query_param_defaults_when_absent(base_url):
    status, body = http_get(base_url, "/hello")
    assert status == 200
    assert body == "Hello stranger"


def test_query_param_url_decoded(base_url):
    status, body = http_get(base_url, "/hello?name=John%20Doe")
    assert status == 200
    assert body == "Hello John Doe"


def test_header_is_parsed(base_url):
    status, body = http_get(base_url, "/agent", headers={"User-Agent": "pytest-agent"})
    assert status == 200
    assert body == "pytest-agent"


def test_unknown_path_returns_404(base_url):
    status, _ = http_get(base_url, "/does-not-exist")
    assert status == 404


def test_wrong_method_returns_405(base_url):
    status, _ = http_get(base_url, "/hello", method="POST")
    assert status == 405


def test_handler_error_returns_500(base_url):
    status, _ = http_get(base_url, "/boom")
    assert status == 500


def test_server_survives_a_handler_crash(base_url):
    http_get(base_url, "/boom")
    status, body = http_get(base_url, "/")
    assert status == 200
    assert "Home" in body


def test_malformed_request_line_returns_400(base_url):
    host, port = base_url.removeprefix("http://").split(":")
    conn = socket.create_connection((host, int(port)), timeout=5)
    conn.sendall(b"GARBAGE\r\nHost: x\r\n\r\n")
    data = conn.recv(200)
    conn.close()
    assert data.startswith(b"HTTP/1.1 400")
