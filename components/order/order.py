from flask import Blueprint, redirect, url_for, jsonify
from flask import render_template, session, current_app, request
from flask_security import current_user
from flask_security import login_required
# from flask_wtf import FlaskForm
# from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, IntegerField
# from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
# from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
# from RECL.components.price.forms import PriceForm
from RECL.components.order.forms import ApplicationForm, ChooseRoleAndPersonForm
from RECL.models import CardUsluga, PriceTable, Order, Role, User, roles_users,\
    StatusOrder, StatusCard, StatusIntermediate
from RECL.models import db
# from RECL.models import Usluga, Link, Order, User, Role, roles_users, UploadFileMy
# from RECL.models import OrderStatus
# from flask_security import login_required, roles_required, roles_accepted
# from RECL.models import db
# from RECL.forms import LoginForm
# import json

import datetime

#  модуль используем для перевода строки в десятичное число
from decimal import Decimal

# getcontext().prec = 2    #  устанавливаем точность
from operator import itemgetter, attrgetter

# Создаем блюпринт управления заказами и корзиной
order_blueprint = Blueprint('order_bp', __name__, template_folder='templates/order/', static_folder='static')

# Очистить сессию - временная потом удалить
@order_blueprint.route('/session_clear/', methods=['GET', 'POST'])
def render_session_clear():
    # Параметр next
    # см. https://habr.com/ru/post/346346/#:~:text=Flask-Login%20отслеживает%20зарегистрированного%20пользователя%2C%20сохраняя,пользователю%2C%20который%20подключается%20к%20приложению
    # https://proproprogs.ru/flask/uluchshenie-processa-avtorizacii-flask-login
    next = request.args.get('next')
    # print('next =', next)
    # print('request.args =', request.args)

    session.clear()
    return redirect(request.args.get("next") or url_for('render_main'))


# Создать заказ
@order_blueprint.route('/create_order/', methods=['GET', 'POST'])
@login_required
def create_order():
    orders=Order.query.all()
    return render_template('show_orders.html',
                           orders=orders)

# роут для выбора пользователя по выбору в роли при назначении ответственного
# на странице show_orders (см скрипт в конце стр show_orders.html)
@order_blueprint.route('/choice_users/', methods=['GET', 'POST'])
def choice_users():
    role = request.args.get('role', '01', type=str)
    role=Role.query.filter(Role.id==int(role)).first()
    # userschoice = [(user.id, user.user_last_name+' '+user.user_first_name+' '+user.user_middle_name) for user in
    #                role.users ]
    userschoice = []
    for user in role.users:

        if user.user_last_name and user.user_first_name and user.user_middle_name:
            d=(user.id, user.user_last_name+' '+user.user_first_name+' '+user.user_middle_name)

        else:
            d=(user.id, user.email)
        userschoice.append(d)

    print(userschoice, type(userschoice[0]))
    return jsonify(userschoice)

