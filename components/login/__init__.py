import hashlib
from flask_login import UserMixin
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, AnonymousUserMixin
from flask import Blueprint
from flask import session, redirect, request, render_template, url_for, abort
from flask_admin import BaseView, expose
from flask_migrate import Migrate
from werkzeug.urls import url_parse
from flask_security import Security
from flask_security import SQLAlchemyUserDatastore

from werkzeug.security import generate_password_hash, check_password_hash

# from RECL.models import db
from RECL.models import Usluga, Link, Order, User, Role, roles_users
from RECL.forms import LoginForm
# from RECL.components.security import security, user_datastore

# migrate = Migrate()

login_blueprint = Blueprint('login', __name__, template_folder='templates', static_folder='static')

# Объявляем экземпляр класса LoginManager() из Flask_login для управления пользователем
login_manager = LoginManager()

# Чтобы инициализировать login_manager (без этого не будет работать) нужно добавить
# login_manager.init_app(app) - в главный __init__.py
# По умолчанию в Flask-Login, когда неавторизованный пользователь
# пытается получить доступ к странице, роут которой защищен с помощью login_required
# (т.е. страница только для авторизованных пользователей)
# Flask-Login выдаст сообщение и перенаправит его в представление входа.
# Если представление входа в систему не задано, оно будет прервано с ошибкой 401.
# Чтобы задать адрес представления входа, по которому нужно перенаправить
# неаворизованного пользователя(у нас на страницу для ввода пароля login)
# нужно задать LoginManager.login_view, где "login.login" - это адрес страницы входа(представления)
login_manager.login_view = "login.login"

# Сообщение по умолчанию при входе в админку? мигает Please log in to access this page.,
# чтобы настроить сообщение, установитьLoginManager.login_message:
login_manager.login_message = u"Для входа на эту страницу требуется ввести пароль"

# login_manager.login_message_category = "info"

# С помощью login_manager загружаем пользователя из сессии
# в данном случае параметр user_id (это произвольное название,
# его можно переименовать по своему усмотрению, также как и название функции load_user)
# - это id пользователя из сессии в формате unicode, поэтому его следует
# перевести в число с помощью int
# После этого становится доступна в шаблонах переменная current_user,
# содержащая информацию о пользователе (из базы) и его свойства, наследуемые из класса UserMixin
# (is_authenticated, is_active, is_anonymous принимающие значения False или True
# и функция получения id пользователя get_id()).
# current_user  можно использовать для ограничения прав и др. например
#     {% if current_user.is_authenticated %}
#     Объект пользователя {{ current_user }}
#     Привет {{ current_user.email }}!
#     {% else %}
#     Пользователь не авторизован
#     {% endif %}
# Запрещает доступ к роутам, перед которыми указано @login_required
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    # Данные о пользователе, получаемые с помощью декоратора @login_manager.user_loader
    print('from login1', user, user.id, user.email, user.password, user.confirmed_at, user.created_on,
    load_user, user.is_authenticated, user.is_active, user.is_anonymous, user.get_id())
    print('from login2', user)
    return user



