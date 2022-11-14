from flask import Blueprint
from flask_mail import Mail

bpp = Blueprint("bpp", __name__)
mail = Mail(None)