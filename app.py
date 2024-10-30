from flask import Flask
from blueprints.stars.stars import stars_bp
from blueprints.planets.planets import planets_bp
from blueprints.auth.auth import auth_bp
from sys import exit

app = Flask(__name__)
app.config["SECRET_KEY"] = "thewitchofcolchis"
app.register_blueprint(stars_bp)
app.register_blueprint(planets_bp)
app.register_blueprint(auth_bp)


def shutdown(signal, frame):  # Facilitates graceful shutdowns.
    print("Shutting down...")
    exit(0)


if __name__ == "__main__":
    app.run(debug=True)
