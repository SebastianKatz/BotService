# Expense Bot Service

A Python-based service that processes expense messages from Telegram users and categorizes them automatically.

## Features

- **User Whitelist**: Only processes messages from users in the database whitelist.
- **Expense Recognition**: Identifies expense-related messages and ignores non-expense texts.
- **Automatic Categorization**: Categorizes expenses into predefined categories based on message content.
- **Response Messages**: Sends confirmation messages with the expense category.

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

## Integration with Connector Service

This service is designed to work with the Telegram Connector Service, which handles the communication with Telegram users and forwards messages to this service for processing.

## Configuración de la Base de Datos PostgreSQL

Este servicio ahora utiliza PostgreSQL para almacenar los mensajes recibidos. Sigue estos pasos para configurar la base de datos:

### Requisitos previos

1. Tener PostgreSQL instalado y en ejecución en tu sistema
2. Tener un usuario con permisos para crear bases de datos

### Configuración

1. Edita el archivo `.env` con los datos de conexión a tu base de datos:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=botservice
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
```

2. Ejecuta el script de inicialización de la base de datos:

```bash
python init_db.py
```

Este script creará la base de datos y las tablas necesarias.

### Endpoints para acceder a los datos

El servicio ahora proporciona los siguientes endpoints para acceder a los datos almacenados:

- `GET /messages`: Obtiene todos los mensajes almacenados en la base de datos
- `GET /messages/<telegram_id>`: Obtiene todos los mensajes de un usuario específico

### Estructura de la base de datos

La base de datos contiene la siguiente tabla:

- `messages`: Almacena los mensajes recibidos
  - `id`: Identificador único del mensaje
  - `telegram_id`: ID de Telegram del usuario que envió el mensaje
  - `message_text`: Contenido del mensaje
  - `processed`: Indica si el mensaje ha sido procesado
  - `created_at`: Fecha y hora en que se recibió el mensaje 