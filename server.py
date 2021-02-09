import json
import logging
import os
import pickle
import socket
import threading
import uuid

print(fr"""
 _____     _     _   _      _
| ____|___| |__ | |_(_) ___| | ____ _
|  _| / __| '_ \| __| |/ __| |/ / _` |
| |__| (__| | | | |_| | (__|   < (_| |
|_____\___|_| |_|\__|_|\___|_|\_\__,_|

Version: v0.1.1-alpha
Made in Iraq, Enjoyed Everywhere.""")

DISCONNECT_MESSAGE = "!dc"
HEADER = 2048

HOST = "0.0.0.0"
PORT = 9024
PASSWORD = ""

logger = logging.getLogger('botto')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(f'%(asctime)s %(message)s'))
logger.addHandler(handler)


def log(sender, message):
    logger.info(f"[{sender}] {message}")


for filename in os.listdir('.'):
    if filename.strip() == "echticka.config":
        config = json.loads(open(filename).read())

        try:
            if config['host']:
                try:
                    num1, num2, num3, num4 = config['host'].split(".")

                    if num1.strip() != "" and num2.strip() != "" and num3.strip() != "" and num4.strip() != "":
                        if int(num1) >= 0 and int(num2) >= 0 and int(num3) >= 0 and int(num4) >= 0:
                            HOST = config['host']
                            log(f"CONFIG",
                                f"Set Host as {HOST} From Configuration File")
                        else:
                            log(f"CONFIG",
                                f"Given Host is Invalid, Set Host as {HOST} "
                                f"From Auto-Configuration")
                    else:
                        log(f"CONFIG",
                            f"Given Host is Invalid, Set Host as {HOST} "
                            f"From Auto-Configuration")
                except ValueError:
                    log(f"CONFIG",
                        f"Given Host is Invalid, Set Host as {HOST} "
                        f"From Auto-Configuration")
            else:
                log(f"CONFIG",
                    f"Set Host as {HOST} From Auto-Configuration")
        except KeyError:
            log(f"CONFIG",
                f"Set Host as {HOST} From Auto-Configuration")

        try:
            if config['port']:
                if config['port'] < 22 or config['port'] > 20000:
                    log(f"CONFIG",
                        f"Given Port is Invalid, Port Set From Auto-Configuration")
                else:
                    PORT = config['port']
                    log(f"CONFIG",
                        f"Set Port as {PORT} From Configuration File")
            else:
                log(f"CONFIG",
                    f"Set Port as {PORT} From Auto-Configuration")
        except KeyError:
            log(f"CONFIG",
                f"Set Port as {PORT} From Auto-Configuration")

        try:
            if config['password']:
                if config['password'].strip() == "":
                    pass
                else:
                    if len(config['password']) > 20:
                        log(f"CONFIG",
                            f"Given Password is Too Long, No Password Set "
                            f"From Auto-Configuration")
                    else:
                        PASSWORD = config['password']
                        log(f"CONFIG",
                            f"Set User Password Access as \"{PASSWORD}\" "
                            f"From Configuration File")
            else:
                log(f"CONFIG",
                    f"No Password Set From Auto-Configuration")
        except KeyError:
            log(f"CONFIG",
                f"No Password Set From Auto-Configuration")

ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind(ADDR)
except OSError:
    logger.error(f"[SERVER] Couldn't Host it, Fuck")
    quit()

users = []
clients = set()
clients_lock = threading.Lock()


def handle_client(connection: socket.socket, address: tuple):
    log(f"SERVER",
        f"New Connection from: {address[0]}:{address[1]}")

    if PASSWORD.strip() != "":
        connection.send(pickle.dumps({'password_required': True}))
    else:
        connection.send(pickle.dumps({'password_required': False}))

    try:
        init_resp = pickle.loads(connection.recv(HEADER))

        client_username = init_resp['username'] \
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
            if PASSWORD.strip() != "":
                if init_resp['password'] != PASSWORD:
                    connection.send(pickle.dumps({'authorized': False}))
                    connection.close()
                else:
                    pass

            try:
                client_sessionid = uuid.uuid4().hex[:6]

                connection.send(pickle.dumps({'username': client_username,
                                              'sessionid': client_sessionid,
                                              'authorized': True}))

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

                    log(f"{client_username}#{client_sessionid}@{address[0]}:{address[1]}",
                        f"JOINED")

                    log(f"SERVER",
                        f"All Connections: {threading.activeCount() - 1}")

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

                                log(f"{username}#{sessionid}@{address[0]}:{address[1]}",
                                    f"DISCONNECTED")

                                log(f"SERVER",
                                    f"All Connections: {threading.activeCount() - 2}")
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

                                        logger.info(f"[{username}#{sessionid}@{address[0]}:{address[1]}]: "
                                                    f"{msg}")
                    except:
                        connected = False
                        clients.remove(connection)
                        users.remove(
                            {'username': client_username, 'sessionid': client_sessionid, 'connection': connection}
                        )
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

                        log(f"{client_username}#{client_sessionid}@{address[0]}:{address[1]}",
                            f"DISCONNECTED")

                        log(f"SERVER",
                            f"All Connections: {threading.activeCount() - 2}")

                connection.close()
            except OSError:
                pass

            except EOFError:
                pass
    except OSError:
        pass

    except EOFError:
        pass


def start():
    server.listen()
    log(f"SERVER", f"Listening on {ADDR[0]}:{ADDR[1]}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


log(f"SERVER", f'Echticka Server is starting...')
start()
