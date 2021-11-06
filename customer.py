import socket

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

PORT = 5500
SERVER = "192.168.242.46"
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send(msg) :
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def receive_message() :
    try :
        user_header = client.recv(HEADER)
        if not len(user_header) :
            return False
        username = client.recv(int(user_header.decode(FORMAT)))
        msg_header = client.recv(HEADER)
        if not len(msg_header) :
            return False
        msg = client.recv(int(msg_header.decode(FORMAT)))
        print(f"{username.decode(FORMAT)} >{msg.decode(FORMAT)}")
        return True
    except BlockingIOError as ex :
        return False


print("Client starting...")
try:
    client.connect(ADDR)
    client.setblocking(False)
    username = input("Username:")
    send(username)
    while True :
        receiving = True
        while receiving:
            receiving = receive_message()
        msg = input(f"{username} >")
        if msg != "" :
            try :
                send(msg)
            except ConnectionResetError :
                print("Server closed.")
                break
        if msg == "!DISCONNECT" :
            break
except ConnectionResetError :
    print("Server closed.")
except ConnectionRefusedError:
    print("Can't connect to server.")
