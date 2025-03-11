from datetime import datetime

class User:
    """
    User model representing a Telegram user
    """
    def __init__(self, telegram_id, id=None):
        self.id = id
        self.telegram_id = telegram_id
        
    def __str__(self):
        return f"User(ID: {self.id}, Telegram ID: {self.telegram_id})"
        
    def to_dict(self):
        """
        Convert user to dictionary for database storage
        """
        return {
            "telegram_id": self.telegram_id
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create a User instance from dictionary data
        """
        if not data:
            return None
            
        return cls(
            id=data.get("id"),
            telegram_id=data.get("telegram_id")
        ) 