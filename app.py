from flask import Flask
from config import SECRET_KEY
from routes import routes

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
