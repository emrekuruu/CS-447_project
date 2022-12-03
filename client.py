from socket import *
import threading

serverName = "127.0.0.1"
port = 60001

#Get a Nick name from the client
nickName = input("What would you like to be called: ")

#Connection syntax
clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect((serverName,port))

#This is to see what everyone else wrote on the chat
def receive():
    while True:
        try:
            message = clientSocket.recv(1024).decode()
            #if the message is NICK this means server wants us to send it our nickname( this is the initial connection )
            if message == "NICK":
                clientSocket.send(nickName.encode())
            else:
               print(message)
        except:
            print("Connection was not successful")
            clientSocket.close()
            break

#This is for writing in the chat
def write():
    while True:
        messageToBeSent = f'{nickName}: {input("")}'
        clientSocket.send(messageToBeSent.encode())


#This is the tricky part !!!
# We will have 2 threads one for receiving messages and another for writing them!!!
receiveThread = threading.Thread(target=receive)
receiveThread.start()

writeThread = threading.Thread(target=write)
writeThread.start()

