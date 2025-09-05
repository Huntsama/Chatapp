import tkinter as tk
from tkinter import messagebox

#https://stackoverflow.com/questions/43360921/dont-understand-tkinter-entry-box-validatiom

"""
LoginScreen screen is a simple tkinter Frame for user login, where users provide their username and IP address to connect to a chat server. 
"""


class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # username label and entry
        self.label = tk.Label(self, text="Enter username:")
        self.label.pack(pady=10)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        # IP address label and entry
        self.label_ip = tk.Label(self, text="Enter IP Address:")
        self.label_ip.pack(pady=10)
        vcmd = (self.register(self.validate_ip), "%P")
        self.ip_entry = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.ip_entry.insert(tk.END, '192.168.0.130')
        self.ip_entry.pack(pady=10)
        #login_button
        self.login_button = tk.Button(self, text="Login", command=self.on_login)
        self.login_button.pack(pady=10)
    
    #IP function used in the  Address Input A labeled entry for the IP address, which includes validation to ensure only numerical input and dots.

    def validate_ip(self, new_value):
        valid_chars = "0123456789."
        for char in new_value:
            if char not in valid_chars:
                return False
        return True
    
    # login function called in the login button Initiates the login process using the provided credentials and handles the connection logic. if the connection is successful, 
    # the screen transitions to the chat list. if not, it shows an error message.

    def on_login(self):
        username = self.username_entry.get()
        ip_address = self.ip_entry.get()
        if not ip_address:
            messagebox.showerror("Login Error", "IP Address cannot be empty.")
            return
        if not username:
            messagebox.showerror("Login Error", "Username cannot be empty.")
            return

        self.controller.connect_client(ip_address, username)

        # if the user is connected you display the chatlistscreen
        if self.controller.client.connected_event.is_set():
            self.controller.show_frame("ChatListScreen")
        else:
            messagebox.showerror("login Failed", "Could not connect to the server. Please try again.")
