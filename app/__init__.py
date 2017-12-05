from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_bootstrap import Bootstrap
import os
SECRET_KEY = os.urandom(24)
app = Flask(__name__)
csrf = CSRFProtect(app)
Bootstrap(app)
app.config['SECRET_KEY'] = SECRET_KEY
from app import views