from flask_wtf.csrf import CSRFProtect
from flask import Flask
import os
SECRET_KEY = os.urandom(24)
app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = SECRET_KEY
from app import views