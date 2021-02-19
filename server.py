"""
Echticka

A Basic CLI-Based Communications App, Server Code
"""

import json
import logging
import os
import pickle
import socket
import sys
import threading
import uuid

print(r""" _____     _     _   _      _
| ____|___| |__ | |_(_) ___| | ____ _
|  _| / __| '_ \| __| |/ __| |/ / _` |
| |__| (__| | | | |_| | (__|   < (_| |
|_____\___|_| |_|\__|_|\___|_|\_\__,_|

Version: v0.1.5-alpha
Made in Iraq, Enjoyed Everywhere.
""")


class User:
    """
    User

    A Class to define an Echticka user in the current Session
    """
    def __init__(self, username: str, sessionid: str, connection: socket.socket):
        self.username = username
        self.sessionid = sessionid
        self.connection = connection


DISCONNECT_MESSAGE = "!dc"
HEADER = 2048

HOST = "0.0.0.0"
PORT = 9024
PASSWORD = ""

logger = logging.getLogger('botto')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(handler)


def log(sender, message):
    """Log a message in the console"""
    logger.info("[%s] " % sender + "%s" % message)


for filename in os.listdir('.'):
    if filename.strip() == "echticka.config":
        CONFIG = None

        try:
            CONFIG = json.loads(open(filename).read())
        except json.JSONDecodeError:
            logger.error("[ERROR] Can't parse The echticka.config File, " \
                          "using Default Configuration")
            break

        try:
            if CONFIG['host']:
                try:
                    num1, num2, num3, num4 = CONFIG['host'].split(".")

                    if num1.strip() != "" and num2.strip() != "" and \
                    num3.strip() != "" and num4.strip() != "":
                        if int(num1) >= 0 and int(num2) >= 0 and int(num3) >= 0 and int(num4) >= 0:
                            HOST = CONFIG['host']
                            log("CONFIG",
                                f"Set Host as ({HOST}) From Configuration File")
                        else:
                            log("CONFIG",
                                f"Given Host is Invalid, Set Host as ({HOST}) "
                                "From Auto-Configuration")
                    else:
                        log("CONFIG",
                            f"Given Host is Invalid, Set Host as ({HOST}) "
                            "From Auto-Configuration")
                except ValueError:
                    log("CONFIG",
                        f"Given Host is Invalid, Set Host as ({HOST}) "
                        "From Auto-Configuration")
            else:
                log("CONFIG",
                    f"Set Host as ({HOST}) From Auto-Configuration")
        except KeyError:
            log("CONFIG",
                f"Set Host as ({HOST}) From Auto-Configuration")

        try:
            if CONFIG['port']:
                if CONFIG['port'] < 22 or CONFIG['port'] > 20000:
                    log("CONFIG",
                        "Given Port is Invalid, Port Set From Auto-Configuration")
                else:
                    PORT = CONFIG['port']
                    log("CONFIG",
                        f"Set Port as ({PORT}) From Configuration File")
            else:
                log("CONFIG",
                    f"Set Port as ({PORT}) From Auto-Configuration")
        except KeyError:
            log("CONFIG",
                f"Set Port as ({PORT}) From Auto-Configuration")

        try:
            if CONFIG['password']:
                if CONFIG['password'].strip() == "":
                    pass
                else:
                    if len(CONFIG['password']) > 20:
                        log("CONFIG",
                            "Given Password is Too Long, No Password Set "
                            "From Auto-Configuration")
                    else:
                        PASSWORD = CONFIG['password']
                        log("CONFIG",
                            "Set Server Password as \"{PASSWORD}\" "
                            "From Configuration File")
            else:
                log("CONFIG",
                    "No Password Set From Auto-Configuration")
        except KeyError:
            log("CONFIG",
                "No Password Set From Auto-Configuration")

ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind(ADDR)
except:
    logger.error("[ERROR] Couldn't Host it, Some error was thrown here or there")
    sys.exit()

users = set()
clients_lock = threading.Lock()


def handle_client(connection: socket.socket, address: tuple):
    """Main function which creates a new thread for each client to handle"""
    log("SERVER",
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
                    users.add(User(client_username, client_sessionid, connection))

                connected = True

                with clients_lock:
                    if len(users) != 0:
                        for a_user in users:
                            if a_user.connection == connection:
                                a_user.connection.send(pickle.dumps(
                                    {
                                        'username': client_username,
                                        'sessionid': client_sessionid,
                                        'message': None,
                                        'disconnected': False,
                                        'new': True
                                    }
                                ))

                    log(f"{client_username}#{client_sessionid}@{address[0]}:{address[1]}",
                        "JOINED")

                    log("SERVER",
                        f"All Connections: {threading.activeCount() - 1}")

                while connected:
                    try:
                        response = pickle.loads(connection.recv(HEADER))

                        sessionid = response['sessionid']
                        msg = response['message']

                        username = "DEFAULT"

                        for user in users:
                            if user.sessionid == sessionid:
                                username = user.username

                        if msg == DISCONNECT_MESSAGE:
                            connected = False
                            for user in users:
                                if user.sessionid == sessionid:
                                    users.remove(user)

                            with clients_lock:
                                if len(users) != 0:
                                    for a_user in users:
                                        if a_user.connection == connection:
                                            a_user.connection.send(
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
                                    "DISCONNECTED")

                                log("SERVER",
                                    f"All Connections: {threading.activeCount() - 2}")
                        else:
                            if msg.strip() != "":
                                with clients_lock:
                                    if len(users) != 0:
                                        for a_user in users:
                                            if a_user.connection:
                                                try:
                                                    a_user.connection.send(
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

                                        logger.info("[%s" % username +
                                                    "#%s@" % sessionid +
                                                    "%s:" % address[0] +
                                                    "%s]:" % address[1] +
                                                    "%s" % msg)
                    except:
                        connected = False
                        for user in users:
                            if user.sessionid == client_sessionid:
                                users.remove(user)
                        with clients_lock:
                            if len(users) != 0:
                                for a_user in users:
                                    if a_user.connection:
                                        a_user.connection.send(
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
                            "DISCONNECTED")

                        log("SERVER",
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


log("SERVER", 'Echticka Server is starting...')
server.listen()
log("SERVER", f"Listening on {ADDR[0]}:{ADDR[1]}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
