import socket
from threading import Thread
import select

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

PORT = 5500
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

sockets_list = [server]
clients = {}


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def receive_message(conn) :
    try :
        msg_header = conn.recv(HEADER)
        if not len(msg_header) :
            return False
        msg = conn.recv(int(msg_header.decode(FORMAT)))
        return {"header" : msg_header, "data" : msg}
    except Exception as ex :
        print(ex)
        return False


def receive(conn) :
    t = ThreadWithReturnValue(target=receive_message, args=conn)
    t.run()
    return t.join()


def send_message(conn, msg) :
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(msg)
    return True


def send(conn, msg) :
    t = ThreadWithReturnValue(target=send_message, args=(conn, msg))
    t.run()
    return t.join()


def start() :
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True :
        read_sockets, _, ex_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets :
            if notified_socket == server :
                conn, addr = server.accept()
                print(f"[NEW CONNECTION] {addr} connected.")
                user = receive_message(conn)
                if user is False :
                    continue
                sockets_list.append(conn)
                clients[conn] = user
            else:
                msg = receive_message(notified_socket)
                if msg is False or msg['data'].decode(FORMAT) == "!DISCONNECT":
                    print(f"Closed connection from {clients[notified_socket]['data'].decode(FORMAT)} ")
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    notified_socket.close()
                    continue
                user = clients[notified_socket]
                print(f"Received message from {user['data'].decode(FORMAT)}: {msg['data'].decode(FORMAT)}")
                for client_socket in clients:
                    if client_socket != notified_socket:
                        send_message(client_socket, user['data'])
                        send_message(client_socket, msg['data'])


print("Server is starting...")
start()
