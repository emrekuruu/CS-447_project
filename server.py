from socket import *
import threading
import tkinter
from tkinter import simpledialog
import tkinter.scrolledtext
import rsa


serverName = "127.0.0.1"
port = 22064
public_key,private_key = rsa.newkeys(1024)

class Client:
    def __init__(self, host, port):
        # Connection syntax
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((host, port))
        self.message = ""
        self.server_key = rsa.PublicKey.load_pkcs1(self.clientSocket.recv(1024))
        self.clientSocket.send(public_key.save_pkcs1("PEM"))


        msg = tkinter.Tk()

        msg.withdraw()

        self.gui_done = False

        self.SignIn = simpledialog.askstring(("User Name"), "CREATE ACCOUNT OR LOG IN", parent=msg)
        self.nickName = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        # Will they sign in log in
        self.password = simpledialog.askstring(("password"), "Password", parent=msg)

        self.running = True
        self.g_thread = threading.Thread(target=self.guiloop)
        self.r_thread = threading.Thread(target=self.receive)
        self.g_thread.start()
        self.r_thread.start()

    def stop(self):
        self.win.destroy()
        self.running = False
        self.clientSocket.close()

    def guiloop(self):
        # Window itself
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        # a small label
        self.chat_label = tkinter.Label(self.win, text="Chat: ", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        # The area where the messages are displayed
        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="normal")
        self.text_area.insert("end","Welcome to our online Chat Room")
        self.text_area.yview("end")
        self.text_area.insert("end","\n")
        self.text_area.yview("end")
        self.text_area.config(state="disabled")


        self.online_label = tkinter.Label(self.win, text="Currently Online: ", bg="lightgray")
        self.online_label.config(font=("Arial", 12))
        self.online_label.pack(padx=20, pady=5)

        self.online_area = tkinter.scrolledtext.ScrolledText(self.win,height=3)
        self.online_area.pack(padx=20,pady=5)
        self.online_area.config(state="disabled")

                # Another label
        self.msg_label = tkinter.Label(self.win, text="Message: ", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)


        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.public_button = tkinter.Button(self.win, text="PUBLIC",command=self.forPublic)
        self.public_button.config(font=("Arial",12))
        self.public_button.pack(padx=20,pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    # This is to see what everyone else wrote on the chat
    def receive(self):
        while self.running:
            try:
                message = rsa.decrypt(self.clientSocket.recv(1024),private_key).decode()
                print(message)
                print(self.gui_done)

                # This is the sign in message
                if message == "SIGN":
                    self.clientSocket.send(rsa.encrypt(self.SignIn.encode(),self.server_key))

                if message == "NEW":
                    online = rsa.decrypt(self.clientSocket.recv(1024),private_key).decode()
                    self.online_area.config(state="normal")
                    self.online_area.insert("end","\n")
                    self.online_area.yview("end")
                    self.online_area.insert("end","")
                    self.online_area.yview("end")
                    self.online_area.insert("end", online)
                    self.online_area.yview("end")
                    self.online_area.config(state="disabled")

                # if the message is NICK this means server wants us to send it our nickname( this is the initial connection )
                elif message == "NICK":
                    self.clientSocket.send(rsa.encrypt(self.nickName.encode(),self.server_key))

                elif message == "PASSWORD":
                    self.clientSocket.send(rsa.encrypt(self.password.encode(),self.server_key))

                elif message == "REFUSED":
                    print(
                        "Server refused the connection\nEither you entered a wrong password\nPicked a username that was already used\nOr Your account is banned"
                        "Try Again")
                    self.stop()

                elif self.gui_done:
                    self.text_area.config(state="normal")
                    self.text_area.insert("end","\n")
                    self.text_area.yview("end")
                    self.text_area.insert("end","")
                    self.text_area.yview("end")
                    self.text_area.insert("end", message)
                    self.text_area.yview("end")
                    self.text_area.config(state="disabled")

            except:
                print("Connection Failed")
                self.stop()

    # This is for writing in the chat
    def write(self):
        self.message += self.input_area.get("1.0", "end")
        self.input_area.delete("1.0", "end")
        self.message = self.nickName + ": " + self.message

            #This is for banning clients
        if self.message[len(self.nickName)+2:].startswith("/"):
            if self.nickName == "admin":
                self.clientSocket.send(rsa.encrypt(self.message[len(self.nickName)+2:].encode(),self.server_key))
            else:
                print("Only Admins can execute commands")

        self.clientSocket.send(rsa.encrypt(self.message.encode(),self.server_key))

        if( self.message[len(self.nickName)+2:] == "EXIT"):
            self.stop()
        self.message = ""

    def forPublic(self):
        self.message += "PUBLIC "


client = Client(serverName, port)
