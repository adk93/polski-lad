# Standard library imports

# Third party imports
from flask import Flask

# Local application imports
from kalkulator.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from kalkulator.main.routes import main

    app.register_blueprint(main)

    return app