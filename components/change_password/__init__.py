from flask_login import LoginManager, current_user
# import hashlib
from flask_login import UserMixin
from flask_login import current_user, login_user, logout_user, login_required
from flask import Blueprint
from flask import session, redirect, request, render_template, url_for, abort
from flask_admin import BaseView, expose
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash

from RECL.models import db
from RECL.models import Usluga, Link, Order, User, Role, roles_users
from RECL.forms import ChangePasswordForm

migrate = Migrate()
login_manager = LoginManager()

change_password_blueprint = Blueprint('change_password', __name__, template_folder='templates', static_folder='static')

# Поменять пароль
@change_password_blueprint.route("/", methods=["GET", "POST"])
def change_password():
    err = ''
    links_menu = Link.query.all()
    form = ChangePasswordForm()
    # if request.method == "POST":
    #     if form.validate_on_submit():
    #         user = User.query.filter_by(id=session.get("user_id")).first()
    #         user.password_hash = generate_password_hash(form.password.data)
    #         db.session.add(user)
    #         db.session.commit()
    #         return redirect("/login/")
    return render_template("change_password/change_password.html", form=form, err=err, links_menu=links_menu)