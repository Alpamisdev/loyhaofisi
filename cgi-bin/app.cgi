#!/usr/bin/env python3
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the necessary environment variables
os.environ['DATABASE_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')
os.environ['SECRET_KEY'] = 'your-secret-key-change-this'

# Import the Flask app
from app import app

# Create a CGI handler
from wsgiref.handlers import CGIHandler
CGIHandler().run(app)
