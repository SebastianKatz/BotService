# Expense Bot Service

A Python-based service that processes expense messages from Telegram users and categorizes them automatically.

## Features

- **User Whitelist**: Only processes messages from users in the database whitelist.
- **Expense Recognition**: Identifies expense-related messages and ignores non-expense texts.
- **Automatic Categorization**: Categorizes expenses into predefined categories based on message content.
- **Response Messages**: Sends confirmation messages with the expense category.
- **Daily Expense Reports**: Provides a summary of expenses recorded in the last 24 hours.
- **API Authentication**: Secures API endpoints with an authentication header.

## Commands

The bot supports the following commands:
- **/start**: Initiates the conversation with the bot
- **/help**: Shows available commands and usage instructions
- **/report**: Shows a summary of expenses recorded in the last 24 hours

## Expense Categories

The bot automatically categorizes expenses into the following predefined categories:
- Housing
- Transportation
- Food
- Utilities
- Insurance
- Medical/Healthcare
- Savings
- Debt
- Education
- Entertainment
- Other

## Message Formats

The bot supports multiple message formats for expense tracking:

1. **Category Specified**: `Category: Description $Amount`
   - Example: `Food: Pizza $15.99`

2. **Description and Amount**: `Description $Amount`
   - Example: `Groceries $45.50`

3. **Amount for Description**: `$Amount for Description`
   - Example: `$20 for movie tickets`

4. **Spent Amount on Description**: `Spent $Amount on Description`
   - Example: `Spent $30 on gas`

## Setup and Configuration

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env` file:
   ```
   PORT=5000
   DEBUG=False
   DATABASE_URL=your_database_url
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   AUTH_KEY=your_auth_key
   ```

3. Start the service:
   ```
   python app.py
   ```

## API Endpoints

- **GET /api/**: Home endpoint
- **GET /api/health**: Health check endpoint
- **POST /api/process-message**: Process expense messages
  - Also available at root level: **/process-message**

## Authentication

All API endpoints are protected with an authentication header. Requests must include an `Authorization` header with the value matching the `AUTH_KEY` environment variable.

Example:
```
Authorization: your_auth_key
```

## Response Format

The service returns a JSON response with the following structure:

```json
{
  "success": true,
  "telegram_id": "user_telegram_id",
  "message": "original_message",
  "user_whitelisted": true,
  "expense_created": true,
  "expense_data": {
    "category": "Food",
    "description": "Pizza",
    "amount": 15.99
  },
  "should_respond": true,
  "response_message": "Food expense added ✅"
}
```

## Daily Report Format

When a user requests a daily report using the `/report` command, the response includes:

```
📊 Expense Report (Last 24 Hours)

Total: $X,XXX.XX

Expenses:
1. Description - $XXX.XX (Category) - HH:MM
2. Description - $XXX.XX (Category) - HH:MM
...
```

## Integration with Connector Service

This service is designed to work with the Telegram Connector Service, which handles the communication with Telegram users and forwards messages to this service for processing.

## Database Configuration

This service uses Supabase (PostgreSQL) to store registered users and their expenses. Follow these steps to configure the database:

### Prerequisites

1. Have a Supabase account
2. Create a new project in Supabase

### Configuration

1. Edit the `.env` file with your database connection details:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-key
AUTH_KEY=your_auth_key
```

### Database Structure

The database contains the following tables:

- `users`: Stores registered users
  - `id`: Unique user identifier
  - `telegram_id`: Telegram ID of the user
  - `created_at`: Registration date and time

- `expenses`: Stores registered expenses
  - `id`: Unique expense identifier
  - `user_id`: ID of the user who registered the expense
  - `description`: Description of the expense
  - `amount`: Amount of the expense
  - `category`: Category of the expense
  - `added_at`: Date and time when the expense was registered 