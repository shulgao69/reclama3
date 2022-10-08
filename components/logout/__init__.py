# from flask_login import LoginManager
from flask_login import logout_user, login_required
from flask import Blueprint
from flask import redirect, session

# login_manager = LoginManager()


logout_blueprint = Blueprint('logout', __name__, template_folder='templates', static_folder='static')


@logout_blueprint.route('/')
@login_required
def render_logout():

    logout_user()

    print('session from logout=', session)
    # session.pop('user_id')
    # session.pop('user_email')
    return redirect('/')

