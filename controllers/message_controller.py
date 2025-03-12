from flask import Blueprint, request, jsonify
from datetime import datetime
from services.user_service import UserService
from models.expense import Expense
from repositories.expense_repository import ExpenseRepository
import os
from langchain_openai import ChatOpenAI
import json
from prompts.expense_prompt import EXPENSE_PROMPT

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

@message_bp.route('/', methods=['GET'])
def home():
    """
    Home endpoint
    """
    return jsonify({"status": "ok", "message": "Bot Service running correctly"})

@message_bp.route('/health', methods=['GET'])
def health():
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
def process_message():
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
                "response_message": "🤖 Expense Bot - Available Commands:\n\n" +
                                 "To register, send:\n" +
                                 "'I want to register to the application'\n\n" +
                                 "Once registered, you can:\n" +
                                 "1. Record expenses by sending messages like:\n" +
                                 "   - 'Bought bread for $100'\n" +
                                 "   - 'Paid $30 for gas'\n" +
                                 "   - 'Taxi $20'\n\n" +
                                 "2. Use /report to see your expenses from the last 24 hours"
            })
        
        # Check if this is a daily report request
        if message.lower().strip() == "/report":
            print("\n=== REPORT COMMAND PROCESSING ===")
            print(f"Received report request from telegram_id: {telegram_id}")
            try:
                # Check if user is registered
                print("Checking if user is registered...")
                if not user_service.user_exists(telegram_id):
                    print(f"User {telegram_id} is not registered")
                    return jsonify({
                        "success": True,
                        "telegram_id": telegram_id,
                        "message": message,
                        "should_respond": False
                    })
                
                print(f"User {telegram_id} is registered")
                # Get user by Telegram ID
                user = user_service.get_user(telegram_id)
                print(f"Retrieved user data: {user.__dict__ if user else None}")
                
                if not user or not user.id:
                    print(f"User with Telegram ID {telegram_id} not found or has no ID")
                    return jsonify({
                        "success": False,
                        "error": "User not found"
                    }), 404
                
                print(f"Getting daily expenses for user {user.id}")
                # Get daily expenses
                try:
                    daily_expenses = expense_repository.get_daily_expenses(user.id)
                    print(f"Successfully retrieved expenses. Count: {len(daily_expenses) if daily_expenses else 0}")
                    if daily_expenses:
                        print("First expense data:", daily_expenses[0].__dict__ if daily_expenses else None)
                except Exception as e:
                    print(f"Error getting daily expenses: {str(e)}")
                    raise e
                
                if not daily_expenses:
                    print("No expenses found in the last 24 hours")
                    return jsonify({
                        "success": True,
                        "telegram_id": telegram_id,
                        "message": message,
                        "should_respond": True,
                        "response_message": "You have no expenses recorded in the last 24 hours."
                    })
                
                print("Formatting expenses report...")
                # Format the expenses report
                try:
                    # Clean and sum amounts
                    amounts = [clean_amount(expense.amount) for expense in daily_expenses]
                    total = sum(amounts)
                    
                    report = "📊 Your expenses in the last 24 hours:\n\n"
                    
                    for expense in daily_expenses:
                        try:
                            time = expense.added_at.strftime("%I:%M %p")
                            amount = clean_amount(expense.amount)
                            report += f"• {expense.description}\n"
                            report += f"  💰 ${amount:,.2f}\n"
                            report += f"  🏷️ {expense.category}\n"
                            report += f"  🕒 {time}\n\n"
                        except Exception as e:
                            print(f"Error formatting expense: {e}")
                            print(f"Expense data: {expense.__dict__}")
                            continue
                    
                    report += f"Total: ${total:,.2f}"
                    print(f"Generated report: {report}")
                    print("=== END REPORT PROCESSING ===\n")
                    
                    return jsonify({
                        "success": True,
                        "telegram_id": telegram_id,
                        "message": message,
                        "should_respond": True,
                        "response_message": report
                    })
                except Exception as e:
                    print(f"Error calculating total or formatting report: {str(e)}")
                    print("Expense amounts:", [expense.amount for expense in daily_expenses])
                    raise Exception("Error processing expense amounts. Please check that all amounts are valid numbers.")
            except Exception as e:
                print(f"Error processing report request: {str(e)}")
                print(f"Full error details: ", e)
                import traceback
                print("Traceback:", traceback.format_exc())
                return jsonify({
                    "success": False,
                    "error": f"Error generating report: {str(e)}"
                }), 500
        
        # Check if this is a registration request
        if message.lower().strip() == "i want to register to the application":
            print("Registration request received")
            
            # Check if user is already registered
            if user_service.user_exists(telegram_id):
                print("User already registered")
                return jsonify({
                    "success": True,
                    "telegram_id": telegram_id,
                    "message": message,
                    "user_whitelisted": True,
                    "should_respond": True,
                    "response_message": "You are already registered in the application."
                })
            
            # Create new user
            try:
                user_service.create_user(telegram_id)
                print(f"User {telegram_id} registered successfully")
                return jsonify({
                    "success": True,
                    "telegram_id": telegram_id,
                    "message": message,
                    "user_whitelisted": True,
                    "should_respond": True,
                    "response_message": "You have been successfully registered. You can now start using the bot."
                })
            except Exception as e:
                print(f"Error registering user: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": "Error registering user"
                }), 500
        
        # Check if the user is in the whitelist
        is_whitelisted = user_service.user_exists(telegram_id)
        print(f"User in whitelist: {'YES' if is_whitelisted else 'NO'}")
        
        # If user is not in the whitelist, ignore the message completely
        if not is_whitelisted:
            print("User not in whitelist. Ignoring message without response.")
            return jsonify({
                "success": True,
                "telegram_id": telegram_id,
                "message": message,
                "user_whitelisted": False,
                "expense_created": False,
                "should_respond": False
            })
        
        # Process the message using Langchain
        expense_data = parse_expense_with_langchain(message)
        
        # If the message is not an expense, return without response
        if not expense_data:
            print("Message is not an expense. No response needed.")
            return jsonify({
                "success": True,
                "telegram_id": telegram_id,
                "message": message,
                "user_whitelisted": is_whitelisted,
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
        print(f"Message processed as expense: {expense_data}")
        expense = Expense(
            user_id=user.id,
            description=expense_data['description'],
            amount=expense_data['amount'],
            category=expense_data['category'],
            added_at=datetime.now()
        )
        
        # Save the expense to the database
        created_expense = expense_repository.create(expense)
        
        # Prepare response message
        response_message = f"{expense_data['category']} expense added ✅"
        
        print(f"Expense created: {created_expense}")
        print(f"Response message: {response_message}")
        print(f"{'='*50}\n")
        
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
def root_process_message():
    """
    Root level endpoint for process-message (for compatibility with existing clients)
    """
    return process_message()

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