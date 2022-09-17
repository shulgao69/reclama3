
from flask import Blueprint
from flask import session, redirect, request, render_template, url_for, abort
from flask_admin import BaseView, expose
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from RECL.models import db
from RECL.models import Usluga, Link, Order, User, Role, roles_users
from RECL.forms import RegistrationForm


migrate = Migrate()

register_blueprint = Blueprint('register', __name__, template_folder='templates', static_folder='static')


# Регистрация
@register_blueprint.route('/', methods=["GET", "POST"])
def render_register():
    err = ""
    links_menu = Link.query.all()
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=username).first()

        if user:
            err = "Такой пользователь уже существует"
            # return render_template("login/login.html", form = form, err = err, links_menu=links_menu)
            return redirect(url_for('login.login', err=err))
        else:
            # print('form.validate_on_submit()=', form.validate_on_submit())
            user = User(email = username, password = generate_password_hash(password), active=True)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login.login'))
    return render_template("register/register.html",
                           form = form,
                           err=err,
                           links_menu=links_menu,
                            )



# *** Тоже работает (переделала короче см выше) - начало
# @register_blueprint.route('/', methods=["GET", "POST"])
# def render_register():
#     err = ""
#     links_menu = Link.query.all()
#     form = RegistrationForm()
#     if request.method == "POST":
#         # получаем данные
#         username = form.username.data
#         password = form.password.data
#         user = User.query.filter_by(email=username).first()
#         if user:
#             err = "Такой пользователь уже существует1"
#             # return render_template("login/login.html", form = form, err = err, links_menu=links_menu)
#             return redirect(url_for('login.login', err=err))
#         else:
#             print('form.validate_on_submit()=', form.validate_on_submit())
#             if form.validate_on_submit():
#                 # role = Role.query.filter_by(name='anonymous').first()
#                 user = User(email = username, password = generate_password_hash(password), active=True)
#                 db.session.add(user)
#                 # role.users.append(user)
#                 db.session.commit()
#                 # session['user_id']=user.id
#                 # session["active"] = True
#                 return redirect("/")
#             else:
#                 print('err1=', err)
#                 return render_template("register/register.html", form = form, err = err, links_menu=links_menu)
#     else:
#         return render_template("register/register.html", form = form, err=err, links_menu=links_menu,
#                                )

# *** Тоже работает (переделала короче см выше) - конец