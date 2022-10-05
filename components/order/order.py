from flask import Blueprint, redirect, url_for
# from flask import request
from flask import render_template, session
# from flask_wtf import FlaskForm
# from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, IntegerField
# from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
# from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
# from RECL.components.price.forms import PriceForm
from RECL.components.order.forms import ApplicationForm
from RECL.models import CardUsluga, PriceTable
# from RECL.models import Usluga, Link, Order, User, Role, roles_users, UploadFileMy
# from RECL.models import OrderStatus
# from flask_security import login_required, roles_required, roles_accepted
# from RECL.models import db
# from RECL.forms import LoginForm
# import json

#  модуль используем для перевода строки в десятичное число
from decimal import Decimal

# getcontext().prec = 2    #  устанавливаем точность


# Создаем блюпринт управления заказами и корзиной
order_blueprint = Blueprint('order_bp', __name__, template_folder='templates/order/', static_folder='static')


# показать содержимое корзины
@order_blueprint.route('/cart/', methods=['GET', 'POST'])
def cart():
    session['order_request_add_to_cart'] = False
    session['order_request'] = {}
    cart = session.get('cart', [])
    # print('cart from cart=', cart)
    orders_requests = []
    for order_request in cart:
        dict = {}
        card_usluga = CardUsluga.query.filter(CardUsluga.id == order_request['card_usluga_id']).first()
        price = PriceTable.query.filter(PriceTable.id == order_request['price_id']).first()
        dict['card_usluga_arhive'] = card_usluga.arhive
        dict['card_usluga_active'] = card_usluga.active
        dict['price_arhive']=price.arhive
        dict['card_usluga'] = card_usluga
        dict['price'] = price
        dict['i'] = order_request['i']
        dict['j'] = order_request['j']
        dict['count'] = order_request['count']
        dict['order_request_sum'] = order_request['order_request_sum']
        orders_requests.append(dict)
    # print('orders_requests from cart=', orders_requests)

    return render_template('cart.html',
                           orders_requests=orders_requests
                           )


# добавить заявку на заказ в корзину
@order_blueprint.route('/order_request_add_to_cart/', methods=['GET', 'POST'])
def order_request_add_to_cart():
    session['order_request_add_to_cart'] = True
    order_request = session.get('order_request', {})
    # print("order_request, type(order_request)=", order_request, type(order_request))

    card_usluga_id = order_request['card_usluga_id']
    price_id = order_request['price_id']
    i = order_request['i']
    j = order_request['j']

    cart = session.get('cart', [])
    # print('order_request from add_to_cart=', order_request)
    # print('cart from add_to_cart=', cart)

    if cart == []:
        cart.append(order_request)
        # print('элемент добавлен в пустую корзину')

    else:
        session['order_request_in_cart'] = False
        if order_request['order_request_sum'] == -1:
            cart.append(order_request)
        else:
            for element in cart:
                if element['card_usluga_id'] == order_request['card_usluga_id'] and element['price_id'] == order_request['price_id'] and \
                        element['i'] == order_request['i'] and element['j'] == order_request['j']:
                    # print('element["card_usluga_id"]=', element['card_usluga_id'])
                    # print('order["card_usluga_id"]=', order_request['card_usluga_id'])
                    # print('element["i"]=', element['i'], 'order["i"]=', order_request['i'])
                    # print('element=', element)
                    # print('такой заказ есть в корзине. изменим кол-во и сумму заказа')

                    # Если перевести в плавающее число (как сначала хотела) то могут быть погрешности при расчетах
                    # y=float(price.value_table[i][j])
                    # см. https://pyprog.pro/python/py/nums/nums.html
                    # поэтому переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                    # type(y)= <class 'decimal.Decimal'>
                    # https://www.delftstack.com/howto/python/string-to-decimal-python/
                    price = PriceTable.query.filter(PriceTable.id == element['price_id']).first()
                    value = Decimal(price.value_table[element['i']][element['j']])
                    print('value=', value)
                    print('order_request["count"]=', order_request['count'])
                    print('element["count"]=', element['count'])
                    count = order_request['count'] + element['count']
                    print('count=', count)

                    # Сосчитаем сумму заказа и округлим до 2 знаков после запятой
                    element['order_request_sum'] = round(count * value, 2)
                    element['count'] = count

                    session['order_request_in_cart']=True
            if session.get('order_request_in_cart')==False:
                cart.append(order_request)

    session['cart'] = cart

    session['order_request'] = {}
    return redirect(url_for('order_bp.order_request',
                            card_usluga_id=card_usluga_id,
                            price_id=price_id,
                            i=i,
                            j=j
                            )
                    )


# удалить из корзины
@order_blueprint.route('/cart/delete/<int:number>', methods=['GET', 'POST'])
def delete_from_cart(number):
    print('number=', number)
    cart = session.get('cart', [])
    print('cart before delete=', cart)
    cart.pop(number)
    session['cart'] = cart
    cart = session.get('cart', [])
    print('cart after delete=', cart)
    print('session=', session)
    return redirect(url_for('order_bp.cart')
                    )


# заявка на заказ по ссылке из прайса на странице услуги
@order_blueprint.route('/order_request/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
def order_request(card_usluga_id, price_id, i, j):
    session['order_request'] = {}
    # print('session.get("count") from order_request=', session.get('count'))
    # Пока оставить для обнуления корзины(пока не напишу всю)
    # session['cart'] = []

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
        value = Decimal(price.value_table[i][j])

        # Сосчитаем сумму заказа и округлим до 2 знаков после запятой
        order_request_sum = round(session.get('count', 1) * value, 2)

    except:
        order_request_sum = -1

    # session['order_request_sum'] = order_request_sum
    order_request = {}
    order_request['card_usluga_id'] = card_usluga_id
    order_request['price_id'] = price_id
    order_request['i'] = i
    order_request['j'] = j
    order_request['count'] = session.get('count', 1)
    order_request['order_request_sum'] = order_request_sum
    session['order_request'] = order_request
    # print('session.get("order_request")=', session.get('order_request'), type(session.get('order_request')))

    # if form.validate_on_submit():
    #     user_phone = form.user_phone.data

    return render_template('order_request.html',
                           card_usluga=card_usluga,
                           price=price,
                           i=i,
                           j=j,
                           order_request_sum=order_request_sum,
                           form=form
                           )


# роут добавления кол-ва в заявке на заказ перед добавлением в корзину
@order_blueprint.route('/order_request_sum_plus/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
def order_request_sum_plus(card_usluga_id, price_id, i, j):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    form = ApplicationForm()
    session['count'] = session.get('count', 1) + 1

    return redirect(url_for('order_bp.order_request',
                            card_usluga_id=card_usluga.id,
                            price_id=price.id,
                            i=i,
                            j=j,
                            form=form
                            ))


# роут уменьшения кол-ва в заявке на заказ перед добавлением в корзину
@order_blueprint.route('/order_request_sum_minus/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
def order_request_sum_minus(card_usluga_id, price_id, i, j):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    form = ApplicationForm()

    if session.get('count') > 0:
        session['count'] = session.get('count', 1) - 1
    else:
        session['count'] = 0

    return redirect(url_for('order_bp.order_request',
                            card_usluga_id=card_usluga.id,
                            price_id=price.id,
                            i=i,
                            j=j,
                            form=form
                            )
                    )


# стр. с подтвержденной заявкой для авторизованного пользователя
@order_blueprint.route('/order_confirm/<int:user_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# @login_required
def order_confirm(user_id):
    session['sum'] = 1
    form = ApplicationForm()
    return render_template('order_confirm.html',
                           form=form
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
