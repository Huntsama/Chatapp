import tkinter as tk
from tkinter import filedialog
import PIL
import PIL.Image
import PIL.ImageTk
import base64
import os

"""
the screen ChatScreen serves as an interface for a chat application it provides for users to send text and images and see their chat unfold in real time.
so in this class is a complete it has multiple fucntion for managing a chat room's interactions.
"""


class ChatScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self._images = []
        header_frame = tk.Frame(self)
        header_frame.pack(side='top', fill='x')
        
        self.back_button = tk.Button(header_frame, text="Back to Rooms List", command=self.leave_room)
        self.back_button.grid(row=0, column=0, sticky='w')
        
        self.label = tk.Label(header_frame, text="Instant Chat")
        self.label.grid(row=0, column=1, sticky='ew')
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.disconnect_button = tk.Button(header_frame, text="Disconnect",
                                           command=controller.disconnect_client)
        self.disconnect_button.grid(row=0, column=2, sticky='e')
        
        self.chat_display = tk.Text(self, state="disabled", height=15)
        self.chat_display.pack(fill="both", expand=True)
        
        message_frame = tk.Frame(self)
        message_frame.pack(fill='x')
        
        self.message_entry = tk.Entry(message_frame)
        self.message_entry.pack(side="left", fill="x", expand=True)
        
        self.send_button = tk.Button(message_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right")
        
        self.image_button = tk.Button(self, text="Send Image", command=self.send_image)
        self.image_button.pack(pady=5)
    

    def update_chat_display_img(self, message):
        self.chat_display.config(state=tk.NORMAL)
        new_image_bytes = base64.b64decode(message['content'])
        image = PIL.Image.frombytes("RGB",(100,100),new_image_bytes,'raw')
        imagetk = PIL.ImageTk.PhotoImage(image)
        self._images.append(imagetk)

        self.chat_display.image_create(tk.END, image=imagetk)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    """
    Displays an image in the chat display area. The image is decoded from base64 also this method ensures images are seamlessly integrated into the chat flow.
    """
    def send_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            img_before = PIL.Image.open(file_path)
            img_before = img_before.resize((100, 100))
            img = img_before.tobytes()
            str_img = base64.b64encode(img).decode('utf-8')
            data = str_img
            self.controller.client.send_image(data)
    
    """
    Updates the chat display with new content, which can be either text messages or images.
    """
    def update_chat_display(self, message):
        self.chat_display.config(state=tk.NORMAL)
        
        if isinstance(message, PIL.ImageTk.PhotoImage):
            self.chat_display.image_create(tk.END, message)
        else:
            self.chat_display.insert(tk.END, message + "\n")

        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    """
    gets the text from the input field and sends it as a message through the connected chat client.
    """
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.controller.client.send_message(message)
            self.message_entry.delete(0, tk.END)
    
    """
    Handles the user's request to leave the current chat room andt then navigates back to the chat room list screen.
    """
    def leave_room(self):
        self.controller.client.leave_room()
        self.clear_screen()
        self.controller.show_frame("ChatListScreen")
        
    def clear_screen(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
