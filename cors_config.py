from flask_cors import CORS
import os

def configure_cors(app):
    """Configure CORS settings for the application"""
    # Get allowed origins from environment or use defaults
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001,https://loyihaofis.uz').split(',')
    
    # Configure CORS for different endpoint groups
    
    # Public endpoints - less restrictive
    CORS(app, resources={
        r"/api/blog/*": {
            "origins": "*",  # Allow any origin for public content
            "methods": ["GET"],  # Only allow GET for public endpoints
        },
        r"/api/about-company/*": {
            "origins": "*",
            "methods": ["GET"],
        },
        r"/api/documents/*": {
            "origins": "*",
            "methods": ["GET"],
        }
    })
    
    # Authentication endpoints - need credentials support
    CORS(app, resources={
        r"/api/auth/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True  # Critical for auth requests with credentials
        }
    })
    
    # Admin/protected endpoints
    CORS(app, resources={
        r"/api/admin/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/api/menu/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/api/feedback/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/api/staff/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/api/restore/*": {
            "origins": allowed_origins,
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Default for any other API endpoints
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    print(f"CORS configured with allowed origins: {allowed_origins}")
