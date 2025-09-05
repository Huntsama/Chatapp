from message import Message
from user import User
from flask_socketio import send, emit
from datetime import datetime, timezone
from functools import partial

class Room:
    """
        Class representing a room
        holds:
            - Messages
            - Room id
            - Name
            - Password Protected
            - Connected users
    """
    # General Id to take track of rooms
    g_id = 0

    def __init__(self, password=None, name=None):
        if name is None:
            name = f'Room{Room.g_id}'
        self._id = Room.g_id
        Room.g_id += 1
        self.messages = []
        self._name = name
        self.password = password
        self._connected_users = set()

    @property
    def id(self):
        """
            id getter
        """
        return self._id

    @property
    def connected_users(self):
        """
            Get set of connected users in room
        """
        return self._connected_users

    @property
    def name(self):
        """
            Get room name
        """
        return self._name


    def add_message(self, msg: Message):
        """
            Adds a message to the history of the room
            Broadcast this message to every client in the room
        """
        self.messages.append(msg)
        self.broadcast(msg)

    def send_image(self, image_data):
        """
            Sends image to all the user in the room
            image_data in binary base64 encoded image
        """
        for user in self._connected_users:
            emit("image", {"sender": user.name, "content": image_data}, to=user.sid)

    def user_join(self,  usr: User):
        """
            Adds user to connected users in room
        """
        usr.room = self.id
        self._connected_users.add(usr)
        self.broadcast(Message(datetime.now(timezone.utc), f"{usr.name} joined", "SERVER"))

    def user_leave(self, usr: User):
        """
            Removes user from connected users in room
        """
        usr.room = None
        self._connected_users.remove(usr)
        self.broadcast(Message(datetime.now(timezone.utc), f"{usr.name} left", "SERVER"))

    def broadcast(self, message: Message):
        """
            Sends message to all users of room
        """
        content = f"""({message.stamp.strftime('%H:%M')}) {message.sender} : {message.content}"""

        # partial application of content to send function
        send_partial = partial(send, {'content': content})

        # get all the sid from the connected users
        list_sid = list(map(lambda user: user.sid, self._connected_users))

        # call send_partial using all previous sids
        # we need to convert it to a list to apply the map function (otherwise it does not work)
        list(map(lambda sid: send_partial(to=sid), list_sid))

        # for user in self._connected_users:
        #     send({'content': content}, to=user.sid)
