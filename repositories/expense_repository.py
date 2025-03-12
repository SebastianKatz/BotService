from database import get_client
from models.expense import Expense
from datetime import datetime, timedelta

class ExpenseRepository:
    """
    Repository for expense operations
    """
    def __init__(self):
        self.supabase = get_client()
        self.table_name = "expenses"
        
    def get_by_id(self, expense_id):
        """
        Get an expense by ID
        """
        try:
            response = self.supabase.table(self.table_name).select("*").eq("id", expense_id).execute()
            if response.data and len(response.data) > 0:
                return Expense.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error getting expense by ID: {e}")
            return None
            
    def create(self, expense):
        """
        Create a new expense
        """
        try:
            expense_data = expense.to_dict()
            response = self.supabase.table(self.table_name).insert(expense_data).execute()
            if response.data and len(response.data) > 0:
                return Expense.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error creating expense: {e}")
            return None

    def get_daily_expenses(self, user_id):
        """
        Get all expenses for a user from the last 24 hours
        """
        try:
            # Calculate the timestamp for 24 hours ago
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_iso = yesterday.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            
            # Query expenses for the user in the last 24 hours
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("added_at", yesterday_iso)\
                .order("added_at", desc=True)\
                .execute()
            
            # Convert the response data to Expense objects
            if response.data:
                return [Expense.from_dict(expense_data) for expense_data in response.data]
            return []
            
        except Exception as e:
            print(f"Error getting daily expenses: {e}")
            print(f"Query parameters: user_id={user_id}, yesterday={yesterday_iso}")
            return []
