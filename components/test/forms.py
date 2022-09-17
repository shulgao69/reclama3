import re
import email_validator

from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField
from wtforms import PasswordField, IntegerField, validators, TextAreaField
# from wtforms import TextField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
# from wtforms.validators import ValidationError
# from RECL.models import db, Link, Usluga

# импорты для загрузки файлов - начало
from flask_wtf.file import FileField, FileAllowed, FileRequired
# импорты для загрузки файлов - конец

password_length = 2



class TestForm(FlaskForm):

    menu = SelectField('Раздел:', validators=[DataRequired()], id='select_menu')
    usluga = SelectField('Услуга:', validators=[DataRequired()], id='select_usluga')
    comments = TextAreaField("Сопроводительный текст")
    title = StringField("Заголовок услуги")
    photo = FileField('Выбор фото')
    submit = SubmitField('Загрузить')