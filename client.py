from socket import *
import threading
import tkinter
from tkinter import simpledialog
import tkinter.scrolledtext

serverName = "127.0.0.1"
port = 22047


class Client:

    def __init__(self, host, port):
        # Connection syntax
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((host, port))
        self.message = ""

        msg = tkinter.Tk()
        msg.withdraw()

        self.gui_done = False

        self.SignIn = simpledialog.askstring(("User Name"), "SIGN IN", parent=msg)
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
        self.text_area.config(state="disabled")

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

        self.get_nicknames = tkinter.Button(self.win,text="See Who is Online",command=self.online)
        self.get_nicknames.config(font=("Ariel",12))
        self.get_nicknames.pack(padx=25,pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    # This is to see what everyone else wrote on the chat
    def receive(self):
        while self.running:
            try:
                message = self.clientSocket.recv(1024).decode()
                print(message)
                print(self.gui_done)

                # This is the sign in message
                if message == "SIGN":
                    self.clientSocket.send(self.SignIn.encode())

                # if the message is NICK this means server wants us to send it our nickname( this is the initial connection )
                elif message == "NICK":
                    self.clientSocket.send(self.nickName.encode())

                elif message == "PASSWORD":
                    self.clientSocket.send(self.password.encode())

                elif message == "REFUSED":
                    print(
                        "Server refused the connection\nEither you entered a wrong password\nPicked a username that was already used\nOr Your account is banned"
                        "Try Again")
                    self.stop()

                if self.gui_done:
                    self.text_area.config(state="normal")
                    self.text_area.insert("end"," ")
                    self.text_area.yview("end+2l")
                    self.text_area.insert("end-1c", message)
                    self.text_area.yview("end+2l")
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
                self.clientSocket.send(self.message[len(self.nickName)+2:].encode())
            else:
                print("Only Admins can execute commands")

        self.clientSocket.send(self.message.encode())

        if( self.message[len(self.nickName)+2:] == "EXIT"):
            self.stop()
        self.message = ""

    def forPublic(self):
        self.message += "PUBLIC "

    def online(self):
        self.clientSocket.send(f"ONLINE {self.nickName}".encode())


client = Client(serverName, port)



