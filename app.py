from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flasgger import Swagger
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime
import jwt
import functools
from cors_config import configure_cors

# Initialize Flask app
app = Flask(__name__)

# Configure CORS before any other setup
configure_cors(app)
application = app

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DATABASE_PATH'] = os.environ.get('DATABASE_PATH', 'database.db')
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=1)

# Initialize Swagger documentation
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}

swagger = Swagger(app, config=swagger_config)

# Database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE_PATH'])
        db.row_factory = sqlite3.Row
        # Enable foreign keys
        db.execute("PRAGMA foreign_keys = ON")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Authentication middleware
def token_required(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Get admin user from database
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT * FROM admin_users WHERE id = ?", (data['user_id'],))
            current_user = cur.fetchone()
            
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
                
        except:
            return jsonify({'message': 'Invalid token!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorator

# Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'API is running',
        'docs': '/api/docs'
    })

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
        
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM admin_users WHERE username = ?", (data['username'],))
    user = cur.fetchone()
    
    if not user or not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    # Update last login time
    now = datetime.datetime.now().isoformat()
    cur.execute("UPDATE admin_users SET last_login = ? WHERE id = ?", (now, user['id']))
    db.commit()
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.datetime.now() + app.config['JWT_EXPIRATION_DELTA']
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    })

@app.route('/api/auth/register', methods=['POST'])
@token_required
def register(current_user):
    """
    Register a new admin user
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
            role:
              type: string
              default: admin
    responses:
      201:
        description: User created
      400:
        description: Invalid input
      409:
        description: Username already exists
    """
    # Only allow if current user has admin role
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Not authorized'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
    
    db = get_db()
    cur = db.cursor()
    
    # Check if username already exists
    cur.execute("SELECT id FROM admin_users WHERE username = ?", (data['username'],))
    if cur.fetchone():
        return jsonify({'message': 'Username already exists'}), 409
    
    # Create new user
    now = datetime.datetime.now().isoformat()
    role = data.get('role', 'admin')
    password_hash = generate_password_hash(data['password'])
    
    cur.execute(
        "INSERT INTO admin_users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
        (data['username'], password_hash, role, now)
    )
    db.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

# Utility endpoint to restore soft-deleted items
@app.route('/api/restore/<string:table_name>/<int:item_id>', methods=['POST'])
@token_required
def restore_item(current_user, table_name, item_id):
    """
    Restore a soft-deleted item
    ---
    tags:
      - Utility
    security:
      - Bearer: []
    parameters:
      - name: table_name
        in: path
        type: string
        required: true
        description: Name of the table
      - name: item_id
        in: path
        type: integer
        required: true
        description: ID of the item to restore
    responses:
      200:
        description: Item restored
      400:
        description: Invalid table name
      404:
        description: Item not found
    """
    # Only allow if current user has admin role
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Not authorized'}), 403
    
    # Validate table name to prevent SQL injection
    valid_tables = [
        'menu', 'year_name', 'contacts', 'social_networks', 'feedback',
        'staff', 'blog_categories', 'blog_items', 'about_company',
        'about_company_categories', 'about_company_category_items',
        'documents_categories', 'documents_items', 'admin_users'
    ]
    
    if table_name not in valid_tables:
        return jsonify({'message': 'Invalid table name'}), 400
    
    db = get_db()
    cur = db.cursor()
    
    # Check if item exists and is deleted
    cur.execute(f"SELECT id FROM {table_name} WHERE id = ? AND is_deleted = 1", (item_id,))
    if not cur.fetchone():
        return jsonify({'message': 'Item not found or not deleted'}), 404
    
    # Restore item
    cur.execute(f"UPDATE {table_name} SET is_deleted = 0 WHERE id = ?", (item_id,))
    db.commit()
    
    return jsonify({'message': f'Item restored in {table_name}'})

# Include other route modules
from routes.menu import register_menu_routes
from routes.year_name import register_year_name_routes
from routes.contacts import register_contacts_routes
from routes.social_networks import register_social_networks_routes
from routes.feedback import register_feedback_routes
from routes.staff import register_staff_routes
from routes.blog import register_blog_routes
from routes.about_company import register_about_company_routes
from routes.documents import register_documents_routes
from routes.admin import register_admin_routes

register_menu_routes(app, get_db, token_required)
register_year_name_routes(app, get_db, token_required)
register_contacts_routes(app, get_db, token_required)
register_social_networks_routes(app, get_db, token_required)
register_feedback_routes(app, get_db, token_required)
register_staff_routes(app, get_db, token_required)
register_blog_routes(app, get_db, token_required)
register_about_company_routes(app, get_db, token_required)
register_documents_routes(app, get_db, token_required)
register_admin_routes(app, get_db, token_required)

if __name__ == '__main__':
    app.run(debug=True)
