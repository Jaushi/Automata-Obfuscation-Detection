from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__) 
CORS(app)

from .routes.dictionary_routes import dictionary_bp
from .routes.translation_routes import translation_bp 

app.register_blueprint(dictionary_bp)
app.register_blueprint(translation_bp)


