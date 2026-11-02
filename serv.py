import socket
from threading import Thread 


SERVER_HOST = "0.0.0.0"
SERVER_PORT=5002
serparator_token ="<SEP>" #we will use this to separate the client name & message

#initialize list/set of all connected client's sockets
client_sockets = set()

#create a TCP socket
s = socket.socket()

#make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))

s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")



def listen_for_clients(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try:
            #keep listening for a message from 'cs' socket'
            msg = cs.recv(1024).decode()
        except Exception as e:  # noqa: BLE001
            #client no longer connected
            #remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
            break
        else:
            #if we received a message, replace the <SEP>
            #token with ":" for nice printing
            if not msg:
                client_sockets.remove(cs)
                break
            msg=msg.replace(serparator_token, ":")

        #iterate over all connected sockets :
        for client_socket in client_sockets:
            client_socket.send(msg.encode())


while True:
    #we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    t = Thread(target=listen_for_clients, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    #start the new thread
    t.start()