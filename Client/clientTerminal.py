import socketio
import threading

class Client:
    def __init__(self, server_url, name):
        self.server_url = server_url
        self.name = name
        self.sio = socketio.Client()
        self.connected_event = threading.Event()
        self.room_event = threading.Event()  # Event to signal when room data is received
        self.rooms_list = []  # List to store the names of the rooms
        self.room_lock = threading.Lock()  # Lock for synchronizing access to rooms_list
        self.setup_handlers()


    def setup_handlers(self):
        @self.sio.event
        def connect():
            self.connected_event.set()  # Signal that the client has connected
            self.sio.emit('register', {'name': self.name})  # Emit an event to register the client with its name

        @self.sio.event
        def disconnect():
            print("Disconnected from server.")
            self.connected_event.clear()  # Clear the connected event when disconnected

        @self.sio.on('message')
        def handle_message(data):
            try:
                if isinstance(data, dict) and 'sender' in data and 'content' in data:
                    print(f"{data['sender']}: {data['content']}")
                elif isinstance(data, dict) and 'message' in data:
                    print(data['message'])
            except Exception as e:
                print(f"An exception occurred while handling the message: {e}")
                
        @self.sio.on('connected')
        def on_connected(data):
            print(data['message'])

        @self.sio.on('availableRooms')
        def on_available_rooms(data):
            if isinstance(data, dict) and 'rooms' in data:
                self.rooms_list = data['rooms']  # Assuming 'rooms' is a list or dict of rooms
                self.room_event.set()  # Signal that room data is received
                self.room_event.clear()  # Immediately clear the event after setting
            else:
                pass
            
    def show_and_select_room(self):
        self.room_event.wait()  # Wait for the event to be set
        if self.rooms_list:
            print("Available rooms:")
            for room_name in self.rooms_list:
                print(room_name)
            room_name = input("Enter room name to join: ")
            self.sio.emit('join', {'room_name': room_name})  # Send the room name
        else:
            print("No rooms available to join.")


    def chat_loop(self):
        print("You can now send messages. Type 'exit' to leave.")
        while True:
            message = input("")
            if message.lower() == 'exit':
                break
            self.sio.emit('message', {'content': message})
        self.disconnect()

    def disconnect(self):
        print("Disconnecting from server...")
        self.sio.disconnect()

    def run(self):
        self.sio.connect(self.server_url)
        # Start the Socket.IO event loop in a separate daemon thread
        event_thread = threading.Thread(target=self.sio.wait)
        event_thread.daemon = True
        event_thread.start()

        # Block the main thread until the 'connected_event' is set
        self.connected_event.wait()

        # Signal that the client is ready to receive room information
        self.room_event.clear()

        # Call the function to handle room selection
        self.show_and_select_room()

        # Start the chat loop in the main thread
        self.chat_loop()

        # Keep the main thread running until disconnected
        self.connected_event.wait()
        print("Client event loop has ended.")

if __name__ == "__main__":
    server_url = 'http://127.0.0.1:5000'
    name = input("Enter your name: ")
    client = Client(server_url, name)
    client.run()
