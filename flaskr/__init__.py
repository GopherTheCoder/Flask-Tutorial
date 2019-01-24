import os

from flask import Flask

def create_app(test_config=None):
    # 创建并配置Flask实例
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # 重载实例配置 用于部署
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载传入的实例配置 用于测试
        app.config.from_mapping(test_config)

    # 创建实例目录
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 页面
    @app.route('/initiates') # 路由
    def hello():
        return 'Welcome to ANIMUS'

    return app
        