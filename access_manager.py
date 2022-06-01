# -*- coding: utf-8 -*-
"""
Created on May 30, 2022

@author: Riccardo Gambino

"""
import tkinter as tk
import tkinter.simpledialog
from tkinter import messagebox
import ttkbootstrap as ttk
import json, os, xnat
import pyAesCrypt, webbrowser
from accessory_functions import *

PATH_IMAGE = "images\\"
CURSOR_HAND = "hand2"
SMALL_FONT_2 = ("Calibri", 10)

with open("layout_colors.json", "r") as theme_file:
    theme_colors = json.load(theme_file)

class AccessManager():

    def __init__(self, root):

        # Load icons
        self.open_eye = open_image(PATH_IMAGE + "open_eye.png", 15, 15)
        self.closed_eye = open_image(PATH_IMAGE + "closed_eye.png", 15, 15)

        self.connected = None

        # Start with a popup to get credentials
        self.popup = tk.Toplevel(root)
        self.popup.title("XNAT-PIC ~ Login")
        self.popup.geometry("%dx%d+%d+%d" % (410, 240, 600, 400))
        self.popup.resizable(False, False)

        # Closing window event: if it occurs, the popup must be destroyed and the main frame buttons must be enabled
        def closed_window():
            self.connected = False
            self.popup.destroy()
        self.popup.protocol("WM_DELETE_WINDOW", closed_window)

        # Credentials Label Frame
        self.popup.cred_frame = ttk.LabelFrame(self.popup, text="Credentials", style="Popup.TLabelframe")
        self.popup.cred_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

        # XNAT ADDRESS      
        self.popup.label_address = ttk.Label(self.popup.cred_frame, text="XNAT web address")   
        self.popup.label_address.grid(row=1, column=0, padx=2, pady=2, sticky=tk.E)
        self.popup.entry_address = ttk.Entry(self.popup.cred_frame, width=25)
        self.popup.entry_address.var = tk.StringVar()
        self.popup.entry_address["textvariable"] = self.popup.entry_address.var
        self.popup.entry_address.grid(row=1, column=1, padx=2, pady=2)

        def enable_address_modification(*args):
            if self.popup.modify_address_flag.get() == 1:
                self.popup.entry_address.configure(state='normal')
            else:
                self.popup.entry_address.configure(state='disabled')
        self.popup.modify_address_flag = tk.IntVar()
        self.popup.modify_address_btn = ttk.Checkbutton(self.popup.cred_frame, text="Change address", state='disabled', 
                                                        style="Popup.TCheckbutton",
                                                        onvalue=1, offvalue=0, variable=self.popup.modify_address_flag)
        self.popup.modify_address_btn.grid(row=1, column=2, padx=2, pady=2, sticky=tk.W)
        self.popup.modify_address_flag.trace('w', enable_address_modification)
        
        # XNAT USER 
        self.popup.label_user = ttk.Label(self.popup.cred_frame, text="Username")
        self.popup.label_user.grid(row=2, column=0, padx=1, ipadx=1, sticky=tk.E)

        self.popup.entry_user = tk.StringVar()
        self.popup.combo_user = ttk.Combobox(self.popup.cred_frame, font=SMALL_FONT_2, takefocus=0, textvariable=self.popup.entry_user, 
                                                state='normal', width=19, style="Popup.TCombobox")
        self.popup.combo_user['values'] = self.get_list_of_users()
        self.popup.entry_user.trace('w', self.get_credentials)
        self.popup.combo_user.grid(row=2, column=1, padx=2, pady=2)

        # XNAT PASSWORD 
        self.popup.label_psw = ttk.Label(self.popup.cred_frame, text="Password")
        self.popup.label_psw.grid(row=3, column=0, padx=1, ipadx=1, sticky=tk.E)

        # Show/Hide the password
        def toggle_password(*args):
            if self.popup.entry_psw.cget('show') == '':
                self.popup.entry_psw.config(show='*')
                self.popup.toggle_btn.config(image=self.open_eye)
            else:
                ans = tkinter.simpledialog.askstring("PIN", "Enter PIN: ", show='*', parent=self.popup.cred_frame)
                if ans:
                    if ans == os.environ.get('secretPIN'):
                        self.popup.entry_psw.config(show='')
                        self.popup.toggle_btn.config(image=self.closed_eye)
                    else:
                        messagebox.showerror("XNAT-PIC Uploader", "Error! The PIN code does not correspond")
                        self.popup.deiconify()
                else:
                    pass
        
        self.popup.entry_psw = ttk.Entry(self.popup.cred_frame, show="*", width=25)
        self.popup.entry_psw.var = tk.StringVar()
        self.popup.entry_psw["textvariable"] = self.popup.entry_psw.var
        self.popup.entry_psw.grid(row=3, column=1, padx=2, pady=2)
        self.popup.toggle_btn = ttk.Button(self.popup.cred_frame, image= self.open_eye,
                                            command=toggle_password, state='disabled', 
                                            cursor=CURSOR_HAND, style="Popup.TButton")
        self.popup.toggle_btn.grid(row=3, column=2, padx=2, pady=2, sticky=tk.W)
        def enable_toggle(*args):
            if self.popup.entry_psw.var.get() != "":
                self.popup.toggle_btn.config(state='normal')
                if self.popup.entry_user.get() != "":
                    self.popup.btn_remember.configure(state='normal')
                else:
                    self.popup.btn_remember.configure(state='disabled')
            else:
                self.popup.toggle_btn.config(state='disabled')
                self.popup.btn_remember.configure(state='disabled')
        self.popup.entry_psw.var.trace('w', enable_toggle)

        self.popup.forgot_psw = ttk.Label(self.popup.cred_frame, text="Forgot password", style="Popup.TLabel", 
                                        cursor=CURSOR_HAND)
        self.popup.forgot_psw.grid(row=4, column=1, padx=1, ipadx=1)
        self.popup.forgot_psw.bind("<Button-1>", self.forgot_psw)

        self.popup.register_btn = ttk.Label(self.popup.cred_frame, text="Register", style="Popup.TLabel",
                                        cursor=CURSOR_HAND)
        self.popup.register_btn.grid(row=4, column=2, padx=2, pady=2, sticky=tk.W)
        self.popup.register_btn.bind("<Button-1>", self.register)

        # Label Frame for HTTP buttons
        self.popup.label_frame_http = ttk.LabelFrame(self.popup, text="Options", style="Popup.TLabelframe")
        self.popup.label_frame_http.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)
        
        # HTTP/HTTPS 
        self.popup.http = tk.StringVar()
        self.popup.button_http = ttk.Radiobutton(self.popup.label_frame_http, text=" http:// ", variable=self.popup.http, 
                                                    value="http://", style="Popup.TRadiobutton")
        self.popup.button_http.grid(row=1, column=0, sticky=tk.E, padx=2, pady=2)
        self.popup.button_https = ttk.Radiobutton(self.popup.label_frame_http, text=" https:// ", variable=self.popup.http, 
                                                    value="https://", style="Popup.TRadiobutton")
        self.popup.button_https.grid(row=1, column=1, padx=2, pady=2, sticky=tk.E)
        self.popup.http.set("http://")

        # SAVE CREDENTIALS CHECKBUTTON
        self.popup.remember = tk.IntVar()
        self.popup.btn_remember = ttk.Checkbutton(self.popup.cred_frame, text="Remember me", variable=self.popup.remember, state='disabled',
                                                    onvalue=1, offvalue=0, style="Popup.TCheckbutton")
        self.popup.btn_remember.grid(row=2, column=2, padx=2, pady=2, sticky=tk.W)

        # CONNECTION
        self.popup.button_connect = ttk.Button(self.popup, text="Login", style="MainPopup.TButton",
                                                command=self.login)
        self.popup.button_connect.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

        # QUIT button
        def quit_event():
            self.connected = False
            self.popup.destroy()

        self.popup.button_quit = ttk.Button(self.popup, text='Quit', command=quit_event, style="MainPopup.TButton")
        self.popup.button_quit.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    def forgot_psw(self, *args):
        webbrowser.open("http://130.192.212.48:8080/app/template/ForgotLogin.vm#!", new=1)

    def register(self, *args):
        webbrowser.open("http://130.192.212.48:8080/app/template/Register.vm#!", new=1)

    def get_list_of_users(self):
            # Get the list of registered and stored users
            try:
                home = os.path.expanduser("~")
                # Define the encrypted file path
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                # Define the decrypted file path
                decrypted_file = os.path.join(home, "Documents", ".XNAT_login_file00000.txt")
                # Decrypt the encrypted file
                pyAesCrypt.decryptFile(encrypted_file, decrypted_file, os.environ.get('secretKey'), 
                                        int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
                # Open the decrypted file
                with open(decrypted_file, 'r') as credentials_file:
                    # Read the data
                    data = json.load(credentials_file)
                    # Get the list of users
                    list_of_users = list(data.keys())
                # Clear the 'data' variable
                data = ''
                # Remove the decrypted file
                os.remove(decrypted_file)
                return list_of_users
            except Exception as error:
                return []

    def get_credentials(self, *args):

        if self.popup.entry_user.get() != '':
            if self.popup.entry_user.get() in self.popup.combo_user['values']:
                # Load stored credentials
                self.load_saved_credentials()
                # Disable the button to modify the web address
                self.popup.entry_address.configure(state='disabled')
                # Enable the 'Change address' button
                self.popup.modify_address_btn.configure(state='normal')
                # Enable the 'Remember me' button
                self.popup.btn_remember.configure(state='normal')
                # Enable the 'Show password' toggle button
                self.popup.toggle_btn.configure(state='normal')
            else:
                if self.popup.entry_psw.var.get() != '':
                    # Enable the 'Remember me' button
                    self.popup.btn_remember.configure(state='normal')
        else:
            # Disable the 'Remember me' button
            self.popup.btn_remember.configure(state='disabled')
            # Reset 'Remember me' button
            self.popup.remember.set(0)
            # Disable the 'Show password' toggle button
            self.popup.toggle_btn.configure(state='disabled')

    def load_saved_credentials(self):

        try:
            home = os.path.expanduser("~")
            # Define the encrypted file path
            encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
            # Define the decrypted file path
            decrypted_file = os.path.join(home, "Documents", ".XNAT_login_file00000.txt")
            # Decrypt the file
            pyAesCrypt.decryptFile(encrypted_file, decrypted_file, os.environ.get('secretKey'), 
                                    int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
            # Open the decrypted file in 'read' mode
            with open(decrypted_file, 'r') as credentials_file:
                # Read the data
                data = json.load(credentials_file)
                # Fill the empty fields
                self.popup.entry_address.var.set(data[self.popup.entry_user.get()]['Address'])
                self.popup.entry_user.set(data[self.popup.entry_user.get()]['Username'])
                self.popup.entry_psw.var.set(data[self.popup.entry_user.get()]['Password'])
            # Clear the 'data' variable
            data = ''
            # Remove the decrypted file
            os.remove(decrypted_file)
            # Check the 'Remember me' button
            self.popup.btn_remember.config(state='normal')
            self.popup.remember.set(1)
        except Exception as error:
            messagebox.showerror("XNAT-PIC Login", "Error! The user information is not available, or you don't have access to it.")

    def login(self):

        # Retireve the complete address
        self.popup.entry_address_complete = self.popup.http.get() + self.popup.entry_address.var.get()

        home = os.path.expanduser("~")
        try:
            # Start a new xnat session
            self.session = xnat.connect(
                self.popup.entry_address_complete,
                self.popup.entry_user.get(),
                self.popup.entry_psw.var.get(),
            )
            self.connected = True
            # Check if the 'Remember Button' is checked
            if self.popup.remember.get() == True:
                # Save credentials
                self.save_credentials()
            else:
                # Try to remove the existent encrypted file
                try:
                    os.remove(
                        os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                    )
                except FileNotFoundError:
                    pass
            self.popup.destroy()

        except Exception as error:
            messagebox.showerror("Error!", error)
            self.connected = False
            self.popup.destroy()

    def save_credentials(self):

        home = os.path.expanduser("~")

        if os.path.exists(os.path.join(home, "Documents")):
            
            # Define the path of the encrypted file
            encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
            # Define the path of the decrypted file
            decrypted_file = os.path.join(home, "Documents", ".XNAT_login_file00000.txt")

            if os.path.isfile(encrypted_file):

                # Decrypt the encrypted file exploiting the secret key
                pyAesCrypt.decryptFile(encrypted_file, decrypted_file, os.environ.get('secretKey'), 
                                        int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
                # Open decrypted file and read the data stored
                with open(decrypted_file, 'r') as credentials_file:
                    data = json.load(credentials_file)
                # Update the already stored data with the current session parameters
                data[str(self.popup.entry_user.get())] = {
                            "Address": self.popup.entry_address.var.get(),
                            "Username": self.popup.entry_user.get(),
                            "Password": self.popup.entry_psw.var.get(),
                            "HTTP": self.popup.http.get()
                    }
                # Remove the decrypted file
                os.remove(decrypted_file)
            
            else:
                # Define empty dictionary for credentials
                data = {}
                # Add the current credentials to the dictionary
                data[str(self.popup.entry_user.get())] = {
                            "Address": self.popup.entry_address.var.get(),
                            "Username": self.popup.entry_user.get(),
                            "Password": self.popup.entry_psw.var.get(),
                            "HTTP": self.popup.http.get()
                    }

            # Define the path of the file
            file = os.path.join(home, "Documents", ".XNAT_login_file.txt")
            # Open the file to write in the data to be stored
            with open(file, 'w+') as login_file:
                json.dump(data, login_file)
            # Clear data variable
            data = {}
            # Encrypt the file
            pyAesCrypt.encryptFile(file, encrypted_file, os.environ.get('secretKey'), 
                                    int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
            # Remove the file
            os.remove(file)