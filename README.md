# http-server

An HTTP/1.1 server written from scratch in Python on top of raw TCP sockets. No
`http.server`, no framework, no third-party dependencies. It parses the HTTP
wire format by hand, routes requests to handler functions, and ships in two
interchangeable concurrency models: a thread-per-connection server and an
asyncio server.

Built as a learning project to understand how a request travels from bytes on a
socket to a routed response, and what production tools like nginx, uvicorn, and
Flask actually do under the hood.

## What it does

- Accepts TCP connections and speaks HTTP/1.1 on the wire.
- Reads a full request off the stream (request line, headers, body) with correct
  message framing.
- Parses the method, path, headers (into a case-insensitive dict), and query
  string.
- Routes `(path, method)` to a registered handler function.
- Returns proper responses with `Content-Length`: `200`, `400` (malformed
  request), `404` (unknown path), `405` (wrong method), `500` (handler raised).
- Passes each handler a `Request` object (`method`, `path`, `headers`, `body`,
  `query_params`).
- Runs on either a thread pool of one-thread-per-connection, or a single-thread
  asyncio event loop, using the same application code.

## Requirements

Python 3.10 or newer. No runtime dependencies (`pytest` only for the test suite).

## Install

```bash
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# macOS/Linux:         source .venv/bin/activate

pip install -e ".[dev]"
```

## Run the example app

```bash
python examples/hello.py           # threaded server on 127.0.0.1:8080
python examples/hello_async.py     # same app, asyncio server
```

Then, from another terminal:

```bash
curl http://127.0.0.1:8080/
curl "http://127.0.0.1:8080/hello?name=ada"
curl -i http://127.0.0.1:8080/missing    # 404
```

## Writing your own app

The server is a library. An application registers routes and starts a server.
Handlers are plain functions that take a `Request` and return a body string.

```python
from httpserver.router import add_route
from httpserver.server import run          # threaded
# from httpserver.server_async import run  # asyncio (same app)

def home(request):
    return "<h1>Home</h1>"

def greet(request):
    name = request.query_params.get("name", "stranger")
    return f"<h1>Hello {name}</h1>"

add_route("/", "GET", home)
add_route("/greet", "GET", greet)

if __name__ == "__main__":
    run()                                  # run(host="0.0.0.0", port=9000) to override
```

`add_route(path, method, handler)` is the registration seam, equivalent to
`@app.get(path)` in FastAPI or a `urls.py` entry in Django. Switching the server
between threaded and asyncio is a one-line import change, because the
application never touches sockets.

## Architecture

```
src/httpserver/
    request.py        Request dataclass (method, path, headers, body, query_params)
    response.py       Response dataclass, serializes itself to HTTP bytes
    router.py         shared routing table and add_route()
    server.py         thread-per-connection server
    server_async.py   asyncio server (same parsing and routing)
examples/
    hello.py          demo app on the threaded server
    hello_async.py    the same app on the asyncio server
tests/
    test_server.py    behavior tests run against both servers
```

I/O lives only in the two server files. Parsing, routing, and the request and
response types are pure logic with no socket code, which is why the asyncio
rewrite reused them unchanged.

## Testing

```bash
pytest
```

The suite starts each server as a subprocess on a free port and exercises it
over real HTTP. Every test is parameterized over both the threaded and asyncio
server, so the two implementations are verified to behave identically.

## Differences from a production web server

This is a teaching implementation. A production stack (nginx in front of
gunicorn/uvicorn in front of Django/FastAPI) differs in ways that matter:

- No TLS/HTTPS. A production edge terminates TLS; this speaks plain HTTP only.
- No keep-alive. Each request uses one connection and then closes
  (`Connection: close`). Production reuses connections for many requests.
- Exact-path routing only. No path parameters (`/users/{id}`), no wildcards, no
  middleware. Routing is a dict keyed on `(path, method)`.
- Handlers return a body string only. They cannot set status codes, custom
  headers, or content types. A real framework returns a full response object.
- No request-body handling for applications. The body is read and framed but not
  exposed to handlers in a useful form (no form or JSON parsing).
- Blocking work is unsafe on the asyncio server. Handlers run on the event loop,
  so a slow handler stalls all connections. Production ASGI servers offload sync
  handlers to a thread pool.
- Thread-per-connection does not scale. The threaded server spends about 1 MB
  per connection and collapses under thousands of concurrent clients (the C10k
  problem). The asyncio server is the answer to that, but still uses the
  higher-level stream API rather than the lower-level protocol API plus uvloop
  that fast servers use.
- Minimal hardening. Limited handling of malformed input, no timeouts on the
  threaded server, no rate limiting, no logging framework, no graceful shutdown.

## License

MIT
