import tkinter as tk
from tkinter import simpledialog, messagebox

"""
ChatListScreen handles the display and interaction of chat room listings. 
it allows users to connect to, join, or create new chat rooms. this screen includes features to disconnect from the server,
view a list of available chat rooms, and handles the user authentication when the room is private.
"""

class ChatListScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #updated when receive a room list
        self.chat_rooms = None

        header_frame = tk.Frame(self)
        header_frame.pack(side='top', fill='x')
        self.disconnect_button = tk.Button(header_frame, text="Disconnect", command=controller.disconnect_client)
        self.disconnect_button.grid(row=0, column=0, sticky='w')        
        self.label = tk.Label(header_frame, text="Choose a room from the list", anchor='center')
        self.label.grid(row=0, column=1, padx=100)
        self.chat_listbox = tk.Listbox(self)
        self.chat_listbox.pack(fill="both", expand=True)
        self.go_to_chat_button = tk.Button(self, text="Join chat", command=self.join)
        self.go_to_chat_button.pack(pady=10)
        self.add_room_button = tk.Button(self, text="Add room", command=self.add_room)
        self.add_room_button.pack(pady=10)


    """
    when trying to join a chat room from the listbox. this method first retrieves the selected room's details and then checks if the room is public or private.
    for public rooms the user joins directly but for private rooms, a password dialog is displayed. if the room is not recognized or another error happened an
    error message are displayed to the user.
    """
    def join(self):
        selected_room = self.chat_listbox.get(tk.ACTIVE)
        if selected_room:
            try:
                room = self.chat_rooms[selected_room]
                room_id = room['id']
                public = room['public']
                if public:
                    self.controller.client.join_room(room_id, None)
                elif not public:
                    password = simpledialog.askstring("Password", "Enter password:", show='*')
                    if password:
                        self.controller.client.join_room(room_id, password)
            except KeyError as ke:
                print(f"Error{ke}: {selected_room} is not known by client")
            except Exception as e:
                print(f"Ooops something when wrong somewhere: {e}")


    def on_join_room_confirmation(self, data):
        """
            Updates the view to a chat screen view
        """
        self.controller.show_frame('ChatScreen')

    def on_error(self, error_message: str):
        messagebox.showerror("Error", error_message)

    """
    Updates the chat rooms and refreshes the listbox display to show the latest available rooms. 
    This method clears any existing entries in the listbox before inserting the updated list of room names received from the server or another source. 
    This ensures that the listbox only displays the current set of rooms.
    """

    def update_room_list(self, rooms):
        self.chat_rooms = rooms
        print(f"Updated Rooms {self.chat_rooms}")
        """Update the chat listbox with a list of room names."""
        self.chat_listbox.delete(0, tk.END)  # Clear all current entries in the listbox
        for room in rooms:
            self.chat_listbox.insert(tk.END, room)  # Add new entries to the listbox
    """
    This function allow the user to create both public and private rooms.
    u can creates a new chat room by prompting for the room's name and an optional password but when you pass none you create a public room
    if the user cancels the room creation process at any point, the function returns without making changes.
    """
 
    def add_room(self):
        new_room_name = simpledialog.askstring("Add Room", "Enter the new room name:")
        if (new_room_name is None):
            # user pressed cancel button, we dont add the room
            return
        password = simpledialog.askstring("Add Password", "Enter password:\n(leave empty for none)", show='*')
        if (password is None):
            # user pressed cancel button, we dont add the room
            return
        if password == "":
            password = None
        if new_room_name:
                self.controller.client.add_room(new_room_name, password)