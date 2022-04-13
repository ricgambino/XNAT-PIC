import os
import getpass
import tkinter as tk
from tkinter import ttk
from accessory_functions import disable_buttons


class CredentialManager():

    def __init__(self):

        popup = tk.Tk()
        popup.title("XNAT-PIC ~ Credentials")
        popup.geometry("%dx%d+%d+%d" % (600, 300, 500, 250))

        popup.tk_label = tk.Label(popup, text="XNAT-PIC Configuration", font=("Calibri", 20, "bold"))
        popup.tk_label.grid(row=0, column=1, padx=10, pady=10)

        # XNAT-PIC secretUser
        popup.label_secretUser = tk.Label(popup, text="User", font=("Calibri", 10))
        popup.label_secretUser.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        popup.entry_secretUser = ttk.Entry(popup, show="", width=50, state='disabled')
        popup.entry_secretUser.var = tk.StringVar()
        popup.entry_secretUser["textvariable"] = popup.entry_secretUser.var
        popup.entry_secretUser.grid(row=1, column=1, padx=5, pady=5)
        popup.entry_secretUser.var.set(getpass.getuser())

        # User CheckButton
        def enable_user_entry(*args):
            popup.entry_secretUser.configure(state='normal')
        popup.change_user_btn_var = tk.IntVar()
        popup.change_user_btn= tk.Checkbutton(popup, variable=popup.change_user_btn_var, onvalue=1, offvalue=0, text="Change User")
        popup.change_user_btn.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        popup.change_user_btn_var.trace('w', enable_user_entry)
        
        # XNAT-PIC secretKey
        def enable_secretPIN(*args):
            if popup.entry_secretKey_2.var.get() != '':
                popup.entry_secretPIN.configure(state='normal')
                popup.entry_secretPIN_2.configure(state='normal')
            else:
                popup.entry_secretPIN.configure(state='disabled')
                popup.entry_secretPIN_2.configure(state='disabled')
        popup.label_secretKey = tk.Label(popup, text="Insert Key", font=("Calibri", 10))
        popup.label_secretKey.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        popup.entry_secretKey = ttk.Entry(popup, show="*", width=50)
        popup.entry_secretKey.var = tk.StringVar()
        popup.entry_secretKey["textvariable"] = popup.entry_secretKey.var
        popup.entry_secretKey.grid(row=2, column=1, padx=5, pady=5)
        
        # Re-insert secretKey
        def check_Key(*args):
            try:
                popup.checked_key.destroy()
            except:
                pass
            if popup.entry_secretKey_2.var.get() != '':
                if popup.entry_secretKey.var.get() != popup.entry_secretKey_2.var.get():
                    popup.checked_key = tk.Label(popup, font=("Calibri", 8, "underline"), text="Password does not correspond!", fg='red')
                    popup.checked_key.grid(row=3, column=2, padx=5, sticky=tk.W)
                else:
                    popup.checked_key = tk.Label(popup, font=("Calibri", 8, "underline"), text="OK!", fg='green')
                    popup.checked_key.grid(row=3, column=2, padx=5, sticky=tk.W)

        popup.label_secretKey_2 = tk.Label(popup, text="Insert Key again", font=("Calibri", 10))
        popup.label_secretKey_2.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        popup.entry_secretKey_2 = ttk.Entry(popup, show="*", width=50)
        popup.entry_secretKey_2.var = tk.StringVar()
        popup.entry_secretKey_2["textvariable"] = popup.entry_secretKey_2.var
        popup.entry_secretKey_2.grid(row=3, column=1, padx=5, pady=5)
        popup.entry_secretKey_2.var.trace('w', check_Key)
        popup.entry_secretKey_2.var.trace('w', enable_secretPIN)

        # XNAT-PIC secretPIN
        def enable_next_btn(*args):
            if popup.entry_secretPIN_2.var.get() != '':
                popup.next_btn.configure(state='normal')
            else:
                popup.next_btn.configure(state='disabled')
        popup.label_secretPIN = tk.Label(popup, text="Insert PIN", font=("Calibri", 10))
        popup.label_secretPIN.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        popup.entry_secretPIN = ttk.Entry(popup, show="*", width=50, state='disabled')
        popup.entry_secretPIN.var = tk.StringVar()
        popup.entry_secretPIN["textvariable"] = popup.entry_secretPIN.var
        popup.entry_secretPIN.grid(row=4, column=1, padx=5)

        # Re-insert secretPIN
        def check_PIN(*args):
            try:
                popup.checked_PIN.destroy()
            except:
                pass
            if popup.entry_secretPIN_2.var.get() != '':
                if popup.entry_secretPIN.var.get() != popup.entry_secretPIN_2.var.get():
                    popup.checked_PIN = tk.Label(popup, font=("Calibri", 8, "underline"), text="Password does not correspond!", fg='red')
                    popup.checked_PIN.grid(row=5, column=2, padx=5, sticky=tk.W)
                else:
                    popup.checked_PIN = tk.Label(popup, font=("Calibri", 8, "underline"), text="OK!", fg='green')
                    popup.checked_PIN.grid(row=5, column=2, padx=5, sticky=tk.W)

        popup.label_secretPIN_2 = tk.Label(popup, text="Insert PIN again", font=("Calibri", 10))
        popup.label_secretPIN_2.grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        popup.entry_secretPIN_2 = ttk.Entry(popup, show="*", width=50, state='disabled')
        popup.entry_secretPIN_2.var = tk.StringVar()
        popup.entry_secretPIN_2["textvariable"] = popup.entry_secretPIN_2.var
        popup.entry_secretPIN_2.grid(row=5, column=1, padx=5)
        popup.entry_secretPIN_2.var.trace('w', check_PIN)
        popup.entry_secretPIN_2.var.trace('w', enable_next_btn)

        # NEXT Button
        def next():
            popup.destroy()
            self.write_credentials(popup.entry_secretUser.var, popup.entry_secretKey.var, popup.entry_secretPIN.var)
        popup.next_text = tk.StringVar() 
        popup.next_btn = tk.Button(popup, textvariable=popup.next_text, font=("Calibri", 16), bg="#80FFE6", fg="black", 
                                    borderwidth=3, command=next, cursor="hand2", takefocus=0, state='disabled')
        popup.next_text.set("Next")
        popup.next_btn.grid(row=6, column=1, padx=10, pady=10)

        popup.mainloop()
    
    def write_credentials(self, user, psw, pin):

        dir = os.getcwd().replace('\\', '/')
        head, tail = os.path.split(dir)
        head, tail = os.path.split(head)

        with open(head + '/.env', 'w+') as credential_file:
            credential_file.write('secretUser=' + '"' + str(user.get()) + '"' + '\n')
            credential_file.write('secretKey=' + '"' + str(psw.get()) + '"' + '\n')
            credential_file.write('secretPIN=' + '"' + str(pin.get()) + '"' + '\n')
            credential_file.write('bufferSize1=64\n')
            credential_file.write('bufferSize2=1024')

    def change_credentials(self, user, psw, pin):

        dir = os.getcwd().replace('\\', '/')
        head, tail = os.path.split(dir)
        head, tail = os.path.split(head)
        with open(head + '/.env', 'r') as credential_file:
            data = credential_file.read().split('\n')
            for i, d in enumerate(data):
                if 'secretUser' in d:
                    data.remove(d)
                    data.insert(i, 'secretUser=' + '"' + str(user) + '"')
                if 'secretKey' in d:
                    data.remove(d)
                    data.insert(i, 'secretKey=' + '"' + str(psw) + '"')
                elif 'secretPIN' in d:
                    data.remove(d)
                    data.insert(i, 'secretPIN=' + '"' + str(pin) + '"')

        with open(head + '/.env', 'w+') as credential_file:
            for d in data:
                credential_file.write(d + '\n')
