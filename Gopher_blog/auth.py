import functools

from flask import Blueprint, flash, g, render_template, request, url_for, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 视图：注册
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # 检验合法性
        if not username:
            error = '请输入用户名\n'
        if not password:
            error = '请输入密码\n'
        if error is None:
            if db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
                ).fetchone() is not None:
                error += '用户名{}已存在\n'.format(username)

        # 添加用户信息至数据库
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)', (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

# 视图：登录
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # 输入检验
        if not username:
            error = '请输入用户名\n'
        if not password:
            error = '请输入密码\n'

        if error is None:
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()
            if not check_password_hash(user['password'], password):
                error = '密码错误'

        # 登录成功
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# 已登录用户信息
@bp.before_app_request # 在视图执行前执行，无论URL为何
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# 注销
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 装饰器：登录验证
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))

        return view(**kwargs)
    
    return wrapped_view