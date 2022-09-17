
from flask import Blueprint, redirect, url_for
from flask import request, render_template
from RECL.models import Usluga, Link, Order, User, Role, roles_users, UploadFileMy
# from RECL.components.admin.forms import  DeleteForm, FormChoice1, PhotoFormAdmin, FormChoice2, DeleteFormFromMini, EditFormFromMini
# from RECL.models import db
# from RECL.__init__ import app, db, login_manager


# Этот блюпринт - формирует страницу notactive.html -
# если пользователь неактивен и его аккаунт заблокирован
notactive_blueprint = Blueprint('notactive_bp', __name__, template_folder='templates', static_folder='static')

@notactive_blueprint.route('/', methods=["GET", "POST"])
def notactive():
    print('vvvv')
    err = request.args.get('err')
    links_menu = Link.query.all()
    return render_template("notactive/notactive.html",
                           links_menu=links_menu,
                           err=err)