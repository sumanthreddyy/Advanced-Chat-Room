import socket
import threading

# Set the host IP and port number
host = '127.0.0.1'
port = 55555

# Create a server socket object using AF_INET (IPv4) and SOCK_STREAM (TCP) protocol
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the host and port
server.bind((host, port))

# Listen for incoming connections
server.listen()

# Initialize empty lists for storing clients and their nicknames
clients = []
nicknames = []

# Function to broadcast messages to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Function to handle messages from a client
def handle(client):
    while True:
        try:
            # Receive a message from the client
            msg = message = client.recv(1024)
            # Check if the message starts with "KICK"
            if msg.decode('ascii').startswith('KICK '):
                # If the nickname of the client is "admin"
                if nicknames[clients.index(client)] == 'admin':
                   # Get the name of the client to be kicked
                   name_to_kick = msg.decode('ascii')[5:]
                   # Call the kick_user() function to kick the client
                   kick_user(name_to_kick)
                else:
                    client.send('Command was refused!'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                   name_to_ban = msg.decode('ascii')[4:]
                   kick_user(name_to_ban)
                   with open('bans.txt', 'a') as f:
                       f.write(f'{name_to_ban}\n')
                   print(f'{name_to_ban}was banned!')
                else:
                   client.send('Command was refused!'.encode('ascii'))
            elif msg.decode('ascii').startswith('UNBAN '):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_unban = msg.decode('ascii')[6:]
                    unban_user(name_to_unban)
                    client.send(f'{name_to_unban} was unbanned!'.encode('ascii'))
                else:
                    client.send('Command was refused!'.encode('ascii'))
            else:
                broadcast(message)
        except:
             # If an error occurs while receiving the message
            if client in clients:
                # Get the index of the client in the "clients" list
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nickname[index]
                broadcast(f'{nickname}left the chat'.encode('ascii'))
                nicknames.remove(nickname)
                break

def recieve():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('NICK'.encode('ascii'))
                                  
        nickname = client.recv(1024).decode('ascii')

        with open('bans.txt','r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname == 'admin':
           client.send('PASS'.encode('ascii'))
           password = client.recv(1024).decode('ascii')

           if password !='adminpass':
              client.send('REFUSE'.encode('ascii'))
              client.close()
              continue              
              
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode('ascii'))
        client.send('Connected to the server'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by the admin'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin!'.encode('ascii'))  

def unban_user(name):
    with open('bans.txt', 'r') as f:
        lines = f.readlines()
    with open('bans.txt', 'w') as f:
        for line in lines:
            if line.strip() != name:
                f.write(line)
    print(f'{name} was unbanned!')

print("Server is listening...")
recieve()