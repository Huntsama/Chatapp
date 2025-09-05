from flask_socketio import emit, ConnectionRefusedError, send
from user import User
from room import Room

import logging
log = logging.getLogger('SERVER')

class State:
    """
    Represents general state of our application
    """

    def __init__(self):
        """
            Constructor
            users are stored in a dictionnary {sid : usrObj}
            rooms are stored in a dictionnary {id : roomObj}
            user name are stored in a set. This helps for a fast
             search when a new client is connecting to verify if
            his name is already present
        """
        self.users = {}
        self.rooms = {}
        self.connected_user_names = set()

    def connect_user(self, user_name, user_sid):
        """
            Connects a user, checks if that username is already
            taken, if its the case, raises an error
        """
        if user_name in self.connected_user_names:
            raise NameError('Username already connected.')
        user = User(user_name, user_sid)
        self.users[user_sid] = user
        self.connected_user_names.add(user_name)

    def disconnect_user(self, user_sid):
        """
            Disconnects a user, removes him from the user list
            If that user was in a room, we remove him from the connected
            users in that room
        """
        user = self.users.pop(user_sid, None)
        if user:
            self.connected_user_names.remove(user.name)
            if user.room:
                room = self.rooms.get(user.room)
                if room:
                    room.user_leave(user)


    def add_room(self, name="", password=None):
        """
            Adds a new room
        """
        if any(name == room.name for room in self.rooms.values()):
            raise ValueError("Room name must be unique.")
        room = Room(password=password, name=name)
        log.info(f"Added room {name}")
        self.rooms[room.id] = room
        return room


    def delete_room(self, room_id):
        """
            Delets a room, functionality not implemented
        """
        if room_id in self.rooms:
            del self.rooms[room_id]
        else:
            raise ValueError("Room not found.")


    def join_room(self, user_sid, room_id):
        """
            user with user_sid joins room with room_id
        """
        user = self.get_user(user_sid)

        #User is already subscribed to a room
        if user.room is not None:
            log.info(f"User already subscribed in room {user.room}")
            #Make user leaves current room before entering a new one
            self.leave_room(user_sid)

        room = self.get_room(room_id)
        if user and room:
            log.info(f"User {user.name} joined room {room.name}")
            room.user_join(user)
        else:
            raise ValueError("From join room: Invalid user or room ID.")

    def leave_room(self, user_sid):
        user = self.get_user(user_sid)
        room = self.get_room(user.room)
        log.info(f"User {user} left room {room}")
        if user and room:
            log.info(f"User {user.name} left room {room.name}")
            room.user_leave(user)
        else:
            raise ValueError("From leave room: Invalid user or room ID.")

    def get_user(self, user_sid):
        """
            returns user object given sid
        """
        return self.users.get(user_sid)

    def get_room(self, room_id):
        """
            returns room object given sid
        """
        return self.rooms.get(room_id)

    def get_rooms_dict(self):
        """
            Returns list of available rooms
            Adds a (P) to the name of private rooms
        """
        availableRooms = {}
        for room in self.rooms.values():
            add_str = ""
            is_public = True
            if room.password is not None:
                add_str = " (P)"
                is_public = False
            availableRooms[f"{room.name}{add_str}"] = {"id": room.id, "public": is_public}
        wrapped = {}
        wrapped['rooms'] = availableRooms
        return wrapped


    def get_room_by_name(self, room_name):
        for room in self.rooms.values():
            if room.name == room_name:
                return room
        return None
