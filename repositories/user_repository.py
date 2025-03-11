from database import get_client
from models.user import User
from datetime import datetime

class UserRepository:
    """
    Repository for user operations
    """
    def __init__(self):
        self.supabase = get_client()
        self.table_name = "users"
        
    def get_by_telegram_id(self, telegram_id):
        """
        Get a user by Telegram ID
        """
        try:
            response = self.supabase.table(self.table_name).select("*").eq("telegram_id", telegram_id).execute()
            if response.data and len(response.data) > 0:
                return User.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user by Telegram ID: {e}")
            return None
            
    def create(self, user):
        """
        Create a new user
        """
        try:
            user_data = user.to_dict()
            response = self.supabase.table(self.table_name).insert(user_data).execute()
            if response.data and len(response.data) > 0:
                return User.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
            
    def user_exists(self, telegram_id):
        """
        Check if a user exists by Telegram ID
        """
        try:
            user = self.get_by_telegram_id(telegram_id)
            return user is not None
        except Exception as e:
            print(f"Error checking if user exists: {e}")
            return False 