from langchain.prompts import ChatPromptTemplate

EXPENSE_PROMPT = ChatPromptTemplate.from_template("""
You are an expense analyzer. Your task is to analyze a message and determine if it contains information about an expense.

IMPORTANT: The following examples should ALL be considered expenses:
- "Groceries $50"
- "Paid $30 for gas"
- "Heladera 300 pesos"
- "Bought a new phone for 500 euros"
- "Taxi 20"
- "Coffee 5 dollars"

If the message contains an expense, extract the following information:
- Description: What was purchased or what the expense is for
- Amount: The monetary value of the expense (convert to numeric value only)
- Category: The category of the expense (Housing, Transportation, Food, Utilities, Insurance, Medical, Healthcare, Savings, Debt, Education, Entertainment, Other)

If the message does not contain an expense, return null.

The message might be in any format and any language. Try to extract the information as best as you can.
Recognize various currency formats including:
- Dollar amounts: $50, 50 dollars, USD 50
- Peso amounts: 300 pesos, ARS 300
- Euro amounts: €50, 50 euros, EUR 50
- Any other currency mentioned or implied

For any currency, extract only the numeric value for the amount field.

IMPORTANT: Any message that mentions a product or service with a numeric value should be considered an expense, even if it doesn't explicitly use words like "bought", "paid", or "spent".

Return your analysis as a JSON object with the following structure:
{{
  "is_expense": true,
  "description": "description of the expense",
  "amount": numeric_value,
  "category": "category of the expense"
}}

If it's not an expense, return:
{{
  "is_expense": false
}}

Message: {message}
""") 