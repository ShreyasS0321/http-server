import socket
import threading


def main() -> None:
    
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
            body = b"<h1>400 Bad Request</h1>"
            headers = "HTTP/1.1 400 Bad Request\r\n"
            headers += "Content-Type: text/html\r\n"
            headers += f"Content-Length: {len(body)}\r\n"
            headers += "Connection: close\r\n"
            headers += "\r\n"
            client_socket.sendall(headers.encode("latin-1") + body)
            client_socket.close()
            return

        method, path, version = parts
        print(f"[{addr}] method={method} path={path} version={version}")

        request_headers = {}
        for line in header_lines[1:]:
            name, sep, value = line.partition(b":")
            if not sep:
                continue
            key = name.decode('latin-1').strip().lower()
            request_headers[key] = value.decode('latin-1').strip()

        print(f"[{addr}] headers: {request_headers}")
        
        body = b"<h1>Hello from my custom server!</h1>"

        headers = "HTTP/1.1 200 OK\r\n"
        headers += "Content-Type: text/html\r\n"
        headers += f"Content-Length: {len(body)}\r\n"
        headers += "Connection: close\r\n"
        headers += "\r\n"

        response = headers.encode("latin-1") + body

        client_socket.sendall(response)
        client_socket.close()
            
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
    main()
