# Import Flask
from flask import Flask

# Create an instance of Flask
app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def home():
    return "Server is running"

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
