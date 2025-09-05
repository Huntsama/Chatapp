import tkinter as tk
from tkinter import messagebox
from login_screen import LoginScreen
from chat_list_screen import ChatListScreen
from chat_screen import ChatScreen
from client import Client

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Chat Application')
        self.geometry('500x500')

        # This will hold the Client instance once the user logs in
        self.client = None

        # Main container for the frames
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to hold the different frames/screens
        self.frames = {}
        self.frame_classes = {
            "LoginScreen": LoginScreen,
            "ChatListScreen": ChatListScreen,
            "ChatScreen": ChatScreen
        }
        self.active_frame = None

        # Initialize and store all frames
        for frame_name, FrameClass in self.frame_classes.items():
            frame = FrameClass(self.container, self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginScreen")

    def get_active_frame(self):
        return self.active_frame

    def show_frame(self, frame_name):
        """Bring a frame to the front for the user to see."""
        try:
            frame = self.frames[frame_name]
            frame.tkraise()
            self.active_frame = frame_name
        except KeyError:
            print(f"Error: The frame {frame_name} does not exist.")
            messagebox.showerror("Error", f"The frame {frame_name} does not exist.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            messagebox.showerror("Error", "An unexpected error occurred.")

    def connect_client(self, ip_address, username):
        """Attempt to connect to the server and handle any connection issues."""
        try:
            url = f'http://{ip_address}:5000'
            #sets url in client class
            self.client = Client(url, username, gui_mode=True, update_gui=self.update_gui)
            #connect method of client which uses url to connect to server
            self.client.connect()
            self.client.connected_event.wait(timeout=10)  # Wait for up to 10 seconds
            if not self.client.connected_event.is_set():
                raise ConnectionError("Failed to connect within the timeout period.")
        except Exception as e:
            print(f"Failed to connect: {e}")
            messagebox.showerror("Connection Error", "Failed to connect to the server.")


    def update_gui(self, event_type, data):
        """Update the GUI based on network events from the Client."""
        print("GUI Event type", event_type)
        match (event_type):
            case 'message':
                self.frames['ChatScreen'].update_chat_display(data)
            case 'rooms':
                self.frames['ChatListScreen'].update_room_list(data)
            case 'join_room_confirmation':
                self.frames['ChatListScreen'].on_join_room_confirmation(data)
            case 'wrong_pass':
                self.frames['ChatListScreen'].on_error(data)
            case 'image':
                self.frames['ChatScreen'].update_chat_display_img(data)
            case 'name_already_taken':
                messagebox.showerror("Connection Error", data)
                self.disconnect_client()
            case _:
                print(f"Error: No event type {event_type}")

    def disconnect_client(self):
        """Disconnect the client from the server."""
        if self.client:
            self.client.disconnect()
            self.client = None
        self.show_frame("LoginScreen")

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
