# см также https://stepik.org/lesson/300655/step/10

from flask import Blueprint, jsonify, redirect, session, request, render_template
from flask import has_app_context, flash, current_app, abort, url_for

from flask_admin import BaseView, Admin, AdminIndexView
from flask_admin import  helpers, expose
from flask_admin import form
from flask_admin.form import rules, Select2Widget

from flask_admin.base import MenuLink

from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import BooleanEqualFilter

from flask_admin.contrib import sqla

# from flask.ext.admin.form import Select2Widget

# Импортирую валидатор для проверки вводимых данных (интервал от min до max)
# в MyStatusCardUsluga
from wtforms.validators import NumberRange


# https://question-it.com/questions/6537146/flask-sqlalchemy-filtr-po-kolichestvu-obektov-otnoshenij
from sqlalchemy.sql.expression import func

# from wtforms.fields import StringField

# Модуль для загрузки файлов, создания директорий в Flask-admin
# from flask_admin.contrib.fileadmin import FileAdmin

from werkzeug.security import generate_password_hash, check_password_hash

# импорты для загрузки файлов - начало
# from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from sqlalchemy.dialects.postgresql import JSON
# импорты для загрузки файлов - конец

# from flask_security import UserMixin, RoleMixin

# Импорт, необходимый для работы модуля FileAdmin
# import os.path as op

import random

import os
from os import path
from os.path import join, dirname, realpath, getsize

# Модуль shutil используем для удаления папки со всеми файлами (MyCardUsluga)
 # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
import shutil

from pathlib import Path
import re
from transliterate import translit

# Импорт, необходимый для создания уникального имени загружаемого файла по времени загрузки
import datetime
from datetime import datetime

# Импорт, необходимый для перехвата предупреждений при задании form_edit_rules
import warnings

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, HiddenField, DateField, \
    DateTimeField, TimeField
# from wtforms import BooleanField, IntegerField

from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
# from wtforms.validators import InputRequired, Length

from flask_login import logout_user, login_required
from flask_login import LoginManager

from flask_security import SQLAlchemyUserDatastore
from flask_security import Security, AnonymousUser
from flask_security import current_user, url_for_security
from flask_security import login_required, roles_required, roles_accepted
# from flask_security import UserMixin, RoleMixin

from werkzeug.urls import url_parse

# from flask_principal import Principal

from RECL.models import ListModel, SettingAdmin
from RECL.models import User, Role, roles_users, Phone, Payer
from RECL.models import Link, Usluga
from RECL.models import CardUsluga, Photo, PriceTable
from RECL.models import TypeProduction

from RECL.models import StatusCard, StatusIntermediate, StatusOrder
from RECL.models import SpecificationStatusCard, SpecificationStatusIntermediate
from RECL.models import StaffAction, GoalAction, ResultAction, MethodAction, ActionOrder
from RECL.models import ActionOrder, ActionOrderItem
# from RECL.models import StatusCardUsluga, Status
# from RECL.models import OrderStatus
from RECL.models import Order, OrderItem, ProgressOrder

from RECL.models import Carousel, PlaceCarousel
from RECL.models import PlaceElement, PlaceModelElement, BaseLocationElement, \
    BasePositionElement, HorizontalPositionElement, VerticalPositionElement, \
    PositionElement, ContainerElement, ColumnElement, PriorityElement
from RECL.models import WidthElement, HeightElement
from RECL.models import UploadFileMy
# from RECL.models import roles_models

from RECL.models import db

# from RECL.forms import PhotoFormAdmin, PhotoForm, FormChoice2, FormChoice1

from RECL.components.admin.forms import PhotoFormAdmin
# from RECL.components.admin.forms import  DeleteForm, FormChoice1, FormChoice2, DeleteFormFromMini, EditFormFromMini

# Пока оставить
# from RECL.components.admin.forms import PhotoFormAdmin2
# Пока оставить -  конец

# Этот импорт использовать с осторожностью, так как он циклический
# Лучше использовать контекст приложения from flask import current_app()
# тк при обращении к блюпринту приложение уже создано и соответственно уже существует его контекст
# и например вместо  path_full = app.config['UPLOAD_PATH'] - так в блюпринтах не делать!!!
# делать   path_full = current_app.config['UPLOAD_PATH']
# Но в админке app используется до создания контекста приложения
# security = Security(app, user_datastore),  @app.before_request и др поэтому оставим
from RECL.__init__ import app

# from RECL.components.login import login_manager
# from RECL import app


# Длину пароля нужно брать из файла конфигурации, но не получалось почему-то.
# Поэтому задавала здесь напрямую.
# Это требовалось при сбросе и смене пароля в class MyUser(SpecificView)
# Но теперь работает с помощью
# password_length = 2

# principal=Principal()

# Если делала блюпринт админки в файли админ/инит - почему-то не работало
# нашла вариант где сам блюпринт в отдельном файле в папке админ (у меня rote.py)
# и все заработало. Почему - не поняла
# Вообще-то сама админка основана на блюпринте, поэтому блюпринт блюпринта получается.
# Надо разобраться

# admin_blueprint = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

# Подключение к LoginManager() из Flask-Login нужно для доступа к переменной current_user,
# но мы используем Security(app, user_datastore), а она содержит Flask-Login поэтому
# отдельно подключать не надо
# login_manager = LoginManager()

# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.query(User).get(user_id)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Класс входа в админ панель дополняем  @app.before_request (выполняется перед
# входом в админку) в которой определяем критерии входа в админку
# У нас войти в админку может пользователь с ролью(любой).
# Обычные юзеры (в том числе зарегистрированные) роли не имеют
# Если потребуется разграничить права обычных пользователей, возможно нужно будет
# добавить пользователю роль и добавить в админку ограничения на вход.
class HomeAdminView(AdminIndexView):
    # current_user работает только в контексте приложения в функции, поэтому будет None
    # print('2-from admin from class HomeAdminView current_user=', current_user)

    @app.before_request
    def before_request():

        if request.full_path.startswith('/admin/'):

            # print('3-from admin class HomeAdminView def before_request current_user=', current_user)
            # print('3-from admin class HomeAdminView def before_request current_user.is_authenticated=', current_user.is_authenticated)
            # print('3-from admin class HomeAdminView def before_request current_user.roles=', current_user.roles)
            if not current_user.is_authenticated:
                err = '11 Авторизуйтесь пожалуйста'
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('render_main')
                return redirect(url_for('login.login', next=next_page, err=err))
            # разрешаем вход в админку только определенным ролям (admin, editor, manager)
            # elif current_user.is_authenticated and not (current_user.has_role('admin') or current_user.has_role('editor') or current_user.has_role('manager')):

            # разрешаем вход в админку ВСЕМ ролям (то есть всем юзерам у которых не пустая роль!!)
            # если юзер аутентифицирован но его роль пустая просим войти с другой учетной записью

            # Активировать после настройки - начало!!

            # elif current_user.is_authenticated and User.query.filter(User.id == current_user.id).first().roles == []:
            #     err = '11 Вы вошли в систему, однако у вас недостаточно прав для просмотра данной страницы. ' \
            #       'Возможно, вы хотели бы войти в систему, используя другую учётную запись? '
            #     next_page = request.args.get('next')
            #     if not next_page or url_parse(next_page).netloc != '':
            #         next_page = url_for('render_main')
            #     return redirect(url_for('login.login', next=next_page, err=err))

            # Активировать после настройки - конец!!

            # else:
            #     session["user_role"] = current_user.roles
            #     print('3-1 session["user_role"] = current_user.roles', session.get("user_role"))


    # def inaccessible_callback(self, name, **kwargs):
    #     err = 'у вас нед'
    #     return redirect (url_for('login.login', next=request.url, err=err))

    # # @app.before_request
    # # def _handle_view(self):
    # def _handle_view(self, name, **kwargs):
    #     if request.full_path.startswith('/admin/'):
    #     # Override builtin _handle_view in order to redirect users when a view is not accessible.
    #     # Переопределение встроенного _handle_view для перенаправления пользователей,
    #     #  когда представление недоступно.
    #
    #         if not self.is_accessible():
    #             if current_user.is_authenticated:
    #                 # permission denied
    #                 # abort(403)
    #                 # next=request.url
    #                 next_page = request.args.get('next')
    #
    #                 # Проверка параметра next
    #                 # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
    #                 # Login Example  Once a user has .......
    #                 # is_safe_url должен проверить, безопасен ли URL-адрес для перенаправления.
    #                 # См. http://flask.pocoo.org/snippets/62/ для примера.
    #                 # Предупреждение: Вы ДОЛЖНЫ проверить значение следующего параметра. Если вы этого не сделаете,
    #                 # ваше приложение будет уязвимо для открытых перенаправлений.
    #                 # if not is_safe_url(next):
    #                 #     # return redirect('errors/400.html')
    #                 #     return render_template('errors/400.html')
    #                 if not next_page or url_parse(next_page).netloc != '':
    #                     next_page = url_for('render_main')
    #                 err = 'Вы вошли в систему, но у вас нет прав на просмотр этой страницы.
    #                 Попробуйте зайти в другой аккаунт.'
    #                 return redirect(url_for('login.login', next=next_page, err=err))
    #             else:
    #                 # next=request.url
    #                 next_page = request.args.get('next')
    #
    #                 # Проверка параметра next
    #                 # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
    #                 # Login Example     Once a user has .......
    #                 # is_safe_url должен проверить, безопасен ли URL-адрес для перенаправления.
    #                 # См. http://flask.pocoo.org/snippets/62/ для примера.
    #                 # Предупреждение: Вы ДОЛЖНЫ проверить значение следующего параметра. Если вы этого не сделаете,
    #                 # ваше приложение будет уязвимо для открытых перенаправлений.
    #
    #                 # if not is_safe_url(next):
    #                 #     # return redirect('errors/400.html')
    #                 #     return render_template('errors/400.html')
    #                 if not next_page or url_parse(next_page).netloc != '':
    #                     next_page = url_for('render_main')
    #                 err = 'Если вы хотите просмотреть эту страницу, авторизуйтесь пожалуйста'
    #                 return redirect(url_for('login.login', next=next_page, err=err))


# Выход из административной панели
class MyView(BaseView):
    @expose('/')
    @login_required
    def exit_admin(self):
        logout_user()
        return redirect('/')

# Смена пароля администратора
class MyAdminChangeView(BaseView):
    @expose('/')
    def change_password_admin(self):
        return redirect('/change_password/')


# ***** Загрузка файлов (фото) - РАБОТАЕТ!!!
# частично использовала нижеуказанный файл, частично другие источники
# https://docs-python.ru/packages/veb-frejmvork-flask-python/rasshirenie-flask-wtf/
# Данный загрузчик хоть и называется UploadPhotoAdmin на самом деле
# загружает любые файлы. В нем реализовано:
#       - создание безопасного имени функцией secure_filename (тк могут быть поддельные имена, способные изменить файловую систему)
#       - проверка что метод POST и отправленные данные не пусты
# но не реализованы:
# 1) проверка допустимости формата загружаемого файла (то есть ограничения на форматы загружаемых файлов)
# 2) проверка содержимого на соответствие формату, указанному в расширении файла(могут быть поддельные)
# 3) проверка на максимально допустимый размер загружаемого файла (для ограничения згрузки больших файлов)
# Поэтому данный загрузчик, я думаю, можно использовать только для загрузки проверенным пользователем
# 4) проверка специфических свойств изображений и редактирование размеров картинки(например)
#
# ** Конфигурации, используемые для загрузки файлов

# Теоретически формат возможных загрузок, но не использовала
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# ***** UPLOAD_FOLDER
# В некоторых примерах используется для определения папки загрузки UPLOAD_FOLDER
# у меня почему-то не цепляется. (Может это с пакетом Flask_Upload?) Читать!!!
#  Использовала поэтому для определения пути загрузки UPLOAD_PATH
# app.config['UPLOAD_FOLDER'] = '/static/images/uploads/'
# UPLOAD_FOLDER = 'static/images/uploads/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(os.path.join(app.instance_path, 'static/uploads/'), exist_ok=True)
# print(app.instance_path)
# ***** UPLOAD_FOLDER - конец

# *****MAX_CONTENT_LENGTH
# # Максимальный размер загружаемого файла (у нас пока 1 Mb)
# # Обязательно!!! чтобы избежать загрузки большого файла,
# # который может занять все место на сервере и привести к сбою
# app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
# # app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 (16 Mb)

# ******UPLOAD_EXTENSIONS
# # Возможные форматы файлов загрузки
# UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
# app.config['UPLOAD_EXTENSIONS'] = UPLOAD_EXTENSIONS

# ***** UPLOAD_PATH
# Путь загрузки файлов. Обратить внимание:
# В config приложения тоже задан путь UPLOAD_PATH загрузки файлов.
# Он задает путь от корневых директорий.
# То есть (например) UPLOAD_PATH = RECL/static/uploads/ и загрузка идет туда
# Задав здесь UPLOAD_PATH 'static/images/uploads/' мы переопределяем его
# в блюпринте с конечной точкой админ.
# следовательно UPLOAD_PATH = RECL/components/admin/static/images/uploads/
# и все загрузки, в которых используется UPLOAD_PATH
# (в том числе и в функциях, находящихся вне блюпринта админ)
# будет использоваться не определенный в конфиге приложения путь,
# а переопределенный (у нас в частности в админке) т.к. UPLOAD_PATH глобальная переменная
# UPLOAD_PATH = join(dirname(realpath(__file__)), 'static/images/uploads/')
# app.config['UPLOAD_PATH'] = UPLOAD_PATH
# *****UPLOAD_PATH - конец
# ** Конфигурации, используемые для загрузки файлов - конец


class UploadPhotoAdmin(BaseView):
    @expose('/', methods=['GET', 'POST'])
    # Декоратор, который указывает, что пользователь должен иметь хотя бы одну из указанных ролей.
    @roles_accepted('superadmin')
    def foto_load(self):
        err = ''
        success = False
        links_menu = Link.query.all()

        # Создаем экземпляр класса формы
        form = PhotoFormAdmin()

        # form.validate_on_submit() заменяет строку
        # if request.method == 'POST' and form.photo.data != '':
        # То есть проверяем заполнена ли форма и убеждаемся, что метод "POST" и файл выбран
        # Но в классе PhotoFormAdmin(FlaskForm) из форм админки должен быть задан встроенный
        # валидатор FileRequired().
        # class PhotoFormAdmin(FlaskForm):
        #             photo = FileField('Фото', [FileRequired()])
        #             submit = SubmitField('Загрузить файл')
        # Если не задать, то проверка form.validate_on_submit() проверит только что метод POST,
        # а что файл не выбран не проверит и тогда выдаст ошибку что определенный позднее
        # filename будет None
        if form.validate_on_submit():

            # Получаем данные из формы - имя файла
            photo_name = form.photo.data

            # п.1 С помощью функции secure_filename делаем имя безопасным! (пояснение https://translate.yandex.ru/translate)
            # Ее нужно использовать всегда, т.к. могут отправить имя, кот.может изменить файловую систему
            # Например имя ДКТ20-11-Фирма Вертикаль-чб.jpg преобразует в 20-11-_-.jpg
            # Но поскольку кириллические символы удаляются, то название например лифт.tif
            # преобразуется в .tif Поэтому добавила перед именем 'my'
            # В последствии можно добавлять значимые элементы
            # (например дату и время или имя переведенное в латиницу? - это просто мысли, как сделать пока не знаю)
            filename = secure_filename('my'+ photo_name.filename)

            # п.2 Присоединяем безопасное имя файла к пути загрузки
            file_path = os.path.join(app.config['UPLOAD_PATH'], filename)

            # п.3 Сохраняем в выбранное место файл с безопасным именем
            photo_name.save(file_path)

            # Тоже самое (то есть п.1-3) можно записать в одну строку так:
            # photo_name.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(photo_name.filename)))
            success = True
            render_template('admin/upload-foto.html',
                           form=form,
                           links_menu=links_menu, success=success, err=err)

        # Показываем форму если метод GET (то есть if not form.validate_on_submit())
        # То есть при открытии страницы (пока без отправки файлов)
        return render_template('admin/upload-foto.html',
                           form=form, links_menu=links_menu, success=success)
# Загрузка фото - конец - РАБОТАЕТ!!!


# ******
# Выбор из выпадающего списка и обновление другого списка в формах -РАБОТАЕТ!!!
# class Choice1, FormChoice1(form_name='FormChoice1Name') и
#  @app.route('/_get_usl_choice1_admin/')
#  def _get_usl_choice1_admin():
# Полностью основано на https://stackoverflow.com/questions/41232105/populate-wtforms-select-field-using-value-selected-from-previous-field
# Заменены переменные, названия функций, также в choice1.html добавлен
# # <script src="https://code.jquery.com/jquery-3.2.1.min.js"
#       integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
#       crossorigin="anonymous">
#     </script>!!!

class Choice1(BaseView):
    @expose('/', methods=['GET', 'POST'])
    @roles_accepted('superadmin')
    def choice1(self):
        form = FormChoice1(form_name='FormChoice1Name')
        form.menu.choices = [(menu.id, menu.title) for menu in Link.query.order_by('title').all()]
        form.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.order_by('title').all()]
        if request.method == 'GET':
            return render_template('admin/choice1.html', form=form)
        if form.validate_on_submit() and request.form['form_name'] == 'FormChoice1Name':
            flash('menu: %s, usluga: %s' % (form.menu.data, form.usluga.data))
        return redirect(url_for('choice1'))

    @app.route('/_get_usl_choice1_admin/')
    def _get_usl_choice1_admin():
        menu = request.args.get('menu', '01', type=str)
        uslugschoice1 = [(usluga.id, usluga.title) for usluga in Usluga.query.filter_by(punkt_menu_id=menu).order_by('title').all()]
        print ('uslugschoice1 from admin=', uslugschoice1)
        return jsonify(uslugschoice1)
# Выбор из выпадающего списка и обновление другого списка в формах - конец - РАБОТАЕТ!!!
# ******


# ****** Класс Choice2 - перенесла в fotomanager.py - начало -  не удалять это все работает!!!
# Выбор из выпадающего списка с обновлением другого списка, формирование
# пути загрузки файла на основе выбора + загрузка файла + запись в базу - начало - РАБОТАЕТ!!!
# ******
# (Объединение функций:
# - class Choice1(BaseView) и др.(см выше))(выбор из выпадающих списков)
# - формирование пути записи файлов (на основе выбора из выпадающих списков)
# - class UploadPhotoAdmin(загрузка файлов)(см выше)
# - запись в базу
# - удаление ненужных файлов из папки загрузки (на той же странице)
# (форма class DeleteForm(FlaskForm) из E:\0-ALL-FLASK\REKLAMA1\RECL\components\admin\forms.py)

# Выбор из выпадающего списка и обновление другого списка в формах
# class Choice2, FormChoice2(form_name='FormChoice2Name') и
#  @app.route('/_get_usl_choice2_admin/')
#  def _get_usl_choice2_admin():
# Полностью основано на https://stackoverflow.com/questions/41232105/populate-wtforms-select-field-using-value-selected-from-previous-field
# Заменены переменные, названия функций, также в choice2.html добавлен
# # <script src="https://code.jquery.com/jquery-3.2.1.min.js"
#       integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
#       crossorigin="anonymous">
#     </script>!!!  и  собственно сам скрипт

# * 2 формы на одной странице
# см https://fooobar.com/questions/140124/multiple-forms-in-a-single-page-using-flask-and-wtforms


