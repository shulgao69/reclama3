from flask import Flask
# from flask import request, redirect, url_for
# from flask import session
# from flask import Blueprint
# from flask_security import Security, current_user
# from flask_security import SQLAlchemyUserDatastore

from flask_ckeditor import CKEditor


from flask_migrate import Migrate
# from flask_login import LoginManager
#
# from flask_admin import Admin
# from flask_admin import BaseView, expose, AdminIndexView
# from flask_admin.contrib.sqla import ModelView
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.urls import url_parse


# from RECL.models import Usluga, Link, Order, User, Role, roles_users
# from flask_sqlalchemy import SQLAlchemy
from RECL.models import db
from RECL.models import *
# from RECL.models import UploadFileMy, Usluga, Link, Order, User, Role, roles_users, ListModel, \
#     SettingAdmin, UploadFileMy, PriceTable, Carousel, Carouseli
from RECL.config import DevelopConfig, Config
# from RECL.components.admin import security, user_datastore


# Импортируем экземпляры класса Blueprint (test_bp, admin_blueprint, errors_blueprint и др.)
# из файлов соответствующих папок, а затем регистрируем его (см ниже)

# В компонентах 1-***** блюпринты объявлены в файлах __init__.py, поэтому можно не указывать имя файла
# из которого импортируется блюпринт, например
# from RECL.components.errors а не from RECL.components.errors.__init__.py
# Но если блюпринты объявлены в файлах с именем отличным от __init__.py то нужно указывать
# имя файла, например(rotes - имя файл из которого импоритруется блюпринт) 2-*****
# from RECL.components.admin.rotes import admin_blueprint

# 1-*****
from RECL.components.errors import errors_blueprint
from RECL.components.register import register_blueprint
from RECL.components.login import login_blueprint, login_manager
from RECL.components.logout import logout_blueprint
from RECL.components.notactive import notactive_blueprint
# 1-*****

# 2-*****
from RECL.components.admin.rotes import admin_blueprint
from RECL.components.change_password import change_password_blueprint
from RECL.components.price.price import price_blueprint
from RECL.components.test.bptest import test_bp
from RECL.components.fotomanager.fotomanager import foto_manager
from RECL.components.carouselmanager.carousel import carousel_manager
from RECL.components.order.order import order_blueprint
from RECL.components.card_usluga.card_usluga import card_usluga_blueprint
from RECL.components.test_form.test_form import test_form_blueprint
# 2-*****

# from RECL.components.security import security_blueprint, user_datastore, security


migrate = Migrate()

# Flask_Security - начало
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security()
# Flask_Security - конец


app = Flask(__name__)
app.config.from_object(DevelopConfig)

ckeditor = CKEditor(app)

# Инициализация экземпляров классов
db.init_app(app)
migrate.init_app(app, db)
# security.init_app(app, user_datastore)


# Flask-Login - начало

# Перенесла в login/__init__.py все кроме login_manager.init_app(app)
# # Объявляем экземпляр класса LoginManager() из Flask_login для управления пользователем
# login_manager = LoginManager()

# # По умолчанию в Flask-Login, когда неавторизованный пользователь
# # пытается получить доступ к странице, роут которой защищен с помощью login_required
# # (т.е. страница только для авторизованных пользователей)
# # Flask-Login выдаст сообщение и перенаправит его в представление входа.
# # Если представление входа в систему не задано, оно будет прервано с ошибкой 401.
# # Чтобы задать представление входа(т.е.адрес), по которому нужно перенаправить
# # неаворизованного пользователя(у нас на страницу для ввода пароля login)
# # нужно задать LoginManager.login_view
# login_manager.login_view = "login.login"
# # Сообщение по умолчанию при входе в админку? мигает Please log in to access this page.,
# # чтобы настроить сообщение, установитьLoginManager.login_message:
# login_manager.login_message = u"Для входа на эту страницу требуется ввести пароль"
# # login_manager.login_message_category = "info"
#
# # С помощью login_manager загружаем пользователя из сессии
# # в данном случае параметр user_id (это произвольное название,
# # его можно переименовать по своему усмотрению, также как и название функции load_user)
# # - это id пользователя из сессии в формате unicode, поэтому его следует
# # первести в число с помощью int
# # После этого становится доступна в шаблонах переменная current_user,
# # содержащая информацию о пользователе (из базы) и его свойства, наследуемые из класса UserMixin
# # (is_authenticated, is_active, is_anonymous принимающие значения False или True
# # и функция получения id пользователя get_id()).
# # current_user  можно использовать для ограничения прав и др. например
# #     {% if current_user.is_authenticated %}
# #     Объект пользователя {{ current_user }}
# #     Привет {{ current_user.email }}!
# #     {% else %}
# #     Пользователь не авторизован
# #     {% endif %}
# # Запрещает доступ к роутам, перед которыми указано @login_required
# @login_manager.user_loader
# def load_user(user_id):
#     user = User.query.get(int(user_id))
#     # Данные о пользователе, получаемые с помощью декоратора @login_manager.user_loader#
#     print(user, user.id, user.email,user.password)#
#     # print(user.confirmed_at, user.created_on)#
#     # print(load_user)
#     # print(user.is_authenticated, user.is_active, user.is_anonymous)#
#     # print(user.get_id())
#     return user
# Flask-Login - конец


