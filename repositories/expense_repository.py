from database import get_client
from models.expense import Expense
from datetime import datetime

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
