import socket
import threading


def main() -> None:
    
    def handle_connection(client_socket,addr):
        
        
        while True:
            data=client_socket.recv(4096)
            if not data:
                break
            client_socket.sendall(data)
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