# class Choice2(BaseView):
#     @expose('/', methods=['GET', 'POST'])
#     @roles_accepted('superadmin')
#     def choice2(self):
#         menu_all = Link.query.all()
#         uslugi_all = Usluga.query.all()
#         foto_all = UploadFileMy.query.all()
#
#         form_delete=DeleteForm(form2_name='DeleteFormName')
#         # print(DeleteForm())
#
#         form = FormChoice2(form_name='FormChoice2Name')
#         # print(FormChoice2())
#
#         form.menu.choices = [(menu.id, menu.title) for menu in Link.query.order_by('title').all()]
#         form.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.order_by('title').all()]
#
#         form_delete.menu.choices = [(menu.id, menu.title) for menu in Link.query.order_by('title').all()]
#         form_delete.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.order_by('title').all()]
#         form_delete.names_files_for_delete.choices = [(i.id, i.origin_name_photo) for i in UploadFileMy.query.all()]
#
#         # if request.method == 'POST':
#         # При проверке request.form['form_name'] == 'FormChoice2Name'
#         # возникает ошибка 400 - "странный" запрос (у меня Остановлена попытка перенаправления на др. сайт)
#         # почему данная проверка в примере - не очень поняла.
#         # Заменила ее на проверку form.form_name.data == 'FormChoice2Name'
#         # (проверяю дополнительно имя формы из скрытого поля)
#         # В принципе проверку на имя формы можно убрать
#         # if form.validate_on_submit() and request.form['form_name'] == 'FormChoice2Name':
#
#         # Еще делаем проверку form.photo.data (чтобы была не None)
#         # Пока на стр. была одна форма загрузки мы в форме поставили валидатор
#         # photo = FileField('Выбор фото', validators=[FileRequired()])
#         # чтобы проверить что файл выбран.
#         # Поскольку мы делаем на 1 стр. 2 формы при нажатии любой из кнопок отправки
#         # происходит прием и обработка на этом роуте, но мы не загрузили имя файл загрузки(например)
#         # и он при приеме будет None, поэтому этот валидатор из формы убрали
#         # и сделали проверку внутри роута
#
#         if form.validate_on_submit() and form.form_name.data == 'FormChoice2Name' and form.photo.data:
#
#             # print("2-form.form_name.data=", form.form_name.data)
#             # print('POST-form.menu.data=', form.menu.data, 'form.usluga.data=', form.usluga.data)
#             # flash('menu: %s, usluga: %s' % (form.menu.data, form.usluga.data))
#             menu_choice2=Link.query.filter_by(id=form.menu.data).first()
#             # print('menu_choice2=', menu_choice2, 'type menu_choice2=', type(menu_choice2))
#             # print('menu_choice2.title=', menu_choice2.title, 'type menu_choice2.title=', type(menu_choice2.title))
#             # print('menu_choice2.link=', menu_choice2.link)
#             usluga_choice2=Usluga.query.filter_by(id=form.usluga.data).first()
#             # print('usluga_choice2=', usluga_choice2)
#             # print('usluga_choice2.title=', usluga_choice2.title)
#             # print('usluga_choice2.link=', usluga_choice2.link)
#             # Формируем часть пути загрузки файла на основе выбранных меню и услуги:
#             # директория меню сайта + директория услуги (из базы(эти директории (имена директорий) создаются при внесении в базу услуги или пункта меню))
#             path_choice2=menu_choice2.link +'/' + usluga_choice2.link +'/'
#             # print('path_choice2=', path_choice2, 'type path_choice2=', type(path_choice2))
#
#             # Формируем полный путь загрузки файла на основе выбранных меню и услуги:
#             path_full = app.config['UPLOAD_PATH']+path_choice2
#             # print('path_full(Директория для загрузки файла)=', path_full)
#             # try:
#             #     os.makedirs(path_full)
#             # except OSError:
#             #     print("Создать директорию %s не удалось" %path_full)
#             # else:
#             #     print("Успешно создана директория %s" %path_full)
#             # print('os.path.isdir(path_full)=', os.path.isdir(path_full))
#             if not os.path.isdir(path_full):
#                 os.makedirs(path_full)
#                 # print('создана новая директория', path_full)
#             # else:
#             #     print('директория', path_full,'уже существует')
#
#
#             # ***** загрузка фото и запись в базу
#             # Получаем данные из формы -
#             # заголовок услуги
#             title = form.title.data
#
#             # Сопроводительный текст услуги
#             comments = form.comments.data
#
#             # имя файла c расширением
#             photo_name = form.photo.data
#             # print('photo_name=', photo_name.filename, 'type photo_name=', type(photo_name.filename))
#
#             # **** задаем время загрузки файла и включаем его (ниже) в имя загружаемого файла (таким образом оно будет уникальным)
#             # для этого импортировали модуль datetime
#             # replace(microsecond=0) - чтобы отсечь миллисекунды
#             # replace(':', '-') - чтобы заменить : так как может в файловой системе создать проблемы
#             uniq_filename = str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')
#             # **** задаем время загрузки файла -  конец
#
#            # п.1 С помощью функции secure_filename делаем имя безопасным! (пояснение https://translate.yandex.ru/translate)
#             # Ее нужно использовать всегда, т.к. могут отправить имя, кот.может изменить файловую систему
#             # Например имя ДКТ20-11-Фирма Вертикаль-чб.jpg преобразует в 20-11-_-.jpg
#             # Но поскольку кириллические символы удаляются, то название например лифт.tif
#             # преобразуется в tif Поэтому добавила перед именем 'my'
#             # В последствии можно добавлять значимые элементы
#             # (например дату и время или имя переведенное в латиницу? - это просто мысли, как сделать пока не знаю)
#             # filename = secure_filename('my'+photo_name.filename)
#             filename = secure_filename(uniq_filename+'_'+photo_name.filename)
#             # print('filename=', filename, 'type filename=', type(filename))
#
#             # п.2 Присоединяем безопасное имя файла к пути загрузки
#             # file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
#             file_path = os.path.join(path_full, filename)
#             # print('file_path=', file_path, 'type file_path=', type(file_path))
#
#
#             # п.3 Сохраняем в выбранное место файл с безопасным именем
#             photo_name.save(file_path)
#             # print('photo_name.save(file_path)=', photo_name.save(file_path))
#
#             # Тоже самое (то есть п.1-3) можно записать в одну строку так:
#             # photo_name.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(photo_name.filename)))
#
#             # п.4 Вычислим размер загруженного файла - вариант 1
#             # Полученный размер отличается от того, что в проводнике.
#             # Так и должно быть!!!! (и в варианте 2 тоже самое!!) Читать про это:
#             # https://question-it.com/questions/1398830/python-ospathgetsize-otlichaetsja-ot-len-fread
#             # https://translate.yandex.ru/translate?lang=en-ru&url=https%3A%2F%2Fstackoverflow.com%2Fquestions%2F26603698%2Fwhy-does-os-path-getsize-give-me-the-wrong-size&view=c
#             # Можно наверное использовать и другой метод -см views.py
#             #         @app.route('/upl/', methods=['GET', 'POST'])
#
#             file_size=os.path.getsize(file_path)
#             # print('file_size=', file_size, 'type file_size=', type(file_size))
#             # Вычислим размер загруженного файла - вариант 1 - конец
#
#             # п.4 Вычислим размер загруженного файла -  вариант 2
#             # (дает тот же результат что и вар 1)
#             # Этот вар.работает, но воспользуемся вар.1 (чтобы не импортировать лишнюю библиотеку)
#             # from pathlib import Path
#             # file_obj = Path(file_path)
#             # size = file_obj.stat().st_size
#             # print('size=', file_size, 'type size=', type(file_size))
#             # Вычислим размер загруженного файла -  вариант 2 - конец
#
#             # п.5 Выделим расширение файла
#             name_ext = os.path.splitext(file_path)[1]
#             # print('name_ext=', name_ext, 'type name_ext=', type(name_ext))
#             # Выделим расширение файла - конец
#
#             # п.6 Запишем параметры загрузки файла в базу
#             upload_file=UploadFileMy(origin_name_photo = photo_name.filename,
#                                      secure_name_photo = filename,
#                                      menu = menu_choice2.title,
#                                      dir_menu = menu_choice2.link,
#                                      usluga = usluga_choice2.title,
#                                      dir_usluga = usluga_choice2.link,
#                                      # Часть пути загрузки(меню+услуга)
#                                      dir_uploads = path_choice2,
#                                      # Полный путь загрузки(путь проекта + путь меню+услуга)
#                                      # dir_uploads = file_path,
#                                      file_ext = name_ext,
#                                      file_size = file_size,
#                                      title=title,
#                                      comments=comments
#                                      )
#             db.session.add(upload_file)
#             db.session.commit()
#
#             success = True
#
#             # Данный редирект нужен для сброса данных POST запроса после отправки формы
#             # и предотвращения повторной загрузки файла при обновлении страницы
#             # Можно сделать 2 вариантами: 1- редирект на отдельный роут(сделала в views.py)
#             # return redirect('/sbroschoice2/')
#             # 2 вариант(оставим его) - редирект на функцию этой страницы (саму себя)
#
#             return redirect(url_for('choice2.choice2'))
#
#         # else:
#             upload_rezult = False
#             # return render_template('admin/choice2.html', form=form, form_delete=form_delete, upload_rezult=upload_rezult)
#         # print(form_delete.validate_on_submit())
#         # print('1-form_delete.delete_file.data-', form_delete.delete_file.data)
#
#
#         #***** Удаление фото и записи из базы
#         # Это пока не работает!!! на 23.10.21
#         delete_file = form_delete.delete_file.data
#         # print('delete_file=', delete_file)
#
#
#         if form_delete.validate_on_submit() and form_delete.delete_file.data:
#             # print('form_delete.data-', form_delete.data)
#             # print('os.path.dirname(__file__)-', os.path.dirname(__file__))
#             # print('os.path.abspath(os.path.dirname(__file__))-', os.path.abspath(os.path.dirname(__file__)))
#             path = os.path.join(os.path.abspath(os.path.dirname(__file__)), form_delete.delete_file.data.filename)
#             print('path-', path)
#
#             menu_choice2=Link.query.filter_by(id=form_delete.menu.data).first()
#             usluga_choice2=Usluga.query.filter_by(id=form_delete.usluga.data).first()
#             # Формируем часть пути удаления файла на основе выбранных меню и услуги:
#             # директория меню сайта + директория услуги (из базы(эти директории (имена директорий) создаются при внесении в базу услуги или пункта меню))
#             path_choice2_for_delete=menu_choice2.link +'/' + usluga_choice2.link +'/'
#             # print('path_choice2=', path_choice2, 'type path_choice2=', type(path_choice2))
#
#             # Формируем полный путь удаления файла на основе выбранных меню и услуги:
#             path_full_for_delete = app.config['UPLOAD_PATH']+path_choice2_for_delete
#             print('path_full_for_delete(Директория для удаления файла)=', path_full_for_delete)
#
#
#             # choice2_for_del_file=UploadFileMy.query.all()
#             # for i in choice2_for_del_file:
#             #     print(i)
#             # files_choice2 = os.listdir(path_full_for_delete)
#             # form_delete.names_files_for_delete.choices = os.listdir(path_full_for_delete)
#             # form_delete.names_files_for_delete.choices = [(i.id, i.origin_name_photo) for i in UploadFileMy.query.all()]
#             # form.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.order_by('title').all()]
#             # print('os.listdir(path_full_for_delete)=', os.listdir(path_full_for_delete))
#             # for file_for_delete in os.listdir(path_full_for_delete):
#             #     print(file_for_delete)
#
#             # print('os.path.split()-', os.path.split(path))
#             # tree = os.walk(os.path.dirname(__file__))
#             # for item in tree:
#                 # print('len(item)=', len(item))
#                 # print('item=', item)
#                 # print('item[0]=', item[0])
#                 # print('item[1]=', item[1])
#                 # print('item[2]', item[2])
#
#             # os.remove('/0-ALL-FLASK\REKLAMA1\RECL\static/images/uploads/lera/lera-usl/myokna1.jpg')
#             # p = os.path.abspath('form_delete.delete_file.data')
#             # import pathlib
#             # p = pathlib.Path('form_delete.delete_file.data')
#             # print(p)
#             # print('2---', form_delete.delete_file.data)
#             # print('os.path-', os.path)
#             # print('os.pathlike-', os.pathlike)
#             # print('os.getcwd()', os.getcwd())
#             # print('os.path.exists(file_path)', os.path.exists(form_delete.delete_file.data))
#             # print('os.path.abspath(', os.path.abspath('form_delete.delete_file.data'))
#             # print('os.path.relpath(form_delete.delete_file.data)', os.path.relpath('form_delete.delete_file.data'))
#             # print('os.path.basename()', os.path.basename())
#             # print('os.path.dirname()', os.path.dirname())
#             # print('os.path.join()', os.path.join())
#             # print('os.path.split()', os.path.split())
#                 # os.remove(form.delete_file.data)
#                 # form_delete=DeleteForm(form2_name='DeleteFormName')
#
#             # *** Имя исполняемого файла
#             # так можем получить имя и путь исполняемого (этого файла в котором находимся) файл
#             # Нам это здесь не нужно. Оставим просто для инфо
#             # import inspect, os.path
#             # filename = inspect.getframeinfo(inspect.currentframe()).filename
#             # print('filename-', filename)
#             # path = os.path.dirname(os.path.abspath(filename))
#             # print('path-', path)
#             # *** Имя исполняемого файла - конец
#
#
#             # Данный редирект нужен для сброса данных POST запроса после отправки формы
#             # и предотвращения повторной загрузки файла при обновлении страницы
#             # Можно сделать 2 вариантами: 1- редирект на отдельный роут(сделала в views.py)
#             # return redirect('/sbroschoice2/')
#             # 2 вариант(оставим его) - редирект на функцию этой страницы (саму себя)
#
#             return redirect(url_for('choice2.choice2'))
#         return render_template('admin/choice2.html', form=form, form_delete=form_delete)
#
#
#     @app.route('/_get_usl_choice2_admin/')
#     def _get_usl_choice2_admin():
#         menu = request.args.get('menu', '01', type=str)
#         uslugschoice2 = [(usluga.id, usluga.title) for usluga in Usluga.query.filter_by(punkt_menu_id=menu).order_by('title').all()]
#         # print ('uslugschoice2 from admin=', uslugschoice2)
#         return jsonify(uslugschoice2)
#
#
#     # Выбор из выпадающего списка на основании выбора предыдущего
#     # для удаления файлов. Выбор работает, само удаление НЕТ!!
#     @app.route('/_get_files_choice2_admin/')
#     def _get_files_choice2_admin():
#         usluga = request.args.get('usluga', '01', type=str)
#         print(usluga)
#         fileschoice2 = [(files.id, files.secure_name_photo) for files in UploadFileMy.query.filter_by(usluga=usluga).all()]
#         print ('fileschoice2 from admin=', fileschoice2)
#         return jsonify(fileschoice2)


# Выбор из выпадающего списка с обновлением другого списка, формирование
# пути загрузки файла на основе выбора + загрузка файла + запись в базу - конец
# ******
# ****** Класс Choice2 - конец
# ****** Класс Choice2 - перенесла в fotomanager.py - конец

# Класс настроек админ.(SettingAdminForAllRoles), общих для всех ролей
# Наследуется от базового класса ModelView, поэтому при создании представлений моделей
# в админ панели нужно будет указать уже класс SettingAdminForAllRoles
# Остальные (индивидуальные) настройки для разных моделей и ролей планируем создавать
# с помощью классов SpecificView(SettingAdminForAllRoles) и MyUser, MyRole  и тд
class SettingAdminForAllRoles(ModelView):

    # ***
    # Данные настройки разрешений на операции CRUD действуют по умолчанию для всех ролей,
    # если администратором не задана специфическая настройка для роли и модели в SettingAdmin
    # Они должны быть все False!!, но пока временно все True

    # Активировать False после настройки ОБЯЗАТЕЛЬНО- начало!!

    # can_create = False
    # can_edit = False
    # can_delete = False
    # can_export = False

    can_create = True
    can_edit = True
    can_delete = True
    can_export = True

    # Активировать False после настройки - конец!!
    # ***

    # export_types - Задает формат экспорта строк
    # (если впоследствии для данной роли экспорт будет разрешен)
    # Если export_types явно не указан - по умолчанию экспортирует в csv
    # Чтобы использовать другие форматы кроме csv понадобилось инсталлировать Tablib
    # https://tablib.readthedocs.io/en/stable/
    # $ pip install "tablib[all]"
    # Можно инсталлировать выборочно определенные форматы например $ pip install "tablib[xlsx]"
    # Я инсталлировала все форматы
    # Форматы, которые поддерживает Tablib
    # cli, csv,dbf, df (DataFrame), html, jira, json, latex, ods, rst, tsv, xls, xlsx, yaml
    export_types = ['csv', 'xls', 'html', 'json']

     # Определяет, должен ли первичный ключ отображаться в представлении списка.
    column_display_pk = True

    # Добавляет столбцы-отношения
    # Можно ли вынести в общие? т.к.не понятно как отражается в зависимости от видов отношений
    # в моделях(один к одному, один ко многим, многие ко многим?)
    # Ранее читала что эту настройку можно применять только к отношению один ко многим.
    # Верно ли это? Уточнять!!!
    # Пока оставлю здесь. Если для всех не применима, значит выносить в класс
    # SettingAdmin в файле models.py
    column_display_all_relations = True

    # ???
    # column_hide_backrefs = True
    # column_hide_backrefs = False

    # Позволяет выбрать кол-во строк-записей из базы на стр. с помощью выпадающего списка
    can_set_page_size = True

    # Редактирование в модальном окне, а не на отдельной странице
    edit_modal = True

    # Создание новой записи в модальном окне, а не на отдельной странице
    create_modal = True

    # Удалить столбцы из списка (будем этот параметр задавать в классах, специфических для
    # модели (MyUser, MyRole и тп)
    # column_exclude_list = ['password']

    # Изменение наименований столбцов из моделей базы на "удобоваримые"
    # Данная настройка позволяет в общий список поместить наименования столбцов из разных моделей,
    # поэтому ее можно использовать в SettingAdminForAllRoles, но можно ее применить для каждого
    # класса, специфического для модели(MyUser, MyRole и тд)
    # Мы будем ее применять в индивидуальных классах (MyUser, MyRole и тд)
    # column_labels = dict(uslugs='Услуги', punkt_menu='Пункт меню', roles='роли', orders='заказы')

    # ****
    # Класс формы. Переопределите, если вы хотите использовать
    # пользовательскую форму для своей модели.
    # Полностью отключит остальную функциональность форм!!!!
    # Перед этим нужно создать класс формы(у нас MyForm (см выше)
    # унаследовать его от FlaskForm(тк мы используем flask_wtf
    #  (в документации просто Form - можно использовать что-то другое видимо)
    # и сделать импорты
    # from flask_wtf import FlaskForm
    # from wtforms import StringField
    # Эта форма появляется при нажатии редактирования строки модели
    # и содержит поле ввода Name
    #
    # form = MyForm

    # Позволяет добавить дополнительное поле в форму редактирования
    # Как сохранить инфу, введенную в этом поле?
    # form_extra_fields = {
    #                 'строка комментарии': StringField('комментарии')
    #             }
    # ****

# Настройки, кот.задает суперадмин в модели SettingAdmin в зависимости от роли и модели
# Это разрешения на создание, редактирование, удаление, экспорт, кол-во экспортируемых столбцов
# По умолчанию все разрешения CRUD равны False. Это задано в SettingAdminForAllRoles(ModelView)
# Поэтому если нужно выдать разрешение на определенные действия для определенной модели и роли
# нужно создать настройку. А в дальнейшем эти специфические настройки будут родителями настроек
# для разных моделей MyUser и тд
class SpecificView(SettingAdminForAllRoles):
    def _handle_view(self, name, **kwargs):
        settings_for_role = {}
        can_edit_1 = False
        can_create_1 = False
        can_delete_1 = False
        can_export_1 = False
        export_max_rows_1 = 0
        for i in range(len(current_user.roles)):
            settings_for_role[i] = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[i]).all()
            for j in range(len(settings_for_role[i])):
                path = '/admin/'+str(settings_for_role[i][j].model).lower()+'/'
                if request.full_path.startswith(path):
                    # print('path1=', path)
                    # print(settings_for_role[i][j].name_setting, settings_for_role[i][j].model, path,  'can_edit=', settings_for_role[i][j].can_edit, 'can_create=', settings_for_role[i][j].can_create, 'can_delete=', settings_for_role[i][j].can_delete, 'can_export=', settings_for_role[i][j].can_export, 'export_max_rows=', settings_for_role[i][j].export_max_rows )
                    self.can_edit = settings_for_role[i][j].can_edit or can_edit_1
                    self.can_create = settings_for_role[i][j].can_create or can_create_1
                    self.can_delete = settings_for_role[i][j].can_delete or can_delete_1
                    self.can_export = settings_for_role[i][j].can_export or can_export_1
                    if settings_for_role[i][j].export_max_rows == None:
                        self.export_max_rows = export_max_rows_1
                    else:
                        if export_max_rows_1 <= settings_for_role[i][j].export_max_rows:
                            self.export_max_rows = settings_for_role[i][j].export_max_rows
                        else:
                            self.export_max_rows = export_max_rows_1
                    can_edit_1 = self.can_edit
                    can_create_1 = self.can_create
                    can_delete_1 = self.can_delete
                    can_export_1 = self.can_export
                    export_max_rows_1 = self.export_max_rows
                    # print('path', path)

        # print('Настройка для пути=', path, 'can_edit=', self.can_edit, 'can_create=', self.can_create, 'can_delete=', self.can_delete, 'can_export=', self.can_export, 'export_max_rows=', self.export_max_rows )
        # print('Итоговая настройка', 'can_edit=', self.can_edit, 'can_create=', self.can_create, 'can_delete=', self.can_delete, 'can_export=', self.can_export, 'export_max_rows=', self.export_max_rows )


# *****
# Остальные настройки, специфичные для определенных моделей и ролей из файла models.py

class MyUploadFileMy(SpecificView):

    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin'):
            return True
    # *** def is_visible(self): -Делаем модель  видимой только для определенных ролей - конец

class UserView(SpecificView):

    # ***** column_list - начало
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка,
    # но тогда порядок столбцов в админке будет произвольный)
    # column_list = ['id', 'roles', 'email', 'active', 'confirmed_at', 'created_on', 'updated_on', 'orders']

    # Для того, чтобы задать разный column_list в зависимости от роли,\
    # необходимо переопределить _list_columns.
    # Это приватный аргумент, в который кэшируется  column_list
    # Попытка воспользоваться функцией def _handle_view (как в SpecifiView) не дает результата!
    # так как некоторые настройки  (например column_list) кэшируются в приватные аргументы,
    # и переопределять надо их!!!
    # # def _handle_view(self, name, **kwargs): - Это не работает!!!!
    # #     if current_user.has_role('superadmin'):
    # #         column_list = ['id', 'roles', 'email', 'active', 'confirmed_at', 'created_on', 'updated_on', 'orders']
    # #         self.list_columns = column_list
    # решение - https://progi.pro/flask-admin-razlichnie-formi-i-column_list-dlya-raznih-roley-4053295
    # Это и другие кеширования см.:
    # https://github.com/flask-admin/flask-admin/blob/master/flask_admin/model/base.py#L876%23L876
    # has_app_context метод необходим здесь, потому что первый column_list чтение
    # произошло при запуске приложения,
    # когда  current_user переменная не имеет значимое значения пока

    @property
    def column_list(self):
        if has_app_context() and current_user.has_role('superadmin'):
            # superadmin_column_list = ['id', 'roles', 'email', 'active', 'confirmed_at', 'created_on', 'updated_on', 'orders', 'phones', 'password']
            superadmin_column_list = ['id', 'active', 'email', 'roles', 'orders', 'orders_manager',
                                      'orders_items',
                                      'user_last_name', 'user_first_name', 'user_middle_name',
                                        'created_on', 'updated_on', 'confirmed_at', 'phones', 'payers']
            return superadmin_column_list
        if has_app_context() and current_user.has_role('admin'):
            admin_column_list = ['id', 'active', 'email', 'roles', 'created_on']
            return admin_column_list
        if has_app_context() and current_user.has_role('manager'):
            manager_column_list = ['id', 'active', 'email']
            return manager_column_list
        user_column_list = ['active', 'email']
        return user_column_list

    @property
    def _list_columns(self):
        return self.get_list_columns()

    @_list_columns.setter
    def _list_columns(self, value):
        pass
    # ***** column_list - конец


    # *** column_exclude_list-Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['password']
    # *** column_exclude_list- Удалить столбцы из списка - конец


    # *** column_labels - Присвоить столбцам из модели заголовки - начало
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения. , orders='Заказы'
    column_labels = dict(user_first_name='Имя',
                         user_middle_name='Отчество',
                         user_last_name='Фамилия',
                         email='Логин(e-mail)',
                         orders ='Собственные заказы',
                         orders_manager='Отвечает за заказы',
                         orders_items='Отвечает за определенный этап(статус) элемента заказа',
                         confirmed_at='Подтвержден',
                         created_on='Создан',
                         updated_on='Обновлен',
                         active='Активен',
                         roles='Роли',
                         phones='Тел.',
                         payers='Плательщики')
   # *** column_labels - Присвоить столбцам из модели заголовки - конец

    # **** column_display_all_relations- Добавляет столбцы-отношения - начало
    #  - задаем в SettingAdminForAllRoles
    # column_display_all_relations = True
    # **** column_display_all_relations- Добавляет столбцы-отношения - конец

    # *** column_searchable_list- Задает поля, в которых возможен поиск по словам - начало
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не roles а roles.name, не 'orders' а 'orders.order'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView  'orders.order',
    column_searchable_list = ['id', 'orders.number', 'orders_manager.number',
                              'orders_items.id',
                              'user_first_name', 'user_middle_name', 'user_last_name',
                              'roles.name', 'email', 'active',
                              'confirmed_at', 'created_on', 'updated_on',
                              'phones.phone', 'payers.id']
    # *** column_searchable_list- Задает поля, в которых возможен поиск по словам - конец

    # *** column_filters - Задает поля, в которых возможна булева фильтрация - начало
    # column_filters = (BooleanEqualFilter(column=User.active, name='active'),)
    # *** column_filters - Задает поля, в которых возможна булева фильтрация - конец

    # *** column_filters - Задает поля, в которых возможна фильтрация - начало
    # (выбирается столбец, в кот. осyществляется поиск
    # (по ключевому слову например или по булеву значению))
    # Если включить отношение к Role ('roles'),
    # то в выпадающем списке AddFilter кроме имени, роли, описания, id
    # увидим и все поля модели Role(например name, description и тп)
    # и следовательно можно искать те роли в которых например name содержит сочетание ad и тп)
    # column_filters = ['id', 'user_first_name', 'email', 'active', 'password', 'confirmed_at', 'created_on', 'updated_on', 'roles', 'orders', 'phones']
    column_filters = ['id', 'user_first_name', 'user_middle_name', 'user_last_name', 'email',
                      BooleanEqualFilter(column=User.active, name='active'),
                      'password', 'confirmed_at', 'created_on',
                      'updated_on', 'roles', 'phones', 'payers',
                      'orders_items']
    # *** column_filters - Задает поля, в которых возможна фильтрация - конец

    # *** column_sortable_list- Задает поля, в которых возможна сортировка - начало
    # (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # так как при включении просто roles или orders при попытке сортировки выдаст ошибку
    # поскольку, видимо, ролей и заказов может быть несколько и, следовательно,
    # не понятно как сортировать???
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView ('orders', 'orders.order'),
    column_sortable_list = ['id', ('orders', 'orders.number'),
                            ('orders_manager', 'orders_manager.number'),
                            ('orders_items', 'orders_items.id'),
                            'user_first_name', 'user_middle_name',
                            'user_last_name',
                            ('roles', 'roles.name'),
                            ('phones', 'phones.phone'), 'email', 'active', 'confirmed_at', 'created_on', 'updated_on' ]
    # *** column_sortable_list- Задает поля, в которых возможна сортировка - конец


    # *** column_editable_list - Задает поля, в кот. возможно БЫСТРОЕ редактирование - начало
    # (то есть при нажатии на это поле)
    # id не включать!!!
    # Однако при использовании  scaffold_form() и  update_model(self, form, model) - см ниже
    # перестал работать!!! (Редактирование в обычной форме работает!)
    # Причину не выяснила, поэтому отключаю в данной модели!!!
    # column_editable_list = ['active']
    # *** column_editable_list - Задает поля, в кот. возможно БЫСТРОЕ редактирование - конец

