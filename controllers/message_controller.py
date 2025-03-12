from flask import Blueprint, request, jsonify
from datetime import datetime
from services.user_service import UserService
from models.expense import Expense
from repositories.expense_repository import ExpenseRepository
import os
from langchain_openai import ChatOpenAI
import json
from prompts.expense_prompt import EXPENSE_PROMPT
from middleware.auth_middleware import auth_middleware

# Create a blueprint for message routes
message_bp = Blueprint('message', __name__, url_prefix='/api')

# Also register the process-message endpoint at the root level for compatibility
root_message_bp = Blueprint('root_message', __name__)

# Initialize services and repositories
user_service = UserService()
expense_repository = ExpenseRepository()

# Initialize Langchain components
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Helper function to get the help message
def get_help_message():
    return "🤖 Expense Bot - Available Commands:\n\n" + \
           "To register, send:\n" + \
           '"I want to register to the application"\n\n' + \
           "Once registered, you can:\n" + \
           "1. Record expenses by sending messages like:\n" + \
           '   - "Bought bread for $100"\n' + \
           '   - "Paid $30 for gas"\n' + \
           '   - "Taxi $20"\n\n' + \
           "2. Use /report to see your expenses from the last 24 hours"

@message_bp.route('/', methods=['GET'])
@auth_middleware
def api_home():
    """
    Home endpoint
    """
    return jsonify({"status": "ok", "message": "Bot Service running correctly"})

@message_bp.route('/health', methods=['GET'])
@auth_middleware
def api_health():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

def clean_amount(amount_str):
    """
    Clean amount string by removing currency symbol and thousands separators
    """
    try:
        # Remove currency symbol and any whitespace
        cleaned = amount_str.replace('$', '').strip()
        # Remove thousands separators
        cleaned = cleaned.replace(',', '')
        # Convert to float
        return float(cleaned)
    except (ValueError, AttributeError) as e:
        print(f"Error cleaning amount '{amount_str}': {e}")
        return 0.0

