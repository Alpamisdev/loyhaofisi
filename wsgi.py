from app import app as application

# This is for WSGI servers like Passenger
# The variable must be named 'application'

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
