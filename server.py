import pickle
import socket
import threading
import os
import json
import uuid

DISCONNECT_MESSAGE = "!dc"
HEADER = 2048

HOST = "0.0.0.0"
PORT = 9024

for filename in os.listdir('.'):
    if filename.strip() == "echticka.config":
        config = json.loads(open(filename).read())
        if config['host']:
            HOST = config['host']
            print(f"[CONFIG] Set Host as {HOST} From Configuration File")
        else:
            print(f"[CONFIG] Set Host as {HOST} From Auto-Configuration")

        if config['port']:
            PORT = config['port']
            print(f"[CONFIG] Set Port as {PORT} From Configuration File")
        else:
            print(f"[CONFIG] Set Port as {PORT} From Auto-Configuration")

ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

users = []
clients = set()
clients_lock = threading.Lock()


def handle_client(connection, address):
    print(f"[SERVER] New Connection from: {address[0]}:{address[1]}")

    init = pickle.loads(connection.recv(HEADER))

    client_username = init['username'] \
        .replace('[', '') \
        .replace('#', '') \
        .replace('@', '') \
        .replace(':', '') \
        .replace(']', '') \
        .strip()

    if client_username == "" or len(client_username) >= 20:
        connection.send(pickle.dumps({'username': False, 'sessionid': False}))
        connection.close()
    else:
        client_sessionid = uuid.uuid4().hex[:6]

        connection.send(pickle.dumps({'username': client_username,
                                      'sessionid': client_sessionid}))

        with clients_lock:
            clients.add(connection)

        users.append({'username': client_username, 'sessionid': client_sessionid, 'connection': connection})

        connected = True

        with clients_lock:
            if len(clients) != 0:
                for a_client in clients:
                    if a_client:
                        a_client.send(pickle.dumps(
                            {
                                'username': client_username,
                                'sessionid': client_sessionid,
                                'message': None,
                                'disconnected': False,
                                'new': True
                            }
                        ))

            print(f"[{client_username}#{client_sessionid}@{address[0]}:{address[1]}] JOINED")

        while connected:
            try:
                response = pickle.loads(connection.recv(HEADER))

                sessionid = response['sessionid']
                msg = response['message']

                username = "DEFAULT"

                for user in users:
                    if user['sessionid'] == sessionid:
                        username = user['username']

                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    clients.remove(connection)
                    users.remove({'username': username, 'sessionid': sessionid, 'connection': connection})
                    with clients_lock:
                        if len(clients) != 0:
                            for a_client in clients:
                                if a_client:
                                    a_client.send(
                                        pickle.dumps(
                                            {
                                                'username': username,
                                                'sessionid': sessionid,
                                                'message': None,
                                                'disconnected': True,
                                                'new': False
                                            }
                                        )
                                    )

                        print(f"[{username}#{sessionid}@{address[0]}:{address[1]}] DISCONNECTED")
                else:
                    if msg.strip() != "":
                        with clients_lock:
                            if len(clients) != 0:
                                for a_client in clients:
                                    if a_client:
                                        try:
                                            a_client.send(
                                                pickle.dumps(
                                                    {
                                                        'username': username,
                                                        'sessionid': sessionid,
                                                        'message': msg,
                                                        'disconnected': False,
                                                        'new': False
                                                    }
                                                )
                                            )
                                        except:
                                            connected = False

                                print(f"[{username}#{sessionid}@{address[0]}:{address[1]} MESSAGE] {msg}")
            except:
                connected = False
                clients.remove(connection)
                users.remove({'username': client_username, 'sessionid': client_sessionid, 'connection': connection})
                with clients_lock:
                    if len(clients) != 0:
                        for a_client in clients:
                            if a_client:
                                a_client.send(
                                    pickle.dumps(
                                        {
                                            'username': client_username,
                                            'sessionid': client_sessionid,
                                            'message': None,
                                            'disconnected': True,
                                            'new': False
                                        }
                                    )
                                )

                print(f"[{client_username}#{client_sessionid}@{address[0]}:{address[1]}] DISCONNECTED")

        connection.close()


def start():
    server.listen()
    print(f"[SERVER] Listening on {ADDR[0]}:{ADDR[1]}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
        print(f"[SERVER] All Connections: {threading.activeCount() - 1}")


print('[SERVER] Echticka Server is starting...')
start()