# Показать все заказы сайта
@order_blueprint.route('/show_orders/', methods=['GET', 'POST'])
@login_required
def show_orders():
    flag_new_orders = session.get('new_orders', True)
    flag_all_orders = session.get('all_orders', True)
    flag_end_orders = session.get('end_orders', True)
    flag_work_orders = session.get('work_orders', True)
    flag_cancel_orders = session.get('cancel_orders', True)
    statuses_orders = StatusOrder.query.all()

    # Новые поступившие заказы (у них еще не определена роль ответственного)
    new_orders = Order.query.filter(Order.manager_role == None).order_by(Order.date_create.desc()).all()

    # Персонал исполнителя(все у кого определены роли)
    staff_user=User.query.filter(User.roles != None).all()

    # Заказы, у которых назначен исполнитель (роль) и отсортированные по дате(новые в начале)
    orders=Order.query.filter(db.and_(Order.manager_role != None,  Order.date_end ==None)).order_by(
        Order.date_create.desc()).all()
    # Задаем актуальное дату и время без секунд и миллисекунд
    # (используем для подсчета времени прогресса заказа)
    actual_time=datetime.datetime.now().replace(second=0, microsecond=0)

    # Задаем временной интервал равный 0
    # (используем для подсчета времени прогресса заказа)
    new_timedelta = datetime.timedelta(0)

    # Заказы, закрытые
    orders_end = Order.query.filter(db.and_(Order.manager_role != None, Order.date_end != None)).order_by(
        Order.date_create.desc()).all()

    # Хочу по умолчанию задать в SelectField определенные значения из списка
    # (чтобы по умолчанию в поле стояло определенное значение из списка)
    # https://translated.turbopages.org/proxy_u/en-ru.ru.b7ea63a3-637db9a6-891bac08-74722d776562 / https/stackoverflow.com/questions/12099741/how-do-you-set-a-default-value-for-a-wtforms-selectfield
    # Можно задать так (где цифры - это id из таблиу Role  и User соответственно)
    # form = ChooseRoleAndPersonForm(manager_role=6, manager_person=4)
    # но если этих id нет будет ошибка. Поэтому делаю проверку и условие:

    try:
        # Где project_manager - роль по умолчанию(чтобы не выбирать)
        role=Role.query.filter(Role.name=='project_manager').first()
        # пользователь первый в списке с такой ролью(ноль тк может быть один)
        # user=role.users[0]
        # form = ChooseRoleAndPersonForm(manager_role=role.id, manager_person=user.id)
        form = ChooseRoleAndPersonForm(manager_role=role.id)
    except:
        form = ChooseRoleAndPersonForm()
    # Этот вариант(выше) плох тем что задаю роль по умолчанию в самом коде

    # Все роли исполнителя
    roles = Role.query.order_by('name').all()


    # Задаем способ заполнения выпадающих списков ролей и персонала
    form.manager_role.choices = [(manager_role.id, manager_role.name) for manager_role in
                                 roles]
    form.manager_person.choices = [(manager_person.id, manager_person.email) for manager_person in
                                    User.query.all()]

    if form.validate_on_submit():
        # Получаем данные из формы
        manager_role = form.manager_role.data
        manager_person = form.manager_person.data
        order = form.order.data
        # Заполяем данными заказ
        # int тк type(manager_role, order, manager_person) - строки
        order=Order.query.filter(Order.id==int(order)).first()
        order.manager_role_id = int(manager_role)
        order.manager_person_id = int(manager_person)
        # Заносим в базу
        db.session.commit()
        return redirect(url_for('order_bp.show_orders'))

    return render_template('show_orders.html',
                           form=form,
                           roles=roles,
                           staff_user=staff_user,
                           new_orders=new_orders,
                           orders=orders,
                           orders_end=orders_end,
                           statuses_orders=statuses_orders,
                           flag_new_orders=flag_new_orders,
                           flag_all_orders=flag_all_orders,
                           flag_end_orders=flag_end_orders,
                           flag_work_orders=flag_work_orders,
                           flag_cancel_orders=flag_cancel_orders,
                           actual_time=actual_time,
                           new_timedelta=new_timedelta
                           )

