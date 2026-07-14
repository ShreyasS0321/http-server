# http-server

A minimal HTTP/1.1 server written from scratch in Python, on top of raw TCP
sockets — no `http.server`, no framework. Built as a learning project to
understand how a request goes from bytes on a socket to a routed response.

## Goals

- Accept TCP connections and speak HTTP/1.1 on the wire
- Parse the request line, headers, and body by hand
- Route requests to handlers and build proper responses
- Handle multiple connections concurrently
- Support `keep-alive` connection reuse

## Requirements

- Python 3.10+

## Setup

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -e ".[dev]"
```

## Running

```bash
httpserver
# or
python -m httpserver.server
```

## Testing

```bash
pytest
```

## Project layout

```
src/httpserver/    # server package
tests/             # unit + integration tests
```

## Status

Scaffold only. The TCP accept loop and HTTP parsing land in subsequent commits.

## License

MIT
