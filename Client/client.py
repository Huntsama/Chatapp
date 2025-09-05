import socketio
import threading

class Client:
    def __init__(self, server_url, name, gui_mode=False, update_gui=None):
        self.server_url = server_url
        self.name = name
        self.gui_mode = gui_mode
        self.update_gui = update_gui
        self.sio = socketio.Client(reconnection=True,handle_sigint=True)
        self.connected_event = threading.Event()
        self.room_event = threading.Event()  # Event to signal when room data is received
        self.rooms = {}  # List to store the names of the rooms, stored also in chat_list_screen
        self.room_lock = threading.Lock()  # Lock for synchronizing access to rooms_list
        self.setup_handlers()

    def setup_handlers(self):

        @self.sio.event
        def connect():
            print("Connected to server.")
            self.connected_event.set()  # Signal that the client has connected
            self.sio.emit('register', {'name': self.name})  # Emit an event to register the client with its name

        @self.sio.event
        def disconnect():
            print("Disconnected from server.")
            self.connected_event.clear()  # Clear the connected event when disconnected

        @self.sio.on('message')
        def handle_message(data):
            try:
                if 'content' in data:
                    message = data['content']
                    if self.gui_mode and self.update_gui:
                        self.update_gui('message', message)
            except Exception as e:
                print(f"An exception occurred while handling the message: {e}")

        @self.sio.on('availableRooms')
        def on_available_rooms(data):
            if isinstance(data, dict) and 'rooms' in data:
                with self.room_lock:
                    self.rooms = data['rooms']
                    print(f"in client {self.rooms}")
                if self.gui_mode and self.update_gui:
                    self.update_gui('rooms', self.rooms)
                self.room_event.set()

        @self.sio.on('join_room_confirmation')
        def on_join_room_confirmation(data):
            """
                Recieved if authentification to enter room is successfull
            """
            if self.gui_mode and self.update_gui:
                self.update_gui('join_room_confirmation', data)

        @self.sio.on('status')
        def status(data):
            try:
                status = data['message']
                match (status):
                    case 'wrong_pass':
                        # If password sent was wrong we display message
                        if self.gui_mode and self.update_gui:
                            self.update_gui('wrong_pass', "Wrong Password")
                    case 'name_already_taken':
                        # If name already exists update gui to login
                        if self.gui_mode and self.update_gui:
                            self.update_gui('name_already_taken', "User name already taken")
                    case _:
                        print(f"Unknown status code {status}")
            except Exception as e:
                print(e)

        @self.sio.on('error')
        def on_error(data):
            if self.gui_mode and self.update_gui:
                self.update_gui('wrong_pass', data)

        @self.sio.on("image")
        def handle_image(data):
            self.update_gui('image', data)

    def connect(self):
        self.sio.connect(self.server_url)
        # Start the Socket.IO event loop in a separate daemon thread
        event_thread = threading.Thread(target=self.sio.wait)
        event_thread.daemon = True
        event_thread.start()

    def send_message(self, message):
        self.sio.emit('message', {'content': message})

    def send_image(self, image_data):
        print("sending image data to server..")
        self.sio.emit('image', {'image_data': image_data})

    def join_room(self, room_id, password):
        """
            Sends room_id and password to join a room
        """
        self.sio.emit('join', {'room_id': room_id, 'password': password})

    def leave_room(self):
        self.sio.emit('leave', {'content': 'None'})

    def disconnect(self):
        self.sio.disconnect()

    def add_room(self, room_name, password):
        self.sio.emit('add_room',{'room_name': room_name, 'password': password})
