from datetime import datetime

class Message:
    """
    Class representing a message object.
    """
    def __init__(self, stamp: datetime, content: str, sender: str, image_data=None):
        self.stamp = stamp
        self.content = content
        self.sender = sender
        self.image_data = image_data

    def __repr__(self):
        """
            repr str for a msg
        """
        return f"Message(stamp={self.stamp!r}, content={self.content!r}, sender={self.sender!r}, image_data={self.image_data!r})"

    def __str__(self):
        return f"{self.sender} ({self.stamp.strftime('%Y-%m-%d %H:%M:%S')}): {self.content}"