# регистрируем Блюпринты из файлов - начало

# test/lueprinttest, register/__init__.py, errors/__init__.py, admin/__init__.py и т.д.
# url_prefix='/f' - это то, что будет добавляться в url после домена
# и перед путями указанными в роутах Блюпринта

app.register_blueprint(login_blueprint, url_prefix='/login')
app.register_blueprint(register_blueprint, url_prefix='/register')
app.register_blueprint(logout_blueprint, url_prefix='/logout')
app.register_blueprint(errors_blueprint, url_prefix='/errors')
app.register_blueprint(change_password_blueprint, url_prefix='/change_password')

# В блюпринте админки префикс(url_prefix='/all') задала какой-то произвольный
# Этот префикс нигде почему-то не отражается.
# ВНИМАНИЕ!!! Если задавала url_prefix='/admin' то вся верстка админки съезжает!!!
# Поэтому url_prefix задаю отличный от admin!!!!!!
# Теоретически путь в админку задается при создании экземпляра класса Admin в файле admin/__init__.py
# admin = Admin(app, 'Панель управления', url='/admin/', index_view=HomeAdminView(name='_'), template_mode='bootstrap4')
# но когда я задала url='/ad/' все равно путь в браузере был указан /admin/ Путаница
# Поэтому оставить так!!!
# см https://ploshadka.net/flask-delaem-avtorizaciju-na-sajjte/

app.register_blueprint(admin_blueprint, url_prefix='/all')

# app.register_blueprint(security_blueprint, url_prefix='/security_bp')

# Префикс админ ниже сделала для того чтобы обезопасить вход
# и не писать повторно startswitch(/admin/)(см class HomeAdminView(AdminIndexView) в админке)

# Создание, удаление и редактирование прайсов
# app.register_blueprint(price_blueprint, url_prefix='/admin/priceprefix')
app.register_blueprint(price_blueprint, url_prefix='/admin/price')

# Управление загрузкой, удалением и редактированием фото услуг из components/admin/fotomanager.py
app.register_blueprint(foto_manager, url_prefix='/admin/foto')
app.register_blueprint(carousel_manager, url_prefix='/admin/carousel')

# Управление заказами из components/admin/order.py
app.register_blueprint(order_blueprint, url_prefix='/order')

# Управление карточками услуг из components/card_usluga/card_usluga.py
app.register_blueprint(card_usluga_blueprint, url_prefix='/admin/card_usluga')

app.register_blueprint(notactive_blueprint, url_prefix='/notactive')

# Блюпринт для тестирования
app.register_blueprint(test_bp, url_prefix='/testprefix')
app.register_blueprint(test_form_blueprint, url_prefix='/test_form')


# регистрируем Блюпринты из файлов - конец



# Flask-Login
# login_manager ВАЖНО!!!
#
# Инициировала login_manager.init_app(app) ПОСЛЕ БЛЮПРИНТА!!! login_blueprint,
# тк. именно там (в файле components/login/__init__.py) определяется путь\
# (с помощью login_manager.login_view = "login.login"),
# на который перекидывается неавторизованный пользователь при попытке попасть
# на защищенную декоратором @login_required вьюшку
# Если сделать до блюпринта - перекинет на страницу Flask_login логина по умолчанию

login_manager.init_app(app)

# Flask-Login  login_manager - конец



# Flask-Admin
# Перенесла в admin/__init__.py и rote.py
# Если делать блюпринт админки в файли админ/инит - почему-то не получается
# нашла вариант где сам блюпринт в отдельном файле в папке админ (у меня rote.py)
# и все заработало. Почему - не поняла

# # Создание административной панели
# admin = Admin(app, name='Панель администратора', template_mode='bootstrap4')
#
# # Объявление представлений админ. панели с помощью встроенной функции add_view из Flask-Admin
# # каждое из представлений добавляет в админ.панель данные из конкретной модели
# admin.add_view(MyAdminView(Link, db.session, name='Меню(модель Menu)', category="Меню и все услуги"))
# # admin.add_view(MyAdminView(Link, db.session, name='Меню(модель Menu)', category="Меню и все услуги", endpoint="admins_user"))
# admin.add_view(ModelView(Usluga, db.session, name='Услуги(модель Usluga)', category="Меню и все услуги"))
# admin.add_view(ModelView(User, db.session, name='Пользователь(User)'))
# admin.add_view(ModelView(Role, db.session, name='Роли(Role)'))
# admin.add_view(ModelView(Order, db.session, name='Заказы(Order)'))
# # Other
# admin.add_view(MyAdminChangeView(name='Смена пароля'))
# admin.add_view(MyView(name='Выйти'))
#
# # Группировка пунктов меню админки в выпадающий список
# # см. # https://flask-admin.readthedocs.io/en/latest/introduction/#adding-your-own-views
# admin.add_sub_category(name="Links", parent_name="Меню и все услуги")
#
# # Что это за функция при группировки пунктов меню в админке не разобралась, см.
# # https://flask-admin.readthedocs.io/en/latest/introduction/#adding-your-own-views
# # admin.add_link(MenuLinks(name='Home Page', url='/', category='Links'))

# Flask-Admin - конец

from RECL.views import *
