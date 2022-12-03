from socket import *
import threading

host = "127.0.0.1"
port = 22001

serverSocket = socket(AF_INET,SOCK_STREAM )
serverSocket.bind((host,port))
serverSocket.listen(1)
print("Server is now ready to accept connections")

#Clients list
clients = []

#Nickname list
nickNames = []

#for sending a message to each client
def broadcast(message):
    for client in clients:
        client.send(message)


#business logic for one client (later this method will run for all clients)
def handle(client):
    while True:
        try:
          message = client.recv(1024)
          decodedMessage = message.decode()
          myList = decodedMessage.split(" ")
          print(myList[1])

          #Were checking if this message is for the public or its a private message!
          if(myList[1] == "PUBLIC"):
              print("There is a public message!")
              broadcast(message)

          #If we can match the nickname with our cleints send the message to them
          else:
              for nickname in nickNames:
                  if(myList[1] == nickname):
                         print(f"There is a private message to {nickname}")
                         index = nickNames.index(nickname)
                         wantedClient = clients[index]
                         wantedClient.send(message)

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            broadcast(f"{nickNames[index]} has left the chat".encode())
            nickNames.remove(nickNames[index])
            break


#basiclly the main function
def receive():
    while True:
        #once a client connects get its address and create a socket for them
        clientSocket,address = serverSocket.accept()
        print(f"Connected from {address}")

        #ask them for a username than add them to our lists
        clientSocket.send("NICK".encode())
        nickname = clientSocket.recv(1024).decode()
        nickNames.append(nickname)
        clients.append(clientSocket)
        print(f"Nickname of the client is {nickname}")

        #tell everyone in the chat someone has connected
        broadcast(f"{nickname} has entered the chat".encode())

        #Tell the client connection is successful
        clientSocket.send("Connection successful Welcome".encode())

        #We will have a new thread for each client we want to handle each connection separately !!!
        thread = threading.Thread(target=handle,args=(clientSocket,))
        thread.start()

receive()
serverSocket.close()
