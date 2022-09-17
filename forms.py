# import re
# import email_validator

from flask_wtf import FlaskForm

from wtforms import SubmitField, SelectField, HiddenField, BooleanField, StringField, \
    PasswordField, IntegerField, validators, DateField, DateTimeField, RadioField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo

# импорты для загрузки файлов - начало

from flask_wtf.file import FileField, FileAllowed, FileRequired
# from werkzeug.utils import secure_filename
# импорты для загрузки файлов - конец

# Задавала длину пароля для валидации, так как не могла импортировать данные из конфига,
# но позже (см ниже) все получилось, поэтому закоммитила
# password_length = 2

# *** Получение данных для валидации (PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH) из файла config.py - начало
# Следующие импорты нужны для того чтобы загрузить данные из корневого файла config.py
# и затем использовать для получения значения
# app.config['PASSWORD_MIN_LENGTH'] и app.config['PASSWORD_MAX_LENGTH']
# Если же попытаться  сделать такой импорт
# from RECL.__init__ import app
# а затем получать значение app.config['PASSWORD_MIN_LENGTH']
# то выдает ошибку импорта app. В блюпринте админки такой импорт почему-то ошибки не дает! Разобраться!!
# НЕ ЗАБЫТЬ ПОМЕНЯТЬ ПОТОМ (при запуске на продакшн)
# app.config.from_object(DevelopConfig) на app.config.from_object(Config)!!!
from flask import Flask
from RECL.config import DevelopConfig, Config
app = Flask(__name__)
app.config.from_object(DevelopConfig)
# *** Получение данных для валидации (PASSWORD_MIN_LENGTH) из корневого файла config.py - конец



# Форма для загрузки файла (cv в views.py)
# https://docs-python.ru/packages/veb-frejmvork-flask-python/rasshirenie-flask-wtf/
class PhotoForm(FlaskForm):
    # name_photo = StringField("Имя файла", [InputRequired()])
    # dir_uploads = StringField("Директория загрузки", [InputRequired()])
    # path_photo = StringField("Путь")
    # upload = FileField('image', validators=[FileRequired(),
    #     FileAllowed(['jpg', 'png'], 'Images only!')
    # ])
    # photo = FileField(validators=[FileRequired()])
    photo = FileField()


class OrderFormFromMenu(FlaskForm):
    name_user = StringField("Ваше имя", [InputRequired()])
    email_user = StringField("Электронная почта", [InputRequired()])
    phone_user = StringField("Телефон", [InputRequired()])
    order_user = StringField("Параметры заказа", [InputRequired()])


# ВНИМАНИЕ!
# В RegistrationForm и LoginForm
# Были такие ошибки: Сами валидаторы работают, а сообщения заданные в валидаторах не появляются!!!
# В итоге  добавила в html
# {% for err in form.username.errors %}-->
# <!--<p class="error alert alert-warning" role="alert" >{{ err }}</p>-->
# <!--{% endfor %} и все заработало

# В словаре render_kw={....} можно задать атрибуты поля,
# которые (если не используется Flask-wtform) можно задать в теге <input>
# перечень этих атрибутов см например http://htmlbook.ru/html/input
# Какие из этих атрибутов будут работать - не знаю, не все проверяла
# Такие работают - проверяла:
# 'autofocus': True/False, 'placeholder': "name@mail.ru",
# disabled': True/False, 'readonly': True/False
# у нас это - автофокус (autofocus': True) и placeholder (образец заполнения поля (подсказка))
# если например задать 'disabled': True или 'readonly': True то поле будет не активным.
# Но тогда если задать валидатор InputRequired то все время будет ругаться
# что поле должно быть заполнено. Поэтому внимательно с render_kw
class RegistrationForm(FlaskForm):
    username = StringField("Электронная почта",
                           [InputRequired(), Email(message='Проверьте адрес электронной почты1')],
                           render_kw={'autofocus': True, 'placeholder': "E-mail"}
                           )
    password = PasswordField("Пароль", [InputRequired(message='Вы не ввели пароль'),
            Length(min=app.config['PASSWORD_MIN_LENGTH'],
                   max=app.config['PASSWORD_MAX_LENGTH'],
                   message="Пароль должен быть не менее " + str(app.config['PASSWORD_MIN_LENGTH']) +' и не более ' + str(app.config['PASSWORD_MAX_LENGTH']) + " символов"
                   )
                                        ],
                             render_kw={'placeholder': "Пароль"}
                             )

    # Подтверждение что user - юридическое лицо
    user_organization = RadioField("Укажите тип пользователя", [InputRequired()], default='value_one', choices=[('value_one', 'юридическое лицо'),
                          ('value_two', 'индивидуальный предприниматель'), ('value_three', 'частное лицо')])




class LoginForm(FlaskForm):
    username = StringField("Электронная почта",
                           [InputRequired(), Email(message='Проверьте адрес электронной почты')],
                           render_kw={'autofocus': True, 'placeholder': "E-mail"}
                           )
    password = PasswordField("Пароль", [InputRequired(),
            Length(min=app.config['PASSWORD_MIN_LENGTH'],
                   message="Пароль должен быть не менее " + str(app.config['PASSWORD_MIN_LENGTH']) +" символов"
                   )
                                        ],
                             render_kw={'placeholder': "Пароль"}
                             )


# Согласие об использовании cookies
class ConsentForm(FlaskForm):
    consent = BooleanField('Принять')


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Пароль:", validators=[DataRequired(),
        Length(min=app.config['PASSWORD_MIN_LENGTH'], message="Пароль должен быть не менее " + str(app.config['PASSWORD_MIN_LENGTH']) +" символов")])
    confirm_password = PasswordField("Пароль ещё раз:")


class SettingForm(FlaskForm):
    can_delete = BooleanField("Разрешить удаление (can_delete)")
    can_edit = BooleanField("Разрешить редактирование (can_edit)")
    can_create = BooleanField("Разрешить создание (can_create)")
    columns = StringField("Количество колонок", [InputRequired()])
    any = StringField("Что-то еще", [InputRequired()])

    can_export = BooleanField("Разрешить экспорт (can_export)")
    export_max_rows = IntegerField("Укажите макс. кол-во строк?(или столбцов?) для экспорта (export_max_rows)")
    # Определяет, должен ли первичный ключ отображаться в представлении списка.
    column_display_pk = BooleanField("Отобразить первичный ключ (column_display_pk)")

    # Редактирование в модальном окне, а не на отдельной странице
    edit_modal = BooleanField("Редактировать в модальном окне? (а не на отдельной стр.)(edit_modal)")


class UserOrder(FlaskForm):
    name_user = StringField("Ваше имя", [InputRequired()])
    address_user = StringField("Адрес", [InputRequired()])
    email_user = StringField("Электропочта", [InputRequired()])
    phone_user = StringField("Телефон", [InputRequired()])