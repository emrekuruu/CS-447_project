import tkinter as tk
from tkinter import *


def gonder(event=None):
    msg = e1.get()
    e1.insert(0,"")
    client_socket.send(bytes(msg,"utf8"))
    if msg == "{cikis}":
        client_socket.close()
        app.quit()

def cikis_durumu(event=None):
    e1.insert(0,"{cikis}")
    gonder()
        
app = tk.Tk()
app.title("Chat")

mesaj_alani = tk.Frame(app)

e1 = Entry(app)
e1.insert(0, 'Message')
e1.bind("<FocusIn>", lambda args: e1.delete('0', 'end'))



scrollbar = tk.Scrollbar(mesaj_alani)
mesaj_listesi = tk.Listbox(mesaj_alani, height=20, width=70, yscrollcommand=scrollbar.set)
mesaj_listesi.see("end")

scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
mesaj_listesi.pack(side=tk.LEFT, fill=tk.BOTH)
mesaj_alani.pack()
e1.pack()

giris_alani = tk.Entry(app, textvariable=e1)
giris_alani.bind("<Return>", gonder)


gonder_buton = tk.Button(app, text="Gonder", command=gonder)
gonder_buton.pack()
app.protocol("WM_DELETE_WİNDOW", cikis_durumu)
