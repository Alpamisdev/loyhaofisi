from flask_cors import CORS
import os
import json

def load_cors_config():
    """Load CORS configuration from file or environment"""
    config_path = os.environ.get('CORS_CONFIG_PATH', 'cors_config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "default": {
                    "origins": ["http://localhost:3000"],
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"]
                },
                "public": {
                    "origins": "*",
                    "methods": ["GET"]
                }
            }
    except Exception as e:
        print(f"Error loading CORS configuration: {e}")
        # Fallback to allowing localhost only
        return {
            "default": {
                "origins": ["http://localhost:3000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        }

def configure_cors(app):
    """Configure CORS with dynamic settings"""
    cors_config = load_cors_config()
    
    # Apply public endpoints configuration
    if "public" in cors_config:
        public_config = cors_config["public"]
        CORS(app, resources={
            r"/api/blog/*": public_config,
            r"/api/about-company/*": public_config,
            r"/api/documents/*": public_config
        })
    
    # Apply admin endpoints configuration
    if "admin" in cors_config:
        admin_config = cors_config["admin"]
        CORS(app, resources={
            r"/api/auth/*": admin_config,
            r"/api/admin/*": admin_config
        })
    
    # Apply default configuration to all other routes
    default_config = cors_config.get("default", {"origins": "*"})
    CORS(app, resources={r"/api/*": default_config})
    
    print(f"CORS configured with dynamic settings")
