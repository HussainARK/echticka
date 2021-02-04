import pickle
import socket
from threading import Thread
from colorama import init, Fore
import time

init()
print(f'{Fore.LIGHTWHITE_EX}Enter your Username: {Fore.RESET}', end='')
username = input()

print(f"{Fore.LIGHTWHITE_EX}Server Host: {Fore.RESET}", end='')
tcp_hostname = input()

print(f"{Fore.LIGHTWHITE_EX}Server Port (Default: 9024): {Fore.RESET}", end='')
tcp_port = input()

if not tcp_port:
    tcp_port = 9024
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
    print(f"{Fore.LIGHTRED_EX}Couldn't connect to The Server!{Fore.RESET}")
    quit()

print(f"{Fore.CYAN}Registering the Client...{Fore.RESET}")

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
    print(f"{Fore.LIGHTWHITE_EX}Disconnected from the Server: {Fore.MAGENTA}{SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
          f"{Fore.RESET}")
    client.close()
    quit()

sessionid = init_resp['sessionid']

if not init_resp['username']:
    print(f"{Fore.LIGHTRED_EX}Invalid Username{Fore.RESET}")
    client.close()
    exit()
else:
    username = init_resp['username']

print(f"{Fore.CYAN}Connected to the Server: {Fore.MAGENTA}{SERVER_ADDR[0]}:{SERVER_ADDR[1]}{Fore.RESET}")


def get_messages(sure):
    if sure:
        try:
            while True:
                response = pickle.loads(client.recv(HEADER))
                if not response['sessionid'] == "69420NICE":
                    if not response['sessionid'] == sessionid:
                        if response['message'] is None:
                            if response['new']:
                                print(f"{Fore.GREEN}{response['username']} JOINED THE CHAT{Fore.RESET}")
                            elif response['disconnected']:
                                print(f"{Fore.LIGHTRED_EX}{response['username']} LEFT THE CHAT{Fore.RESET}")
                        else:
                            print(f"{Fore.YELLOW}{response['username']}: {Fore.LIGHTWHITE_EX}{response['message']}"
                                  f"{Fore.RESET}")
                else:
                    print(f"{Fore.LIGHTRED_EX}THE SERVER ATTEMPTS TO SHUTDOWN{Fore.RESET}")
                    send(DISCONNECT_MESSAGE)
                    print(
                        f"{Fore.LIGHTWHITE_EX}Disconnected from the Server: {Fore.MAGENTA}{SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
                        f"{Fore.RESET}")
                    client.close()
                    quit()
        except:
            time.sleep(0.1)
            print(f"{Fore.LIGHTRED_EX}Disconnected!?{Fore.RESET}")
            quit()
    else:
        pass


print(f'{Fore.LIGHTWHITE_EX}{Fore.CYAN}To Disconnect, send: {Fore.RED}{DISCONNECT_MESSAGE}{Fore.RESET}')

print(f'{Fore.CYAN}You joined as {Fore.RESET}{Fore.YELLOW}{username}{Fore.RESET} '
      f'{Fore.CYAN}with Session ID {Fore.RESET}{Fore.LIGHTRED_EX}{sessionid}{Fore.RESET}{Fore.CYAN}, '
      f'{Fore.RESET}{Fore.GREEN}Enjoy!{Fore.RESET}\n')

thread = Thread(target=get_messages, args=(True,))
thread.start()

try:
    while True:
        if client:
            message = input()
            if message == DISCONNECT_MESSAGE:
                send(message)
                print(
                    f"{Fore.LIGHTWHITE_EX}Disconnected from the Server: {Fore.MAGENTA}{SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
                    f"{Fore.RESET}")
                client.close()
                quit()
            else:
                send(message)
        else:
            break

except KeyboardInterrupt:
    send(DISCONNECT_MESSAGE)
    print(f"{Fore.LIGHTWHITE_EX}Disconnected from the Server: {Fore.MAGENTA}{SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
          f"{Fore.RESET}")
    client.close()
    quit()

except EOFError:
    send(DISCONNECT_MESSAGE)
    print(f"{Fore.LIGHTWHITE_EX}Disconnected from the Server: {Fore.MAGENTA}{SERVER_ADDR[0]}:{SERVER_ADDR[1]}"
          f"{Fore.RESET}")
    client.close()
    quit()