# ****** form_edit_rules - Задает форму для редактирования. - начало
    # 1) Если 'id' включен, то редактирование дает ошибку
    # 2) Если не задать то по умолчанию доступны для редактирования все поля
    # 3) если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    # 4) Для того чтобы задать в форме разные поля в зависимости от роли
    # необходимо переопределить _form_edit_rules.
    # Это приватный аргумент, в который кэшируется  form_edit_rules
    # см. https://stackoverflow.com/questions/63337371/flask-admin-how-to-set-form-edit-rules-or-form-create-rules-based-on-role-of-u
    # Используем свойства # пункты 1., 2., 3.
    # 5) Кроме того включили в форму поля для сброса и смены пароля суперадмином
    # (остальным ролям редактирование юзеров не доступно либо своя (урезанная) форма редактирования)
    # Этих полей в исходной модели юзера не было!!!
    # Поэтому ПОСЛЕ СВОЙСТВ (propety) изменяем форму с помощью scaffold_form()
    # и меняем модель с помощью update_model(self, form, model) - см ниже
    # https://russianblogs.com/article/37171301805/

    # пункт 1.
    @property
    def _form_edit_rules(self):
        return rules.RuleSet(self, self.form_edit_rules)

    # пункт 2.
    @_form_edit_rules.setter
    def _form_edit_rules(self, value):
        pass

    # пункт 3.
    @property
    def form_edit_rules(self):
        #  Если return () - то порядок в форме будет тот что указан в списке
        #  Если return {} - то порядок в форме будет произвольный
        if not has_app_context() or current_user.has_role('superadmin'):
            # Если включала в return поля 'created_on' и 'updated_on', вот так:
            # return ('roles', 'email', 'active', 'created_on', 'confirmed_at', 'updated_on',
            #            'orders', rules.Header('Сбросить пароль'), 'new_password', 'confirm')
            # то возникала ошибка при входе в редактирование юзера в админке - серый экран
            # из-за default=datetime.utcnow (см модель юзера). Почему - не знаю. Исключила - работает.
            # 'orders',
            return ('roles', 'orders', 'orders_items', 'orders_manager',
                    'user_first_name', 'user_middle_name', 'user_last_name',
                    'phones', 'email', 'active',
                       rules.Header('Сбросить пароль'), 'new_password', 'confirm')
        # В этом выводе тоже самое - см выше ошибка из-за 'created_on'
        # return ('roles', 'email', 'active', 'created_on') - не работает
        # return ('roles', 'email', 'active') - работает
        # решила сделать всем кроме superadmin редактирование пустым, поэтому return ()
        return ()

    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password = PasswordField("Password")
        form_class.new_password = PasswordField('Новый пароль')
        form_class.confirm = PasswordField('Повторить новый пароль')
        # Проверку длины пароля (пока только это, можно позже добавить другие проверки)
        # реализовали в функции def update_model(self, form, model) см.ниже,
        # так как если проверять с помощью встроенных валидаторов то не дает сохранить остальные
        # изменения без сброса пароля и введения нового пароля
        # form_class.password = PasswordField("Password", [InputRequired(), Length(min=password_length, message="Пароль должен быть не менее " + str(password_length) +" символов")])
        # form_class.new_password = PasswordField('Новый пароль', [InputRequired(), Length(min=password_length, message="Пароль должен быть не менее " + str(password_length) +" символов")])
        # form_class.confirm = PasswordField('Повторить новый пароль', [InputRequired(), Length(min=password_length, message="Пароль должен быть не менее " + str(password_length) +" символов")])
        return form_class

    def update_model(self, form, model):
        form.populate_obj(model)
        # Изменение пароля (для чего мы и меняем и обновляем форму) в нашем приложении
        # разрешено только суперадмину, поэтому проверяем условие суперадмин или нет.
        # Если не наложить это условие при попытке редактирования модели User для других ролей
        # будет выдавать ошибку
        # 'NoneType' object has no attribute 'data'так как полей смены пароля у них нет!!!
        if current_user.has_role('superadmin'):
            # print('form.new_password.data)=', form.new_password.data)
            # print('type(form.new_password.data)=', type(form.new_password.data))
            # Если пароль не введен (то есть пустая строка), то запоминаем остальные изменения (кроме пароля)
            if form.new_password.data == '':
                self.session.add(model)
                self._on_model_change(form, model, False)
                self.session.commit()
                # print (form.active.data )
                # print('Изменения успешно сохранены. Пароль остался без изменений')
                flash('Изменения успешно сохранены. Пароль остался без изменений')
            # Если пароль введен, но короткий или новый пароль и его повтор не совпадают - выдает сообщение
            elif form.new_password.data and (form.new_password.data != form.confirm.data or len(form.new_password.data) < app.config['PASSWORD_MIN_LENGTH'] or len(form.new_password.data) > app.config['PASSWORD_MAX_LENGTH']):
            # elif form.new_password.data and (form.new_password.data != form.confirm.data or len(form.new_password.data) < password_length):
                # print('Пароли не совпадают или длина пароля менее '+ str(password_length) + ' символов')
                # flash('Пароли не совпадают или длина пароля менее '+ str(password_length) + ' символов')
                flash(message="Пароль должен быть не менее " + str(app.config['PASSWORD_MIN_LENGTH']) +' и не более ' + str(app.config['PASSWORD_MAX_LENGTH'])+" символов")
            # Если пароль введен, и он длинный и новый пароль и его повтор совпадают -
            # сохраняем кэшированный новый пароль и все остальное в базу и не меняем модель
            else:
                model.password = generate_password_hash(form.new_password.data)
                # Это (без хэша) оставляю пока для удобства проверки
                # model.password = form.new_password.data
                self.session.add(model)
                self._on_model_change(form, model, False)
                self.session.commit()
                # print('Изменения (в том числе новый пароль) успешно сохранены')
                flash('Изменения (в том числе новый пароль) успешно сохранены')
        else:
            self.session.add(model)
            self._on_model_change(form, model, False)
            self.session.commit()

# ****** form_edit_rules - Задает форму для редактирования. - конец


    # **** form_create_rules = ()- Форма создания пользователя - начало
    # В нашем сервисе НЕЛЬЗЯ создать пользователя из админки.
    # Для этого мы задаем form_create_rules = ()
    # Но если просто указать пустой список, то в форме создания появится все,
    # что по умолчанию плюс те поля которые мы определили ранее
    # в def scaffold_form(self) и обновили в def update_model(self, form, model)
    # Поэтому мы снова применим способ с свойствами (пункты 11, 22, 33)
    # но уже не будем в пункте 33 устанавливать зависимость от роли или контекста
    # В принципе можно запретить создание пользователя и с помощью создания настроек
    # class SpecificView(SettingAdminForAllRoles),
    # но если вдруг все-таки кто-то разрешит создание, то пароль будет записан без хэша,
    # т.к. эта функция не реализована через админку (и не нужна). Если разрешать создание юзера
    # через админку надо реализовывать хеширование и валидацию пароля.
    # Поэтому задание пустой формы создания пользователя является подстраховкой
    # Пользователь в сервисе создается на общих основаниях через кнопку Войти! (блюпринт регистрации)
    # Там реализованы и хеширование и валидация пароля

    # пункт 11.
    @property
    def _form_create_rules(self):
        return rules.RuleSet(self, self.form_create_rules)

    # пункт 22.
    @_form_create_rules.setter
    def _form_create_rules(self, value):
        pass

    # пункт 33.
    @property
    def form_create_rules(self):
        return ()
    # **** form_create_rules = ()- Форма создания пользователя - конец

    # *** def is_visible(self): -Делаем модель User видимой только для определенных ролей - начало


    def is_visible(self):
        if current_user.has_role('admin') or current_user.has_role('superadmin') or current_user.has_role('manager'):

            return True


    # *** def is_visible(self): -Делаем модель User видимой только для определенных ролей - конец

class RoleView(SpecificView):
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
    column_list = ['id', 'name', 'description', 'setting', 'users']

    # Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['']

    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    column_labels = dict(name='Роль', description='Описание', setting='Список настроек с ролью')

    # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
    # column_display_all_relations = True


    # Определяет, должен ли первичный ключ отображаться в представлении списка - задаем в SettingAdminForAllRoles
    # column_display_pk = True

    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не roles а roles.name, не 'orders' а 'orders.order'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # В данном случае все закоментированные варианты выдают ошибку(видимо потому,
    # что название настройки определено гибридным свойством) и этот столбец исключаю из сортировки
    # Разобраться!!!
    # column_searchable_list = ['id', 'name', 'description', ('setting', 'SettingAdmin.name_setting')]
    # column_searchable_list = ['id', 'name', 'description', ('setting', 'setting.name_setting')]
    # column_searchable_list = ['id', 'name', 'description', 'setting.name_setting']
    # column_searchable_list = ['id', 'name', 'description', 'setting']
    column_searchable_list = ['id', 'name', 'description']

    # Задает поля, в которых возможна фильтрация (выбирается столбец
    # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к настройкам SettingAdmin ('setting'),
    # то в выпадающем списке AddFilter кроме имени, роли, описания, id
    # увидим и все поля модели SettingAdmin(например can_create, can_delete и тп)
    # и следовательно можно искать те роли в которых например can_create = True)
    # column_filters = ['id', 'name', 'description']
    column_filters = ['id', 'name', 'description', 'setting']


    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # так как при включении просто roles или orders при попытке сортировки выдаст ошибку
    # поскольку, видимо, ролей и заказов может быть несколько и, следовательно,
    # не понятно как сортировать???
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # column_sortable_list = ['id', 'name', 'description', ('setting', 'setting.name_setting')]
    column_sortable_list = ['id', 'name', 'description', ('users', 'users.email')]

    # Задает редактируемые поля.
    # Если не задать то по умолчанию доступны для редактирования все поля
    # Если 'id' включен, то редактирование дает ошибку
    # если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    form_edit_rules = {'name', 'description'}

    # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
    # id не включать!!!
    # В данном случае включать не будем (хотя работает) так как встроенное поле
    # быстрого редактирования маленькое и редактировать длинное описание не удобно
    # column_editable_list = ['name', 'description']

    # Переопределите этот метод, если вы хотите динамически скрывать или
    # показывать административные представления из структуры меню Flask-Admin
    # По умолчанию пункт отображается в меню.
    # Обратите внимание, что пункт должен быть как видимым, так и доступным для отображения в меню.
    # По умолчанию возвращает True
    # Если False то заданные представления
    # не будут показаны в панели при заданных условиях (напрмер при определенной роли)
    # В нашем случае модель Role будет доступна только админу и суперадмину



    def is_visible(self):
        # if current_user.has_role('admin') or current_user.has_role('superadmin'):
        if current_user.has_role('superadmin') or current_user.has_role('admin'):
            return True



    # либо скрыть модель из админки можно методом is_accessible(self)
    # Мы оставим is_visible()
    # def is_accessible(self):
    #     return (current_user.has_role('manager'))

class PayerView(SpecificView):
    column_list = ['id', 'name', 'user', 'payer_status', 'payer_info']
    column_labels = dict(user='Пользователь',
                         name='Имя плательщика',
                         payer_status='Статус плательщика(юр или физ)',
                         payer_info='Инфо о плательщике')
    column_searchable_list = ['id', 'name', 'user.email', 'payer_status', 'payer_info']
    column_sortable_list = ['id', 'name', ('user', 'user.email'), 'payer_status']
    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin'):
            return True

class MyListModel(SpecificView):
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
    column_list = ['id', 'name_model', 'setting']

    # Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['']

    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    column_labels = dict(name_model='Модель(name_model)',
                         setting='Список настроек с моделью(setting)')

    # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
    # column_display_all_relations = True

    # Определяет, должен ли первичный ключ отображаться в представлении списка - задаем в SettingAdminForAllRoles
    # column_display_pk = True

    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не roles а roles.name, не 'orders' а 'orders.order'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # В данном случае все закоментированные варианты выдают ошибку(видимо потому,
    # что название настройки определено гибридным свойством) и этот столбец исключаю из сортировки
    # Разобраться!!!
    # column_searchable_list = ['id', 'name_model', ('setting', 'SettingAdmin.'setting.model'')]
    # column_searchable_list = ['id', 'name_model', ('setting', 'setting.model')]
    # column_searchable_list = ['id', 'name_model', 'setting.model']
    # column_searchable_list = ['id', 'name_model', setting']
    # column_searchable_list = ['id', 'name_model', 'setting.name_setting'
    column_searchable_list = ['id', 'name_model']

    # Задает поля, в которых возможна фильтрация (выбирается столбец
    # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к настройкам SettingAdmin ('setting'),
    # то в выпадающем списке AddFilter кроме имя модели, id
    # увидим и все поля модели SettingAdmin(например can_create, can_delete и тп)
    # и следовательно можно искать те роли в которых например can_create = True)
    # Но в нашем случае это делать не будем!!!! Оставим фильтр простой
    column_filters = ['id', 'name_model']

    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # ('setting', 'setting.model')
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    column_sortable_list = ['id', 'name_model', ('setting', 'setting.model')]

     # Задает редактируемые поля.
    # Если не задать то по умолчанию доступны для редактирования все поля
    # Если 'id' включен, то редактирование дает ошибку
    # если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    form_edit_rules = {'name_model'}

    # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
    # id не включать!!!
    column_editable_list = ['name_model']

    # Переопределите этот метод, если вы хотите динамически скрывать или
    # показывать административные представления из структуры меню Flask-Admin
    # По умолчанию пункт отображается в меню.
    # Обратите внимание, что пункт должен быть как видимым, так и доступным для отображения в меню.
    # По умолчанию возвращает True
    # Если False то заданные представления
    # не будут показаны в панели при заданных условиях (напрмер при определенной роли)
    # В нашем случае модель Role будет доступна только админу и суперадмину
    def is_visible(self):
        # if current_user.has_role('admin') or current_user.has_role('superadmin'):
        if current_user.has_role('superadmin'):
            return True

    # либо скрыть модель из админки можно методом is_accessible(self)
    # Мы оставим is_visible()
    # def is_accessible(self):
    #     return (current_user.has_role('manager'))

class MySettingAdmin(SpecificView):
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
    column_list = ['id', 'role', 'model', 'name_setting', 'can_create', 'can_edit', 'can_delete', 'can_export', 'export_max_rows']

    # Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['']

    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    column_labels = dict(name_setting='Имя настройки(name_setting)', can_create='can_create', can_edit='can_edit', can_delete='can_delete', can_export='can_export', export_max_rows='export_max_rows', role='Роль', model='Модель')

    # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
    # column_display_all_relations = True

    # Определяет, должен ли первичный ключ отображаться в представлении списка - задаем в SettingAdminForAllRoles
    # column_display_pk = True

    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не role а role.name, не 'model' а 'model.name_model'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # В данном случае все закоментированные варианты выдают ошибку(видимо потому,
    # что название настройки определено гибридным свойством) и этот столбец исключаю из сортировки
    # Включение 'name_setting' или ('name_setting', 'role.name', 'model.name_model')
    # дает ошибку   Разобраться!!!
    column_searchable_list = ['id', 'role.name', 'model.name_model', 'can_create', 'can_edit', 'can_delete', 'can_export', 'export_max_rows']

    # Задает поля, в которых возможна фильтрация (выбирается столбец
    # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к настройкам SettingAdmin ('setting'),
    # то в выпадающем списке AddFilter кроме имя модели, id
    # увидим и все поля модели SettingAdmin(например can_create, can_delete и тп)
    # и следовательно можно искать те роли в которых например can_create = True)
    column_filters = ['id', 'role.name', 'model.name_model', 'can_create', 'can_edit', 'can_delete', 'can_export', 'export_max_rows']

    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не role а role.name, не 'model' а 'model.name_model'
    # Включение 'name_setting' работает только при такой записи
    # ('name_setting', 'role.name', 'model.name_model')
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # Разбираться с гибридными свойствами в SettingAdmin
    column_sortable_list =['id', ('role', 'role.name'), ('model', 'model.name_model'), ('name_setting', 'role.name', 'model.name_model'), 'can_create', 'can_edit', 'can_delete', 'can_export', 'export_max_rows']

     # Задает редактируемые поля.
    # Если не задать то по умолчанию доступны для редактирования все поля
    # Если 'id' включен, то редактирование дает ошибку
    # если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    # Если включить ('name_setting' или, ('name_setting', 'role.name', 'model.name_model'),
    # выдает ошибку. Но редактировать название и или модель и роль не требуется!!!!
    form_edit_rules = {'can_create', 'can_edit', 'can_delete', 'can_export', 'export_max_rows'}

    # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
    # id не включать!!!
    column_editable_list = ['can_create', 'can_edit', 'can_delete', 'can_export']

    # Переопределите этот метод, если вы хотите динамически скрывать или
    # показывать административные представления из структуры меню Flask-Admin
    # По умолчанию пункт отображается в меню.
    # Обратите внимание, что пункт должен быть как видимым, так и доступным для отображения в меню.
    # По умолчанию возвращает True. Если False то заданные представления
    # не будут показаны в панели при заданных условиях (напрмер при определенной роли)
    # В нашем случае модель Role будет доступна только админу и суперадмину
    def is_visible(self):
        # if current_user.has_role('admin') or current_user.has_role('superadmin'):
        if current_user.has_role('superadmin'):
            return True

    # либо скрыть модель из админки можно методом is_accessible(self)
    # Мы оставим is_visible()
    # def is_accessible(self):
    #     return (current_user.has_role('manager'))

class MyLink(SpecificView):

    # ВНИМАНИЕ!!! нужно определить функцию  def on_model_delete(self, model):
    # при каскадном удалении если есть карточки услуг с фото чтобы удалялись
    # и фото из файловой системы! (см MyCardUsluga) На 16/06/22 сделано


    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)

    column_list = ['id', 'title', 'link', 'comments_1', 'comments_2', 'comments_3', 'comments_4', 'count_uslugs', 'count_uslugs_in_model', 'uslugs']
    # Здесь count_uslugs - счетчик, создаваемый в админке!
    # а count_uslugs_in_link - счетчик создаваемый в модели (те атрибут модели)

    # Создадим счетчик кол-ва услуг - начало!
    # Он нужен чтобы в админке не перечислять все услуги(их может быть много), а указать только их количество
    # https://translated.turbopages.org/proxy_u/en-ru.ru.a8edd97f-62d92535-0d2a131f-74722d776562/https/stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # В ссылке указаны 2 способа (один в модели(ответ), второй  в админке - оба работают!!!)
    # для них нужны импорты
    # from sqlalchemy.ext.hybrid import hybrid_property
    # from sqlalchemy import select, func

    def _count_formatter(view, context, model, name):
        return len(model.uslugs)

    column_formatters = {
        'count_uslugs': _count_formatter
    }
    # Создадим счетчик кол-ва услуг - конец!

    # Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['']

    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    column_labels = dict(title='Пункт меню (title)',
                         link='Путь (link)',
                         uslugs='Прикрепленные услуги (uslugs)',
                         count_uslugs='Кол-во услуг (из column_formatters)',
                         count_uslugs_in_model='Кол-во услуг(из модели)')

    # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
    # column_display_all_relations = True

    # Определяет, должен ли первичный ключ отображаться в представлении списка - задаем в SettingAdminForAllRoles
    # column_display_pk = True

    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не role а role.name, не 'model' а 'model.name_model'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # В данном случае все закоментированные варианты выдают ошибку(видимо потому,
    # что название настройки определено гибридным свойством) и этот столбец исключаю из сортировки
    # Включение 'uslugs' или 'uslugs.punkt_menu', ('uslugs', 'uslugs.punkt_menu')
    # дает ошибку   Разобраться!!!
    column_searchable_list = ['id', 'title', 'link']

    # Задает поля, в которых возможна фильтрация (выбирается столбец
    # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к настройкам SettingAdmin ('setting'),
    # то в выпадающем списке AddFilter кроме имя модели, id
    # увидим и все поля модели SettingAdmin(например can_create, can_delete и тп)
    # и следовательно можно искать те роли в которых например can_create = True)
    # column_filters = ['id', 'title', 'link', 'uslugs.punkt_menu']
    column_filters = ['id', 'title', 'link', 'uslugs.title']


    # Столбец сортировки по умолчанию, если сортировка не применяется.
    # column_default_sort = [('title', True)]
    column_default_sort = [('title', False)]

    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не role а role.name, не 'model' а 'model.name_model'
    # Включение 'name_setting' работает только при такой записи
    # ('name_setting', 'role.name', 'model.name_model')
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # Разбираться с гибридными свойствами в SettingAdmin
    # column_sortable_list =['id', 'title', 'link', ('uslugs', 'uslugs.punkt_menu')]
    # Если включать просто count_uslugs_in_model - гибридное из модели - ОШИБКА!! -
    # если включить ('count_uslugs_in_model', 'uslugs.title') - работает,
    # но это сортировка по имени услуги, а не по кол-ву услуг поэтому убрала из списка сортировки
    # РАЗБИРАТЬСЯ - на 25.07.22 не сделано!!!
    column_sortable_list =['id', 'title', 'link', ('uslugs', 'uslugs.title')]


    # Задает редактируемые поля.
    # id не включать!!!  Если 'id' включен, то редактирование дает ошибку
    # Если не задать то по умолчанию доступны для редактирования все поля
    # если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    # Если включить 'uslugs' или, ('uslugs', 'uslugs.punkt_menu'),
    # выдает ошибку. Но редактировать услуги не требуется!!!! Их редактируем в своей модели
    form_edit_rules = ['title', 'comments_1', 'comments_2', 'comments_3', 'comments_4']
    # исключила из списка редактирования link,
    # т.к. используется в директории загрузки фото в карточках услуг!!!
    # То есть при загрузке фото в карточку услуг фото загружается в
    # определенное место(директорию), зависящую от директориии меню и директории услуг.
    # Поэтому директорию запрещаю редактировать!!
    # form_edit_rules = ['title', 'comments_1', 'comments_2', 'comments_3', 'comments_4']

    form_create_rules = ['title', 'comments_1', 'comments_2', 'comments_3', 'comments_4']

    # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
    # id не включать!!!
    # column_editable_list = ['title', 'link', 'comments_1', 'comments_2', 'comments_3', 'comments_4']
    # исключила из списка редактирования link,
    # т.к. используется в директории загрузки фото в карточках услуг!!!
    # То есть при загрузке фото в карточку услуг фото загружается в
    # определенное место(директорию), зависящую от директориии меню и директории услуг.
    # Поэтому директорию запрещаю редактировать!!
    column_editable_list = ['title', 'comments_1', 'comments_2', 'comments_3', 'comments_4']



       # Функция def on_model_change выполнит некоторые действия перед созданием
    # или обновлением модели.
    # Вызывается из create_model и update_model в одной и той же транзакции
    # (если это имеет какое-либо значение для серверной части магазина).
    # По умолчанию ничего не делает.Параметры:
    #     form – Форма, используемая для создания/обновления модели
    #     model – Модель, которая будет создана/обновлена
    #     is_created — будет установлено значение True, если модель была создана, и значение False, если она была отредактирована .
    # def on_model_change см. https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions

    # Нам она нужна чтобы преобразовать вводимые пользователем данные
    # 1) в вид где первая буква строки имени заглавная (только в первом слове),
    # остальные прописные str.capitalize() (метод str.title() - все первые буквы ВСЕХ слов в строке заглавные )
    # см https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-title/
    # 2) преобразовать уникальное имя в путь, предварительно преобразовав его в латиницу
    # и затем задав нижний регистр
    # см https://docs-python.ru/packages/modul-transliterate-python/
    # Для этого инсталлировали модуль transliterate и использовали функцию translit

    def on_model_change(self, form, model, is_created):

        # Сделаем первую заглавную букву в заголовке меню
        model.title=model.title[0].capitalize()+model.title[1:]

        # Удалим лишние пробелы если есть (если один - оставляем, если 2 заменяем на 1)
        # https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-split/
        # https://tonais.ru/string/zamena-neskolkih-probelov-odnim-python
        model.title = " ".join(model.title.split())

        # Проблема 1 - начало
        # Путь меню (модель Link)в базе может совпасть с путем роута личного кабинета (например)
        # или др.произвольных стр. Тогда при нажатии на пункт меню переход на личный кабинет
        # (например) а не на стр.с услугами. Но тогда надо все такие возможные стр (их пути)
        # проверять. Это плохо.Поэтому изменила путь def render_menu с @app.route('/<punkt_menu>/')
        #  на @app.route('/раздел-меню/<punkt_menu>/') чтобы пути не пересеклись.
        # И тогда проверка и принудительное изменение пути перед записью в базе ниже не нужна.
        # if model.link=='profil':
        #     model.link=model.link + '2'
        # Проблема 1 - конец

        # *** Сформируем путь меню из имени - начало

        # путь меню из имени title хотим  формировать один раз,
        # только при создании экземпляра модели и не изменять его при изменении
        # имени пункта меню, тк фото в карточках услуг загружаются в директорию,
        # путь которой состоит в том числе из пути меню.
        # Для этого понадобится параметр функции def on_model_change(self, form, model, is_created)
        # is_created который == True если экземпляр модели создается
        # и ==False - если изменяется.

        if is_created:

            # Преобразуем русские буквы в латиницу и переведем в нижний регистр
            model.link=translit(model.title, language_code='ru', reversed=True).lower()

            # re.search(r'[^a-zA-Z]', model.link) возвращает объект, если есть несовпадения
            # Если текст полностью соответствует шаблону (у нас латинские буквы) - то выдает None

            # **** Проверка на символы типа #$&$^%*&|/ - начало
            # Если символы в строке model.link, заданных юзером не a-zA-Z0-9\s- (регулярка),
            # где \s -символ пробела экранированный
            # тогда удаляем их из model.link и проверяем чтобы не стало пустой строкой
            new_model_link=''
            for i in list(model.link):
                if re.fullmatch(r'^[a-zA-Z0-9\s-]+$', i):
                    new_model_link=new_model_link + i

            # заменим пробелы на '_' (то есть если заголовок меню из двух слов напрмер)
            new_model_link = "_".join(new_model_link.split())

            # заменим все '-' на пробелы
            new_model_link = " ".join(new_model_link.split('-'))
            # заменим пробелы идущие подряд на 1 '-'
            new_model_link = "-".join(new_model_link.split())


            if len(new_model_link)>=1:
                model.link=new_model_link
            else:
                # Если в заданном юзером пути нет символов, соответствующих шаблону регулярки
                # то в результате преобразований длина пути становится равна 0.
                # Поэтому задаем время загрузки файла в качестве пути загрузки (пока так)
                # для этого импортировали модуль datetime
                # replace(microsecond=0) - чтобы отсечь миллисекунды
                # replace(':', '-') - чтобы заменить : тк может в файловой системе создать проблемы
                uniq_time = 'menu_link-'+ str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')

                model.link=uniq_time
            # **** Проверка на символы типа #$&$^%*&|/ - конец

            # *** Сформируем путь меню из имени - конец


     # При удалении раздела меню в файловой системе в карточках услуг остается пустая директория,
    # если были карточки услуг с фото в этом разделе меню, но их удалили
    # Мы хотим удалить эти пустые директории
    # Для этого используем функцию on_model_delete (которая сама по себе ничего не делает)
    # Функция on_model_delete ( модель ) Выполнит некоторые действия ПЕРЕД удалением модели.
    # Вызывается из delete_model в той же транзакции (если это имеет какое-либо значение для бэкенда магазина).
    # По умолчанию ничего не делает.
    # см https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions

    def on_model_delete(self, model):
        # Формируем путь для удаления папки в карточках услуг в файловой системе
        # (если она пуста после удаления всех карточек услуг)
        path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + str(model.link)

        # Проверяем что такая директория существует
        # (она существует если в ней были карточки услуги с фото и карточка удалена).
        # Если карточек не было то такой директории не должно было существовать.
        # Для проверки используем модуль pathlib  -  from pathlib import Path
        # https://docs-python.ru/standart-library/modul-pathlib-python/opredelit-tip-puti-fajlovoj-sistemy-fajl-katalog-ssylka/
        is_dir=Path(path_delete).is_dir()
        # print(is_dir)
        if not model.uslugs and is_dir==True:
            # Удаляем папку со всем содержимым
            # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
            shutil.rmtree(path_delete)
            # или можно так: -удаляем каждое фото отдельно, но тогда надо потом удалять пустую папку)
            # for photo in model.photos:
            #     # Формируем путь для удаления файла
            #     path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + photo.dir_uploads + photo.secure_name_photo
            #     os.remove(path_delete)


    # Переопределите этот метод, если вы хотите динамически скрывать или
    # показывать административные представления из структуры меню Flask-Admin
    # По умолчанию пункт отображается в меню.
    # Внимание! Пункт должен быть как видимым, так и доступным для отображения в меню.
    # По умолчанию возвращает True. Если False то заданные представления
    # не будут показаны в панели при заданных условиях (напрмер при определенной роли)
    # В нашем случае модель будет доступна только этим ролям
    def is_visible(self):
        if current_user.has_role('admin') or current_user.has_role('superadmin') or current_user.has_role('editor'):
            return True

    # либо скрыть модель из админки можно методом is_accessible(self)
    # Мы оставим is_visible()
    # def is_accessible(self):
    #     return (current_user.has_role('manager'))

    # ********

    # Загрузка файла в модальном окне админки, картинки - начало
    # https://dev-gang.ru/article/flask-admin-zagruzka-faylov-i-obrabotka-formy-v-modeli/

    # Первая же строка form_extra_fields создает ошибку при попытке создать новую запись
    # в меню сайта(модель link)
    # form_extra_fields = {
    #     'file': form.FileUploadField('file')
    # }
    #
    # def _change_path_data(self, _form):
    #     try:
    #         storage_file = _form.file.data
    #
    #         if storage_file is not None:
    #             hash = random.getrandbits(128)
    #             ext = storage_file.filename.split('.')[-1]
    #             path = '%s.%s' % (hash, ext)
    #
    #             storage_file.save(
    #                 os.path.join(app.config['STORAGE'], path)
    #             )
    #
    #             _form.name.data = _form.name.data or storage_file.filename
    #             _form.path.data = path
    #             _form.type.data = ext
    #
    #             del _form.file
    #
    #     except Exception as ex:
    #         pass
    #
    #     return _form
    #
    # def edit_form(self, obj=None):
    #     return self._change_path_data(
    #         super(MyLink, self).edit_form(obj)
    #     )
    #
    # def create_form(self, obj=None):
    #     return self._change_path_data(
    #         super(MyLink, self).create_form(obj)
    #     )
    # ********

