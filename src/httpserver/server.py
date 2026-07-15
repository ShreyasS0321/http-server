import socket
import threading


def main() -> None:
    
    def handle_connection(client_socket,addr):

        buffer=b""
        # Read until we have the request line's terminating CRLF.
        while b"\r\n" not in buffer:
            data=client_socket.recv(4096)
            if not data:
                # Client hung up before sending a full request line.
                client_socket.close()
                return
            buffer+=data

        request_line_bytes, remaining_bytes = buffer.split(b"\r\n", 1)
        request_line_text = request_line_bytes.decode('latin-1')
        parts = request_line_text.split(" ")

        if len(parts) == 3:
            method, path, version = parts
            print(f"[{addr}] method={method} path={path} version={version}")
        else:
            print(f"[{addr}] malformed request line: {request_line_text!r}")

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
