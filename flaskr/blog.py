from flask import Blueprint, flash, g, request, redirect, url_for, render_template

from werkzeug.exceptions import abort

from .db import get_db
from .auth import login_required

bp = Blueprint('blog', __name__)

# 视图：索引
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        'FROM post p JOIN user u ON p.author_id = u.id'
        'ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)