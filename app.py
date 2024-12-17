from flask import Flask
from eKom.views import views_blueprint

app = Flask(__name__)


# Импортируем и регистрируем Blueprint -> views.py
app.register_blueprint(views_blueprint, url_prefix='/')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")