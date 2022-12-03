from socket import *
import threading

serverName = "127.0.0.1"
port = 22011

#Get a Nick name from the client
print("INFO PLEASE READ BEFORE CHATTING")
print("For public messages start your messages with the keyword PUBLIC")
print("Example: PUBLIC Hello World")
print("\nFor private messages please write the nickname of the person you want to message at the start of your message")
print(("Example: Emre Hello World"))
print("\nIf you wish to leave the chat please enter EXIT")


nickName = input("\nWhat would you like to be called: ")

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
        inp = input("")
        messageToBeSent = f'{nickName}: {inp}'
        clientSocket.send(messageToBeSent.encode())
        if(inp == "EXIT"):
            clientSocket.close()
            break


#This is the tricky part !!!
# We will have 2 threads one for receiving messages and another for writing them!!!
receiveThread = threading.Thread(target=receive)
receiveThread.start()

writeThread = threading.Thread(target=write)
writeThread.start()



