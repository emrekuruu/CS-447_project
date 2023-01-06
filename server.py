from socket import *
import threading

host = "127.0.0.1"
port = 22047

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


# for sending a message to each client
def broadcast(message):
    for client in clients:
        client.send(message)


# business logic for one client (later this method will run for all clients)
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            decodedMessage = message.decode()
            myList = decodedMessage.split(" ")
            print(myList)

            if (myList[0] == "/ban"):
                print("An account is Banned")
                nickNameToBeBanned = myList[1]
                banned.append(nickNameToBeBanned)
                for client_ in client_dick.keys():
                    if client_dick[client_] == nickNameToBeBanned:
                        client_.send("REFUSED".encode())
                        client_.close()
                        clients.remove(client_)

                broadcast(f"{nickNameToBeBanned} is now banned".encode())

            elif(myList[0] == "ONLINE"):
                print("Someone asked for user list")
                to = myList[1]
                for WantedClient in client_dick.keys():
                            if client_dick[WantedClient] == to:
                                result = ""
                                for x in nickNames:
                                    if(x != "admin"):
                                            result += f"{x} "
                                    WantedClient.send(result.encode())
                                    result = ""




            elif (myList[1] == "EXIT"):
                clients.remove(client)
                client.close()
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
                            if client_dick[WantedClient] == nickname:
                                WantedClient.send(message.encode())

        except:
            clients.remove(client)
            client.close()
            broadcast(f"{client_dick[client]} has left the chat".encode())
            break


# basiclly the main function
def receive():
    while True:

        # once a client connects get its address and create a socket for them
        clientSocket, address = serverSocket.accept()
        print(f"Connected from {address}")

        # Sign in or Log in?
        clientSocket.send("SIGN".encode())
        first_time = clientSocket.recv(1024).decode()

        if (first_time == "SIGN IN"):
            # ask them for a username than add them to our lists
            clientSocket.send("NICK".encode())
            nickname = clientSocket.recv(1024).decode()
            # Used nickname
            nickname_alredy_used = True
            if (nickNames.__contains__(nickname)):
                clientSocket.send("REFUSED".encode())
                continue
            else:
                nickname_alredy_used = False
            nickNames.append(nickname)
            clients.append(clientSocket)
            client_dick[clientSocket] = nickname

            # ask them to pick a password
            clientSocket.send("PASSWORD".encode())
            password = clientSocket.recv(1024).decode()
            passwords[nickname] = password

        else:
            # ask them their nickname to verify
            clientSocket.send("NICK".encode())
            nickname = clientSocket.recv(1024).decode()
            if ((nickNames.__contains__(nickname)) and nickname not in banned):
                # Get password to verify nickname
                clientSocket.send("PASSWORD".encode())
                password = clientSocket.recv(1024).decode()
                if (passwords[nickname] != password):
                    clientSocket.send("REFUSED".encode())
                    clientSocket.close()
                    continue
                else:
                    clients.append(clientSocket)
            else:
                clientSocket.send("REFUSED".encode())
                clientSocket.close()
                continue

        print(f"Nickname of the client is {nickname}")

        # We will have a new thread for each client we want to handle each connection separately !!!
        thread = threading.Thread(target=handle, args=(clientSocket,))
        thread.start()


receive()
serverSocket.close()