@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('render_profil'))
    # err = ''
    err=request.args.get('err')
    # print('err from login=', err)
    # links_menu = Link.query.all()
    form = LoginForm()
    # проверяет что метод POST
    # if request.method == "POST":

    # Это правило говорит: Если метод запроса - POST (т.е.проверять на POST отдельно не надо)
    # и если поля формы валидны. Выдавал ошибки какие-то, (до 21.11.21) разобраться!!!

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=username).first()
        # print('username=', username, current_user,current_user.is_active)

        # Пояснения (не удалять)
        # Пока user не загружен с помощью LoginManager с помощью функции login_user(user)
        # user относится к классу flask_security AnonimousUser и print(current_user) дает объект
        # <flask_security.core.AnonymousUser object at 0x04190AF0> и соответственно
        # при попытке такому зайти в админку /admin
        # current_user.is_authenticated будет равно False
        # (Если убрать в админке user_datastore = SQLAlchemyUserDatastore(db, User, Role) и
        # security = Security(app, user_datastore) и контекстный процессор секьюритии,
        # то вместо <flask_security.core.AnonymousUser object at 0x04190AF0>
        # print(current_user) выдаст
        # <flask_login.mixins.AnonymousUserMixin object at 0x03ECC890> так как секюрити
        # основывается на Flask-Login
        # (см в админке :
        #   class HomeAdminView(AdminIndexView):
        #   @app.before_request
        #   def before_request():
        #       if request.full_path.startswith('/admin/'):
        #           if not current_user.is_authenticated:
        #               ....... и т.д.
        #
        # Как только загрузили в LoginManager то будет <User№> (номер авторизованного пользователя),
        # но мы агрузим только если аккаунт активен (то есть ) user.active == True
        # и соответственно current_user.is_active==True
        # Пояснения - конец

        if user and check_password_hash(user.password, password) and user.active == False:
            print('notactive_bp')
            print('url_for("notactive_bp.notactive")=', url_for('notactive_bp.notactive'))
            # print(current_user, current_user.is_active)
            # return redirect(url_for('admin_bp.render_notactive'))
            return redirect(url_for('notactive_bp.notactive'))

        elif user and check_password_hash(user.password, password) and user.active == True:
            # загружаем данные пользователя в функцию и запоминаем после выхода из браузера(remember=True)
            # login_user(user, remember=True)
            # загружаем данные пользователя в функцию и НЕ запоминаем после выхода из браузера(remember=True)
            # print('current_user.is_authenticated1=', current_user.is_authenticated)- дает ошибку
            # print('current_user1=', current_user)- дает ошибку
            login_user(user)
            # print('current_user=', current_user) - дает ошибку
            # print('current_user.is_authenticated2=', current_user.is_authenticated)
            # print(current_user, current_user.is_active)

            # Параметр next
            # см. https://habr.com/ru/post/346346/#:~:text=Flask-Login%20отслеживает%20зарегистрированного%20пользователя%2C%20сохраняя,пользователю%2C%20который%20подключается%20к%20приложению
            # https://proproprogs.ru/flask/uluchshenie-processa-avtorizacii-flask-login

            # После того, как пользователь выполнил вход, вызвав функцию login_user() из Flask-Login,
            # вы получите значение next-аргумента строки запроса. Flask содержит переменную запроса,
            # содержащую всю информацию, которую клиент отправил с запросом.
            # В частности, атрибут request.args предоставляет содержимое строки запроса
            # в формате дружественного словаря. Существует три возможных случая, кот. нужно учитывать,
            # чтобы определить, куда перенаправить после успешного входа в систему:
            # -Если URL-адрес входа не имеет следующего аргумента,
            # пользователь перенаправляется на индексную страницу.
            # -Если URL-адрес входа включает аргумент next, который установлен в относительный путь
            # (или, другими словами, URL-адрес без части домена),
            # тогда пользователь перенаправляется на этот URL-адрес.
            # -Если URL-адрес входа включает аргумент next, который установлен на полный URL-адрес,
            # кот. включает имя домена, то пользователь перенаправляется на страницу индекса.
            # Первый и второй случаи не требуют пояснений.
            # Третий случай заключается в том, чтобы сделать приложение более безопасным.
            # Злоумышленник может вставить URL-адрес на злоумышленный сайт в аргумент next,
            # поэтому приложение перенаправляет только URL-адрес, что гарантирует,
            # что перенаправление останется на том же сайте, что и приложение.
            # Чтобы определить, является ли URL относительным или абсолютным,
            # анализируем его с помощью функции url_parse() Werkzeug,
            # а затем проверяю, установлен ли компонент netloc или нет.
            # netloc - содержит имя домена на котором запущено приложение(?)

            # Кроме того обязательно нужно прописать в login.html
            # <form action="" method="post" class="form-contact">
            # (см. # https://proproprogs.ru/flask/uluchshenie-processa-avtorizacii-flask-login)
            # Здесь происходит дублирование обратного URL-адреса, который был в браузере.
            # Далее, в обработчике /login сделаем перенаправление с учетом наличия этого параметра:
            # РАЗБИРАТЬСЯ!!!!


            next_page = request.args.get('next')
            # if next:
            #     print('next_page1=', next_page)
            #     print('type(next_page1)=', type(next_page))
            # print('request.url=', request.url)
            # print('request.args=', request.args)
            # print(next_page)

            # Проверка безопастности next параметра
            # Вариант 1
             # см. https://habr.com/ru/post/346346/#:~:text=Flask-Login%20отслеживает%20зарегистрированного%20пользователя%2C%20сохраняя,пользователю%2C%20который%20подключается%20к%20приложению

            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('render_main')
                # print('next_page2=', next_page)


            user_id = session.get('_user_id')
            carts_users = session.get('carts_users', [])
            print('carts_users=', carts_users)
            list_users_id = []
            for cart_user in carts_users:
                list_users_id.append(cart_user['user_id'])
            print('list_users_id=', list_users_id)
            dict_anonymous = {}
            dict_anonymous['user_id']='anonymous'
            dict_anonymous['cart']=[]
            dict_user_id = {}
            # user_anonymous_in_carts_users = False
            user_authenticated_in_carts_users = False
            if len(carts_users) != 0:
                print('len(carts_users)=', len(carts_users))
                for cart_user in carts_users:
                    if cart_user['user_id'] == 'anonymous' and len(cart_user['cart']) != 0:
                        # user_anonymous_in_carts_users = True
                        # dict_anonymous['user_id'] = cart_user['user_id']
                        dict_anonymous['cart'] = cart_user['cart']
                        cart_user['cart']=[]
                        print('dict_anonymous=', dict_anonymous)
                    if cart_user['user_id'] == current_user.id and cart_user['user_id'] != 'anonymous':
                        user_authenticated_in_carts_users = True
                        dict_user_id['user_id'] = cart_user['user_id']
                        dict_user_id['cart'] = cart_user['cart']
                        print('dict_user_id=', dict_user_id)

                # Если авторизуемого пользователя нет в списке корзин пользователей
                # и словарь, кот. создали из анонимной корзины не пуст добавим в список корзин
                if user_authenticated_in_carts_users == False and len(dict_anonymous['cart']) != 0:
                    new_cart_user={}
                    new_cart_user['user_id']=current_user.id
                    new_cart_user['cart']=dict_anonymous['cart']
                    carts_users.append(new_cart_user)
                # Если авторизуемый пользователь в списке корзин пользователей
                # и словарь, кот. создали из анонимной корзины не пуст добавим
                # его в корзину пользователя
                if user_authenticated_in_carts_users == True and len(dict_anonymous['cart']) != 0:

                    for cart_user in carts_users:
                        print('cart_user=', cart_user)
                        if cart_user['user_id'] == current_user.id:
                            print('cart_user["cart"]=', cart_user['cart'], type(cart_user['cart']))
                            print('dict_anonymous["cart"]=', dict_anonymous['cart'], type(dict_anonymous['cart']))
                            # cart_user['cart'].append(dict_anonymous['cart'])
                            for d in dict_anonymous['cart']:
                                cart_user['cart'].append(d)
                            # cart_user['cart']+dict_anonymous['cart']
                            # print('cart_user user_id=', cart_user, cart_user['user_id'])

            session['carts_users'] = carts_users
            session['user_id'] = user_id
            # print('session.get("carts_users")=', session.get('carts_users'))
            #
            print('session from login=', session)

            return redirect(next_page)

            # Вариант2 (не проверила!!! 23.04.21)
            # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
            # Login Example
            #     Once a user has .......

            # if not next or not is_safe_url(next):
            #     return flask.abort(400)
            #     return redirect(url_for('errors.400'))
            #
            # return redirect(next or url_for('render_main'))
            # is_safe_url должен проверить, безопасен ли URL-адрес для перенаправления.
            # См. http://flask.pocoo.org/snippets/62/ для примера.
            # Предупреждение: Вы ДОЛЖНЫ проверить значение следующего параметра. Если вы этого не сделаете,
            # ваше приложение будет уязвимо для открытых перенаправлений.

        else:
            err = "Неверное имя или пароль"
            # print("err = Неверное имя или пароль")
            # return render_template('login/login.html', form=form, err=err, links_menu=links_menu)
            return redirect(url_for('login.login', err=err))

    return render_template('login/login.html',
                           form=form,
                           err=err,
                           # links_menu=links_menu
                           )

