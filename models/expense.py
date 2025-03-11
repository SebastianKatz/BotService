from datetime import datetime

class Expense:
    """
    Expense model representing a user's expense
    """
    def __init__(self, user_id, description, amount, category, added_at=None, id=None):
        self.id = id
        self.user_id = user_id
        self.description = description
        self.amount = amount
        self.category = category
        self.added_at = added_at or datetime.now()
        
    def __str__(self):
        return f"Expense(ID: {self.id}, User ID: {self.user_id}, Amount: {self.amount}, Category: {self.category})"
        
    def to_dict(self):
        """
        Convert expense to dictionary for database storage
        """
        return {
            "user_id": self.user_id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "added_at": self.added_at.isoformat() if isinstance(self.added_at, datetime) else self.added_at
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create an Expense instance from dictionary data
        """
        if not data:
            return None
            
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            description=data.get("description"),
            amount=data.get("amount"),
            category=data.get("category"),
            added_at=data.get("added_at")
        ) 