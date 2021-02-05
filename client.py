import pickle
import socket
from threading import Thread
import time
import getpass

print(f'Enter your Username: ', end='')
username = input()

print(f"Server Host: ", end='')
tcp_hostname = input()

print(f"Server Port (Default: 9024): ", end='')
tcp_port = input()

if not tcp_port:
    tcp_port = 9024
else:
    if int(tcp_port) < 22 or int(tcp_port) > 20000:
        print(f"Given Port is Invalid")
        quit()
    else:
        tcp_port = int(tcp_port)

DISCONNECT_MESSAGE = "!dc"
HEADER = 2048

SERVER_HOST = socket.gethostbyname(tcp_hostname)
SERVER_PORT = tcp_port
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(SERVER_ADDR)
except:
    print(f"Couldn't connect to The Server")
    quit()

print(f"Registering the Client...")

init_resp = pickle.loads(client.recv(HEADER))

if init_resp['password_required']:
    print(f"Server Password: ", end='')
    password = getpass.getpass("")
    client.send(pickle.dumps({'username': username, 'password': password}))
else:
    print(f"No Password needed, Accessing The Server...")
    client.send(pickle.dumps({'username': username}))


def send(msg):
    try:
        client.send(pickle.dumps({'sessionid': sessionid, 'message': msg}))
    except:
        client.close()
        exit()


init_resp = object()

try:
    init_resp = pickle.loads(client.recv(HEADER))
except:
    send(DISCONNECT_MESSAGE)
    print(f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
          f"")
    client.close()
    quit()

if not init_resp['authorized']:
    print(f"Wrong Password Given")
    print(f"Disconnecting")
    client.close()
else:
    sessionid = init_resp['sessionid']

    if not init_resp['username']:
        print(f"Invalid Username")
        client.close()
        exit()
    else:
        username = init_resp['username']

    print(f"Connected to the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}")


    def get_messages(sure):
        if sure:
            try:
                while True:
                    response = pickle.loads(client.recv(HEADER))
                    if not response['sessionid'] == "69420NICE":
                        if not response['sessionid'] == sessionid:
                            if response['message'] is None:
                                if response['new']:
                                    print(f"{response['username']} JOINED THE CHAT")
                                elif response['disconnected']:
                                    print(f"{response['username']} LEFT THE CHAT")
                            else:
                                print(f"{response['username']}: {response['message']}"
                                      f"")
                    else:
                        print(f"THE SERVER ATTEMPTS TO SHUTDOWN")
                        send(DISCONNECT_MESSAGE)
                        print(
                            f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
                            f"")
                        client.close()
                        quit()
            except:
                time.sleep(0.1)
                print(f"Disconnected!?")
                quit()
        else:
            pass


    print(f'To Disconnect, send: {DISCONNECT_MESSAGE}')

    print(f'You joined as {username} '
          f'with Session ID {sessionid}, '
          f'Enjoy!\n')

    thread = Thread(target=get_messages, args=(True,))
    thread.start()

    try:
        while True:
            if client:
                message = input()
                if message == DISCONNECT_MESSAGE:
                    send(message)
                    print(
                        f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
                        f"")
                    client.close()
                    quit()
                else:
                    send(message)
            else:
                break

    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE)
        print(f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
              f"")
        client.close()
        quit()

    except EOFError:
        send(DISCONNECT_MESSAGE)
        print(f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
              f"")
        client.close()
        quit()
