from flask import Flask
from database import init_db
from routes import routes

app = Flask(__name__)
init_db()

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
