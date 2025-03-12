from flask import Flask, redirect
import os
from dotenv import load_dotenv

# Import controllers
from controllers.message_controller import message_bp, root_message_bp

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Initialize Flask
app = Flask(__name__)

# Register blueprints
app.register_blueprint(message_bp)
app.register_blueprint(root_message_bp)  # Register root level endpoints

# Root endpoint redirects to API root
@app.route('/')
def root():
    return redirect('/api/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG) 