class MyUsluga(SpecificView):
    # ВНИМАНИЕ!!! нужно определить функцию  def on_model_delete(self, model):
    # при каскадном удалении если есть карточки услуг с фото чтобы удалялись
    # и фото из файловой системы! (см MyCardUsluga) На 10/06/22 е сделано

    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
    column_list = ['id', 'title', 'punkt_menu', 'link', 'comments_1', 'comments_2', 'comments_3', 'comments_4', 'count_cards_uslugs_in_model', 'cards_usluga']

    # Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['']

    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    column_labels = dict(punkt_menu='Относится к разделу (punkt_menu)',
                         title='Услуга (title)',
                         link='Путь (link)',
                         cards_usluga='Карточки услуги (cards_usluga)',
                         count_cards_uslugs_in_model='Кол-во карточек (из модели)')

    # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
    # column_display_all_relations = True

    # Определяет, должен ли первичный ключ отображаться в представлении списка - задаем в SettingAdminForAllRoles
    # column_display_pk = True

    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не role а role.name, не 'model' а 'model.name_model'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    #    Разобраться!!!
    column_searchable_list = ['id', 'title', 'link', 'punkt_menu.title']

    # Задает поля, в которых возможна фильтрация (выбирается столбец
    # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к настройкам SettingAdmin ('setting'),
    # то в выпадающем списке AddFilter кроме имя модели, id
    # увидим и все поля модели SettingAdmin(например can_create, can_delete и тп)
    # и следовательно можно искать те роли в которых например can_create = True)
    column_filters = ['id', 'title', 'link']

    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не role а role.name, не 'model' а 'model.name_model'
    # Включение 'punkt_menu' работает только при такой записи
    # ('punkt_menu', 'punkt_menu.title')
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # Разбираться с гибридными свойствами в SettingAdmin
    # сортировка по 'count_cards_uslugs_in_model' дает ошибку поэтому исключила.
    # Но хотелось бы иметь сортировку по кол-ву карточек -  РАЗБИРАТЬСЯ! На 25.07.22 не сделано
    column_sortable_list =['id', 'title', 'link', ('punkt_menu', 'punkt_menu.title')]

    # Задает редактируемые поля.
    # id не включать!!!  Если 'id' включен, то редактирование дает ошибку
    # Если не задать то по умолчанию доступны для редактирования все поля
    # если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    # исключила из списка редактирования link и 'punkt_menu',
    # т.к. используется в директории загрузки фото в карточках услуг!!!
    # То есть при загрузке фото в карточку услуг фото загружается в
    # определенное место(директорию), зависящую от директориии меню и директории услуг.
    # Поэтому директорию запрещаю редактировать!!
    # form_edit_rules = ['title', 'link', 'punkt_menu', 'comments_1', 'comments_2', 'comments_3', 'comments_4']
    form_edit_rules = ['title', 'comments_1', 'comments_2', 'comments_3', 'comments_4']

    # Форма для создания услуги (задаем список полей при создании услуги)
    # Если не задать то по умолчанию доступны для редактирования все поля
    # (в том числе cards_usluga)
    form_create_rules = ['title', 'punkt_menu', 'comments_1', 'comments_2', 'comments_3', 'comments_4']

    # Задает поля, в которых возможно быстрое редактирование(то есть при нажатии на это поле)
    # id не включать!!!
    # исключила из списка редактирования link и 'punkt_menu',
    # т.к. используется в директории загрузки фото в карточках услуг!!!
    # То есть при загрузке фото в карточку услуг фото загружается в
    # определенное место(директорию), зависящую от директориии меню и директории услуг.
    # Поэтому директорию запрещаю редактировать!!
    # column_editable_list = ['title', 'link', 'punkt_menu', 'comments_1', 'comments_2', 'comments_3', 'comments_4']
    column_editable_list = ['title', 'comments_1', 'comments_2', 'comments_3', 'comments_4']


    # Функция def on_model_change выполнит некоторые действия перед созданием
    # или обновлением модели.
    # Нам нужна чтобы преобразовать вводимые пользователем данные
    # в вид где первая буква строки заглавная (только в первом слове),
    # остальные прописные str.capitalize()
    # (метод str.title() - все первые буквы слов в строке заглавные )
    # см https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-title/
    # Вызывается из create_model и update_model в одной и той же транзакции
    # (если это имеет какое-либо значение для серверной части магазина).
    # По умолчанию ничего не делает.Параметры:
    #     form – Форма, используемая для создания/обновления модели
    #     model – Модель, которая будет создана/обновлена
    #     is_created — будет установлено значение True, если модель была создана, и значение False, если она была отредактирована .
    # def on_model_change см. https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions

    # Нам она нужна чтобы преобразовать вводимые пользователем данные
    # 1) в вид где первая буква строки имени заглавная (только в первом слове),
    # остальные прописные str.capitalize() (метод str.title() - все первые буквы ВСЕХ слов в строке заглавные )
    # см https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-title/
    # 2) если пользователь ввел путь на русском или заглавными буквами - преобразовать его в латиницу
    # и затем в нижний регистр
    # см https://docs-python.ru/packages/modul-transliterate-python/
    # Для этого инсталлировали модуль transliterate и использовали функцию translit

    def on_model_change(self, form, model, is_created):

        # Сделаем первую заглавную букву в заголовке меню
        model.title=model.title[0].capitalize()+model.title[1:]

        # print(model.link)
        # print(re.search(r'[^a-z]', model.link))

        # Удалим лишние пробелы если есть
        # https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-split/
        # https://tonais.ru/string/zamena-neskolkih-probelov-odnim-python
        model.title = " ".join(model.title.split())


        # Проблема 1 - начало
        # Путь меню (модель Link)в базе может совпасть с путем роута личного кабинета (например)
        # или др.произвольных стр. Тогда при нажатии на пункт меню переход на личный кабинет
        # (например) а не на стр.с услугами. Но тогда надо все такие возможные стр (их пути)
        # проверять. Это плохо.Поэтому изменила путь def render_menu с @app.route('/<punkt_menu>/')
        #  на @app.route('/раздел-меню/<punkt_menu>/') чтобы пути не пересеклись.
        # И тогда проверка и принудительное изменение пути перед записью в базе ниже не нужна.
        # if model.link=='profil':
        #     model.link=model.link + '2'
        # Проблема 1 - конец

        # *** Сформируем путь меню из имени - начало

        # путь меню из имени title хотим  формировать один раз,
        # только при создании экземпляра модели и не изменять его при изменении
        # имени пункта меню, тк фото в карточках услуг загружаются в директорию,
        # путь которой состоит в том числе из пути меню.
        # Для этого понадобится параметр функции def on_model_change(self, form, model, is_created)
        # is_created который == True если экземпляр модели создается
        # и ==False - если изменяется.

        if is_created:
            # re.search(r'[^a-zA-Z]', model.link) возвращает объект, если есть несовпадения
            # Если текст полностью соответствует шаблону (у нас латинские буквы) - то выдает None
            # Преобразуем русские буквы в латиницу и переведем в нижний регистр
            model.link=translit(model.title, language_code='ru', reversed=True).lower()

            # **** Проверка на символы типа #$&$^%*&|/ - начало
            # Если символы в строке model.link, заданных юзером не a-zA-Z0-9\s- (регулярка),
            # где \s -символ пробела экранированный
            # тогда удаляем их из model.link и проверяем чтобы не стало пустой строкой
            new_model_link=''
            for i in list(model.link):
                if re.fullmatch(r'^[a-zA-Z0-9\s-]+$', i):
                    new_model_link=new_model_link + i

            # заменим пробелы на '_' (то есть если заголовок меню из двух слов напрмер)
            new_model_link = "_".join(new_model_link.split())

            # заменим все '-' на пробелы
            new_model_link = " ".join(new_model_link.split('-'))

            # заменим пробелы идущие подряд на 1 '-'
            new_model_link = "-".join(new_model_link.split())

            if len(new_model_link)>=1:
                model.link=new_model_link
            else:
                # Если в заданном юзером пути нет символов, соответствующих шаблону регулярки
                # то в результате преобразований длина пути становится равна 0.
                # Поэтому задаем время загрузки файла в качестве пути загрузки (пока так)
                # для этого импортировали модуль datetime
                # replace(microsecond=0) - чтобы отсечь миллисекунды
                # replace(':', '-') - чтобы заменить : тк может в файловой системе создать проблемы
                uniq_time = 'menu_link-'+ str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')

                model.link=uniq_time
            # **** Проверка на символы типа #$&$^%*&|/ - конец


            # *** Сформируем путь меню из имени - конец



    # При удалении услуги в файловой системе в карточках услуг остается пустая директория,
    # если были карточки услуг с фото, но их удалили
    # Мы хотим удалить эти пустые директории
    # Для этого используем функцию on_model_delete (которая сама по себе ничего не делает)
    # Функция on_model_delete ( модель ) Выполнит некоторые действия ПЕРЕД удалением модели.
    # Вызывается из delete_model в той же транзакции (если это имеет какое-либо значение для бэкенда магазина).
    # По умолчанию ничего не делает.
    # см https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions


    def on_model_delete(self, model):
        # Формируем путь для удаления папки в файловой системе (если она пуста после удаления всех карточек услуг)
        path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + str(model.punkt_menu.link)+'/' + str(model.link)
        # print(path_delete)
        # Проверяем что такая директория существует
        # (она существует если в ней были карточки услуги с фото и карточка удалена).
        # Если карточек не было то такой директории не должно было существовать.
        # Для проверки используем модуль pathlib  -  from pathlib import Path
        # https://docs-python.ru/standart-library/modul-pathlib-python/opredelit-tip-puti-fajlovoj-sistemy-fajl-katalog-ssylka/
        is_dir=Path(path_delete).is_dir()
        # print(is_dir)
        if not model.cards_usluga and is_dir==True:
            # Удаляем папку со всем содержимым
            # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
            shutil.rmtree(path_delete)
            # либо так (удаляем каждое фото отдельно, но тогда надо потом удалять пустую папку)
            # for photo in model.photos:
            #     # Формируем путь для удаления файла
            #     path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + photo.dir_uploads + photo.secure_name_photo
            #     os.remove(path_delete)



    # Переопределите этот метод, если вы хотите динамически скрывать или
    # показывать административные представления из структуры меню Flask-Admin
    # По умолчанию пункт отображается в меню.
    # Обратите внимание, что пункт должен быть как видимым, так и доступным для отображения в меню.
    # По умолчанию возвращает True. Если False то заданные представления
    # не будут показаны в панели при заданных условиях (напрмер при определенной роли)
    # В нашем случае модель Role будет доступна только админу и суперадмину
    def is_visible(self):
        if current_user.has_role('admin') or current_user.has_role('superadmin') or current_user.has_role('editor'):
            return True

    # либо скрыть модель из админки можно методом is_accessible(self)
    # Мы оставим is_visible()
    # def is_accessible(self):
    #     return (current_user.has_role('manager'))

class CardUslugaView(SpecificView):
    # Пыталась сделать выбор меню, потом из выбранных услуг по услуге - не получилось пока на 16.07.22 - начало
    # тк сейчас для определения места карточки есть выбор услуги только из списка услуг,
    # а он большой и не понятно к какому пункту меню относится.
    #  Надо сначала меню, потом из выбранного списка услуг данного пункта меню выбор услуги
    # https://stackoverflow.com/questions/31764400/custom-flask-admin-form-with-some-select-field-choices-set-according-to-another
    # column_hide_backrefs = False
    # form_extra_fields = {
    #     'menu': sqla.fields.QuerySelectField(
    #         label='Link',
    #         # query_factory=lambda: Link.query.filter(Link.id==91).first(),
    #         query_factory=lambda: Link.query.all(),
    #         widget=Select2Widget()
    #     ),
    #     # 'usluga': sqla.fields.QuerySelectField(
    #     #     label='Usluga',
    #     #     query_factory=lambda: Usluga.query.filter(Usluga.punkt_menu_id==Link.id).all(),
    #     #     # query_factory=lambda: Link.query.all(),
    #     #     widget=Select2Widget()
    #     # )
    # }
    # column_list = ['id', 'name_card_usluga', 'dir_photos', 'menu', 'usluga.punkt_menu', 'usluga', 'comments', 'photos']
    # Пыталась сделать выбор по меню потом по услуге - не получилось пока на 16.07.22 - конец

    # ***** Попытка 2 form_args-вар 2 - начало
    # form_args = {
    #         # 'menu': {
    #         #     'query_factory': lambda: Link.query.all()
    #         # }
    #         'usluga': {
    #             'query_factory': lambda: Usluga.query.filter(Usluga.punkt_menu_id==Link.id)
    #         }
    # }
    # ***** Попытка 2 form_args-вар 2 - конец


    # 'punkt_menu_card_usluga' - из гибридного св-ва модели CardUsluga
    # 'usluga.punkt_menu' - просто из отношения в CardUsluga
    # Проблема в том что я не могу задать псевдоним в column_labels для 'usluga.punkt_menu'
    # тк пишет что в usluga.punkt_menu='еееее')
    # SyntaxError: keyword can't be an expression
    # Как ее решить не знаю поэтому использовала гибридное св-во в модели def punkt_menu_card_usluga
    # которое позволяет в данном случае задать и псевдоним  column_labels и сортировку column_sortable_list
    # column_list = ['id', 'name_card_usluga', 'punkt_menu_card_usluga', 'usluga.punkt_menu', 'usluga', 'dir_photos', 'comments', 'count_photos_in_card_usluga', 'photos', 'count_prices_in_card_usluga', 'prices']
    column_list = ['id', 'name_card_usluga', 'punkt_menu_card_usluga', 'usluga',
                   'type_production',
                   # 'type_production.statuses_intermediate' потом убрать из админки, он не информативен
                   'type_production.statuses_intermediate',
                   'dir_photos', 'comments', 'count_photos_in_card_usluga',
                   'photos', 'count_prices_in_card_usluga', 'prices',
                    'arhive', 'active']

    # Если включаю 'count_photos_in_card_usluga' для возможности сортировки - выдает ошибку поэтому исключила
    # Нужно разбираться с гибридными св-вами модели ('count_photos_in_card_usluga' оттуда)
    # column_sortable_list =['id', ('punkt_menu_card_usluga', 'usluga.punkt_menu.title'), ('usluga.punkt_menu', 'usluga.punkt_menu.title'), ('usluga', 'usluga.title'), 'name_card_usluga', 'dir_photos', 'comments']
    column_sortable_list =['id', 'arhive', 'active', 'name_card_usluga', ('punkt_menu_card_usluga',
                                                                         'usluga.punkt_menu.title'),
                           ('usluga', 'usluga.title'), 'dir_photos', 'comments',
                           ('type_production', 'type_production.name'),
                           # ('statuses_card_usluga', 'statuses_card_usluga.status.number')
                           ]

    column_searchable_list = ['id', 'arhive', 'active', 'name_card_usluga', 'usluga.punkt_menu.title', 'usluga.title',
                              'dir_photos', 'comments',
                              'type_production.name',
                              # 'statuses_card_usluga.status.status'
                              ]
    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    # Если задавала column_labels как dict(...), а не как {"card_usluga": 'Карточка услуги',....}
    # то невозможно задать лейбл для поля двойного отношения (отношения отношений)
    # (например 'status_intermediate.status_card')
    # Если задаю как column_labels = {"card_usluga": 'Ка......}, то лейблы для
    # поля двойного отношения (отношения отношений) задаются!!!
    # column_labels = dict (usluga='Относится к услуге (usluga)',
    #                       type_production='Тип производства',
    #                       arhive='Архив', active='Активна',
    #                       punkt_menu_card_usluga='Относится к разделу',
    #                       dir_photos='Директория загрузки фото (dir_photos)',
    #                       name_card_usluga='Имя карточки (name_card_usluga)',
    #                       comments='Комментарии',
    #                       count_photos_in_card_usluga='кол-во фото',
    #                       count_prices_in_card_usluga= 'кол-во прайсов')
    column_labels = {"usluga": 'Относится к услуге (usluga)',
                         "type_production": 'Тип производства',
                         "type_production.statuses_intermediate": 'Промежуточные статусы(зависят от типа пр-ва)',
                         "arhive": 'Архив',
                         "active": 'Активна',
                         "punkt_menu_card_usluga": 'Относится к разделу',
                         "dir_photos": 'Директория загрузки фото (dir_photos)',
                         "name_card_usluga": 'Имя карточки (name_card_usluga)',
                         "comments": 'Комментарии',
                         "count_photos_in_card_usluga": 'кол-во фото',
                         "count_prices_in_card_usluga": 'кол-во прайсов'}

    form_create_rules = ['usluga', 'type_production', 'name_card_usluga', 'comments']

    column_editable_list = ['name_card_usluga', 'type_production', 'arhive', 'active', 'comments']
    form_edit_rules = ['name_card_usluga', 'type_production', 'arhive', 'active', 'comments']
    edit_modal = True
    # can_view_details = True



    # **** Функция def on_model_change выполнит некоторые действия перед созданием
    # или обновлением модели.
    # Вызывается из create_model и update_model в одной и той же транзакции
    # (если это имеет какое-либо значение для серверной части магазина).
    # По умолчанию ничего не делает.Параметры:
    #     form – Форма, используемая для создания/обновления модели
    #     model – Модель, которая будет создана/обновлена
    #     is_created — будет установлено значение True, если модель была создана, и значение False, если она была отредактирована .
    # def on_model_change см. https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions

    # Нам она нужна чтобы преобразовать вводимые пользователем данные
    # 1) если пользователь ввел путь на русском или заглавными буквами - преобразовать его в латиницу
    # и затем в нижний регистр
    # см https://docs-python.ru/packages/modul-transliterate-python/
    # Для этого инсталлировали модуль transliterate и использовали функцию translit

    def on_model_change(self, form, model, is_created):

        # Сделаем первую заглавную букву в заголовке меню
        model.name_card_usluga=model.name_card_usluga[0].capitalize() + model.name_card_usluga[1:]

        # Удалим лишние пробелы если есть
        # https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-split/
        # https://tonais.ru/string/zamena-neskolkih-probelov-odnim-python
        model.name_card_usluga = " ".join(model.name_card_usluga.split())

        # print('model.name_card_usluga=', model.name_card_usluga)
        # print('model.photos=', model.photos)
        # print('len(model.photos)=', len(model.photos))
        # self.kk=len(model.photos)
        self.kk=2

        # *** Сформируем путь меню из имени - начало

        # путь меню из имени title хотим  формировать один раз,
        # только при создании экземпляра модели и не изменять его при изменении
        # имени пункта меню, тк фото в карточках услуг загружаются в директорию,
        # путь которой состоит в том числе из пути меню.
        # Для этого понадобится параметр функции def on_model_change(self, form, model, is_created)
        # is_created который == True если экземпляр модели создается
        # и ==False - если изменяется.

        if is_created:

            # re.search(r'[^a-zA-Z]', model.link) возвращает объект, если есть несовпадения
            # Если текст полностью соответствует шаблону (у нас латинские буквы) - то выдает None

            # Преобразуем русские буквы в латиницу и переведем в нижний регистр
            model.dir_photos=translit(model.name_card_usluga, language_code='ru', reversed=True).lower()

            # **** Проверка на символы типа #$&$^%*&|/ - начало
            # Если символы в строке model.link, заданных юзером не a-zA-Z0-9\s- (регулярка),
            # где \s -символ пробела экранированный
            # тогда удаляем их из model.link и проверяем чтобы не стало пустой строкой
            new_model_dir_photos=''
            for i in list(model.dir_photos):
                if re.fullmatch(r'^[a-zA-Z0-9\s-]+$', i):
                    new_model_dir_photos=new_model_dir_photos + i

            # заменим пробелы на '_' (то есть если заголовок меню из двух слов напрмер)
            new_model_dir_photos = "_".join(new_model_dir_photos.split())

            # заменим все '-' на пробелы
            new_model_dir_photos = " ".join(new_model_dir_photos.split('-'))

            # заменим пробелы идущие подряд на 1 '-'
            new_model_dir_photos = "-".join(new_model_dir_photos.split())


            if len(new_model_dir_photos)>=1:
                model.dir_photos=new_model_dir_photos
            else:
                # Если в заданном юзером пути нет символов, соответствующих шаблону регулярки
                # то в результате преобразований длина пути становится равна 0.
                # Поэтому задаем время загрузки файла в качестве пути загрузки (пока так)
                # для этого импортировали модуль datetime
                # replace(microsecond=0) - чтобы отсечь миллисекунды
                # replace(':', '-') - чтобы заменить : тк может в файловой системе создать проблемы
                uniq_time = 'menu_link-'+ str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')

                model.dir_photos=uniq_time
            # **** Проверка на символы типа #$&$^%*&|/ - конец

            # *** Сформируем путь меню из имени - конец


    # При задании модели CardUsluga определили параметр cascade="all,delete" в photos
    #  photos = db.relationship("Photo", back_populates='card_usluga', cascade="all,delete")
    # Это позволяет удалять запись photos при удалении карточки услуг из flask-admin
    # Но при этом сами загруженные изображения остаются в файловой системе. Нам нужно это изменить.
    # Для этого используем функцию on_model_delete (которая сама по себе ничего не делает)
    # Функция on_model_delete ( модель ) Выполнит некоторые действия ПЕРЕД удалением модели.
    # Вызывается из delete_model в той же транзакции (если это имеет какое-либо значение для бэкенда магазина).
    # По умолчанию ничего не делает.
    # см https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions



    def on_model_delete(self, model):
        if model.photos:
            # Формируем путь для удаления папки с фото
            path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + str(model.usluga.punkt_menu.link)+'/' + str(model.usluga.link) + '/' +str(model.dir_photos)

            # Удаляем папку со всем содержимым
            # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
            shutil.rmtree(path_delete)
            # либо так (каждое фото отдельно, но тогда надо потом удалять пустую папку)
            # for photo in model.photos:
            #     # Формируем путь для удаления файла
            #     path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + photo.dir_uploads + photo.secure_name_photo
            #     os.remove(path_delete)

        
    def is_visible(self):
        if current_user.has_role('admin') or current_user.has_role('superadmin') or current_user.has_role('editor'):
            return True