@message_bp.route('/process-message', methods=['POST'])
@auth_middleware
def api_process_message():
    """
    Receives messages from the Connector Service, verifies if the user is in the whitelist,
    processes the message using Langchain, and returns a response
    """
    try:
        print("=== PROCESSING NEW MESSAGE ===")
        # Get data from the request
        data = request.json
        
        # Verify that the data is valid
        if not data:
            print("Error: No data received")
            return jsonify({"success": False, "error": "No data received"}), 400
        
        # Extract message information
        telegram_id = data.get('telegram_id')
        message = data.get('message')
        
        if not telegram_id or not message:
            print("Error: Missing required data (telegram_id or message)")
            return jsonify({"success": False, "error": "Missing required data"}), 400
            
        # Print the message to the console
        print(f"\n{'='*50}")
        print(f"Message received at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"From: {telegram_id}")
        print(f"Message: {message}")
        
        # Check if this is a help command
        if message.lower().strip() == "/help":
            print("Help command received")
            return jsonify({
                "success": True,
                "telegram_id": telegram_id,
                "message": message,
                "should_respond": True,
                "response_message": get_help_message()
            })
        
        # Check if this is a report command
        if message.lower().strip() == "/report":
            print("Report command received")
            
            # Check if the user is registered
            is_registered = user_service.user_exists(telegram_id)
            
            if not is_registered:
                print(f"User {telegram_id} is not registered")
                # For unregistered users, send the help message
                return jsonify({
                    "success": True,
                    "telegram_id": telegram_id,
                    "message": message,
                    "user_whitelisted": False,
                    "should_respond": True,
                    "response_message": "You need to register first to use this command.\n\n" + get_help_message()
                })
            
            try:
                # Get user by Telegram ID
                user = user_service.get_user(telegram_id)
                
                if not user or not user.id:
                    print(f"User with Telegram ID {telegram_id} not found or has no ID")
                    return jsonify({
                        "success": False,
                        "error": "User not found"
                    }), 404
                
                # Get daily expenses
                expenses = expense_repository.get_daily_expenses(user.id)
                
                if not expenses or len(expenses) == 0:
                    print(f"No expenses found for user {telegram_id}")
                    return jsonify({
                        "success": True,
                        "telegram_id": telegram_id,
                        "message": message,
                        "user_whitelisted": True,
                        "should_respond": True,
                        "response_message": "📊 Expense Report (Last 24 Hours)\n\nNo expenses recorded in the last 24 hours."
                    })
                
                # Calculate total
                total = sum(clean_amount(expense.amount) for expense in expenses)
                
                # Format the report with the preferred style
                report = "📊 Your expenses in the last 24 hours:\n\n"
                
                for expense in expenses:
                    amount = clean_amount(expense.amount)
                    # Format time in 12-hour format with AM/PM
                    time_str = expense.added_at.strftime("%I:%M %p") if expense.added_at else "N/A"
                    
                    report += f"• {expense.description}\n"
                    report += f"  💰 ${amount:,.2f}\n"
                    report += f"  🏷️ {expense.category}\n"
                    report += f"  🕒 {time_str}\n\n"
                
                # Add total at the end
                report += f"Total: ${total:,.2f}"
                
                print(f"Report generated for user {telegram_id}")
                return jsonify({
                    "success": True,
                    "telegram_id": telegram_id,
                    "message": message,
                    "user_whitelisted": True,
                    "should_respond": True,
                    "response_message": report
                })
            except Exception as e:
                print(f"Error generating report: {str(e)}")
                return jsonify({
                    "success": False,
                    "telegram_id": telegram_id,
                    "message": message,
                    "user_whitelisted": True,
                    "should_respond": True,
                    "response_message": "Sorry, I couldn't generate your expense report. Please try again later."
                })
        
        # Check if the user is registered
        is_registered = user_service.user_exists(telegram_id)
        
        if not is_registered:
            print(f"User {telegram_id} is not registered")
            
            # Check if this is a registration request
            if "register" in message.lower():
                print(f"Registration request from {telegram_id}")
                
                # Register the user
                user_service.create_user(telegram_id)
                
                return jsonify({
                    "success": True,
                    "telegram_id": telegram_id,
                    "message": message,
                    "user_whitelisted": True,
                    "should_respond": True,
                    "response_message": "You have been registered successfully! You can now start tracking your expenses."
                })
            
            # If not a registration request, send the help message
            print(f"Sending help message to unregistered user {telegram_id}")
            return jsonify({
                "success": True,
                "telegram_id": telegram_id,
                "message": message,
                "user_whitelisted": False,
                "should_respond": True,
                "response_message": "Welcome! To use this bot, you need to register first.\n\n" + get_help_message()
            })
        
        # Parse the expense using Langchain
        expense_data = parse_expense_with_langchain(message)
        
        # If the message is not an expense, ignore it
        if not expense_data:
            print(f"Message is not an expense: {message}")
            return jsonify({
                "success": True,
                "telegram_id": telegram_id,
                "message": message,
                "user_whitelisted": True,
                "expense_created": False,
                "should_respond": False
            })
        
        # Get user by Telegram ID
        user = user_service.get_user(telegram_id)
        if not user or not user.id:
            print(f"User with Telegram ID {telegram_id} not found or has no ID")
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        # Create the expense
        expense = Expense(
            user_id=user.id,
            description=expense_data["description"],
            amount=expense_data["amount"],
            category=expense_data["category"]
        )
        
        # Save the expense
        expense_repository.create(expense)
        
        # Create a response message
        response_message = f"{expense_data['category']} expense added ✅"
        
        # Return response with expense information and response message
        return jsonify({
            "success": True,
            "telegram_id": telegram_id,
            "message": message,
            "user_whitelisted": True,
            "expense_created": True,
            "expense_data": expense_data,
            "should_respond": True,
            "response_message": response_message
        })
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Root level endpoint for process-message (for compatibility)
@root_message_bp.route('/process-message', methods=['POST'])
@auth_middleware
def root_process_message():
    """
    Root level endpoint for process-message (for compatibility with existing clients)
    """
    return api_process_message()

def parse_expense_with_langchain(message):
    """
    Parse an expense from a message using Langchain
    
    Returns a dictionary with the expense information or None if the message is not an expense
    """
    try:
        # Create the chain
        chain = EXPENSE_PROMPT | llm
        
        # Run the chain
        result = chain.invoke({"message": message})
        
        # Parse the result
        content = result.content
        print(f"Raw Langchain response: {content}")
        
        # Extract the JSON part
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].strip()
        else:
            json_str = content.strip()
        
        print(f"Extracted JSON string: {json_str}")
        
        # Parse the JSON
        expense_data = json.loads(json_str)
        
        print(f"Langchain analysis result: {expense_data}")
        
        # If it's not an expense, return None
        if not expense_data.get('is_expense', False):
            return None
        
        # Return the expense data
        return {
            "description": expense_data.get('description', 'Unknown expense'),
            "amount": expense_data.get('amount', 0),
            "category": expense_data.get('category', 'Other')
        }
    except Exception as e:
        print(f"Error parsing expense with Langchain: {str(e)}")
        # For debugging purposes, print the full message
        print(f"Original message: {message}")
        # In case of error, return None to indicate it's not a valid expense
        return None