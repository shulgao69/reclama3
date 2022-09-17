from flask import Blueprint

# Без этого блюпринта и регистрации(c предварительным импортом) в главном __init__
# админка не работает!!!!! Не удалять!!!
# см https://ploshadka.net/flask-delaem-avtorizaciju-na-sajjte/

admin_blueprint = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