class MyPhone(SpecificView):
    # ***** column_list - начало
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
    column_list = ['id', 'phone', 'user']

    # Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['password']

    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    column_labels = dict(phone='Тел.', user='Пользователь')

    # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
    # column_display_all_relations = True

    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не roles а roles.name, не 'orders' а 'orders.order'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    column_searchable_list = ['id', 'phone', 'user.email']

    # Задает поля, в которых возможна булева фильтрация
    # column_filters = (BooleanEqualFilter(column=User.active, name='active'),)

    # Задает поля, в которых возможна фильтрация (выбирается столбец
    # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к Role ('roles'),
    # то в выпадающем списке AddFilter кроме имени, роли, описания, id
    # увидим и все поля модели Role(например name, description и тп)
    # и следовательно можно искать те роли в которых например name содержит сочетание ad и тп)
    column_filters = ['id', 'phone', 'user.email']

    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # ('roles', 'roles.name')
    # так как при включении просто roles или orders при попытке сортировки выдаст ошибку
    # поскольку, видимо, ролей и заказов может быть несколько и, следовательно,
    # не понятно как сортировать???
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    # column_sortable_list = ['id', 'phone', ('users', 'user.email')]
    column_sortable_list = ['id', 'phone', ('user', 'user.email')]

    # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
    # id не включать!!!
    # column_editable_list = ['active']

    # Задает редактируемые поля.
    # id не включать!!!  Если 'id' включен, то редактирование дает ошибку
    # Если не задать то по умолчанию доступны для редактирования все поля
    # если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    form_edit_rules = {'phone', 'user'}

    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin') or current_user.has_role('manager'):
            return True

# Данный класс предназначен фактически только для просмотра информации по загруженным фото
# Из админки можно только удалить фото или отредактировать заголовок и комментарий к нему.
# Остальное (загрузка фото в карточку услуг или в другой вид(если будет))
# - делать через специальные сервисы в админке (например Управление карточками услуг)
class MyPhoto(SpecificView):
    # 'photo_card_usluga_usluga_punkt_menu', 'photo_card_usluga_usluga'-из гибридных св-в модели Photo
    # 'card_usluga.usluga.punkt_menu', 'card_usluga.usluga' - просто из отношения в Photo
    # Проблема в том что я не могу задать псевдоним в column_labels для 'card_usluga.usluga.punkt_menu', 'card_usluga.usluga'
    # тк пишет что SyntaxError: keyword can't be an expression
    # Как ее решить не знаю поэтому использовала гибридные св-ва в модели def photo_card_usluga_usluga_punkt_menu и
    # def photo_card_usluga_usluga кот. позволяют в данном случае задать
    # и псевдоним  column_labels и сортировку column_sortable_list
    # column_list = ['id', 'secure_name_photo', 'origin_name_photo', 'dir_uploads',
    #                'card_usluga', 'photo_card_usluga_usluga', 'card_usluga.usluga',
    #                'photo_card_usluga_usluga_punkt_menu', 'card_usluga.usluga.punkt_menu',
    #                'title', 'comments', 'file_ext', 'file_size']
    column_list = ['id', 'secure_name_photo', 'origin_name_photo', 'dir_uploads',
                   'photo_card_usluga_usluga_punkt_menu',
                   'photo_card_usluga_usluga', 'card_usluga',
                   'title', 'comments', 'file_ext', 'file_size']
    column_labels = dict(secure_name_photo='Безопасное имя файла',
                          origin_name_photo='исходное имя фото',
                          dir_uploads='директория загрузки',
                          card_usluga='Относится к карточке услуги',
                          title='Заголовок фото',
                          comments='Комментарий к фото',
                          file_ext='Расширение файла',
                          file_size='Размер файла',
                         photo_card_usluga_usluga='Относится к услуге (из модели)',
                         photo_card_usluga_usluga_punkt_menu='Относится к разделу (из модели)')
    column_sortable_list = ('secure_name_photo',
                            'origin_name_photo',
                            'dir_uploads',
                            ('card_usluga', 'card_usluga.name_card_usluga'),
                            ('photo_card_usluga_usluga', 'card_usluga.usluga.title'),
                            ('card_usluga.usluga', 'card_usluga.usluga.title'),
                            ('photo_card_usluga_usluga_punkt_menu', 'card_usluga.usluga.punkt_menu.title'),
                            ('card_usluga.usluga.punkt_menu', 'card_usluga.usluga.punkt_menu.title'),
                            'title',
                            'comments',
                            'file_ext',
                            'file_size')

    column_searchable_list = ['secure_name_photo', 'origin_name_photo', 'dir_uploads',
                            'card_usluga.name_card_usluga', 'card_usluga.usluga.title',
                            'card_usluga.usluga.punkt_menu.title',
                            'title', 'comments', 'file_ext', 'file_size']

    form_edit_rules = ['title', 'comments']


    # **** form_create_rules = ()- Форма создания пользователя - начало
    # В нашем сервисе НЕЛЬЗЯ создавать загрузку фото в админке.
    # Для этого мы задаем form_create_rules = ()
    # Но если просто указать пустой список, то в форме создания появится все,
    # что по умолчанию плюс те поля которые мы определили ранее
    # в def scaffold_form(self) и обновили в def update_model(self, form, model)
    # Поэтому мы снова применим способ с свойствами (пункты 11, 22, 33)
    # но уже не будем в пункте 33 устанавливать зависимость от роли или контекста
    # В принципе можно запретить создание  и с помощью создания настроек
    # class SpecificView(SettingAdminForAllRoles),
    # но если вдруг все-таки кто-то разрешит создание,
    # то данные введенные вручную могут содержать много ошибок(адрес, безопасное имя и тд)
    # Поэтому задание пустой формы создания фото является подстраховкой

     # пункт 11.
    @property
    def _form_create_rules(self):
        return rules.RuleSet(self, self.form_create_rules)

    # пункт 22.
    @_form_create_rules.setter
    def _form_create_rules(self, value):
        pass

    # пункт 33.
    @property
    def form_create_rules(self):
        return ()
    # **** form_create_rules = ()- Форма создания пользователя - конец



    # При удалении фото из flask-admin удаляется только запись в базе, а
    # сами загруженные изображения остаются в файловой системе. Нам нужно их удалить.
    # Для этого используем функцию on_model_delete (которая сама по себе ничего не делает)
    # Функция on_model_delete ( модель ) Выполнит некоторые действия перед удалением модели.
    # Вызывается из delete_model в той же транзакции (если это имеет какое-либо значение для бэкенда магазина).
    # По умолчанию ничего не делает.
    # см https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions

    def on_model_delete(self, model):
        if model:
            # print(model)
            # считаем кол-во файлов в папке см https://qna.habr.com/q/727615
            files = os.listdir(path=current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + model.dir_uploads)
            # print(len(files))
            # если удаляемый файл один в папке - удаляем папку со всем содержимым
            # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
            # Если нет то только этот файл
            if len(files)==1:
                path_delete=current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + model.dir_uploads
                shutil.rmtree(path_delete)
            else:
                path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + model.dir_uploads + model.secure_name_photo
                # print(path_delete)
                os.remove(path_delete)


    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin') or current_user.has_role('manager'):
            return True

class OrderView(SpecificView):
    # ***** column_list - начало
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)

    column_list = ['id', 'number', 'user',
                   'manager_person',
                  'manager_person.user_last_name',
                   'manager_person.user_first_name',
                  'manager_person.user_middle_name',
                   'manager_role',
                   'date_create', 'date_end',
                   'progresses',
                   'order_items']

    # Удалить столбцы из списка.
    # Если задан column_list, где данный столбец не включен, то column_exclude_list
    # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
    # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
    # column_exclude_list = ['password']

    # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.

    column_labels = dict(number='Номер заказа', user='Заказчик',
                         manager_person='Менеджер заказа',
                         # в полях с отношением не могу задать псевдоним - ошибка!!
                         # manager_person.user_last_name= 'Фамилия',
                         # manager_person.user_first_name='Имя',
                         # manager_person.user_middle_name='Отчество',
                         manager_role='Должность ответственного',
                         date_create='Дата создания',
                         date_end='Дата закрытия',
                         # statuses='Статусы заказа',
                         progresses='Прогресс',
                         order_items='Элементы заказа'
                         )

    # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles для всех моделей
    # column_display_all_relations = True

    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не roles а roles.name, не 'orders' а 'orders.order'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    column_searchable_list = ['id', 'number', 'user.email',
                              'manager_person.email',
                              'date_create',
                              'date_end',
                              # 'statuses.status',
                              # 'progresses',
                              'order_items.id'
                              ]

    # Задает поля, в которых возможна булева фильтрация
    # column_filters = (BooleanEqualFilter(column=User.active, name='active'),)

    # Задает поля, в которых возможна фильтрация (выбирается столбец
    # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к Role ('roles'),
    # то в выпадающем списке AddFilter кроме имени, роли, описания, id
    # увидим и все поля модели Role(например name, description и тп)
    # и следовательно можно искать те роли в которых например name содержит сочетание ad и тп)
    column_filters = ['id', 'number', 'user.email',
                      'manager_person.email',
                      'date_create', 'date_end',
                      # 'statuses.status',
                      'manager_role.name',
                              'order_items.id']

    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # ('roles', 'roles.name')
    # так как при включении просто roles или orders при попытке сортировки выдаст ошибку
    # поскольку, видимо, ролей и заказов может быть несколько и, следовательно,
    # не понятно как сортировать???
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    column_sortable_list = ['id', 'number', ('user', 'user.email'), 'date_create',
                            ('manager_person', 'manager_person.email'),
                            ('manager_role', 'manager_role.name'),
                            'date_end',
                            # ('statuses', 'statuses.status'),
                            ('order_items', 'order_items.id')
                            ]

    # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
    # id не включать!!!
    # column_editable_list = ['active']

    # Задает редактируемые поля.
    # id не включать!!!  Если 'id' включен, то редактирование дает ошибку
    # Если не задать то по умолчанию доступны для редактирования все поля
    # если в этом списке не все поля - то выдает предупреждение в терминале
    # об отсутствующих в списке полях модели, например:
    # Fields missing from ruleset: password,created_on
    # warnings.warn(text)
    # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
    # при создании представлений (admin.add_view...) конкретных моделей см. ниже
    # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
    # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
    # form_edit_rules = {'order', 'user'}
    # form_create_rules = {'order', 'user'}



     # **** Функция def on_model_change выполнит некоторые действия перед созданием или обновлением модели.
    # Вызывается из create_model и update_model в одной и той же транзакции (если это имеет какое-либо значение для серверной части магазина).
    # По умолчанию ничего не делает.Параметры:
    #     form – Форма, используемая для создания/обновления модели
    #     model – Модель, которая будет создана/обновлена
    #     is_created — будет установлено значение True, если модель была создана, и значение False, если она была отредактирована .
    # def on_model_change см. https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions

    # Нам она нужна чтобы отсечь миллисекунды в дате создания
    # https://docs-python.ru/packages/modul-transliterate-python

    # def on_model_change(self, form, model, is_created):
    #     if is_created:
    #         # uniq_time = datetime.now().time().replace(microsecond=0)
    #         model.order_create=str(datetime.now)



    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin') or current_user.has_role('manager'):
            return True

class OrderItemView(SpecificView):
    column_list = ['id', 'order', 'card_usluga', 'price',
                   'gorizontal_position_price_i', 'vertical_position_price_j',
                   'actual_offer',
                   # 'actual_status',
                   'date_create_actual_status',
                   'progress']

    column_labels = dict(order='Номер заказа',
                         card_usluga='Карточка услуги',
                         price='Прайс',
                         gorizontal_position_price_i='Горизонт. позиция прайса',
                         vertical_position_price_j='Вертик. позиция прайса',
                         actual_offer='Актуальность предложения',
                         # actual_status='Актуальный статус',
                         date_create_actual_status='Дата начала актуального статуса',
                         progress='Прогресс',
                         )
    # Задает поля, в которых возможен поиск по словам
    # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
    # не roles а roles.name, не 'orders' а 'orders.order'
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    column_searchable_list = ['id',
                              'order.number',
                              'card_usluga.name_card_usluga',
                              'price.name_price_table',
                              'gorizontal_position_price_i',
                              'vertical_position_price_j',
                              'actual_offer',
                              # 'actual_status.status.status',
                              'date_create_actual_status',
                              'progress'
                              ]

    # Задает поля, в которых возможна сортировка (по алфавиту например)
    # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!('roles', 'roles.name')
    # тк при включении просто orders при попытке сортировки выдаст ошибку
    # тк, заказов может быть несколько и, следовательно, не понятно как сортировать???
    # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
    column_sortable_list = ['id',
                            ('order', 'order.number'),
                            ('card_usluga', 'card_usluga.name_card_usluga'),
                            ('price', 'price.name_price_table'),
                              'gorizontal_position_price_i',
                              'vertical_position_price_j',
                              'actual_offer',
                            # ('actual_status', 'actual_status.status.status'),
                              'date_create_actual_status'
                            ]
    # Задает поля, в которых возможна фильтрация (выбирается столбец в кот.
    # осyществляется поиск (по ключевому слову например или по булеву значению))
    # Если включить отношение к Role ('roles'),
    # то в выпадающем списке AddFilter кроме имени, роли, описания, id
    # увидим и все поля модели Role(например name, description и тп)
    # и следовательно можно искать те роли в которых например name содержит сочетание ad и тп)
    column_filters = ['id',
                      'order.number',
                      'card_usluga.name_card_usluga',
                      'price.name_price_table',
                      'gorizontal_position_price_i',
                      'vertical_position_price_j',
                      'actual_offer',
                      # 'actual_status.status.status',
                      'date_create_actual_status'
                      ]


# Попытка отформатировать форму ввода данных даты на временной интервал (timedelta) - начало!
# Работает, но форматирует вид введенных данных а не форму ввода
# https://question-it.com/questions/7718893/flask-admin-nastroit-prosmotr-daty-i-vremeni
#https://pythonhosted.org/invenio-oaiserver/_modules/flask_admin/model/base.html

# from flask_admin.model import typefmt
# from datetime import date
#
# def date_format(view, value):
#     # return value.strftime('%Y-%m-%d')
#     return value.strftime('%H:%M')
#
# MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
# MY_DEFAULT_FORMATTERS.update({
#     date: date_format
# })
#
# # это внутрь модели админки - начало
# form_args = dict(
#     time = dict(validators=[DataRequired()],format='%Y-%m-%d %H:%M')
#         )
#     form_widget_args = dict(
#     time={'data-date-format': u'YYYY-MM-DD HH:mm'}
#     )
#     column_type_formatters = MY_DEFAULT_FORMATTERS
#     # это внутрь модели админки - конец

# Попытка отформатировать форму ввода данных даты на временной интервал (timedelta) - конец!


class PriceTableView(SpecificView):
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    column_list = ['id', 'name_price_table', 'arhive', 'active', 'card_usluga', 'row_table', 'col_table', 'value_table']

    column_sortable_list = ['id', 'arhive', 'active', 'name_price_table', ('card_usluga',
                                                                           'card_usluga.name_card_usluga')]

    # Быстрое редактирование
    column_editable_list = ['arhive', 'active', 'name_price_table']

    # Задает поля, в которых возможна фильтрация (в том числе булева )
    column_filters = ('id', 'name_price_table', 'row_table',
                      BooleanEqualFilter(column=PriceTable.arhive, name='arhive'),
                      BooleanEqualFilter(column=PriceTable.arhive, name='active'),
                      'col_table',
                      'card_usluga.name_card_usluga')

    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin'):
            return True
    # *** def is_visible(self): -Делаем модель  видимой только для определенных ролей - конец

class MyCarousel(SpecificView):
    # Задает поля из базы, отображаемые в админ панели. Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
    column_list = ['id', 'place_carousel', 'name_carousel', 'dir_carousel', 'number_foto', 'date_create', 'active', 'arhive', 'dict_all_foto_carousel_name']

    # column_sortable_list = ['id', ('place_carousel', 'place_carousel.place_model_element.place_element.name_place_element'), 'name_carousel', 'dir_carousel', 'number_foto', 'date_create', 'active', 'arhive']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало

    # column_labels = dict(place_carousel='Места размещения', name_carousel='Имя карусели', dir_carousel='Директория загрузки', number_foto='Кол-во изображений', date_create='Дата создания', dict_all_foto_carousel_name='Список изображений')

    # Быстрое редактирование
    column_editable_list = ['active', 'arhive']

    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin'):
            return True
    # *** def is_visible(self): -Делаем модель  видимой только для определенных ролей - конец

class MyContainerElement(SpecificView):
    # column_list = ['id', 'name_container', 'comment_container']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyPriorityElement(SpecificView):
    # column_list = ['id', 'name_container', 'comment_container']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyColumnElement(SpecificView):
    # column_list = ['id', 'name_container', 'comment_container']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyBasePositionElement(SpecificView):
    column_list = ['id', 'name_base_position', 'comment_base_position', 'code']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    form_columns = ['name_base_position', 'comment_base_position', 'code']
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyBaseLocationElement(SpecificView):
    column_list = ['id', 'name_base_location', 'comment_base_location', 'code']
     # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    form_columns = ['name_base_location', 'comment_base_location', 'code']
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyWidthElement(SpecificView):
    # column_list = ['id', 'name_width_carousel', 'width_carousel', 'comment_width_carousel']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyHeightElement(SpecificView):
    # column_list = ['id', 'name_height_carousel', 'height_carousel', 'comment_height_carousel']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyVerticalPositionElement(SpecificView):
    # column_list = ['id', 'name_container', 'comment_container']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyHorizontalPositionElement(SpecificView):
    # column_list = ['id', 'name_container', 'comment_container']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyPositionElement(SpecificView):
    # column_display_all_relations = True
    column_list = ['id', 'name_position', 'alias_position', 'comment_position', 'vertical_position', 'horizontal_position']
    column_sortable_list = ['id',
                            ('name_position', 'horizontal_position.name_horizontal_position', 'vertical_position.name_vertical_position'),
                            ('alias_position', 'vertical_position.code'),
                            ('comment_position', 'horizontal_position.name_horizontal_position', 'vertical_position.name_vertical_position'),
                            ('horizontal_position', 'horizontal_position.name_horizontal_position'),
                            ('vertical_position', 'vertical_position.name_vertical_position') ]
    form_columns = ['vertical_position', 'horizontal_position']
    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True
    # *** def is_visible(self): -Делаем модель  видимой только для определенных ролей - конец

class MyPlaceCarousel(SpecificView):
    column_list = ['id', 'carousel', 'place_model_element', 'base_position',  'vertical_position',
                   'horizontal_position', 'base_location', 'column_element', 'container_element',
                   'priority_element', 'comment_place_element']
    column_sortable_list = ['id', 'priority_element',
                            ('base_location', 'place_model_element.place_element.base_location.name_base_location'),
                            ('base_position', 'place_model_element.place_element.base_position.name_base_position'),
                            ('vertical_position', 'place_model_element.place_element.position.vertical_position.name_vertical_position'),
                            ('horizontal_position', 'place_model_element.place_element.position.horizontal_position.name_horizontal_position'),
                            ('container_element', 'place_model_element.place_element.container_element.name_container_element'),
                            ('column_element', 'place_model_element.place_element.column_element.column_element'),
                            ('carousel', 'carousel.name_carousel'),
                            ('place_model_element', 'place_model_element.place_element.base_position.code',
                             'place_model_element.place_element.position.alias_position',
                             'place_model_element.place_element.base_location.code',
                             'place_model_element.place_element.column_element.code',
                             'place_model_element.place_element.container_element.code'),
                            ('comment_place_element', 'place_model_element.place_element.base_position.comment_base_position')
                            ]
    column_labels = dict(priority_element='Приоритет', carousel='Имя карусели', place_model_element='Модель, ее место и размер', comment_place_element='Комментарий места размещения')



    # ***** form_args - начало
    # https://question-it.com/questions/3511025/filtratsija-znachenij-stolbtsov-v-flask-admin-s-otnosheniem-odin-ko-mnogim
    # https://progi.pro/ispolzovanie-foreignkey-v-modelyah-sqlalchemy-v-pythonflask-342165
    # (работало когда в class PlaceModelElement(db.Model внешний ключ в отношениях
    # ссылался на поле id(name_model_id = db.Column(db.Integer, db.ForeignKey("list_models.id")))
    # Позднее для удобства описания в модели PlaceCarousel и последующих аналогичных сделала
    # name_model_id = db.Column(db.String, db.ForeignKey("list_models.name_model"))
    # Это было возможно, т.к. name_model была задана в ListModel как unique=True и, следовательно, могло
    # служить внешним ключом ForeignKey)
    # Теперь работающая конструкция - ***** form_args-вар 2 - начало

    # В этой конструкции задали фильтр, который покажет в админке при создании записи PlaceСCarousel
    # только те записи PlaceModelElement, которые соответствуют модели Carousel из списка моделей ListModel
    # id записи в ListModel с именем Carousel == 12 (что и указано ниже)
    # Использовала
    # https://question-it.com/questions/3511025/filtratsija-znachenij-stolbtsov-v-flask-admin-s-otnosheniem-odin-ko-mnogim
    # https://progi.pro/ispolzovanie-foreignkey-v-modelyah-sqlalchemy-v-pythonflask-342165
    # form_args = {
    #         'place_model_element': {
    #             'query_factory': lambda: PlaceModelElement.query.filter(PlaceModelElement.name_model_id==12).all()
    #         }
    # }
    # form_args - конец

    # ***** form_args-вар 2 - начало
    form_args = {
            'place_model_element': {
                'query_factory': lambda: PlaceModelElement.query.filter(PlaceModelElement.name_model_id=='Carousel').all()
            }
    }
    # ***** form_args-вар 2 - конец

    def is_visible(self):
        if current_user.has_role('superadmin') or current_user.has_role('admin'):
            return True

class MyPlaceModelElement(SpecificView):

    column_list = ['id','name_model', 'place_element', 'width_element', 'height_element']
    column_sortable_list = ['id',
                            ('name_model', 'name_model.name_model'),
                            ('place_element', 'place_element.base_position.code',
                             'place_element.position.alias_position',
                             'place_element.base_location.code',
                             'place_element.column_element.code',
                             'place_element.container_element.code'
                             ),
                            ('width_element', 'width_element.width_element'),
                            ('height_element', 'height_element.height_element')]
    column_labels = dict(name_model='Модель', place_element='Место размещения', width_element='Ширина элемента', height_element='Высота элемента')
    # Задаем фильтр для показа только тех моделей из ListModel, кот. соответствуют тем элементам
    # кот. разрешены к размещению на сайте(карусели, реклама, фото например) - как мы решили
    # фильтр .in_  - см  https://stackoverflow.com/questions/21674303/flask-sqlalchemy-filters-and-operators
     # form_args см. - https://question-it.com/questions/3511025/filtratsija-znachenij-stolbtsov-v-flask-admin-s-otnosheniem-odin-ko-mnogim
    # https://progi.pro/ispolzovanie-foreignkey-v-modelyah-sqlalchemy-v-pythonflask-342165
    form_args = {
            'name_model': {
                'query_factory': lambda: ListModel.query.filter(ListModel.name_model.in_(('Carousel', 'PriceTable', 'UploadFileMy')))
            }
    }

    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True

