import sqlite3
import click

from flask import current_app, g # 存储数据库连接
from flask.cli import with_appcontext


# 建立数据库连接
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# 关闭数据库连接
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# 初始化数据库
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """清除原有数据并建立新表"""
    init_db()
    click.echo('数据库初始化完成~')

# 在应用中注册
def init_app(app):
    app.teardown_appcontext(close_db)   # 返回响应后进行清理时调用
    app.cli.add_command(init_db_command)    # 添加命令