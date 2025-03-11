from repositories.user_repository import UserRepository
from models.user import User

class UserService:
    """
    Service for user operations
    """
    def __init__(self):
        self.user_repository = UserRepository()
        
    def get_user(self, telegram_id):
        """
        Get a user by Telegram ID
        """
        return self.user_repository.get_by_telegram_id(telegram_id)
        
    def create_user(self, telegram_id):
        """
        Create a new user with the given Telegram ID
        """
        # Create a new User instance
        user = User(telegram_id=telegram_id)
        
        # Save the user to the database using the repository
        created_user = self.user_repository.create(user)
        
        if not created_user:
            raise Exception("Failed to create user")
            
        return created_user
        
    def user_exists(self, telegram_id):
        """
        Check if a user exists by Telegram ID
        """
        return self.user_repository.user_exists(telegram_id) 