class MyPlaceElement(SpecificView):
    column_list = ['id', 'name_place_element', 'code_place_element', 'base_position', 'base_location', 'position', 'container_element', 'column_element', 'comment_place_element']
    column_searchable_list = ['id', 'container_element.name_container_element',
                              'base_position.code', 'base_position.name_base_position', 'base_position.comment_base_position',
                              'base_location.code', 'base_location.name_base_location', 'base_location.comment_base_location',
                              'position.horizontal_position.name_horizontal_position', 'position.horizontal_position.comment_horizontal_position',
                              'position.vertical_position.name_vertical_position', 'position.vertical_position.comment_vertical_position',
                              'container_element.name_container_element', 'container_element.comment_container_element', 'container_element.code',
                              'column_element.column_element', 'column_element.comment_column_element', 'column_element.code']
    column_sortable_list = ['id',
                            ('name_place_element', 'base_position.code',
                             'base_location.name_base_location',
                             'position.alias_position', 'container_element.code', 'column_element.code'),
                            ('code_place_element', 'base_location.code', 'base_position.code',
                             ('position', 'position.horizontal_position.code', 'position.vertical_position.code'),
                             'container_element.code', 'column_element.code'),
                            ('base_location', 'base_location.name_base_location'),
                            ('base_position', 'base_position.name_base_position'),
                            ('position', 'position.vertical_position.name_vertical_position'),
                            ('container_element', 'container_element.name_container_element'),
                            ('column_element', 'column_element.column_element'),
                            ('comment_place_element',
                             'base_location.comment_base_location',
                             'base_position.comment_base_position',
                             'position.comment_position',
                             'container_element.comment_container_element)',
                             'column_element.comment_column_element',)]


    # Форма создания элемента в базе
    # Если включить 'comment_place_element' - будет ошибка, т.к. этот столбец - производное от других и задается
    # в модели автоматически в гибридном свойстве
    form_columns = ['base_position', 'base_location', 'position', 'container_element', 'column_element']

     # Присвоить столбцам из модели заголовки
    # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
    column_labels = dict(name_place_element='Имя места', code_place_element='Код места', comment_place_element='Комментарии', base_location='Базовая локация', base_position='Базовая позиция', position='Позиция', container_element='Тип контейнера', column_element='Кол-во колонок')

    # *** def is_visible(self): -Делаем модель видимой только для определенных ролей - начало
    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True
    # *** def is_visible(self): -Делаем модель  видимой только для определенных ролей - конец

# Настройки, специфичные для определенных моделей из файла models.py - конец

# Добавили ссылку на стр места из админ панели - начало
# Места размещения элементов - визуал из фотошопа
# сам place.html находится в главной templates!!!
class PlaceView(BaseView):
    @expose('/')
    def place_view(self):
        return self.render('place.html')
# Добавили ссылку на стр из админ панели - конец

# Рассылка писем - проба (можно сделать например)
# https://stepik.org/lesson/300655/step/4
class MailerView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/mailer/index.html')



# *** СТАТУСЫ!!!

# class MyStatus(SpecificView):
#
#     def on_model_change(self, form, model, is_created):
#
#         # Сделаем первую заглавную букву в статусе
#         model.status=model.status[0].capitalize() + model.status[1:]
#
#
#     # ***** column_list - начало
#     # Задает поля из базы, отображаемые в админ панели
#     # Столбцы будут расположены в порядке, указанном в списке!!!
#     # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
#     column_list = ['id', 'number', 'status', 'comment']
#
#     # Удалить столбцы из списка.
#     # Если задан column_list, где данный столбец не включен, то column_exclude_list
#     # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
#     # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
#     # column_exclude_list = ['password']
#
#     # Присвоить столбцам из модели заголовки
#     # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
#     column_labels = dict(status='Статус', number='Вес статуса', comment='Комментарий')
#
#     # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
#     # column_display_all_relations = True
#
#     # Задает поля, в которых возможен поиск по словам
#     # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
#     # не roles а roles.name, не 'orders' а 'orders.order'
#     # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
#     # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
#     column_searchable_list = ['id', 'status', 'number']
#
#     # Задает поля, в которых возможна булева фильтрация
#     # column_filters = (BooleanEqualFilter(column=User.active, name='active'),)
#
#     # Задает поля, в которых возможна фильтрация (выбирается столбец
#     # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
#     # Если включить отношение к Role ('roles'),
#     # то в выпадающем списке AddFilter кроме имени, роли, описания, id
#     # увидим и все поля модели Role(например name, description и тп)
#     # и следовательно можно искать те роли в которых например name содержит сочетание ad и тп)
#     column_filters = ['id', 'status', 'number', 'comment']
#
#     # Задает поля, в которых возможна сортировка (по алфавиту например)
#     # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
#     # ('roles', 'roles.name')
#     # так как при включении просто roles или orders при попытке сортировки выдаст ошибку
#     # поскольку, видимо, ролей и заказов может быть несколько и, следовательно,
#     # не понятно как сортировать???
#     # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
#     # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
#     column_sortable_list = ['id', 'status', 'number', 'comment']
#
#     # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
#     # id не включать!!!
#     # column_editable_list = ['active']
#
#     # Задает редактируемые поля.
#     # id не включать!!!  Если 'id' включен, то редактирование дает ошибку
#     # Если не задать то по умолчанию доступны для редактирования все поля
#     # если в этом списке не все поля - то выдает предупреждение в терминале
#     # об отсутствующих в списке полях модели, например:
#     # Fields missing from ruleset: password,created_on
#     # warnings.warn(text)
#     # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
#     # при создании представлений (admin.add_view...) конкретных моделей см. ниже
#     # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
#     # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
#     form_edit_rules = {'status', 'number', 'comment'}
#
#     # Задает поля при создании записи.
#     form_create_rules = ['status', 'number', 'comment']
#
#     def is_visible(self):
#         if current_user.has_role('superadmin'):
#             return True

# class MyStatusCardUsluga(SpecificView):
#
#     # Добавим валидатор NumberRange (задаем интервалы)
#     # для кол-ва дней часов или минут на выполнение работ.
#     # https://translated.turbopages.org/proxy_u/en-ru.ru.c1b086fc-62f24a67-9453ffe5-74722d776562/https/stackoverflow.com/questions/45458767/change-the-order-or-disable-the-unique-validator-in-flask-admin-with-sqlalchemy
#     form_args = {
#         'days_norma': {
#             'validators': [NumberRange(min=0, max=366)]
#         },
#         'hours_norma': {
#             'validators': [NumberRange(min=0, max=23)]
#         },
#         'minutes_norma': {
#             'validators': [NumberRange(min=0, max=59)]
#         }
#     }
#
#
#     # https://translated.turbopages.org/proxy_u/en-ru.ru.6a4e954e-62f0e5b5-67f2c0ff-74722d776562/https/stackoverflow.com/questions/57794198/flask-admin-not-including-some-columns-in-create-edit-but-are-included-in-the
#     # Без этой строки norma_interval не отображался в форме создания и редактироания
#     # form_extra_fields = {
#     #     'norma_interval': DateTimeField('norma_interval')
#     # }
#     # Но это поле работает не так как я планировала (те тип ИНтервал) а именно дата,
#     # Поэтому я решила вводить и хранить просто целые числа (день, час, минута) а потом в роуте преобразовывать в
#     # timedelta
#
#
#
#     # Создадим normativ2 - начало!
#     # https://translated.turbopages.org/proxy_u/en-ru.ru.a8edd97f-62d92535-0d2a131f-74722d776562/https/stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
#     # В ссылке указаны 2 способа (один в модели(ответ), второй  в админке - оба работают!!!)
#     # для них нужны импорты
#     # from sqlalchemy.ext.hybrid import hybrid_property
#     # from sqlalchemy import select, func
#
#     def _normativ2_formatter(view, context, model, name):
#         # return len(model.uslugs)
#         return str(model.days_norma)+' дн. '+ str(model.hours_norma)+' ч. '+str(model.minutes_norma) + ' мин.'
#
#     column_formatters = {
#         'normativ2': _normativ2_formatter
#     }
#     # Создадим normativ2 - конец!
#
#     column_list = ['id', 'status', 'card_usluga', 'role_responsible', 'normativ', 'normativ2']
#     column_labels = dict(normativ2='Норматив (из админки)', normativ='Норматив (из модели)')
#     column_filters = ['id', 'status', 'card_usluga', 'role_responsible']
#     column_searchable_list = ['id', 'status.status', 'card_usluga.name_card_usluga', 'role_responsible.name']
#     # column_sortable_list = ['id', ('status', 'status.number'),
#     #                         ('card_usluga', 'card_usluga.name_card_usluga'),
#     #                         ('role_responsible', 'role_responsible.name'),
#     #                         ('standard', 'days_norma', 'hours_norma', 'minutes_norma')]
#     # column_default_sort = 'status.number'
#     column_sortable_list = ['id', ('status', 'status.number'),
#                             ('card_usluga', 'card_usluga.name_card_usluga'),
#                             ('role_responsible', 'role_responsible.name')]
#
#     def is_visible(self):
#         if current_user.has_role('superadmin'):
#             return True


# class MyOrderStatus(SpecificView):
#
#     def on_model_change(self, form, model, is_created):
#
#         # Сделаем первую заглавную букву в статусе
#         model.status=model.status[0].capitalize() + model.status[1:]
#
#
#     # ***** column_list - начало
#     # Задает поля из базы, отображаемые в админ панели
#     # Столбцы будут расположены в порядке, указанном в списке!!!
#     # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
#     column_list = ['id', 'status', 'number']
#
#     # Удалить столбцы из списка.
#     # Если задан column_list, где данный столбец не включен, то column_exclude_list
#     # не нужен. Разница в том, что порядок столбцов будет произвольным, а при задании
#     # column_list будет тот, что указан в списке!!! Поэтому зададим column_list!!!
#     # column_exclude_list = ['password']
#
#     # Присвоить столбцам из модели заголовки
#     # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
#     column_labels = dict(status='Статус', number='Вес статуса')
#
#     # Добавляет столбцы-отношения - задаем в SettingAdminForAllRoles
#     # column_display_all_relations = True
#
#     # Задает поля, в которых возможен поиск по словам
#     # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
#     # не roles а roles.name, не 'orders' а 'orders.order'
#     # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
#     # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
#     column_searchable_list = ['id', 'status', 'number']
#
#     # Задает поля, в которых возможна булева фильтрация
#     # column_filters = (BooleanEqualFilter(column=User.active, name='active'),)
#
#     # Задает поля, в которых возможна фильтрация (выбирается столбец
#     # в котором осyществляется поиск (по ключевому слову например или по булеву значению))
#     # Если включить отношение к Role ('roles'),
#     # то в выпадающем списке AddFilter кроме имени, роли, описания, id
#     # увидим и все поля модели Role(например name, description и тп)
#     # и следовательно можно искать те роли в которых например name содержит сочетание ad и тп)
#     column_filters = ['id', 'status', 'number']
#
#     # Задает поля, в которых возможна сортировка (по алфавиту например)
#     # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
#     # ('roles', 'roles.name')
#     # так как при включении просто roles или orders при попытке сортировки выдаст ошибку
#     # поскольку, видимо, ролей и заказов может быть несколько и, следовательно,
#     # не понятно как сортировать???
#     # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
#     # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
#     column_sortable_list = ['id', 'status', 'number']
#
#     # Задает поля, в кот. возможно быстрое редактирование(то есть при нажатии на это поле)
#     # id не включать!!!
#     # column_editable_list = ['active']
#
#     # Задает редактируемые поля.
#     # id не включать!!!  Если 'id' включен, то редактирование дает ошибку
#     # Если не задать то по умолчанию доступны для редактирования все поля
#     # если в этом списке не все поля - то выдает предупреждение в терминале
#     # об отсутствующих в списке полях модели, например:
#     # Fields missing from ruleset: password,created_on
#     # warnings.warn(text)
#     # Для подавления этих сообщений используем функцию with warnings.catch_warnings()
#     # при создании представлений (admin.add_view...) конкретных моделей см. ниже
#     # https://fooobar.com/questions/998148/how-can-i-avoid-flask-admin-21-warning-userwarning-fields-missing-from-ruleset
#     # https://docs-python.ru/standart-library/modul-warnings-python/funktsija-warn-modulja-warnings/
#     form_edit_rules = {'status', 'number'}
#
#     # Задает поля при создании записи.
#     form_create_rules = ['status', 'number']
#
#     def is_visible(self):
#         if current_user.has_role('superadmin') or current_user.has_role('admin'):
#             return True

class TypeProductionView(SpecificView):
    # Задает поля из базы, отображаемые в админ панели
    # Столбцы будут расположены в порядке, указанном в списке!!!
    # (либо в column_exclude_list указать те столбцы, что нужно удалить из списка)
    column_list = ['id', 'name', 'cards_uslugs', 'statuses_intermediate']

class StatusCardView(SpecificView):
    column_list = ['id', 'name', 'weight', 'description', 'statuses_intermediate']

class StatusIntermediateView(SpecificView):
    column_list = ['id', 'type_production', 'status_card', 'name', 'weight', 'description']

class StatusOrderView(SpecificView):
    column_list = ['id', 'name', 'weight', 'description']


class SpecificationStatusCardView(SpecificView):

    # Добавим валидатор NumberRange (задаем интервалы)
    # для кол-ва дней, часов или минут на выполнение работ.
    # https://translated.turbopages.org/proxy_u/en-ru.ru.c1b086fc-62f24a67-9453ffe5-74722d776562/https/stackoverflow.com/questions/45458767/change-the-order-or-disable-the-unique-validator-in-flask-admin-with-sqlalchemy
    form_args = {
        'days_norma': {
            'validators': [NumberRange(min=0, max=366)]
        },
        'hours_norma': {
            'validators': [NumberRange(min=0, max=23)]
        },
        'minutes_norma': {
            'validators': [NumberRange(min=0, max=59)]
        }
    }

    # https://translated.turbopages.org/proxy_u/en-ru.ru.6a4e954e-62f0e5b5-67f2c0ff-74722d776562/https/stackoverflow.com/questions/57794198/flask-admin-not-including-some-columns-in-create-edit-but-are-included-in-the
    # Без этой строки norma_interval не отображался в форме создания и редактироания
    # form_extra_fields = {'norma_interval': DateTimeField('norma_interval')}
    # Но это поле работает не так как я планировала (те тип ИНтервал) а именно дата,
    # Поэтому я решила вводить и хранить просто целые числа (день, час, минута) а потом в роуте преобразовывать в
    # timedelta

    # Создадим normativ2 - начало!
    # https://translated.turbopages.org/proxy_u/en-ru.ru.a8edd97f-62d92535-0d2a131f-74722d776562/https/stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # В ссылке указаны 2 способа (один в модели(ответ), второй  в админке - оба работают!!!)
    # для них нужны импорты
    # from sqlalchemy.ext.hybrid import hybrid_property
    # from sqlalchemy import select, func

    def _normativ2_formatter(view, context, model, name):
        # return len(model.uslugs)
        return str(model.days_norma)+' дн. '+ str(model.hours_norma)+' ч. '+str(model.minutes_norma) + ' мин.'

    column_formatters = {
        'normativ2': _normativ2_formatter
    }
    # Создадим normativ2 - конец!

    column_list = ['id', 'card_usluga', 'status_card',  'role_responsible', 'normativ', 'normativ2']
    column_labels = dict(card_usluga='Карточка услуги',
                         role_responsible='Ответственный (роль)',
                         status_card='Статус карт(StatusCard)',
                         normativ2='Норматив (из админки)',
                         normativ='Норматив (из '
                                                                                                  'модели)')
    column_filters = ['id', 'status_card', 'card_usluga', 'role_responsible']
    column_searchable_list = ['id', 'status_card.name', 'card_usluga.name_card_usluga', 'role_responsible.name']
    # column_sortable_list = ['id', ('status', 'status.number'),
    #                         ('card_usluga', 'card_usluga.name_card_usluga'),
    #                         ('role_responsible', 'role_responsible.name'),
    #                         ('standard', 'days_norma', 'hours_norma', 'minutes_norma')]
    # column_default_sort = 'status_card.name'
    column_sortable_list = ['id', ('status_card', 'status_card.name'),
                            ('card_usluga', 'card_usluga.name_card_usluga'),
                            ('role_responsible', 'role_responsible.name'),
                            ]

    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True


class SpecificationStatusIntermediateView(SpecificView):

    # Добавим валидатор NumberRange (задаем интервалы)
    # для кол-ва дней, часов или минут на выполнение работ.
    # https://translated.turbopages.org/proxy_u/en-ru.ru.c1b086fc-62f24a67-9453ffe5-74722d776562/https/stackoverflow.com/questions/45458767/change-the-order-or-disable-the-unique-validator-in-flask-admin-with-sqlalchemy
    form_args = {
        'days_norma': {
            'validators': [NumberRange(min=0, max=366)]
        },
        'hours_norma': {
            'validators': [NumberRange(min=0, max=23)]
        },
        'minutes_norma': {
            'validators': [NumberRange(min=0, max=59)]
        }
    }

    # https://translated.turbopages.org/proxy_u/en-ru.ru.6a4e954e-62f0e5b5-67f2c0ff-74722d776562/https/stackoverflow.com/questions/57794198/flask-admin-not-including-some-columns-in-create-edit-but-are-included-in-the
    # Без этой строки norma_interval не отображался в форме создания и редактироания
    # form_extra_fields = {'norma_interval': DateTimeField('norma_interval')}
    # Но это поле работает не так как я планировала (те тип ИНтервал) а именно дата,
    # Поэтому я решила вводить и хранить просто целые числа (день, час, минута) а потом в роуте преобразовывать в
    # timedelta

    # Создадим normativ2 - начало!
    # https://translated.turbopages.org/proxy_u/en-ru.ru.a8edd97f-62d92535-0d2a131f-74722d776562/https/stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # В ссылке указаны 2 способа (один в модели(ответ), второй  в админке - оба работают!!!)
    # для них нужны импорты
    # from sqlalchemy.ext.hybrid import hybrid_property
    # from sqlalchemy import select, func

    def _normativ2_formatter(view, context, model, name):
        # return len(model.uslugs)
        return str(model.days_norma)+' дн. '+ str(model.hours_norma)+' ч. '+str(model.minutes_norma) + ' мин.'

    column_formatters = {
        'normativ2': _normativ2_formatter
    }
    # Создадим normativ2 - конец!

    column_list = ['id', 'card_usluga', 'status_intermediate.status_card', 'status_intermediate',  'role_responsible',
                   'normativ', 'normativ2']

    # Если задавала column_labels как dict(...), а не как {"card_usluga": 'Карточка услуги',....}
    # то невозможно задать лейбл для поля двойного отношения (отношения отношений)
    # (например 'status_intermediate.status_card')
    # Если задаю как column_labels = {"card_usluga": 'Ка......}, то лейблы для
    # поля двойного отношения (отношения отношений) задаются!!!
    # column_labels = dict(card_usluga='Карточка услуги',
    #                      role_responsible='Ответственный (роль)',
    #                      status_intermediate='Статус промежуточный',
    #                      normativ2='Норматив (из админки)',
    #                      normativ='Норматив (из модели)'
    #                      )
    column_labels = {"card_usluga": 'Карточка услуги',
                         "role_responsible": 'Ответственный (роль)',
                         "status_intermediate": 'Статус промежуточный',
                     "status_intermediate.status_card": 'Статус основной',
                         "normativ2": 'Норматив (из админки)',
                         "normativ": 'Норматив (из модели)'}

    column_filters = ['id', 'status_intermediate', 'card_usluga', 'role_responsible']
    column_searchable_list = ['id', 'status_intermediate.name', 'card_usluga.name_card_usluga', 'role_responsible.name']
    # column_sortable_list = ['id', ('status', 'status.number'),
    #                         ('card_usluga', 'card_usluga.name_card_usluga'),
    #                         ('role_responsible', 'role_responsible.name'),
    #                         ('standard', 'days_norma', 'hours_norma', 'minutes_norma')]
    # column_default_sort = 'status_card.name'
    column_sortable_list = ['id', ('status_intermediate', 'status_intermediate.name'),
                            ('card_usluga', 'card_usluga.name_card_usluga'),
                            ('role_responsible', 'role_responsible.name'),
                            ]

    def is_visible(self):
        if current_user.has_role('superadmin'):
            return True



class StaffActionView(SpecificView):
    column_list = ['id', 'name']
    column_labels = dict(name='Наименование')
    column_filters = ['id', 'name']
    column_searchable_list = ['id', 'name']


class GoalActionView(SpecificView):
    column_list = ['id', 'name']
    column_labels = dict(name='Наименование')
    column_filters = ['id', 'name']
    column_searchable_list = ['id', 'name']


class MethodActionView(SpecificView):
    column_list = ['id', 'name']
    column_labels = dict(name='Наименование')
    column_filters = ['id', 'name']
    column_searchable_list = ['id', 'name']


class ResultActionView(SpecificView):
    column_list = ['id', 'name']
    column_labels = dict(name='Наименование')
    column_filters = ['id', 'name']
    column_searchable_list = ['id', 'name']

class ActionOrderView(SpecificView):

    column_list = ['id', 'order',
                   'order.manager_person.email',
                   'order.manager_person.user_last_name',
                   'order.manager_person.user_first_name',
                   'order.manager_person.user_middle_name',
                   'status_order', 'date_create', 'staff_action',
                   'goal_action', 'method_action', 'result_action']
    # column_labels = dict(order='Заказ',
    #                      status_order='Статус заказа',
    #                      date_create='Дата действия',
    #                      "order.staff_actual_status_person"='order.staff_actual_status_person',
    #                      staff_action='Действие',
    #                      goal_action='Цель действия',
    #                      method_action='Метод действия',
    #                      result_action='Результат действия',
    #                      )
    column_labels = {"order": 'Заказ',
                     "status_order": 'Статус заказа',
                     "date_create": 'Дата действия',
                     "order.manager_person.email": 'Ответственный',
                     "order.manager_person.user_last_name": 'Фамилия',
                     "order.manager_person.user_first_name": 'Имя',
                     "order.manager_person.user_middle_name": 'Отчество',
                     "staff_action": 'Действие персонала',
                     "goal_action": 'Цель действия',
                     "method_action": 'Метод действия',
                     "result_action": 'Результат действия'
    }

    column_sortable_list = ['id',
                            ('order', 'order.number'),
                            ('order.manager_person.email'),
                            ('order.manager_person.user_last_name'),
                            ('order.manager_person.user_first_name'),
                            ('order.manager_person.user_middle_name'),
                            ('status_order', 'status_order.name'),
                            'date_create',
                            ('staff_action', 'staff_action.name'),
                            ('goal_action', 'goal_action.name'),
                            ('method_action', 'method_action.name'),
                            ('result_action', 'result_action.name'),
                            ]
    column_filters = ['id', 'order', 'status_order', 'date_create',
                      'staff_action','goal_action',
                      'method_action', 'result_action',
                      'order.manager_person.email',
                      'order.manager_person.user_last_name',
                      'order.manager_person.user_first_name',
                       'order.manager_person.user_middle_name']
    column_searchable_list = ['id', 'order.number', 'status_order.name', 'date_create',
                            'staff_action.name', 'goal_action.name',
                            'method_action.name', 'result_action.name',
                              'order.manager_person.email',
                              'order.manager_person.user_last_name',
                              'order.manager_person.user_first_name',
                              'order.manager_person.user_middle_name'
                            ]

class ActionOrderItemView(SpecificView):
    column_list = ['id', 'order_item', 'order_item.staff_actual_status_person',
                   'status_card', 'date_create', 'staff_action',
                   'goal_action', 'method_action', 'result_action']

    column_labels = {"order_item": 'Элемент заказа',
                     "order_item.staff_actual_status_person": 'Ответственный',
                     "status_card": 'Статус карты',
                     "date_create": 'date_create',
                     "staff_action": 'Действие персонала',
                    "goal_action": 'Цель действия',
                    "method_action": 'Метод действия',
                    "result_action": 'Результат действия'
                     }

    column_sortable_list = ['id',
                            ('order_item', 'order_item.id'),
                            ('status_card', 'status_card.name'),
                            'date_create',
                            ('staff_action', 'staff_action.name'),
                            ('goal_action', 'goal_action.name'),
                            ('method_action', 'method_action.name'),
                            ('result_action', 'result_action.name'),
                            ]
    column_filters = ['id', 'order_item', 'status_card', 'date_create', 'staff_action',
                      'goal_action', 'method_action', 'result_action']
    column_searchable_list = ['id', 'order_item.order.number',
                              'status_card.name',
                              'date_create',
                              'staff_action.name',
                              'goal_action.name',
                              'method_action.name',
                              'result_action.name',
                              ]


