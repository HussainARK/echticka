"""
Echticka

A Basic CLI-Based Communications App, Client Code
"""

import getpass
import pickle
import socket
import time
from threading import Thread
import sys

GIVEN_USERNAME = None
GIVEN_HOST = None
GIVEN_PORT = None

try:
    GIVEN_USERNAME = input("Enter your Username: ")

    GIVEN_HOST = input("Server Host: ")

    GIVEN_PORT = input("Server Port (Default: 9024): ")
except EOFError:
    sys.exit()
except KeyboardInterrupt:
    sys.exit()

if not GIVEN_PORT:
    GIVEN_PORT = 9024

DISCONNECT_MESSAGE = "!dc"
HEADER = 2048

SERVER_HOST = socket.gethostbyname(GIVEN_HOST)
SERVER_PORT = GIVEN_PORT
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(SERVER_ADDR)
except OSError:
    print("Couldn't connect to The Server")
    sys.exit()

print("Registering the Client...")

init_resp = pickle.loads(client.recv(HEADER))

if init_resp['password_required']:
    PASSWORD = None
    try:
        PASSWORD = getpass.getpass("Server Password: ")
    except EOFError:
        client.close()
        sys.exit()
    except KeyboardInterrupt:
        client.close()
        sys.exit()

    client.send(pickle.dumps({'username': GIVEN_USERNAME, 'password': PASSWORD}))
else:
    print("No Password needed, Accessing The Server...")
    client.send(pickle.dumps({'username': GIVEN_USERNAME}))


def send(msg):
    """Basic function to send messages to the server"""
    try:
        client.send(pickle.dumps({'sessionid': sessionid, 'message': msg}))
    except OSError:
        client.close()
        sys.exit()


def get_messages(sure):
    """A Function run on a second thread to log any received messages"""
    if sure:
        try:
            while True:
                response = pickle.loads(client.recv(HEADER))
                if not response['sessionid'] == sessionid:
                    if response['message'] is None:
                        if response['new']:
                            print(f"{response['username']} JOINED THE CHAT")
                        elif response['disconnected']:
                            print(f"{response['username']} LEFT THE CHAT")
                    else:
                        print(f"{response['username']}: {response['message']}"
                                f"")
        except OSError:
            time.sleep(0.01)
            print("Disconnected!?")
            sys.exit()
    else:
        pass


init_resp = object()

try:
    init_resp = pickle.loads(client.recv(HEADER))
except OSError:
    send(DISCONNECT_MESSAGE)
    print(f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}")
    client.close()
    sys.exit()

if not init_resp['authorized']:
    print("Wrong Password Given")
    print("Disconnecting")
    client.close()
else:
    sessionid = init_resp['sessionid']

    if not init_resp['username']:
        print("Invalid Username")
        client.close()
        sys.exit()
    else:
        username = init_resp['username']

    print(f"Connected to the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}")
    print("You can disconnect using Ctrl+C")
    print(f'You joined as {username} '
          f'with Session ID {sessionid}, '
          'Enjoy!\n')

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
                    sys.exit()
                else:
                    send(message)
            else:
                break

    except KeyboardInterrupt:
        send(DISCONNECT_MESSAGE)
        print(f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}")
        client.close()
        sys.exit()

    except EOFError:
        send(DISCONNECT_MESSAGE)
        print(f"Disconnected from the Server: {SERVER_ADDR[0]}:{SERVER_ADDR[1]}")
        client.close()
        sys.exit()
