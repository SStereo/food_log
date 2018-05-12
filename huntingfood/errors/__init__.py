from flask import Blueprint

bp = Blueprint('errors', __name__)

from huntingfood.errors import handlers
