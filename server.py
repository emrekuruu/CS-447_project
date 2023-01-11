from socket import *
import threading
import rsa

host = "127.0.0.1"
port = 15000

public_key,private_key = rsa.newkeys(1024)


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((host, port))
serverSocket.listen(1)
print("Server is now ready to accept connections")

# Clients list
clients = []
client_dick = dict()

# Passwords List
passwords = dict()
passwords["admin"] = "admin123"

# Nickname list
nickNames = []
nickNames.append("admin")

# Banned accounts
banned = []

# Public keys of the clients
p_key = dict()


# for sending a message to each client
def broadcast(message):
    for client in clients:
        client.send(rsa.encrypt(message,p_key[client]))


# business logic for one client (later this method will run for all clients)
def handle(client):
    while True:
        try:
            message = rsa.decrypt(client.recv(1024),private_key)
            decodedMessage = message.decode()
            myList = decodedMessage.split(" ")
            print(myList)

            if (myList[0] == "/ban"):
                print("An account is Banned")
                nickNameToBeBanned = myList[1]
                print(nickNameToBeBanned)
                banned.append(nickNameToBeBanned)
                for client_ in client_dick.keys():
                    if client_dick[client_] == nickNameToBeBanned:
                        client_.send(rsa.encrypt("REFUSED".encode(),p_key[client_]))
                        client_.close()
                        clients.remove(client_)

                broadcast(f"{nickNameToBeBanned} is now banned".encode())

            elif (myList[0] == "EXIT"):
                imp = client_dick[client]
                clients.remove(client)
                client.close()
                temp = "LEFT "
                for g in nickNames:
                    if g != imp:
                        temp += f"{g} "
                broadcast(temp.encode())

                broadcast(f"{client_dick[client]} has left the chat".encode())

            # Were checking if this message is for the public or its a private message!
            elif (myList[1] == "PUBLIC"):
                myList.remove("PUBLIC")
                message = ""
                for i in myList:
                    message += f"{i} "

                print("There is a public message!")
                broadcast(message.encode())

            # If we can match the nickname with our cleints send the message to them
            else:
                for nickname in nickNames:
                    if (myList[1] == nickname):
                        myList.remove(nickname)
                        message = ""
                        for i in myList:
                            message += f"{i} "
                        print(f"There is a private message to {nickname}")
                        for WantedClient in client_dick.keys():
                            print(client_dick[WantedClient])
                            if client_dick[WantedClient] == nickname:
                                WantedClient.send(rsa.encrypt(message.encode(),p_key[WantedClient]))

        except:
            break


# basiclly the main function
def receive():
    while True:

        # once a client connects get its address and create a socket for them
        clientSocket, address = serverSocket.accept()
        print(f"Connected from {address}")

        clientSocket.send(public_key.save_pkcs1("PEM"))
        p_key[clientSocket] = rsa.PublicKey.load_pkcs1(clientSocket.recv(1024))

        # Sign in or Log in?
        clientSocket.send(rsa.encrypt("SIGN".encode(),p_key[clientSocket]))
        first_time = rsa.decrypt(clientSocket.recv(1024),private_key).decode()

        if (first_time == "CREATE ACCOUNT"):
            # ask them for a username than add them to our lists
            clientSocket.send(rsa.encrypt("NICK".encode(),p_key[clientSocket]))
            nickname = rsa.decrypt(clientSocket.recv(1024),private_key).decode()
            # Used nickname
            nickname_alredy_used = True
            if (nickNames.__contains__(nickname)):
                clientSocket.send(rsa.encrypt("REFUSED".encode(),p_key[clientSocket]))
                continue

            else:
                nickname_alredy_used = False
            nickNames.append(nickname)
            clients.append(clientSocket)
            client_dick[clientSocket] = nickname

            # ask them to pick a password
            clientSocket.send(rsa.encrypt("PASSWORD".encode(),p_key[clientSocket]))
            password = rsa.decrypt(clientSocket.recv(1024),private_key).decode()
            passwords[nickname] = password

        else:
            # ask them their nickname to verify
            clientSocket.send(rsa.encrypt("NICK".encode(),p_key[clientSocket]))
            nickname = rsa.decrypt(clientSocket.recv(1024),private_key).decode()
            if ((nickNames.__contains__(nickname)) and nickname not in banned):
                # Get password to verify nickname
                clientSocket.send(rsa.encrypt("PASSWORD".encode(),p_key[clientSocket]))
                password = rsa.decrypt(clientSocket.recv(1024),private_key).decode()
                if (passwords[nickname] != password):
                    clientSocket.send(rsa.encrypt("REFUSED".encode(),p_key[clientSocket]))
                    clientSocket.close()
                    continue
                else:
                    clients.append(clientSocket)
            else:
                clientSocket.send(rsa.encrypt("REFUSED".encode(),p_key[clientSocket]))
                clientSocket.close()
                continue

        print(f"Nickname of the client is {nickname}")
        broadcast("NEW".encode())
        temp = ""
        for g in nickNames:
            temp += f"{g} "
        broadcast(temp.encode())

        # We will have a new thread for each client we want to handle each connection separately !!!
        thread = threading.Thread(target=handle, args=(clientSocket,))
        thread.start()


receive()
serverSocket.close()


