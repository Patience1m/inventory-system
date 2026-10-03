from flask import Flask
from config import config_by_name
from app.controller.inventory_controller import inventory_bp
from app.controller.lookup_controller import lookup_bp
from app.data import load_seed_data

def create_app(config_name = "default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    if app.config["SEED_DATA"]:
        load_seed_data()
    app.register_blueprint(inventory_bp)
    app.register_blueprint(lookup_bp)
    return app