# Поменять флаг для показа только новых заказов - начало
@order_blueprint.route('/show_new_orders/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_new_orders():
    session['new_orders']=True
    session['all_orders'] = False
    session['end_orders'] = False
    session['work_orders'] = False
    session['cancel_orders'] = False
    return redirect(url_for('order_bp.show_orders'))
# Поменять флаг для показа только новых заказов - конец

# Поменять флаг для показа всех заказов - начало
@order_blueprint.route('/show_all_orders/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_all_orders():
    session['new_orders']=False
    session['all_orders'] = True
    session['end_orders'] = False
    session['work_orders'] = False
    session['cancel_orders'] = False
    return redirect(url_for('order_bp.show_orders'))
# Поменять флаг для показа всех - конец

# Поменять флаг для показа только новых заказов - начало
@order_blueprint.route('/show_work_orders/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_work_orders():
    session['new_orders']=False
    session['all_orders'] = False
    session['end_orders'] = False
    session['work_orders'] = True
    session['cancel_orders'] = False
    return redirect(url_for('order_bp.show_orders'))
# Поменять флаг для показа только новых заказов - конец

# Поменять флаг для показа только закрытых заказов - начало
@order_blueprint.route('/show_end_orders/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_end_orders():
    session['new_orders']=False
    session['all_orders'] = False
    session['end_orders'] = True
    session['work_orders'] = False
    session['cancel_orders'] = False
    return redirect(url_for('order_bp.show_orders'))
# Поменять флаг для показа только закрытых заказов - конец


# Оформить (разместить) заказ из корзины
@order_blueprint.route('/place_order/', methods=['GET', 'POST'])
@login_required
def place_order():
    print('session=', session)
    cart=session.get('cart', [])
    print('type(cart)=', type(cart))
    print('cart=', cart)
    print('jsonify(cart)=', jsonify(cart), 'type(jsonify(cart))=', type(jsonify(cart)))
    return render_template('place_order.html')


# заявка на заказ по ссылке из прайса на странице услуги
@order_blueprint.route('/order_request/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
def order_request(card_usluga_id, price_id, i, j):
    session['order_request'] = {}
    print('card_usluga_id=', card_usluga_id, 'price_id=', price_id)
    # print('session.get("count") from order_request=', session.get('count'))

    # Пока оставить для обнуления корзины(пока не напишу всю)
    # session['cart'] = []

    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    print('card_usluga=', card_usluga, 'price=', price)
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
        print('value from try=', value)
        # Сосчитаем сумму заказа и округлим до 2 знаков после запятой
        order_request_sum = round(session.get('count', 1) * value, 2)
        print('order_request_sum from try=', order_request_sum)

    except:
        order_request_sum = -1
        print('order_request_sum from except=', order_request_sum)

    order_request = {}
    order_request['card_usluga_id'] = card_usluga_id
    order_request['price_id'] = price_id
    order_request['i'] = i
    order_request['j'] = j
    order_request['count'] = session.get('count', 1)
    order_request['order_request_sum'] = order_request_sum
    session['order_request'] = order_request
    print("session.get('order_request') from order_request=", session.get('order_request'))
    print("session from order_request=", session)
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


# добавить заявку на заказ в корзину
@order_blueprint.route('/order_request_add_to_cart/', methods=['GET', 'POST'])
def order_request_add_to_cart():
    # Очистить все!!! данные сессии - пока оставить
    # session.clear()
    # print('session before add=', session)
    session['order_request_add_to_cart'] = True
    order_request = session.get('order_request', {})
    # print("session.get('order_request') from order_request_add_to_car=", session.get('order_request'))
    print("session from order_request_add_to_cart-before-1=", session)

    card_usluga_id = order_request['card_usluga_id']
    price_id = order_request['price_id']
    i = order_request['i']
    j = order_request['j']

    carts_users=session.get('carts_users', [])

    if current_user.is_anonymous:
        user_id='anonymous'
    else:
        user_id=current_user.id
    session['user_id']=user_id

    # Список user_id в списке корзин пользователей в рамках одной сессии
    # (состоит из id либо 'anonymous', если анонимная корзина)
    # Этот список используем для показа изображения пустой корзины в base.html
    # его не удалять!!! Обновляется при добавлении корзины нового пользователя
    # и при слиянии анонимной корзины при входе нового пользователя в login_blueprint
    list_users_id_in_carts_users=[]
    for cart_user in carts_users:
        list_users_id_in_carts_users.append(cart_user['user_id'])

    cart_new_user = {}
    if user_id not in list_users_id_in_carts_users:
        cart_new_user['user_id'] = user_id
        cart_new_user['cart']=[]
        cart_new_user['cart'].append(order_request)
        carts_users.append(cart_new_user)
        # добавляем нового пользователя в список id
        list_users_id_in_carts_users.append(cart_new_user['user_id'])
        session['list_users_id_in_carts_users'] = list_users_id_in_carts_users
    else:
        for cart_user in carts_users:
            if cart_user['user_id'] == user_id:
                if order_request['order_request_sum'] == -1:
                    cart_user['cart'].append(order_request)
                else:
                    session['order_request_in_cart'] = False
                    for element in cart_user['cart']:
                        if element['card_usluga_id'] == order_request['card_usluga_id'] and \
                                element['price_id'] == order_request['price_id'] and \
                                element['i'] == order_request['i'] and element['j'] == order_request['j']:
                            # Если перевести в плавающее число (как сначала хотела) то могут быть погрешности при расчетах
                            # y=float(price.value_table[i][j])
                            # см. https://pyprog.pro/python/py/nums/nums.html
                            # поэтому переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                            # type(y)= <class 'decimal.Decimal'>
                            # https://www.delftstack.com/howto/python/string-to-decimal-python/
                            price = PriceTable.query.filter(PriceTable.id == element['price_id']).first()
                            print('price=', price)
                            value = Decimal(price.value_table[element['i']][element['j']])
                            count = order_request['count'] + element['count']

                            # Сосчитаем сумму заказа и округлим до 2 знаков после запятой
                            element['order_request_sum'] = round(count * value, 2)
                            element['count'] = count
                            session['order_request_in_cart'] = True

                    if session.get('order_request_in_cart') == False:
                        cart_user['cart'].append(order_request)

    session['carts_users'] = carts_users
    # print('session.get("carts_users") from order_request_add_to_cart=', session.get('carts_users'))
    print('session from order_request_add_to_cart-after-2=', session)
    session['order_request'] = {}
    return redirect(url_for('order_bp.order_request',
                            card_usluga_id=card_usluga_id,
                            price_id=price_id,
                            i=i,
                            j=j
                            )
                    )


# показать содержимое корзины
@order_blueprint.route('/cart/', methods=['GET', 'POST'])
def cart():
    # Сбросим сессию флага сигнализирующего о том что заявка на заказ добавлена в корзину
    session['order_request_add_to_cart'] = False
    # Сбросим сессию order_request, содержащую сведения о заявке на заказ(со стр.карточки услуги с прайсом)
    session['order_request'] = {}

    # print('session.get("cart", []) before-1=', session.get('cart', []))
    # Создадим пустую сессию для корзины пользователя(анонимного или авторизованного)
    session['cart']=[]
    # В рамках одной сессии может быть несколько пользователей (например с одного ПК
    # в одном браузере могут входить разные пользователи либо анонимные(неавторизованные))
    # Их корзины разные!
    # orders_requests - Список словарей карточек услуг в корзине конкретного пользователя
    # (анонимного или авторизованного)
    orders_requests = []
    # Список корзин всех пользователей в рамках одной сессии
    carts_users = session.get('carts_users', [])
    # print('session before-1=', session)

    # Если пользователь авторизован (например его id=1), то в словаре сессии
    # автоматически появляется запись '_user_id': '1'. Если не авторизован - тогда такой записи нет
    # Но мы хотим впоследствии создать словарь, включающий и анонимную корзину, поэтому
    # создадим user_id, кот. == current_user.id  или 'anonymous' если пользователь не авторизовался
    # При авторизации анонимная корзина сливается с корзиной авторизовавшегося пользователя(см login)
    # После регистрации нового пользователя вход автоматически не происходит, необходимо
    # авторизоваться поэтому анонимная корзина также сливается с авторизовавшимся пользователем
    if current_user.is_anonymous:
        user_id='anonymous'
    else:
        user_id=current_user.id
    # print('user_id=', user_id)
    # Временный словарь, который добавляется в список orders_requests
    dict_cart_user = {}
    # Общая сумма заказа (кроме тех карточек услуг, у которых:
    # 1) ячейки - строки!
    # 2) после добавления в корзину прайс или карточка услуги стали не активны,
    # попали в архив или прайс был откреплен от карточки услуги
    # (те услуга стала не актуальна!))
    sum_total=0
    # Список содержимого тех ячеек заказа, у кот.
    # 1) ячейки - строки и сумма заказа не может быть посчитана!
    # и прайс или карточка услуги активны и не в архиве и
    # прайс прикреплен к карточке услуги (те услуга еще актуальна!))
    list_total_without_sum_total=[]

    # Если список корзин всех пользователей в рамках одной сессии не пуст
    if carts_users != []:
        # print('carts_users != []', "True")
        # print('carts_users =', carts_users)
        # Перебираем все корзины
        for cart_user in carts_users:
            # print('cart_user', cart_user)
            # Выбираем корзину авторизованного пользователя или анонимную
            if cart_user['user_id']==user_id:
                # если его корзина не пуста
                if cart_user['cart'] !=[]:
                    # print('cart_user["cart"]=', cart_user['cart'])
                    # Создаем сессию корзины конкретного пользователя(анонимного или авторизованного)
                    # Используем ее для удаления заявки на заказ карточки услуги из корзины конкретного
                    # пользователя, (список словарей orders_requests мы не можем передать через сессию,
                    # тк там есть объекты запроса а не строки)
                    # print('session.get("cart", []) before-2=', session.get('cart', []))
                    session['cart']=cart_user['cart']
                    # print('session.get("cart", []) after-1=', session.get('cart', []))
                    # Перебираем все заказы в корзине пользователя
                    for order_request in cart_user['cart']:
                        card_usluga = CardUsluga.query.filter(CardUsluga.id == order_request['card_usluga_id']).first()
                        price = PriceTable.query.filter(PriceTable.id == order_request['price_id']).first()
                        # Если карта и прайс не удалены из базы данных (или запрос не дает ошибку?)
                        # за время хранения в корзине включаем их в показ в корзине
                        # В принципе эту проверку можно удалить т.к. удаление из корзин пользователей
                        # в случае удаления прайса или карточки услуг  реализованы в price.py и card_usluga.py
                        # но оставим на случай ошибки при запросе из базы?
                        if card_usluga and price:
                            price_in_card_usluga = False
                            # Проверяем не удален (откреплен) ли прайс из карточки услуги
                            # (Сам прайс при удалении из карточки услуги не удаляется, а открепляется)
                            # Если нет price_in_card_usluga=True)
                            if card_usluga.prices:
                                # Если назвать не price_card_usluga  а price - то в
                                # словарь записывался другой прайс и возникала ошибка при отображении в
                                # корзине. Видимо пересечение имен запроса price из базы (выше) и перебора
                                # данных(ниже) Не поняла почему!
                                for price_card_usluga in card_usluga.prices:
                                    if price_card_usluga.id==order_request['price_id']:
                                        price_in_card_usluga=True
                            # print('price_in_card_usluga=', price_in_card_usluga)
                            # Создаем словарь корзины юзера
                            dict_cart_user['price_in_card_usluga'] = price_in_card_usluga
                            dict_cart_user['card_usluga_arhive'] = card_usluga.arhive
                            dict_cart_user['card_usluga_active'] = card_usluga.active
                            dict_cart_user['price_arhive'] = price.arhive
                            dict_cart_user['price_active'] = price.active
                            dict_cart_user['card_usluga'] = card_usluga
                            dict_cart_user['price'] = price
                            # print('price=', price, 'dict_cart_user["price"]=', dict_cart_user['price'])
                            dict_cart_user['i'] = order_request['i']
                            dict_cart_user['j'] = order_request['j']
                            # Проверяем выполнены ли одновременно 5 условий:
                            # 1)прайс не удален из данной карточки 2)карточка не в архиве 3)карточка активна и
                            # 4)прайс не в архиве 5) прайс активен
                            actual_offer=False
                            if price_in_card_usluga == True and card_usluga.arhive == False and \
                                    card_usluga.active == True and price.arhive == False and price.active == True:
                                actual_offer = True
                            dict_cart_user['actual_offer'] = actual_offer
                            # print('dict_cart_user=', dict_cart_user)

                            # *** Этот перевод делаем потому, что при передаче через сессию (видимо?)
                            # класс decimal превращается в строку и поэтому в корзине невозможно
                            # провести сортировку по этому параметру
                            if order_request['order_request_sum'] !=-1:
                                try:
                                    # Переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                                    # https://www.delftstack.com/howto/python/string-to-decimal-python/
                                    # order_request_sum = Decimal(order_request['order_request_sum'])
                                    value_i_j=Decimal(price.value_table[order_request['i']][order_request['j']])
                                    order_request_sum=value_i_j*order_request['count']
                                    dict_cart_user['order_request_sum'] = order_request_sum
                                    dict_cart_user['count'] = order_request['count']
                                    dict_cart_user['value_i_j'] = value_i_j
                                    # Сумму считаем только если actual_offer = True те выполнены 5 условий:
                                    # 1)прайс не удален из данной карточки 2)карточка не в архиве 3)карточка активна и
                                    # 4)прайс не в архиве 5) прайс активен
                                    if actual_offer:
                                        sum_total = sum_total+order_request_sum
                                except:
                                    order_request['order_request_sum'] = -1
                                    dict_cart_user['order_request_sum']=order_request['order_request_sum']
                                    order_request['count']=1
                                    dict_cart_user['count']=order_request['count']
                                    dict_cart_user['value_i_j'] = price.value_table[order_request['i']][order_request['j']]
                                    # В список добавляем только если actual_offer = True те выполнены 5 условий:
                                    # 1)прайс не удален из данной карточки 2)карточка не в архиве 3)карточка активна и
                                    # 4)прайс не в архиве 5) прайс активен
                                    if actual_offer:
                                        list_total_without_sum_total.append(price.value_table[order_request['i']][order_request['j']])
                            # ***
                            else:
                                try:
                                    # Переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                                    # https://www.delftstack.com/howto/python/string-to-decimal-python/
                                    value_i_j = Decimal(price.value_table[order_request['i']][order_request['j']])
                                    order_request['order_request_sum']=value_i_j
                                    dict_cart_user['order_request_sum'] = order_request['order_request_sum']
                                    order_request['count'] = 1
                                    dict_cart_user['count'] = order_request['count']
                                    dict_cart_user['value_i_j'] = value_i_j
                                    # Сумму считаем только если actual_offer = True те выполнены 5 условий:
                                    # 1)прайс не удален из данной карточки 2)карточка не в архиве 3)карточка активна и
                                    # 4)прайс не в архиве 5) прайс активен
                                    if actual_offer:
                                        sum_total = sum_total + value_i_j
                                except:
                                    dict_cart_user['count'] = order_request['count']
                                    dict_cart_user['order_request_sum'] = order_request['order_request_sum']
                                    dict_cart_user['value_i_j']=price.value_table[order_request['i']][order_request['j']]
                                    # В список добавляем только если actual_offer = True те выполнены 5 условий:
                                    # 1)прайс не удален из данной карточки 2)карточка не в архиве 3)карточка активна и
                                    # 4)прайс не в архиве 5) прайс активен
                                    if actual_offer:
                                        list_total_without_sum_total.append(
                                        price.value_table[order_request['i']][order_request['j']])

                            orders_requests.append(dict_cart_user)
                            dict_cart_user = {}
                            session['cart'] = cart_user['cart']
                            # print('session.get("cart", []) after-2=', session.get('cart', []))

                        # Если карта или прайс удалены из базы данных исключаем их
                        # из показа в корзине
                        # else:
                        #     message='Карта или прайс были удалены. Заказ не возможен.'
                        #     print('message=', message)
                        #     # cart_user['cart'].remove(order_request)

        session['carts_users']=carts_users

    # Сортировка в корзине по списку(те по порядку добавления в корзину)-так и оставить!
    # Попыталась сортировать по сумме максим - Не получилось ( и не надо)
    # Сортировка словаря по order_request_sum, при этом если цена была класс строка
    # то order_request_sum ==  -1
    # orders_requests=sorted(orders_requests, key= lambda x: x['order_request_sum'], reverse=True)
    print('session from cart after-2=', session)
    # print('orders_requests from cart 2=', orders_requests)
    return render_template('cart.html',
                           orders_requests=orders_requests,
                           sum_total=sum_total,
                           list_total_without_sum_total=list_total_without_sum_total
                           )


# уменьшить внутри корзины
@order_blueprint.route('/cart_sum_minus/<int:number>/', methods=['GET', 'POST'])
def cart_sum_minus(number):
    # number - это порядковый номер элемента списка словарей (это словарь) заявки на заказ
    # из корзины конкретного пользователя
    # print('number=', number)
    carts_users = session.get('carts_users', [])
    if current_user.is_anonymous:
        user_id = 'anonymous'
    else:
        user_id = current_user.id

    if carts_users != []:
        for cart_user in carts_users:
            if cart_user['user_id'] == user_id:
                print('cart_user=', cart_user)
                print('number=', number)
                price = PriceTable.query.filter(PriceTable.id == cart_user['cart'][number]['price_id']).first()
                if cart_user['cart'][number]['count']>0:
                    count=cart_user['cart'][number]['count']-1
                else:
                    count=0
                cart_user['cart'][number]['count']=count
                # Если перевести в плавающее число (как сначала хотела) то могут быть погрешности при расчетах
                # y=float(price.value_table[i][j])
                # см. https://pyprog.pro/python/py/nums/nums.html
                # поэтому переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                # type(y)= <class 'decimal.Decimal'>
                # https://www.delftstack.com/howto/python/string-to-decimal-python/
                print('price.value=', price.value_table[cart_user['cart'][number]['i']][cart_user['cart'][number]['j']])
                value = Decimal(price.value_table[cart_user['cart'][number]['i']][cart_user['cart'][number]['j']])

                # Сосчитаем сумму заказа и округлим до 2 знаков после запятой
                order_request_sum = round(count * value, 2)

                cart_user['cart'][number]['order_request_sum'] = order_request_sum

    session['carts_users'] = carts_users
    print('session=', session)
    return redirect(url_for('order_bp.cart')
                    )


# добавить внутри корзины
@order_blueprint.route('/cart_sum_plus/<int:number>/', methods=['GET', 'POST'])
def cart_sum_plus(number):
    # number - это порядковый номер элемента списка словарей (это словарь) заявки на заказ
    # из корзины конкретного пользователя
    # print('number=', number)
    carts_users = session.get('carts_users', [])
    if current_user.is_anonymous:
        user_id = 'anonymous'
    else:
        user_id = current_user.id

    if carts_users != []:
        for cart_user in carts_users:
            if cart_user['user_id'] == user_id:
                price = PriceTable.query.filter(PriceTable.id == cart_user['cart'][number]['price_id']).first()
                count=cart_user['cart'][number]['count']+1
                cart_user['cart'][number]['count']=count
                # Если перевести в плавающее число (как сначала хотела) то могут быть погрешности при расчетах
                # y=float(price.value_table[i][j])
                # см. https://pyprog.pro/python/py/nums/nums.html
                # поэтому переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                # type(y)= <class 'decimal.Decimal'>
                # https://www.delftstack.com/howto/python/string-to-decimal-python/
                value = Decimal(price.value_table[cart_user['cart'][number]['i']][cart_user['cart'][number]['j']])

                # Сосчитаем сумму заказа и округлим до 2 знаков после запятой
                order_request_sum = round(count * value, 2)

                cart_user['cart'][number]['order_request_sum'] = order_request_sum

    session['carts_users'] = carts_users
    print('session=', session)
    return redirect(url_for('order_bp.cart')
                    )


# удалить из корзины
@order_blueprint.route('/cart/delete/<int:number>/', methods=['GET', 'POST'])
def delete_from_cart(number):
    # number - это порядковый номер элемента из списка словарей (это словарь) заявки на заказ
    # из корзины конкретного пользователя
    # print('number=', number)
    # Это корзина конкретного пользователя
    cart = session.get('cart', [])
    print('cart before delete=', cart)
    cart.pop(number)
    print('cart after delete=', cart)
    carts_users = session.get('carts_users', [])
    if current_user.is_anonymous:
        user_id = 'anonymous'
    else:
        user_id = current_user.id

    if carts_users != []:
        for cart_user in carts_users:
            if cart_user['user_id'] == user_id:
                cart_user['cart'] = cart

    session['carts_users'] = carts_users
    session.pop('cart')

    print('session=', session)
    return redirect(url_for('order_bp.cart')
                    )


# роут добавления кол-ва в заявке на заказ перед добавлением в корзину
@order_blueprint.route('/order_request_sum_plus/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
def order_request_sum_plus(card_usluga_id, price_id, i, j):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    session['count'] = session.get('count', 1) + 1

    return redirect(url_for('order_bp.order_request',
                            card_usluga_id=card_usluga.id,
                            price_id=price.id,
                            i=i,
                            j=j
                            ))


# роут уменьшения кол-ва в заявке на заказ перед добавлением в корзину
@order_blueprint.route('/order_request_sum_minus/<int:card_usluga_id>/<int:price_id>/<int:i>/<int:j>/', methods=['GET', 'POST'])
def order_request_sum_minus(card_usluga_id, price_id, i, j):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()

    if session.get('count') > 0:
        session['count'] = session.get('count', 1) - 1
    else:
        session['count'] = 0

    return redirect(url_for('order_bp.order_request',
                            card_usluga_id=card_usluga.id,
                            price_id=price.id,
                            i=i,
                            j=j
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