class ProgressOrderView(SpecificView):
    column_list = ['id', 'order',
                   'status_order',
                   'date_create',
                   'date_end']
    column_labels = {"order": 'Заказ',
                     "status_order": 'Статус заказа',
                     "date_create": 'Дата создания',
                     "date_end": 'Дата окончания',
                     }

# Создание административной панели
admin = Admin(app, 'Имя', url='/admin/', index_view=HomeAdminView(name='Гл'), template_mode='bootstrap4')


# ******** warnings.catch_warnings() - начало
# Оператор with с функцией:    with warnings.catch_warnings():
#                                   warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
# использована для того, чтобы при создании представлений admin.add_view...
# классов MyLink, MyUser и др в которых объявлены редактируемые поля
# (напр.form_edit_rules = {'order', 'users'}), отличные от списка по умолчанию (напр.некоторые поля не включены в этот список)
# не выскакивало сообщение в терминале, которое указывает на отсутствующие поля, подобное этому:
#     Fields missing from ruleset: password,created_on
#     warnings.warn(text)
# Если не задать form_edit_rules то по умолчанию доступны для редактирования все поля
# Для подавления этих сообщений и используем функцию (with warnings.catch_warnings())
# Для использования warnings.catch_warnings() нужно сделать импорт import warnings
# А сами представления админки admin.add_view(...) включаем внутрь этого оператора with с функции!!
# ******** warnings.catch_warnings() - конец

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
   # Объявление представлений админ. панели с помощью встроенной функции add_view из Flask-Admin
    # каждое из представлений добавляет в админ.панель данные из конкретной модели

    # Меню, Услуги
    admin.add_view(MyLink(Link, db.session, name='Меню сайта(Link)', category="Меню,Услуги"))
    admin.add_view(MyUsluga(Usluga, db.session, name='Услуги(Usluga)', category="Меню,Услуги"))

    # Пользователи, Роли
    admin.add_view(UserView(User, db.session, name='Пользователи(User)', category="Пользователи,Роли"))
    admin.add_view(RoleView(Role, db.session, name='Роли(Role)', category="Пользователи,Роли"))


    admin.add_view(CardUslugaView(CardUsluga, db.session, name=' Карточки услуг', category="Карточки"))
    admin.add_view(PriceTableView(PriceTable, db.session, name='Прайсы', category="Карточки"))
    admin.add_view(MyPhoto(Photo, db.session, name=' Фото(Photo)', category="Карточки"))

    admin.add_view(TypeProductionView(TypeProduction, db.session, name='Тип производства'))

    # Статусы
    admin.add_view(StatusOrderView(StatusOrder, db.session, name='Статусы заказов', category="Статусы(справочники)"))
    admin.add_view(StatusCardView(StatusCard, db.session, name='Статусы карт', category="Статусы(справочники)"))
    admin.add_view(StatusIntermediateView(StatusIntermediate, db.session, name='Промежуточные статусы карт', category="Статусы(справочники)"))

    admin.add_view(SpecificationStatusCardView(SpecificationStatusCard, db.session,
                                               name='Спецификация статусов карт', category="Спецификации статусов"))
    admin.add_view(SpecificationStatusIntermediateView(SpecificationStatusIntermediate, db.session,
                                                name='Спецификация промежут. статусов', category="Спецификации статусов"))

    # Действия
    admin.add_view(StaffActionView(StaffAction, db.session,
                                   name='Действия персонала',
                                   category="Действия(справочники)"))
    admin.add_view(GoalActionView(GoalAction, db.session, name='Цели действия', category="Действия(справочники)"))
    admin.add_view(MethodActionView(MethodAction, db.session, name='Методы действия', category="Действия(справочники)"))
    admin.add_view(ResultActionView(ResultAction, db.session, name='Результаты действия', category="Действия(справочники)"))
    admin.add_view(ActionOrderView(ActionOrder, db.session, name='Действия по заказу', category="Действия"))
    admin.add_view(ActionOrderItemView(ActionOrderItem, db.session, name='Действия по элем. заказа', category="Действия"))

    # admin.add_view(MyStatus(Status, db.session, name='Возможные статусы', category="Статусы"))
    # admin.add_view(MyStatusCardUsluga(StatusCardUsluga, db.session, name='Статусы карточек', category="Статусы"))
    # admin.add_view(MyOrderStatus(OrderStatus, db.session, name='Статусы заказов'))

    # Заказы
    admin.add_view(OrderView(Order, db.session, name='Заказы', category="Заказы"))
    admin.add_view(OrderItemView(OrderItem, db.session, name='Элементы заказов', category="Заказы"))
    admin.add_view(ProgressOrderView(ProgressOrder, db.session, name='Прогресс заказов'))


    admin.add_view(MyPhone(Phone, db.session, name='Телефоны(Phone)'))
    admin.add_view(PayerView(Payer, db.session, name='Плательщики(Payer)'))

    # Карусели
    admin.add_view(MyCarousel(Carousel, db.session, name='Карусели'))

    # Размещение каруселей
    admin.add_view(MyPlaceCarousel(PlaceCarousel, db.session, name='Place Carousel'))

    # Ссылка на стр из админ панели (наглядно места размещения из фотошопа)
    # admin.add_view(PlaceView(name='Места', endpoint='place'))

    # Категория "Места моделей и размеры"
    # с 2 подкатегориями: 1) 'Размеры элемента'
    # (кот. является категорией для подкатегорий 'Ширина элемента' и 'Высота элемента')
    # 2) PlaceModel Element'
    admin.add_view(MyPlaceModelElement(PlaceModelElement, db.session,
                                       name='PlaceModelElement',
                                       category="Места моделей,Размеры"))
    admin.add_sub_category(name='Размеры элемента', parent_name="Места моделей,Размеры")
    # admin.add_view(MySizeElement(SizeElement, db.session, name='Размеры элементов', category="Размер элемента"))
    admin.add_view(MyWidthElement(WidthElement, db.session, name='Ширина элемента', category="Размеры элемента"))
    admin.add_view(MyHeightElement(HeightElement, db.session, name='Высота элемента', category="Размеры элемента"))
    admin.add_view(MyPlaceElement(PlaceElement, db.session, name='Размещение элемента'))
    admin.add_view(MyBaseLocationElement(BaseLocationElement, db.session, name='Базовая локация', category="Параметры размещ.элем."))
    admin.add_view(MyBasePositionElement(BasePositionElement, db.session, name='Базовая позиция', category="Параметры размещ.элем."))

    # **** Создание подкатегории и вставка внутрь подкатегории представлений классов - начало
    # https://flask-admin.readthedocs.io/en/latest/introduction/#grouping-views
    # https://www.reddit.com/r/flask/comments/cr67hn/flaskadmin_questions_about_the_menu_bar/
    # https://github.com/flask-admin/flask-admin/blob/master/examples/sqla/admin/main.py#L254
    # 1. - Создаем подкатегорию 'Позиция элемента' в родительской категории "Параметры размещ.элем."
    admin.add_sub_category(name='Позиция элемента', parent_name="Параметры размещ.элем.")

    # 2. - Вставляем в подкатегорию 'Позиция элемента' представления
    # admin.add_view(MyHorizontalPositionElement(HorizontalPositionElement.... и др.
    # ВАЖНО!!! Сначала создаем подкатегорию(у нас 'Позиция элемента'),
    #  потом создаем представление где эта подкатегория становится категорией!!!!!!
    admin.add_view(MyPositionElement(PositionElement, db.session, name='Позиции элемента', category="Позиция элемента"))
    admin.add_view(MyHorizontalPositionElement(HorizontalPositionElement, db.session, name='Горизонтальная позиция', category="Позиция элемента"))
    admin.add_view(MyVerticalPositionElement(VerticalPositionElement, db.session, name='Вертикальная позиция', category="Позиция элемента"))
    # **** Создание подкатегории и вставка внутрь подкатегории представлений классов - конец

    admin.add_view(MyContainerElement(ContainerElement, db.session, name='Контейнер элемента', category="Параметры размещ.элем."))
    admin.add_view(MyColumnElement(ColumnElement, db.session, name='Колонки элемента', category="Параметры размещ.элем."))

    # Создание подкатегории и ссылки в ней - начало
    # Сделано для примера - не используется в проекте
    # admin.add_sub_category(name='Имя ссылки', parent_name="Параметры размещ.элем.")
    # admin.add_link(MenuLink(name='Название какое-то', url='/адрес ссылки', category='Имя ссылки'))

    # Приоритет элемента
    # admin.add_view(MyPriorityElement(PriorityElement, db.session, name='Приоритет элемента', category="Приоритет элем."))

    # Модели, Настройки
    admin.add_view(MyListModel(ListModel, db.session, name='Модели(ListModel)', category="Модели,Настройки"))
    admin.add_view(MySettingAdmin(SettingAdmin, db.session, name='Настройки(SettingAdmin)', category="Модели,Настройки"))

    admin.add_view(MyUploadFileMy(UploadFileMy, db.session, name='Фото услуг(UploadFileMy)'))

admin.add_view(MyView(name='Выйти'))

# Рассылка писем - проба
# https://stepik.org/lesson/300655/step/4
# admin.add_view(MailerView(name='Рассылки', endpoint='mailer', category='Models'))


    # *****перенесла в fotomanager.py - начало - не удалять!!!
    # ****перенесла классы Choice2 и DeleteFoto в fotomanager.py
    # (убрав классы и оставив только функции, т.к.классы нужны были чтобы сделать в админке
    # admin.add_view(Choice2.....), то есть кнопку в меню админ панели с помощью
    # @expose('/', methods=['GET', 'POST'])

    # admin.add_view(Choice2(name='Загрузчик(Choice2)'))
    # admin.add_view(DeleteFoto(name='Del и Edit фото из миниатюр(DeleteFoto)'))
    # *****перенесла в fotomanager.py -  конец

    # admin.add_view(Ed(name='Ред фото из миниатюр(DeleteFoto)'))

    # admin.add_view(Choice1(name='Choice1'))
    # admin.add_view(UploadPhotoAdmin(name='фото(UploadPhotoAdmin)'))



# Пояснения security.context_processor - начало
# https://ploshadka.net/flask-delaem-avtorizaciju-na-sajjte/
# define a context processor for merging flask-admin's template context into the
# flask-security views.
# Перевод:
# определите контекстный процессор для слияния контекста шаблона flask-admin с
# представлениями flask-security.
# Не понимаю где используется. Просто передаются значения из админ в секьюрити?
# print(admin.base_template)
# print(admin.index_view)
# print(helpers)
# print(url_for)

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=helpers,
        get_url=url_for
    )
# Пояснения security.context_processor - конец



# Объявление представлений админ. панели с помощью встроенной функции add_view из Flask-Admin
# каждое из представлений добавляет в админ.панель данные из конкретной модели

# admin.add_view(MyLink(Link, db.session, name='Категории услуг в меню сайта(Link)'))
# admin.add_view(MyUsluga(Usluga, db.session, name='Услуги(Usluga)'))
# admin.add_view(MyUser(User, db.session, name='Пользователи(User)'))
# admin.add_view(MyRole(Role, db.session, name='Роли(Role)'))
# admin.add_view(MySettingAdmin(SettingAdmin, db.session, name='Настройки(SettingAdmin)'))
# admin.add_view(MyListModel(ListModel, db.session, name='Модели(ListModel)'))
# admin.add_view(MyOrder(Order, db.session, name='Заказы(Order)'))



# # *******
# UPLOAD_FOLDER = '/static/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# # class MyVV(BaseView):
# @expose('/upload/', methods=('GET', 'POST'))
# @expose('/upload/<path:path>', methods=('GET', 'POST'))
# def upload(self, path=None):
#         # """
#         #     Upload view method
#         #
#         #     # :param path:
#         #         Optional directory path. If not provided, will use the base directory
#         # """
#         # Get path and verify if it is valid
#     base_path, directory, path = self._normalize_path(path)
#
#     if not self.can_upload:
#         flash(gettext('File uploading is disabled.'), 'error')
#         return redirect(self._get_dir_url('.index_view', path))
#
#     if not self.is_accessible_path(path):
#         flash(gettext('Permission denied.'), 'error')
#         return redirect(self._get_dir_url('.index_view'))
#
#     form = self.upload_form()
#     if self.validate_form(form):
#         try:
#             self._save_form_files(directory, path, form)
#             flash(gettext('Successfully saved file: %(name)s',
#                               name=form.upload.data.filename), 'success')
#             return redirect(self._get_dir_url('.index_view', path))
#         except Exception as ex:
#             flash(gettext('Failed to save file: %(error)s', error=ex), 'error')
#
#     if self.upload_modal and request.args.get('modal'):
#         template = self.upload_modal_template
#     else:
#         template = self.upload_template
#
#     return self.render(template, form=form,
#                            header_text=gettext('Upload File'),
#                            modal=request.args.get('modal'))

# admin.add_view(MyVV(name='VV'))
# # *******




# class StorageModel(db.Model):
#     __tablename__ = 'storage'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Unicode(64))
#     path = db.Column(db.Unicode(128))
#     type = db.Column(db.Unicode(3))
#     # create_date = db.Column(db.DateTime, default=datetime.datetime.now)
#
# class StorageAdminModel(ModelView):
#     form_extra_fields = {
#         'file': form.FileUploadField('file')
#     }
#
#     def _change_path_data(self, _form):
#         try:
#             storage_file = _form.file.data
#
#             if storage_file is not None:
#                 hash = random.getrandbits(128)
#                 ext = storage_file.filename.split('.')[-1]
#                 path = '%s.%s' % (hash, ext)
#
#                 storage_file.save(
#                     os.path.join(app.config['STORAGE'], path)
#                 )
#
#                 _form.name.data = _form.name.data or storage_file.filename
#                 _form.path.data = path
#                 _form.type.data = ext
#
#                 del _form.file
#
#         except Exception as ex:
#             pass
#
#         return _form
#
#     def edit_form(self, obj=None):
#         return self._change_path_data(
#             super(StorageAdminModel, self).edit_form(obj)
#         )
#
#     def create_form(self, obj=None):
#         return self._change_path_data(
#             super(StorageAdminModel, self).create_form(obj)
#         )
#
#
# admin.add_view(StorageAdminModel(Usluga, db.session, endpoint='/gg/'))

# Other
# admin.add_view(MyAdminChangeView(name='Смена пароля'))



# ******* Вариант2 - выбор из выпадающего списка- попытка
# Основано на https://www.youtube.com/watch?v=I2dJuNwlIH0
# Но не получилось(10.08.21) - пока оставляю чтобы не потерять вариант, позже попробовать еще
# class LoadPhotoWithChoice2(BaseView):
#     @expose('/', methods=['GET', 'POST'])
#     # Декоратор, который указывает, что пользователь должен иметь хотя бы одну из указанных ролей.
#     @roles_accepted('superadmin')
#     def foto_load_with_choice2(self):
#         form = PhotoFormAdmin2(form_name='LoadPhotoWithChoice2')
#         form.menu.choices = [(row.id, row.title) for row in Link.query.order_by('title').all()]
#         form.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.order_by('title').all()]
#         # menu = form.menu.data
#         # menu = Link.query.filter_by(id=menu).first()
#         # print('menu=', menu)
#         if request.method == 'GET':
#             menu = form.menu.data
#             menu = Link.query.filter_by(id=menu).first()
#             form.usluga.choices = [(row.id, row.title) for row in Usluga.query.filter_by(punkt_menu=menu).all()]
#             print('menu=', menu)
#             return render_template('admin/upload-foto-with-choice2.html', form=form)
#
#         if request.method == 'POST':
#             menu = Link.query.filter_by(id=form.menu.data).first()
#             form.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.filter_by(punkt_menu_id=form.menu.data).all()]
#             # print(menu)
#             return ('<h1> Пункт меню: {} Услуга: {} <h1>').format(menu.title, form.usluga.data)
#         # return render_template('admin/upload-foto-with-choice2.html', form=form)
#
#     @app.route('/usluga/<menu>/')
#     def usluga(menu):
#         uslugs = Usluga.query.filter_by(punkt_menu=menu).all()
#         uslugaArray = []
#         for usluga in uslugs:
#             uslugaObj={}
#             uslugaObj['id']=usluga.id
#             uslugaObj['title']=usluga.title
#             uslugaArray.append(uslugaObj)
#         return jsonify({'uslugs' : uslugaArray})

# ***** Вариант2 - конец

# ******* Вариант2 - выбор из выпадающего списка- попытка не работает
# пока оставить и пропробовать позже (см LoadPhotoWithChoice2 в admin/init.py-->
# admin.add_view(LoadPhotoWithChoice2(name='Фото2(LoadPhotoWithChoice2)'))
#  ***** Вариант2 - конец


# **** загрузка файлов и создания директорий FileAdmin - начало

# Импорт, необходимый для работы модуля FileAdmin
import os.path as op
from flask_admin.contrib.fileadmin import FileAdmin

# Создаем путь для добавления в административную панель модуля для загрузки файлов и создания директорий FileAdmin
path_for_upload_and_make_dir = op.join(op.dirname(__file__), 'static/images/uploads')
# print('op.dirname(__file__)=', op.dirname(__file__))
# print('path_for_upload_and_make_dir=', path_for_upload_and_make_dir)

# # Добавляем в административную панель модуль для загрузки файлов и создания директорий FileAdmin
admin.add_view(FileAdmin(path_for_upload_and_make_dir, '/static/', name='FileAdmin'))

# **** загрузка файлов и создания директорий FileAdmin - конец

class MyFileAdmin(FileAdmin):
    def get_base_path(self):
        path = FileAdmin.get_base_path(self)
        print('path1=', path)
        url = FileAdmin.get_base_url(self)
        print('url=', url)
        if current_user.has_role('superadmin'):
            # return op.join(path, current_user.custom_path)
            print('path superadmin = ', op.join(path, 'superadmin'))
            path = op.join(path, 'superadmin')
            return path
        else:
            return path
        print('path2=', path)

# admin.add_view(MyFileAdmin(path, '/static1/', name='MyFileAdmin'))

# admin.add_views(SpecificView(User, db.session),
#                 SpecificView(Link, db.session),
#                 )

# admin.add_view(ModelView(Link, db.session, name='Меню(модель Menu)'))
# admin.add_view(ModelView(Usluga, db.session, name='Услуги(модель Usluga)'))
# admin.add_view(ModelUserRoleManager(User, db.session, name='Пользователь(User)', endpoint='/manager/user/'))
# admin.add_view(MyRole(Role, db.session, name='Роли(Role)'))
# admin.add_view(ModelView(ListModel, db.session, name='Модели(ListModel)'))
# admin.add_view(ModelView(SettingAdmin, db.session, name='Настройки(SettingAdmin)'))

# admin.add_view(MyAdminView(Link, db.session, name='Меню(модель Menu)', category="Меню и все услуги"))
# admin.add_view(MyAdminView(Link, db.session, name='Меню(модель Menu)', category="Меню и все услуги", endpoint="admins_user"))
# admin.add_view(ModelView(Usluga, db.session, name='Услуги(модель Usluga)', category="Меню и все услуги"))
# admin.add_view(ModelView(Order, db.session, name='Заказы(Order)'))

# admin.add_view(SpecificView(view, db.session, name='Категории услуг в меню сайта(Link)')

# admin.add_view(SpecificView(db.session))
# admin.add_view(SpecificView(User, db.session))
# admin.add_view(SpecificView(Usluga, db.session))
# admin.add_view(SpecificView(Role, db.session, name='Роли(Role)'))
# admin.add_view(SpecificView(SettingAdmin, db.session, name='Настройки(SettingAdmin)'))


# Группировка пунктов меню админки в выпадающий список
# см. # https://flask-admin.readthedocs.io/en/latest/introduction/#adding-your-own-views
# admin.add_sub_category(name="Links", parent_name="Меню и все услуги")

# Что это за функция при группировке пунктов меню в админке не разобралась, см.
# https://flask-admin.readthedocs.io/en/latest/introduction/#adding-your-own-views
# admin.add_link(MenuLinks(name='Home Page', url='/', category='Links'))




# Версия от 13.07.21-работает
# class SpecificView(SettingAdminForAllRoles):
#     def _handle_view(self, name, **kwargs):
#         # **** Напечатаем роли пользователя current_user
#         # print('Все роли пользователя', current_user.roles)
#         # Согласно логике сервиса если пользователь не имеет роли, то он в админку не войдет
#         # поэтому в принципе эта проверка не нужна но на всякий случай пока оставим
#         if current_user.roles == [] or current_user == None:
#             print('current_user не имеет роли', None)
#         else:
#             print('Все роли пользователя', current_user.roles)
#         # ****
#
#         # Если у пользователя одна роль
#         # if len(current_user.roles) == 1:
#         #     names_settings = []
#         #     setting_for_role = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[0]).all()
#         #     # print('Переберем все настройки для роли', current_user.roles[0])
#         #     for sett in setting_for_role:
#         #         names_settings.append(sett.name_setting)
#         #     # print('Все имена настроек', names_settings)
#         #     for sett in setting_for_role:
#         #         path_setting_fol_role_and_model = '/admin/'+str(sett.model).lower()+'/'
#         #         if request.full_path.startswith(path_setting_fol_role_and_model):
#         #             # print(request.full_path)
#         #             # print('запрос request.full_path=', request.full_path, 'СОВПАДАЕТ с путем настройки из списка настроек path_setting_fol_role_and_model=', path_setting_fol_role_and_model, request.full_path.startswith(path_setting_fol_role_and_model))
#         #             self.can_create = sett.can_create
#         #             self.can_edit = sett.can_edit
#         #             self.can_delete = sett.can_delete
#         #             self.can_export = sett.can_export
#         #             # print('Для роли', current_user.roles[0], ' и модели', sett.model,
#         #             #       'Применим настройку', sett.name_setting, 'can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
#         #             break
#                 # else:
#                 #     # print(request.full_path)
#                 #     print('запрос request.full_path=', request.full_path, 'НЕ СОВПАДАЕТ с путем настройки path_setting_fol_role_and_model=', path_setting_fol_role_and_model, request.full_path.startswith(path_setting_fol_role_and_model))
#                 #     print('Переходим к проверке пути настройки следующей модели(если есть)')
#             # Если у пользователя одна роль - конец
#
#         # Если у пользователя несколько ролей
#         if len(current_user.roles) >= 1:
#             path_setting = []
#             all_setting = []
#             setting_dict = {}
#             settings_for_role = {}
#
#             can_edit_1 = False
#             can_create_1 = False
#             can_delete_1 = False
#             can_export_1 = False
#             export_max_rows_1 = 0
#             for i in range(len(current_user.roles)):
#                 settings_for_role[i] = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[i]).all()
#                 # all_setting.append(settings_for_role[i])
#                 for j in range(len(settings_for_role[i])):
#                     path = '/admin/'+str(settings_for_role[i][j].model).lower()+'/'
#                     # print(settings_for_role[i][j].name_setting, path)
#                     if request.full_path.startswith(path):
#                         # print('request.full_path', request.full_path)
#                         print(settings_for_role[i][j].name_setting, settings_for_role[i][j].model, path,  'can_edit=', settings_for_role[i][j].can_edit, 'can_create=', settings_for_role[i][j].can_create, 'can_delete=', settings_for_role[i][j].can_delete, 'can_export=', settings_for_role[i][j].can_export, 'export_max_rows=', settings_for_role[i][j].export_max_rows )
#                     # setting_dict[settings_for_role[i][j].name_setting]={'Role': settings_for_role[i][j].role, 'model': settings_for_role[i][j].model, 'path': path, 'can_edit': settings_for_role[i][j].can_edit}
#                     #     print('can_edit_1', can_edit_1)
#                         self.can_edit = settings_for_role[i][j].can_edit or can_edit_1
#                         self.can_create = settings_for_role[i][j].can_create or can_create_1
#                         self.can_delete = settings_for_role[i][j].can_delete or can_delete_1
#                         self.can_export = settings_for_role[i][j].can_export or can_export_1
#                         if settings_for_role[i][j].export_max_rows == None:
#                             # print('settings_for_role[i][j].export_max_rows', settings_for_role[i][j].export_max_rows)
#                             # print('type(settings_for_role[i][j].export_max_rows)', type(settings_for_role[i][j].export_max_rows))
#                             self.export_max_rows = export_max_rows_1
#                         else:
#                             # print('settings_for_role[i][j].export_max_rows', settings_for_role[i][j].export_max_rows)
#                             if export_max_rows_1 <= settings_for_role[i][j].export_max_rows:
#                                 self.export_max_rows = settings_for_role[i][j].export_max_rows
#                             else:
#                                 self.export_max_rows = export_max_rows_1
#
#                         can_edit_1 = self.can_edit
#                         can_create_1 = self.can_create
#                         can_delete_1 = self.can_delete
#                         can_export_1 = self.can_export
#                         export_max_rows_1 = self.export_max_rows
#                         # print('export_max_rows_1=', export_max_rows_1)
#                         # print('self.export_max_rows=', self.export_max_rows)
#
#                         print('Настройка для пути=', path, 'can_edit=', self.can_edit, 'can_create=', self.can_create, 'can_delete=', self.can_delete, 'can_export=', self.can_export, 'export_max_rows=', self.export_max_rows )
#
#         print('Итоговая настройка', 'can_edit=', self.can_edit, 'can_create=', self.can_create, 'can_delete=', self.can_delete, 'can_export=', self.can_export, 'export_max_rows=', self.export_max_rows )
# Версия от 13.07.21-работает - конец




