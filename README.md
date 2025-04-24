# Flask Website Backend

This is a Flask-based REST API backend for a website with SQLite database.

## Features

- RESTful API with Flask
- SQLite database
- JWT Authentication for admin area
- Swagger documentation
- Complete CRUD operations for all entities

## New Features

### Feedback Theme Field

The feedback form now includes a 'theme' field that allows users to specify the topic or category of their feedback. This helps in organizing and filtering feedback messages.

### Soft Delete Implementation

All delete operations now implement a "soft delete" approach:

- Instead of permanently removing records from the database, they are marked as deleted using an `is_deleted` flag.
- By default, GET endpoints only return active (non-deleted) records.
- You can include soft-deleted records in GET requests by adding the `include_deleted=true` query parameter.
- Administrators can restore soft-deleted items using the `/api/restore/{table_name}/{item_id}` endpoint.

This approach maintains data integrity and allows for potential recovery or analysis of deleted items.

#### Example Usage:

1. To get all menu items including deleted ones:
   \`\`\`
   GET /api/menu?include_deleted=true
   \`\`\`

2. To restore a deleted blog post:
   \`\`\`
   POST /api/restore/blog_items/123
   \`\`\`
   (Requires admin authentication)

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository or download the files

2. Install required packages:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

3. Initialize the database:
   \`\`\`
   python init_db.py
   \`\`\`

4. Run the application:
   \`\`\`
   python app.py
   \`\`\`

The server will start at http://127.0.0.1:5000 by default.

## API Documentation

When the application is running, you can access the Swagger documentation at:
\`\`\`
http://127.0.0.1:5000/api/docs/
\`\`\`

This provides interactive documentation for all available endpoints.

## Default Admin User

A default admin user is created when you initialize the database:
- Username: admin
- Password: admin123

**IMPORTANT:** Change this password after first login!

## Deployment to Shared Hosting

### 1. Preparing your files

Make sure all files are organized in your project directory:
- app.py (main application)
- wsgi.py (WSGI entry point)
- init_db.py (database initialization script)
- routes/ (directory containing all route files)
- requirements.txt (list of dependencies)
- database.db (your SQLite database after running init_db.py)

### 2. Uploading to your shared hosting

Most shared hosting providers support SFTP or FTP uploads. Use an FTP client like FileZilla to upload all your project files to your hosting account.

### 3. Setting up Python environment

Many shared hosts have control panels like cPanel that provide Python app setup options. In cPanel, you might need to:

1. Go to "Setup Python App"
2. Create a new application with the following settings:
   - Python version: 3.8 or newer
   - Application root: Path to your uploaded files
   - Application URL: Your domain or subdomain
   - Application startup file: wsgi.py
   - Application Entry point: app (this is the Flask app instance in wsgi.py)

4. Set up environment variables if needed
   - SECRET_KEY: A secret key for your application
   - DATABASE_PATH: Path to your SQLite database

### 4. Installing dependencies

Some hosts provide a way to install pip packages through the control panel. Otherwise, you may need to use SSH:

\`\`\`
cd /path/to/your/app
pip install -r requirements.txt
\`\`\`

### 5. Initialize the database

Run the initialization script once to set up the database:

\`\`\`
python init_db.py
\`\`\`

### 6. Configure web server

Depending on your hosting provider, you might need to configure Apache or Nginx to work with your Flask application. Most shared hosts will handle this automatically when you set up the Python app.

For Apache, a typical configuration might be:

\`\`\`
<VirtualHost *:80>
    ServerName yourdomain.com
    
    WSGIDaemonProcess flaskapp python-home=/path/to/venv python-path=/path/to/app
    WSGIProcessGroup flaskapp
    WSGIScriptAlias / /path/to/app/wsgi.py
    
    <Directory /path/to/app>
        Require all granted
    </Directory>
</VirtualHost>
\`\`\`

## Security Considerations

1. Change the default admin password immediately after deployment
2. Set a strong SECRET_KEY environment variable for JWT
3. Protect your database file using proper file permissions
4. Consider adding rate limiting for API endpoints

## Troubleshooting

- **500 Internal Server Error**: Check the server logs for details. Common issues include:
  - Missing dependencies
  - Incorrect file permissions
  - Database connection issues

- **Database errors**: Make sure the database file exists and is writable
  - You might need to run `python init_db.py` again
  - Check file permissions on the database file

- **Authentication issues**: Ensure the JWT secret key is properly set
  - Check that the SECRET_KEY environment variable is set correctly

## License

This project is open source and available under the MIT License.
# loyhaofisi
