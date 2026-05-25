"""
Flask Backend Server for Arghadip Gayen Portfolio
Handles contact form submissions and other API endpoints
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configuration
CONTACT_EMAIL = "arghadipgayen4@gmail.com"
MESSAGES_FILE = "messages.json"

def load_messages():
    """Load messages from JSON file"""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_message(message):
    """Save a new message to JSON file"""
    messages = load_messages()
    messages.append(message)
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

# Serve static files
@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('.', path)

# API Endpoints
@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create message object
        message = {
            'id': datetime.now().isoformat(),
            'name': data['name'],
            'email': data['email'],
            'subject': data['subject'],
            'message': data['message'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': False
        }
        
        # Save message to file
        save_message(message)
        
        # Optionally send email notification (Uncomment below if SMTP is configured)
        # send_email_notification(message)
        
        print(f"\n[{message['timestamp']}] New message from {message['name']} ({message['email']})")
        print(f"Subject: {message['subject']}")
        print(f"Message: {message['message'][:100]}...")
        print("-" * 50)
        
        return jsonify({
            'success': True,
            'message': 'Your message has been received! I will get back to you soon.'
        }), 200
        
    except Exception as e:
        print(f"Error handling contact form: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your message.'
        }), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages (for admin purposes)"""
    # In production, add authentication here
    messages = load_messages()
    return jsonify({
        'success': True,
        'messages': messages,
        'count': len(messages)
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

def send_email_notification(message):
    """
    Send email notification for new contact form submission
    Requires SMTP configuration
    """
    # SMTP Configuration (set these as environment variables)
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    
    if not smtp_username or not smtp_password:
        print("Email notification skipped - SMTP credentials not configured")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = CONTACT_EMAIL
        msg['Subject'] = f"Portfolio Contact: {message['subject']}"
        
        body = f"""
        New Contact Form Submission
        
        From: {message['name']}
        Email: {message['email']}
        Subject: {message['subject']}
        Time: {message['timestamp']}
        
        Message:
        {message['message']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print("Email notification sent successfully")
        
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")

if __name__ == '__main__':
    try:
        # Lock to Port 5001 to bypass macOS AirPlay conflicts
        port = 5001
        
        # Safely handle the DEBUG environment variable, default to True for development
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        print(f"""
        ╔══════════════════════════════════════════════════╗
        ║     Arghadip Gayen Portfolio - Backend Server    ║
        ╠══════════════════════════════════════════════════╣
        ║  Server running at: http://127.0.0.1:{port}         ║
        ║  Debug mode: {debug}                               ║
        ╚══════════════════════════════════════════════════╝
        """)
        
        # Run using the synchronized port variable
        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: Server failed to start.\nDetails: {e}")