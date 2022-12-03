from flask import Blueprint, redirect, url_for
from flask import request, render_template, session
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, IntegerField
from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
from RECL.components.price.forms import PriceForm

from RECL.components.test_form.forms import TestForm1, TestForm2, TestForm3
from RECL.models import Usluga, Link, Order, User, Role, roles_users, UploadFileMy, PriceTable
from flask_security import login_required, roles_required, roles_accepted
from RECL.models import db
from RECL.forms import LoginForm
import json


# Создаем блюпринт управления прайсами- создание, редактирование, копирование, удаление таблиц прайсов

test_form_blueprint = Blueprint('test_form_bp', __name__, template_folder='templates/test_form/', static_folder='static')

# страница
@test_form_blueprint.route('/bootstrap/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def bootstrap():

    return render_template('bootstrap.html')


# страница с параметрами заказа
@test_form_blueprint.route('/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def test_form():
    form1=TestForm1()
    form2=TestForm2()
    form3=TestForm3()

    return render_template('test_form.html',
                           form1=form1,
                           form2=form2,
                           form3=form3
                           )