from flask import Blueprint, redirect, url_for
from flask import request, render_template, session
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, IntegerField
from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
from RECL.components.price.forms import PriceForm
from RECL.components.order.forms import ApplicationForm
from RECL.models import Usluga, Link, Order, User, Role, CardUsluga, roles_users, UploadFileMy, PriceTable
# from RECL.models import OrderStatus
from flask_security import login_required, roles_required, roles_accepted
from RECL.models import db
from RECL.forms import LoginForm
import json

#  импортируем модуль используем для перевода сроки в десятичное число
from decimal import Decimal

# getcontext().prec = 2    #  устанавливаем точность


# Создаем блюпринт управления прайсами- создание, редактирование, копирование, удаление таблиц прайсов

order_blueprint = Blueprint('order_bp', __name__, template_folder='templates/order/', static_folder='static')


# заявка на заказ по ссылке из прайса на странице услуги
@order_blueprint.route('/order_request/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def order_request(card_usluga_id, price_id, i, j):
    # print("session.get('sum', 0)=", session.get('sum'))
    # print('session.get("card_usluga_add_to_cart", False)=', session.get('card_usluga_add_to_cart'))

    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    form = ApplicationForm()

    # Если строку прайса можно перевести в число (целое или десятичное число) сделаем это
    # И тогда можно считать сумму услуги, увеличивая кол-во
    # Если строка не число - то оставляем как есть и не даем возможности увеличивать кол-во
    try:
        # Если перевести в плавающее число (как сначала хотела) то могут быть погрешности при расчетах
        # y=float(price.value_table[i][j])
        # см. https://pyprog.pro/python/py/nums/nums.html
        # поэтому переведем в десятичное число с помощью модуля from decimal import Decimal!!!
        # type(y)= <class 'decimal.Decimal'>
        # https://www.delftstack.com/howto/python/string-to-decimal-python/
        y=Decimal(price.value_table[i][j])

        # Сосчитаем сумму заказа и округлим до 2 знаков после запятой
        order_sum=round(session.get('sum', 1)*y, 2)

    except:
        order_sum=-1

    if form.validate_on_submit():
        user_phone = form.user_phone.data

    return render_template('order_request.html',
                           card_usluga=card_usluga,
                           price=price,
                           i=i,
                           j=j,
                           order_sum=order_sum,
                           form=form
                           )


# добавить в корзину
@order_blueprint.route('/card_usluga_add_to_cart/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def card_usluga_add_to_cart(card_usluga_id, price_id, i, j):
    session['card_usluga_add_to_cart']=True
    return redirect(url_for('order_bp.order_request',
                            card_usluga_id=card_usluga_id,
                            price_id=price_id,
                            i=i, j=j
                           )
                    )


# страница с подтвержденной заявкой для авторизованного пользователя
@order_blueprint.route('/order_confirm/<int:user_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def order_confirm(user_id):
    session['sum']=1
    form = ApplicationForm()
    return render_template('order_confirm.html',
                           form=form
                           # punkt_menu=punkt_menu,
                           # category=category,
                           # name_price=name_price,
                           # name_foto=name_foto,
                           # price_0_0=price_0_0,
                           # price_0_j=price_0_j,
                           # price_i_0=price_i_0,
                           # price_i_j=price_i_j,
                           # price_i=price_i,
                           # price_0=price_0,
                           # foto_title=foto_title,
                           # form=form
                           )



# роут добавления количества в заказе
@order_blueprint.route('/order_sum_plus/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def order_sum_plus(card_usluga_id, price_id, i, j):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    form = ApplicationForm()
    session['sum']=session.get('sum', 1)+1

    return redirect(url_for('order_bp.order_request',
                           card_usluga_id=card_usluga.id,
                           price_id=price.id,
                           i=i,
                           j=j,
                           form=form
                            ))


# роут уменьшения количества в заказе
@order_blueprint.route('/order_sum_minus/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def order_sum_minus(card_usluga_id, price_id, i, j):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    form = ApplicationForm()

    if session.get('sum')>0:
        session['sum']=session.get('sum', 1)-1
    else:
        session['sum']=0

    return redirect(url_for('order_bp.order_request',
                           card_usluga_id=card_usluga.id,
                           price_id=price.id,
                           i=i,
                           j=j,
                           form=form
                            )
                    )




# class Status:
#     def __init__(self, name_status, status_weight, norma):
#         self.name_status=name_status
#         self.status_weight=status_weight
#         self.norma=norma
#         # self.start_date=start_date
#         # self.end_date=end_date
#
#     def status(self, start_date, end_date):
#         self.start_date=start_date
#         self.end_date=end_date
#         if end_date and start_date:
#             self.actual_time=end_date - start_date # фактическое время исполнения статуса
#         else:
#             self.actual_time=None
#
#         if self.norma and start_date:
#             self.plan_end_date=start_date + self.norma   # планируемое время исполнения статуса
#         else:
#             self.plan_end_date=None
#         if end_date and start_date and self.norma:
#             self.deviation=self.actual_time - self.norma   # отклонение от норматива
#         else:
#             self.deviation=None
#         return {'name_status': self.name_status, 'status_weight': self.status_weight, 'norma': self.norma, 'start_date': self.start_date,
#                 'end_date': self.end_date, 'actual_time': self.actual_time, 'plan_end_date': self.plan_end_date, 'deviation': self.deviation}


# proba=Status('статус1', 100, 20, 30, 60)
# proba=Status(name_status='статус1', status_weight=100, norma=20)
# print('proba=', proba)
# print('proba.status(start_date=200, end_date=''=', proba.status(start_date='', end_date=''))
# print('proba.deviation=', proba.deviation)