class User:
    def __init__(self, name, sid):
        self._name = name
        self._sid = sid
        self._room = None

    def __repr__(self):
        return f"User(name={self.name}, sid={self.sid}, room={self.room})"
        
    def __str__(self):
        return f"User: {self.name} (Session ID: {self.sid})"


    @property
    def name(self):
        """
            Returns user name
        """
        return self._name

    @property
    def room(self):
        """
            Returns current room (int) or None
        """
        return self._room

    @room.setter
    def room(self, new_room):
        if new_room is None:
            print(f"User {self.name} leaving room {self._room}")
        self._room = new_room
        if new_room is not None:
            print(f"User {self.name} joining room {new_room}")

    def remove_room(self):
        """
            sets room user to None
        """
        self._room = None

    @property
    def sid(self):
        """
            Returns socket Id
        """
        return self._sid
