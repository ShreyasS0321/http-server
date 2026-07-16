import socket
import threading
from httpserver.request import Request
from httpserver.response import Response

handlers={}
path_dict={}
def add_route(path,method,function)->None:

    handlers[(path,method)]=function

    if path not in path_dict:
        path_dict[path]=set()
    path_dict[path].add(method)


def send(client_socket, response):
    client_socket.sendall(response.to_bytes())
    client_socket.close()


def error_response(status):
    return Response(status, f"<h1>{status}</h1>")


def run() -> None:

    def handle_connection(client_socket,addr):

        buffer=b""
        while b"\r\n\r\n" not in buffer:
            data=client_socket.recv(4096)
            if not data:
                client_socket.close()
                return
            buffer+=data

        header_block, body_bytes = buffer.split(b"\r\n\r\n", 1)
        header_lines = header_block.split(b"\r\n")

        request_line_text = header_lines[0].decode('latin-1')
        parts = request_line_text.split(" ")

        if len(parts) != 3:
            print(f"[{addr}] malformed request line: {request_line_text!r}")
            send(client_socket, error_response("400 Bad Request"))
            return

        method, path, version = parts

        if (path,method) not in handlers:
            if path in path_dict:
                send(client_socket, error_response("405 Method Not Allowed"))
            else:
                send(client_socket, error_response("404 Not Found"))
            return

        request_headers = {}
        for line in header_lines[1:]:
            name, sep, value = line.partition(b":")
            if not sep:
                continue
            key = name.decode('latin-1').strip().lower()
            request_headers[key] = value.decode('latin-1').strip()

        print(f"[{addr}] headers: {request_headers}")

        handler= handlers[(path,method)]
        request = Request(method, path, request_headers, body_bytes)

        try:
            body=handler(request)
        except Exception as error:
            print(f"[{addr}] handler error: {error!r}")
            send(client_socket, error_response("500 Internal Server Error"))
            return

        send(client_socket, Response("200 OK", body))

    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host= "127.0.0.1"
    port=8080
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
   
    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=handle_connection,args=(client_socket, addr),daemon=True)
        thread.start()


if __name__ == "__main__":
    run()
