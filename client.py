import socket
import threading
import getpass

nickname = input("Choose a nickname: ")
if nickname =='admin':
   password = getpass.getpass(prompt="Enter password for admin: ")
    # without masking password = input("Enter password for admin: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

stop_thread = False

def recieve():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASS':
                   client.send(password.encode('ascii'))
                   if client.recv(1024).decode('ascii') == 'REFUSE':
                       print('Connection was refused!  wrong password!')
                       stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused because of ban!')
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            print("An error occurred")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        message = f'{nickname}: {input("")}'
        if message[len(nickname)+2:].startswith('/'):
           if nickname == 'admin':
              if message[len(nickname)+2:].startswith('/kick'):
                  client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('ascii'))
              elif message[len(nickname)+2:].startswith('/ban'):
                  client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('ascii'))
              elif message[len(nickname)+2:].startswith('/unban'):
                  client.send(f'UNBAN {message[len(nickname)+2+7:]}'.encode('ascii'))
           else:
               print('Commands can only be executed by the admin!')
        else:
           client.send(message.encode('ascii'))
    
recieve_thread = threading.Thread(target=recieve)
recieve_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
