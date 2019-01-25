import functools

from flask import Blueprint

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')