# РАБОТАЕТ (в зависимости от модели применяет свою настройку, НО
# берет настройку последней роли, а надо придумать логику
#  если у пользователя несколько ролей и есть настройки для одной модели(но они разные)
# сделать одну сборную настройку по максимальным доступам из каждой настройки!!
# class SpecificView(SettingAdminForAllRoles):
#     def _handle_view(self, name, **kwargs):
#         print(current_user.roles)
#         list_models = [Link, User, Role, ListModel, SettingAdmin, Usluga, Order]
#         path_list_models_lower = []
#         for mod in list_models:
#             path_mod = '/admin/'+str(mod.__name__).lower()+'/'
#             path_list_models_lower.append(path_mod)
#         print('path_list_models_lower', path_list_models_lower)
#         for path_model in path_list_models_lower:
#             print('path_model=', path_model)
#
#             if request.full_path.startswith(path_model):
#                 print(request.full_path.startswith(path_model))
#
#                 for i in range(len(current_user.roles)):
#                     setting_admin_for_roles_user = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[i])
#                 # setting_admin_for_roles_user = db.session.query(SettingAdmin).filter(db.and_(SettingAdmin.role == current_user.roles[i], SettingAdmin.model(Usluga))).first()
#                     print('Роль пользователя(current_user.roles[i])=', current_user.roles[i])
#                     # print(setting_admin_for_roles_user)
#                     for sett in setting_admin_for_roles_user:
#                     # print(str(sett.model).lower())
#                     #     path_model = str(sett.model).lower()
#                     #     print('path_model', path_model)
#                         print('str(sett.model).lower()=', str(sett.model).lower())
#                         print('path_model=', path_model)
#                     # for model_lower in list_models_lower:
#                         sett_model_lower_path = '/admin/'+str(sett.model).lower().lower()+'/'
#                         print('sett_model_lower_path', sett_model_lower_path)
#                         if sett_model_lower_path == path_model:
#                             self.name_setting = sett.name_setting
#                             self.role = sett.role
#                             self.can_create = sett.can_create
#                             self.can_edit = sett.can_edit
#                             self.can_delete = sett.can_delete
#                             self.can_export = sett.can_export
#                         # print('1-name_setting=', self.name_setting, 'self.mod=', self.mod, 'role=', self.role)
#                             print('1-name_setting=', self.name_setting, 'role=', self.role)
#                             print('1-can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
#                         # else:
#                         #     print('figny')
#                         #     self.name_setting = 'Такой настройки не существует'
#                         #     self.role = current_user.roles[i]
#                         #     self.can_create = False
#                         #     self.can_edit = False
#                         #     self.can_delete = False
#                         #     self.can_export = False
#                         # # print('2-name_setting=', self.name_setting, 'self.mod=', self.mod, 'role=', self.role)
#                         #     print('2-name_setting=', self.name_setting, 'role=', self.role)
#                         #     print('2-can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
# РАБОТАЕТ!!! - конец



        # print('mm из SpecificView=', mm)
        # list_models = [Link, User, Role, ListModel, SettingAdmin, Usluga, Order]
        # path_list_models_lower = []
        # for mod in list_models:
        #     path_mod = '/admin/'+str(mod.__name__).lower()+'/'
        #     path_list_models_lower.append(path_mod)
        # # print('path_list_models_lower', path_list_models_lower)
        # # for i in range(len(current_user.roles)):
        # #     setting_admin_for_roles_user = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[i])
        # #     for sett in setting_admin_for_roles_user:
        # #         print('0-name_setting=', sett.name_setting, 'role=', sett.role, 'model=', sett.model)
        # #         print('0-can_create =', sett.can_create, 'can_edit =', sett.can_edit, 'can_delete =', sett.can_delete, 'can_export', sett.can_export)
        # #     print('0-can_create =', sett.can_create, 'can_edit =', sett.can_edit, 'can_delete =', sett.can_delete, 'can_export', sett.can_export)
        # for path_model in path_list_models_lower:
        #     # print('path_model=', path_model)
        #
        #     if request.full_path.startswith(path_model):
        #         # print(request.full_path.startswith(path_model))
        #
        #         for i in range(len(current_user.roles)):
        #             setting_admin_for_roles_user = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[i])
        #         # setting_admin_for_roles_user = db.session.query(SettingAdmin).filter(db.and_(SettingAdmin.role == current_user.roles[i], SettingAdmin.model(Usluga))).first()
        #         #     print('Роль пользователя(current_user.roles[i])=', current_user.roles[i])
        #             # print(setting_admin_for_roles_user)
        #             for sett in setting_admin_for_roles_user:
        #             # print(str(sett.model).lower())
        #             #     path_model = str(sett.model).lower()
        #             #     print('path_model', path_model)
        #             #     print('str(sett.model).lower()=', str(sett.model).lower())
        #             #     print('path_model=', path_model)
        #             # for model_lower in list_models_lower:
        #                 sett_model_lower_path = '/admin/'+str(sett.model).lower().lower()+'/'
        #                 # print('sett_model_lower_path', sett_model_lower_path)
        #                 if sett_model_lower_path == path_model:
        #                     # print('sett_model_lower_path=', sett_model_lower_path)
        #                     # print('path_model=', path_model)
        #                     # print('УРА!!!')
        #
        #                     column_list = {'name_setting'}
        #                     self.column_list = column_list
        #                     self.role = sett.role
        #                     self.can_create = sett.can_create
        #                     self.can_edit = sett.can_edit
        #                     self.can_delete = sett.can_delete
        #                     self.can_export = sett.can_export
                            # print('1-name_setting=', self.name_setting, 'role=', self.role)
                            # print('1-can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)


                        # else:
                            # print('sett_model_lower_path=', sett_model_lower_path)
                            # print('path_model=', path_model)
                            # print('1-can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
                            # print('Ну и ну')


                        # print('1-name_setting=', self.name_setting, 'self.mod=', self.mod, 'role=', self.role)
                        #     print('1-name_setting=', self.name_setting, 'role=', self.role)
                        #     print('1-can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
                        # else:
                        #     print('figny')
                        #     self.name_setting = 'Такой настройки не существует'
                        #     self.role = current_user.roles[i]
                        #     self.can_create = False
                        #     self.can_edit = False
                        #     self.can_delete = False
                        #     self.can_export = False
                        # # print('2-name_setting=', self.name_setting, 'self.mod=', self.mod, 'role=', self.role)
                        #     print('2-name_setting=', self.name_setting, 'role=', self.role)
                        #     print('2-can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)




# class SpecificView(SettingAdminForAllRoles):

    # Пыталась использовать current_user но пишет что current_user None
    # Это происходит из-за однопоточности Flask
    # Cервер обслуживает нескольких пользователей,которые сами по себе являются потоками.
    # flask_login не был предназначен для дополнительной потоковой передачи в нем,
    # поэтому дочерний поток печатает None. (м https://question-it.com/questions/1673303/pochemu-dochernie-potoki-ne-mogut-poluchit-dostup-k-peremennoj-current_user-v-flask_login)
    # current_user доступна в функциях класса!!

    # print('9-from admin from class SpecificView current_user', current_user)
    # print('current_user.is_authenticated', current_user.is_authenticated)
    # print('current_user.roles', current_user.roles)
    # print('9-0 SpecificView has_app_context', has_app_context)

    # def is_visible(self):
    #     # Переопределите этот метод, если вы хотите динамически скрывать или
    #     # показывать административные представления из структуры меню Flask-Admin
    #     # По умолчанию пункт отображается в меню.
    #     # Обратите внимание, что пункт должен быть как видимым, так и доступным для отображения в меню.
    #     # По умолчанию возвращает True
    #     # Если False то заданные представления
    #     # (например admin.add_views(SpecificView(User, db.session), SpecificView(Link, db.session)))
    #     # не будут показаны в панели при заданных условиях (напрмер при определенной роли)
    #     # # Например
    #     if current_user.has_role('admin'):
    #         return True
    #     # if current_user.has_role('edit'):
    #     #     return False
    # ????????
    # def get_current_view():
    #     # Get current administrative view.
    #     return getattr(g, '_admin_view', None)


    #     # *** получаем из переменной контекста приложения current_user список ролей пользователя (current_user.roles),
    #     # затем получаем из модели настроек те настройки, которые соответствуют ролям пользователя
    #     # и выводим список наименований настроек.
    #     # print(current_user.roles)

    #     settings = []
    #     mod = []
    #     create = []
    #     # print(name)
    #     for list_model in list_models:

    #
    #     # ****2
    # def _handle_view(self, name, **kwargs):
    #     print(name)
    #     # list_models = [Link, User, Role, ListModel, SettingAdmin, Usluga]
    #     for i in range(len(current_user.roles)):
    #         print(current_user.roles[i])
    #         setting_admin_for_roles_user = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[i])
    #         # print(setting_admin_for_roles_user)
    #         for sett in setting_admin_for_roles_user:
    #             # print(sett.role)
    #             # print(sett.model)
    #             # print(str(sett.model))
    #             # print(type(str(sett.model)))
    #             # print(sett.name_setting)
    #
    #             self.name_setting = sett.name_setting
    #             self.model = sett.model
    #             self.role = sett.role
    #             self.can_create = sett.can_create
    #             self.can_edit = sett.can_edit
    #             self.can_delete = sett.can_delete
    #             self.can_export = sett.can_export
    #             self.name = sett.name_setting
    #             self.view = sett.model
    #
    #             # self.view = list_models[m].__name__
    #                     # print(self.name)
    #             print('name_setting', self.name_setting, 'model', self.model, 'role', self.role)
    #             print('can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
    # #                 else:
    #                     self.can_create = False
    #                     self.can_edit = True
    #                     self.can_delete = False
    #                     self.can_export = False
    # def get_current_view(name):
    #     print(name, g, '_admin_view', None)
    #     return getattr(g, '_admin_view', None)
        # ****2 -  конец


        # ****1
    # def _handle_view(self, name, **kwargs):
    #     list_models = [Link, User, Role, ListModel, SettingAdmin, Usluga]
    #     for i in range(len(current_user.roles)):
    #         setting_admin_for_roles_user = SettingAdmin.query.filter(SettingAdmin.role == current_user.roles[i])
    #         # print(current_user.roles[i])
    #         for sett in setting_admin_for_roles_user:
    #             # print(sett.model)
    #             # print('Применяем настройку с именем', sett.name_setting)
    #             # print(sett.model_id)
    #             for list_model in list_models:
    #                 # print('list_model=', list_model)
    #                 # print(type(list_model))
    #                 # print('Название модели из списка моделей list_model.__name__==', list_model.__name__)
    #                 # print(type(list_model.__name__))
    #                 # print(list_model.__class__.__name__)
    #                 # print(__class__.__name__)
    #                 # print('Название модели из выбранной настройки str(sett.model)==', str(sett.model))
    #                 # print(type(str(sett.model)))
    #                 # print(sett.model_id)
    #
    #                 if list_model.__name__ == str(sett.model):
    #                     # print('list_model.__name__=', list_model.__name__, 'type(list_model.__name__)=', type(list_model.__name__))
    #                     # print('sett.model=', sett.model, 'type(sett.model)=', type(sett.model) )
    #                     # print('str(sett.model)=', str(sett.model), 'type(str(sett.model))=', type(str(sett.model)))
    #                     self.name_setting = sett.name_setting
    #                     # print('self.name_setting=', self.name_setting)
    #                     # self.model = str(sett.model)
    #                     # print('self.model=', self.model)
    #                     self.role = sett.role
    #                     # print('self.role=', self.role)
    #                     # self.name = list_model.__name__
    #                     # print('self.name=', self.name)
    #                     self.can_create = sett.can_create
    #                     self.can_edit = sett.can_edit
    #                     self.can_delete = sett.can_delete
    #                     self.can_export = sett.can_export
    #                     # self.model = list_model.__name__

                        # print('name_setting', self.name_setting, 'model', self.model, 'role', self.role)
                        # print('can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
                        # print('name=', self.name )
        #             else:
        #                 self.can_create = False
        #                 self.can_edit = True
        #                 self.can_delete = False
        #                 self.can_export = False
        #             #     print(False)
        #             #     print('настройка для роли', current_user.roles[i], 'и модели', sett.model)
        #             #     print('can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
        #             #
        #             #
        #
        #         # print('can_create =', sett.can_create, 'can_edit =', sett.can_edit, 'can_delete =', sett.can_delete, 'can_export', sett.can_export)
        #
        #     # print('настройка для роли', current_user.roles[i], 'и модели', sett.model)
        #     # print('can_create =', sett.can_create, 'can_edit =', sett.can_edit, 'can_delete =', sett.can_delete, 'can_export', sett.can_export)
        #     print('can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
        #     print('настройка для роли', current_user.roles[i], ' модели', sett.model, 'настройки', )
        #     print('Применяем настройку с именем', sett.name_setting)
        #         # print(sett.model)
        #         # settings.append(sett)
        #         # print('settings', settings)
        #         # mod.append(sett.model)
        #         # print('mod', mod)
        #         # create.append(sett.can_create)
        #         # print('create', create)
        #         # print('can_create =', sett.can_create, 'can_edit =', sett.can_edit, 'can_delete =', sett.can_delete, 'can_export', sett.can_export)
        #
        #         # print(sett.name_setting, sett.role, sett.model)
        #         # print(settings)
        #         # print(mod)
        #
        #     # если return str(mod), то создаст html страницу
        #     # где будет выведена строка [User, Menu, Order] (значение str(mod))
        #     # return str(mod)
        # # *** - конец
        # # ****1 -  конец

        # **** - выборка настроек из базы ( 2 вар, но он более длинный
        # - сначала выборка всех настроек из базы,
        # затем из них все остальное.  То что выше - оптимальнее(наверное))
        # setting_admin_for_all_roles = SettingAdmin.query.all()
        # for setting_for_user_with_role in setting_admin_for_all_roles:
        #     for i in range(len(current_user.roles)):
        #         print('122-i=', i, 'current_user.roles[i]=', current_user.roles[i])
        #         if setting_for_user_with_role.role ==  current_user.roles[i]:
        #             can_create = setting_for_user_with_role.can_create
        #             print(can_create)
        # **** - конец



                # print(str(sett.model).lower())
                # for list_model in list_models:
                    # print('list_model=', list_model)
                    # print(type(list_model))
                    # print('Название модели из списка моделей list_model.__name__==', list_model.__name__)
                    # print(type(list_model.__name__))
                    # print(list_model.__class__.__name__)
                    # print(__class__.__name__)
                    # print('Название модели из выбранной настройки str(sett.model)==', str(sett.model))
                    # print(type(str(sett.model)))
                    # print(sett.model_id)

                    # if list_model.__name__ == str(sett.model):
                    #     print('list_model.__name__=', list_model.__name__, 'type(list_model.__name__)=', type(list_model.__name__))
                        # print('sett.model=', sett.model, 'type(sett.model)=', type(sett.model) )
                # print('str(sett.model)=', str(sett.model), 'type(str(sett.model))=', type(str(sett.model)))
                # self.name_setting = sett.name_setting
                # self.models = str(sett.model).lower()
                # print('self.models=', self.models)
                # self.role = sett.role
                # self.name = name
                # print('self.name=', self.name)
                #         self.can_create = sett.can_create
                #         self.can_edit = sett.can_edit
                #         self.can_delete = sett.can_delete
                #         self.can_export = sett.can_export
                # endpoint = index_view
                # self.endpoint = self._get_endpoint()
                # print(self.endpoint)
                # print(current_user.roles[i])
                # print('Имя настройки', sett.name_setting, 'Модель=', sett.model, 'Роль=', current_user.roles[i])
                #         print('name_setting', self.name_setting, 'self.mod=', self.mod, 'role=', self.role)
                #         print('can_create =', self.can_create, 'can_edit =', self.can_edit, 'can_delete =', self.can_delete, 'can_export', self.can_export)
                # settings.append(sett)
                # # print('settings', settings)
                # mod.append(sett.model)
                # # print('mod', mod)
                # create.append(sett.can_create)
                # print('create', create)
                # admin.add_view(self,view=view)

                # super(SpecificView, self).__init__(User, session, name=name)


# Модель User для роли admin
# class ModelUserRoleAdmin(ModelView):
#
#     # Задает поля из базы, отображаемые в админ панели
#     column_list = ['id', 'email', 'password', 'active', 'confirmed_at', 'created_on', 'updated_on', 'roles', 'orders']
#
#     # Класс формы. Переопределите, если вы хотите использовать
#     # пользовательскую форму для своей модели.
#     # Полностью отключит остальную функциональность форм!!!!
#     # Перед этим нужно создать класс формы(у нас MyForm (см выше)
#     # унаследовать его от FlaskForm(тк мы используем flask_wtf
#     #  (в документации просто Form - можно использовать что-то другое видимо)
#     # и сделать импорты
#     # from flask_wtf import FlaskForm
#     # from wtforms import StringField
#     # Эта форма появляется при нажатии редактирования строки модели
#     # и содержит поле ввода Name
#     #
#     # form = MyForm
#
#     # Позволяет добавить дополнительное поле в форму редактирования
#     # Как сохранить инфу, введенную в этом поле?
#     # form_extra_fields = {
#     #                 'строка комментарии': StringField('комментарии')
#     #             }
#
#     # Вставляет кнопку экспорта.
#     # Экспортируются все данные, содержащиеся в таблице в формат csv
#     # если не задан export_max_rows = 2, где 2 максимум разрешенных к экспорту строк
#     # какие строки выбирает для экспорта не знаю
#     # (предполагаю что последние по времени сохраненные)
#     can_export = True
#
#     # Устанавливаются колонки, которые экспортируются
#     # Если не установлено - экспортирует все
#     # column_export_list = ['id', 'email', 'roles']
#
#     # Задает максимум разрешенных к экспорту строк
#     # какие строки выбирает для экспорта не знаю
#     # (предполагаю что последние по времени сохраненные)
#     # Если не установлено - экспортирует все
#     export_max_rows = 2
#
#     # export_types - Задает формат экспорта строк
#     # Если export_types явно не указан - по умолчанию экспортирует в csv
#     # Для других форматов кроме csv понадобилось инсталлировать Tablib
#     # https://tablib.readthedocs.io/en/stable/
#     # $ pip install "tablib[all]"
#     # Можно инсталлировать выборочно определенные форматы например $ pip install "tablib[xlsx]"
#     # Я инсталлировала все форматы
#     # Форматы, которые поддерживает Tablib
#     # cli, csv,dbf, df (DataFrame), html, jira, json, latex, ods, rst, tsv, xls, xlsx, yaml
#     export_types = ['csv', 'xls', 'html', 'json']
#
#     # Присвоить столбцам из модели заголовки
#     # Словарь, где ключ-это имя столбца, а значение-строка для отображения.
#     column_labels = dict(email='логин(e-mail)', created_on='создан', updated_on='обновлен', active='активен', roles='роль', orders='заказы')
#
#     # Добавляет столбцы-отношения
#     column_display_all_relations = True
#
#     # ???
#     # column_hide_backrefs = True
#     # column_hide_backrefs = False
#
#     # Определяет, должен ли первичный ключ отображаться в представлении списка.
#     column_display_pk = True
#
#     # Задает поля, в которых возможен поиск
#     # Поля - отношения в поиск ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
#     # не roles а roles.name, не 'orders' а 'orders.order'
#     # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
#     # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
#     column_searchable_list = ['id', 'email', 'active', 'confirmed_at', 'created_on', 'updated_on', 'roles.name', 'orders.order']
#
#     # Задает поля, в которых возможна булева фильтрация
#     column_filters = (BooleanEqualFilter(column=User.active, name='active'),)
#
#     # Задает поля, в которых возможна фильтрация
#     column_filters = ['id', 'email', 'password', 'active', 'confirmed_at', 'created_on', 'updated_on', 'roles', 'orders']
#
#      # ???
#     # column_details_list = ['id', 'email', 'password', 'active', 'confirmed_at', 'created_on', 'updated_on', 'roles', 'orders']
#
#     # Задает поля, в которых возможна сортировка
#     # Поля - отношения в сортировку ВКЛЮЧАТЬ ОСОБЫМ СПОСОБОМ!!!!!
#     # так как при включении просто roles или orders при попытке сортировки выдаст ошибку
#     # поскольку, видимо, ролей и заказов может быть несколько и, следовательно,
#     # не понятно как сортировать???
#     # см. https://progi.pro/kak-ispolzovat-flask-admin-column_sortable_list-s-bazoy-dannih-6787155
#     # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
#     column_sortable_list = ['id', 'email', 'active', 'confirmed_at', 'created_on', 'updated_on', ('roles', 'roles.name'), ('orders', 'orders.order')]
#
#     # Задает поля, в которых возможно быстрое редактирование(то есть при нажатии на это поле)
#     # Почему-то работает не со всеми строками? Почему не знаю
#     # column_editable_list = ['email', 'password', 'active', 'confirmed_at', 'created_on', 'updated_on', 'roles', 'orders']
#
#     # Удалить столбцы из списка
#     column_exclude_list = ['password']
#
#     can_create = True
#     can_edit = True
#     can_delete = True
#
#     # Задает редактируемые поля.
#     # Если не задать то по умолчанию доступны для редактирования все поля
#     # form_edit_rules = {'active', 'roles'}
#
#     # Количество строк-записей из базы на странице
#     # page_size = 5
#
#     # Позволяет выбрать размер страницы с помощью выпадающего списка
#     can_set_page_size = True
#
#     # Редактирование в модальном окне, а не на отдельной странице
#     edit_modal = True
#
#     # Создание новой записи в модальном окне, а не на отдельной странице
#     create_modal = True
#
#     def is_accessible(self):
#         return (current_user.is_active and
#                 current_user.is_authenticated and
#                 current_user.has_role('admin')
#                 )
#     def inaccessible_callback(self, name, **kwargs):
#         # Еще надо защитить и проверить next!!!
#         return redirect (url_for('login.login', next=request.url))






# # Настройка административной панели в зависимости от роли пользователя
# # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
# # Подробнее:
# # E:\0-ALL-FLASK\REKLAMA\RECL\env\Lib\site-packages\flask_admin\model\base.py
#


# Защита Административной панели - пробный вариант
# @app.before_first_request
# @app.before_request
# def before_request():
#     if request.full_path.startswith('/admin/'):
#         if not current_user.is_authenticated:
#             err = '11 Авторизуйтесь пожалуйста'
#             # next=request.url
#             next_page = request.args.get('next')
#             # Проверка параметра next
#             # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
#             # Login Example
#             #     Once a user has .......
#             # is_safe_url должен проверить, безопасен ли URL-адрес для перенаправления.
#             # См. http://flask.pocoo.org/snippets/62/ для примера.
#             # Предупреждение: Вы ДОЛЖНЫ проверить значение следующего параметра. Если вы этого не сделаете,
#                 # ваше приложение будет уязвимо для открытых перенаправлений.
#             if not next or not is_safe_url(next):
#                 return flask.abort(400)
#             #
#             # return redirect(next or url_for('render_main'))
#             return redirect(url_for('login.login', next=next, err=err))
#             if not next_page or url_parse(next_page).netloc != '':
#                 next_page = url_for('render_main')
#         elif current_user.is_authenticated and not current_user.has_role('admin'):
#             err = '11 Вы вошли в систему, однако у вас недостаточно прав для просмотра данной страницы. ' \
#                   'Возможно, вы хотели бы войти в систему, используя другую учётную запись? '
#             next=request.url
#             if not is_safe_url(next):
#                 return flask.abort(400)
#             return redirect(url_for('login.login', next=next, err=err))
# Защита Административной панели - пробный вариант -  конец


