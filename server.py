"""
Echticka

A Basic CLI-Based Communications App, Server Code
"""

import json
import platform
import logging
import os
import pickle
import socket
import sys
import threading
import uuid

print(r"""
 _____     _     _   _      _
| ____|___| |__ | |_(_) ___| | ____ _
|  _| / __| '_ \| __| |/ __| |/ / _` |
| |__| (__| | | | |_| | (__|   < (_| |
|_____\___|_| |_|\__|_|\___|_|\_\__,_|

Version: v0.2.0-alpha
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
    logger.info("[%s] " % sender + message)


def check_address(address: str) -> bool:
    """Return True if it's a valid IP Address, otherwise return False"""
    try:
        number1 = address.split(".")[0]
        number2 = address.split(".")[1]
        number3 = address.split(".")[2]
        number4 = address.split(".")[3]

        return bool(
            number1.strip() != "" and \
            number2.strip() != "" and \
            number3.strip() != "" and \
            number4.strip() != "" and \
            int(number1) >= 0 and \
            int(number2) >= 0 and \
            int(number3) >= 0 and \
            int(number4) >= 0)

    except:
        return False

def get_config() -> dict:
    """Return a dictionary for the configuration file"""
    try:
        file = open('echticka.config', 'r')
        config = file.read()
        if config != '':
            config = json.loads(config)
        else:
            config =  dict()
    except FileNotFoundError:
        file = open('echticka.config', 'x')
        config = dict()

    file = open('echticka.config', 'w')
    try:
        if config['bans'] != []:
            pass
        else:
            config['bans'] = []

    except KeyError:
        config['bans'] = []

    file.write(json.dumps(config, indent=2))
    return config


def ban(address: str) -> bool:
    """Add a user to the ban list"""
    address = address.strip()
    if check_address(address):
        config = get_config()

        file = open('echticka.config', 'w')
        try:
            if config['bans'] != []:
                if address not in config['bans']:
                    config['bans'].append(address)
                else:
                    file.write(json.dumps(config, indent=2))
                    return False
            else:
                config['bans'] = [address,]

        except KeyError:
            config['bans'] = [address,]

        file.write(json.dumps(config, indent=2))

        return True
    else:
        return False

def unban(address: str) -> bool:
    """Remove a user from the ban list"""
    address = address.straddress()
    if check_address(address):
        config = get_config()

        file = open('echticka.config', 'w')
        try:
            if config['bans'] != []:
                if address in config['bans']:
                    config['bans'].remove(address)
                    file.write(json.dumps(config, indent=2))
                    return True
                else:
                    file.write(json.dumps(config, indent=2))
                    return False
            else:
                config['bans'] = []

        except KeyError:
            config['bans'] = []

        file.write(json.dumps(config, indent=2))
        return False
    else:
        return False


def unbanall() -> bool:
    """Remove all users from the ban list"""
    config = get_config()

    file = open('echticka.config', 'w')
    try:
        if config['bans'] != []:
            config['bans'].clear()
            file.write(json.dumps(config, indent=2))
            return True
        else:
            config['bans'] = []

    except KeyError:
        config['bans'] = []

    file.write(json.dumps(config, indent=2))
    return False


def update_config():
    """A Function to set/update the Configuration based on the echticka.config file"""
    global HOST, PORT, PASSWORD

    for filename in os.listdir('.'):
        if filename.strip() == "echticka.config":
            config = None

            file = open(filename, 'r')

            try:
                config = json.loads(file.read())
            except json.JSONDecodeError:
                if file.read().strip() != "":
                    logger.error("[ERROR] Can't parse The echticka.config File, " \
                                "using Default Configuration")
                    break
                else:
                    open(filename, 'w').write(
                        json.dumps(
                            {
                                'host': "0.0.0.0",
                                'port': 9024,
                                'password': ""
                            }
                        )
                    )

                    log("CONFIG", 'No configuration file found, Generated a New one')

                    config = json.loads(file.read())

            try:
                if config['host']:
                    if check_address(config['HOST']):
                        HOST = config['host']
                        log("CONFIG",
                            f"Set Host as ({HOST}) From Configuration File")
                    else:
                        config['host'] = HOST
                        log("CONFIG",
                            f"Given Host is Invalid, Set Host as ({HOST}) "
                            "From Auto-Configuration")
                else:
                    config['host'] = HOST
                    log("CONFIG",
                        f"Set Host as ({HOST}) From Auto-Configuration")
            except KeyError:
                config['host'] = HOST
                log("CONFIG",
                    f"Set Host as ({HOST}) From Auto-Configuration")

            try:
                if config['port']:
                    if config['port'] < 22 or config['port'] > 20000:
                        config['port'] = 9024
                        log("CONFIG",
                            "Given Port is Invalid, Port Set From Auto-Configuration")
                    else:
                        PORT = config['port']
                        log("CONFIG",
                            f"Set Port as ({PORT}) From Configuration File")
                else:
                    config['port'] = 9024
                    log("CONFIG",
                        f"Set Port as ({PORT}) From Auto-Configuration")
            except KeyError:
                config['port'] = 9024
                log("CONFIG",
                    f"Set Port as ({PORT}) From Auto-Configuration")

            try:
                if config['password']:
                    if config['password'].strip() == "":
                        config['password'] = ''
                    else:
                        if len(config['password']) > 20:
                            config['password'] = ''
                            log("CONFIG",
                                "Given Password is Too Long, No Password Set "
                                "From Auto-Configuration")
                        else:
                            PASSWORD = config['password']
                            log("CONFIG",
                                f"Set Server Password as ({PASSWORD}) "
                                "From Configuration File")
                else:
                    config['password'] = ''
                    log("CONFIG",
                        "No Password Set From Auto-Configuration")
            except KeyError:
                config['password'] = ''
                log("CONFIG",
                    "No Password Set From Auto-Configuration")

            open(filename, 'w').write(json.dumps(config, indent=2))

update_config()

ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind(ADDR)
except:
    logger.error("[ERROR] Couldn't Host it, Some error was thrown here or there")
    sys.exit()

users = set()
clients_lock = threading.Lock()


def send_to_all(obj: dict):
    """Forward a message object to all connected clients"""
    with clients_lock:
        if len(users) != 0:
            for a_user in users:
                a_user.connection.send(pickle.dumps(obj))


def handle_client(connection: socket.socket, address: tuple):
    """Main function which creates a new thread for each client to handle"""
    try:
        log("SERVER", "New connection coming!")

        if address[0] in get_config()['bans']:
            connection.send(pickle.dumps({'banned': True}))
            connection.close()

        if PASSWORD.strip() != "":
            connection.send(pickle.dumps({'password_required': True}))
        else:
            connection.send(pickle.dumps({'password_required': False}))

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

        if PASSWORD.strip() != "":
            if init_resp['password'] != PASSWORD:
                connection.send(pickle.dumps({'authorized': False}))
                connection.close()

        client_sessionid = uuid.uuid4().hex[:6]

        connection.send(pickle.dumps({'username': client_username,
                                        'sessionid': client_sessionid,
                                        'authorized': True}))

        with clients_lock:
            users.add(User(client_username, client_sessionid, connection))

        connected = True

        send_to_all(
            {
                'username': client_username,
                'sessionid': client_sessionid,
                'message': None,
                'disconnected': False,
                'new': True,
                'shutdown': False,
                'kicked': False
            }
        )

        log(f"{client_username}#{client_sessionid}",
            "JOINED")

        log("SERVER",
            f"Active Connections: {len(users)}")

        while connected:
            try:
                response = pickle.loads(connection.recv(HEADER))

                sessionid = response['sessionid']
                msg = response['message']

                username = "UNKNOWN"

                for user in users:
                    if user.sessionid == sessionid:
                        username = user.username

                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    for user in users:
                        if user.sessionid == sessionid:
                            users.remove(user)

                    send_to_all(
                        {
                            'username': username,
                            'sessionid': sessionid,
                            'message': None,
                            'disconnected': True,
                            'new': False,
                            'shutdown': False,
                            'kicked': False
                        }
                    )

                    log(f"{username}#{sessionid}",
                        "DISCONNECTED")

                    log("SERVER",
                        f"Active Connections: {len(users)}")
                else:
                    if msg.strip() != "":
                        try:
                            send_to_all(
                                {
                                    'username': username,
                                    'sessionid': sessionid,
                                    'message': msg,
                                    'disconnected': False,
                                    'new': False,
                                    'shutdown': False,
                                    'kicked': False
                                }
                            )
                        except:
                            connected = False

                        logger.info("[%s" % username +
                                    "#%s]" % sessionid +
                                    ": " + msg)
            except:
                connected = False
                for user in users:
                    if user.sessionid == client_sessionid:
                        users.remove(user)
                send_to_all(
                    {
                        'username': client_username,
                        'sessionid': client_sessionid,
                        'message': None,
                        'disconnected': True,
                        'new': False,
                        'shutdown': False,
                        'kicked': False
                    }
                )

                log(f"{client_username}#{client_sessionid}",
                    "DISCONNECTED")

                log("SERVER",
                    f"Active Connections: {len(users)}")

        connection.close()
    except:
        pass


def shutdown():
    """Shutdown the Echticka Server"""
    log("SHELL", 'Attempting shutdown...')
    send_to_all(
        {
            'username': None,
            'sessionid': None,
            'message': None,
            'disconnected': False,
            'new': False,
            'shutdown': True
        }
    )
    server.close()
    log("SERVER", 'Successfully stopped the Server')
    sys.exit()


def shell():
    """Interactive Shell function for controlling the server"""
    while True:
        try:
            command = input().strip().lower()
            if command in ("quit", "q", "exit", "shutdown"):
                shutdown()

            elif command == "updateconfig":
                update_config()

            elif command.startswith('ban '):
                address = command[4:]

                if ban(address):
                    print("[SHELL] " + f"Successfully banned IP Address: {address}")
                else:
                    print("[SHELL] " + f"Can't ban the IP Address: {address}")

            elif command.startswith('unban '):
                address = command[6:]

                if unban(address):
                    print("[SHELL] " + f"Successfully unbanned IP Address: {address}")
                else:
                    print("[SHELL] " + f"Can't unban the IP Address: {address}")

            elif command == 'unbanall':
                if unbanall():
                    print("[SHELL] " + "Successfully unbanned all IP Addresses")
                else:
                    print("[SHELL] " + "Can't unban all IP Addresses")

            elif command == "banlist":
                bans = get_config()['bans']

                print("[SHELL] " + "Banned IP Addresses:\n---")
                for address in bans:
                    print(address)
                if len(bans) == 0:
                    print("-No banned IP Addresses-")
                print("---")

            elif command == "activeconnections":
                print(f"[SHELL] Currently Active Connections ({len(users)}):\n---")
                for user in users:
                    print(f"{user.username}#{user.sessionid}")
                print("---")

            elif command.startswith("kick "):
                kicksessionid = command[5:]
                def kickem(kicksessionid):
                    try:
                        for a_user in users:
                            if a_user.sessionid == kicksessionid:
                                send_to_all(
                                    {
                                        'username': None,
                                        'sessionid': "Server",
                                        'message': f"{a_user.username} got kicked by Server Admin",
                                        'disconnected': True,
                                        'new': False,
                                        'shutdown': False,
                                        'kicked': False
                                    }
                                )

                                a_user.connection.send(pickle.dumps(
                                    {
                                        'username': None,
                                        'sessionid': "Server",
                                        'message': None,
                                        'disconnected': True,
                                        'new': False,
                                        'shutdown': False,
                                        'kicked': True
                                    }
                                ))

                                a_user.connection.close()

                                print(f"[SHELL] Successfully kicked \
{a_user.username}#{a_user.sessionid} out of the server")

                                users.remove(a_user)
                                break

                        print("[SHELL] Invalid Session ID")
                    except:
                        pass

                threading.Thread(target=kickem, args=(kicksessionid,)).start()

            elif command.startswith("send "):
                send_to_all(
                    {
                        'username': None,
                        'sessionid': "Server",
                        'message': command[5:],
                        'disconnected': True,
                        'new': False,
                        'shutdown': False,
                        'kicked': False
                    }
                )

                print(f"[SHELL] Sent message: {command[5:]}")

            elif command == "clear":
                if platform.system() == 'Windows':
                    os.system('cls')
                else:
                    os.system('clear')

            elif command in ("h", "help"):
                print('''[SHELL] Welcome to Echticka's Server Shell!
A Shell used inside the Server to control/manage it, nothing much

Commands:
    help - Show this help message
    ban <Address> - Ban an IP Address from joining the Server
    unban <Address> - Unban an IP Address from here
    kick <SessionID> - Kick a user using their Session ID
    send <message> - Send a message from the Server to all the connected users
    unbanall - Unbans all banned IP Addresses
    banlist - Show all banned IP Addresses
    updateconfig - Update Server Configuration based on the echticka.config File
    clear - Clear the console
    shutdown - Shutdown the Server''')

            else:
                pass
        except KeyboardInterrupt:
            shutdown()

        except EOFError:
            shutdown()

        except:
            shutdown()

log("SERVER", 'Echticka Server is starting...')
server.listen()
log("SERVER", f"Listening on {ADDR[0]}:{ADDR[1]}")
log("SERVER", "Use 'help' for more info")
threading.Thread(target=shell).start()
while True:
    try:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
    except:
        server.close()
        sys.exit()
