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

# 视图：创建
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title, body = request.form['title'], request.form['body']
        error = None

        if not title:
            error = '请输入标题'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# 视图：更新
@bp.route('/<int:id>/update', methodds=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method ==  'POST':
        title, body = request.form['title'], request.form['body']
        error = None

        if not title:
            error = '请输入标题'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title=?, body=?'
                'WHERE id=?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/update.html', post=post)

# 通过id获取post
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        'FROM post p JOIN user u ON p.author_id = u.id'
        'WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "文章ID{0}不存在".format('id'))

    if check_author and post['author_id'] == g.user['id']:
        abort(403)

    return post

# 视图：删除
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))