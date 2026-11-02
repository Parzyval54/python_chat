import socket
from threading import Thread, Lock

class ChatServer:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._separator_token = "<SEP>"
        self._server_socket = socket.socket()
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((host, port))
        self._clients: dict[socket.socket, str] = {}
        self._lock = Lock()


    def start(self):
        self._server_socket.listen(5)
        print(f"[*] Listening as {self._host}:{self._port}")
        while True:
            try :
                client_socket, addr = self._server_socket.accept()
            except ConnectionResetError:
                continue
            print(f"[+] {addr} connected.")
            Thread(target=self._handle_client, args=(client_socket,), daemon=True).start()

    def _handle_client(self, cs):
        """
            This function keep listening for a message from `cs` socket
            Whenever a message is received, broadcast it to all other connected clients
            """
        while True:
                try:
                    #keep listening for a message from 'cs' socket'
                    msg = cs.recv(1024).decode()
                except Exception:  # noqa: BLE001
                    #client no longer connected
                    #remove it from the set
                    name = self._remove(cs)
                    self._broadcast(f"[!] {name} a quitté le chat")
                    break
                else:
                    #if we received a message, replace the <SEP>
                    #token with ":" for nice printing
                    if not msg:
                        name = self._remove(cs)
                        self._broadcast(f"[!] {name} a quitté le chat")
                        break
                    
                    if cs not in self._clients:
                        with self._lock:
                            self._clients[cs] = msg.split(self._separator_token)[0]
                        
                    msg=msg.replace(self._separator_token, ":")
        
                #iterate over all connected sockets :
                self._broadcast(msg)


    def _broadcast(self, text:str):
        with self._lock:
            for client in self._clients:
                client.send(text.encode())

    def _remove(self, cs):
        with self._lock:
            name =self._clients.pop(cs, "un client")
            cs.close()
            return name

if __name__ == "__main__":
    ChatServer("0.0.0.0", 5002).start()