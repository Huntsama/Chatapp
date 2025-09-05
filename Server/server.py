from flask import Flask, request
from flask_socketio import SocketIO, emit, disconnect
import logging
from state import State
from datetime import datetime, timezone
from message import Message

app = Flask(__name__)

# Secret key is public oopsi daisy
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Set up detailed logging for debugging purposes
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('SERVER')

state = State()  # Initialize the state of the application

@socketio.on('message')
def handle_message(data):
    """
        Used when client sends a message in a room
        Message is added to the room.
        In the room class it is broadcasted to 
        every other client in that room
    """
    user = state.get_user(request.sid)
    room = state.get_room(user.room)

    if user and room:
        message_content = data['content']
        new_message = Message(datetime.now(timezone.utc), message_content, user.name)
        room.add_message(new_message)
        #emit('message', {'sender': user.name, 'content': message_content}, room=room.name)
    else:
        log.error("Room not found")

@socketio.on('image')
def handle_image(data):
    """
        Used when client sends a image in a room
        In the room class this image is broadcasted to
        every other client in that room
    """
    user = state.get_user(request.sid)
    room = state.get_room(user.room)
    if user and room:
        image_data = data['image_data']
        new_message = Message(datetime.now(timezone.utc), "<Image>", user.name, image_data=image_data)
        room.add_message(new_message)
        room.send_image(image_data)
    else:
        log.warning("User not found or not in any room")

@socketio.on('join')
def on_join(data):
    """
        Gets called when a user asks to join a room
        This way we can unregister him from its current room
    """
    try:
        password = data.get('password')
        room = state.get_room(data['room_id'])
        log.info(f"room {room.name}, password sent {password}")
        if room.password != password:
            # Sends status message to client, message content has to match
            # Entry in status handler on client side
            emit('status', {'message': 'wrong_pass'})
            log.error("Invalid password for room")
        else:
            # joins rooms on back end
            state.join_room(request.sid, data['room_id'])
            # Sends message to front end to update its display
            emit('join_room_confirmation', {'message': 'Joined room'})

    except ValueError as ve:
        log.error(f"{ve}")

@socketio.on('leave')
def on_leave(data):
    """
        Gets called when a user asks to leave a room
        This way we can unregister him from its current room
    """
    try:
        state.leave_room(request.sid)
    except ValueError as ve:
        log.error(f"{ve}")

@socketio.on('connect')
def handle_connect():
    """
        We can identify a client by his socket ID.
        This implies that if he disconnects we close his socket.
    """
    log.info(f"Client {request.sid} connected")
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    log.info(f"Client {request.sid} disconnected")
    state.disconnect_user(request.sid)

@socketio.on('add_room')
def handle_add_room(data):
    """
        Used to add a room in the server list
    """
    try:
        created_room = state.add_room(data['room_name'], data['password'])
        # Make use join newly created room
        state.join_room(request.sid, created_room.id)
        # Sends message to front end to update its display
        emit('join_room_confirmation', {'message': 'Joined room'})
    except Exception as e: 
        log.error(f"Duplicate room, not added. Event is NOT sent to client atm")
    available_rooms = state.get_rooms_dict()
    for user in state.users.values():
        emit('availableRooms', {'rooms': available_rooms}, to=user.sid)


@socketio.on('register')
def handle_register(data):
    """
        Handles registration of new user
        Will try to see if the username sent by the client exists
        If it does, returns an error by emitting on 'status' handle with the error message
        Else, registers user and sends message to the client to update its view.
    """
    username = data['name']
    session_id = request.sid
    try:
        state.connect_user(username, session_id)
        log.info(f"Registered user {username} with session ID {session_id}")
        # Send the available rooms after registration, as a dictionary
        availableRooms = state.get_rooms_dict()
        emit('availableRooms', availableRooms, to=session_id)
    except NameError as ne:
        # error here is if a user with same name exist already
        log.error(f"Error registering user: {ne}")
        emit('status', {'message': 'name_already_taken'})
        disconnect()
    except Exception as e:
        log.error(f"Error registering user: {e}")
        # If registration fails, disconnect the client
        disconnect()

if __name__ == '__main__':
    state = State()
    state.add_room(name="Lobby", password=None)
    state.add_room(name="General", password=None)
    state.add_room(name="Private", password="1234")

    #socketio.run(app, debug=True)
    socketio.run(app, host='0.0.0.0', debug=True)  # Run the server to be accessible externally
