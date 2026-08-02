import asyncio
from urllib import parse
from httpserver.request import Request
from httpserver.response import Response
from httpserver.router import handlers, path_dict


async def send(writer, response):
    writer.write(response.to_bytes())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


def error_response(status):
    return Response(status, f"<h1>{status}</h1>")


async def handle_connection(reader, writer):
    addr = writer.get_extra_info("peername")

    try:
        head = await reader.readuntil(b"\r\n\r\n")
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError):
        writer.close()
        await writer.wait_closed()
        return

    header_lines = head[:-4].split(b"\r\n")

    request_line_text = header_lines[0].decode("latin-1")
    parts = request_line_text.split(" ")

    if len(parts) != 3:
        print(f"[{addr}] malformed request line: {request_line_text!r}")
        await send(writer, error_response("400 Bad Request"))
        return

    method, full_path, version = parts

    if "?" in full_path:
        path, query_string = full_path.split("?", 1)
        query_params = dict(parse.parse_qsl(query_string))
    else:
        path = full_path
        query_params = {}

    if (path, method) not in handlers:
        if path in path_dict:
            await send(writer, error_response("405 Method Not Allowed"))
        else:
            await send(writer, error_response("404 Not Found"))
        return

    request_headers = {}
    for line in header_lines[1:]:
        name, sep, value = line.partition(b":")
        if not sep:
            continue
        key = name.decode("latin-1").strip().lower()
        request_headers[key] = value.decode("latin-1").strip()

    length = int(request_headers.get("content-length", 0))
    body_bytes = await reader.readexactly(length) if length else b""

    request = Request(method, path, request_headers, body_bytes, query_params)

    print(f"[{addr}] method={method} path={path} version={version}")
    print(f"[{addr}] headers: {request_headers}")

    handler = handlers[(path, method)]

    try:
        body = handler(request)
    except Exception as error:
        print(f"[{addr}] handler error: {error!r}")
        await send(writer, error_response("500 Internal Server Error"))
        return

    await send(writer, Response("200 OK", body))


async def _serve():
    server = await asyncio.start_server(handle_connection, "127.0.0.1", 8080)
    async with server:
        await server.serve_forever()


def run():
    asyncio.run(_serve())


if __name__ == "__main__":
    run()
