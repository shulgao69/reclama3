import re
import email_validator

from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField
# from wtforms import PasswordField, IntegerField, validators, TextAreaField, TextField
from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
# from wtforms.validators import ValidationError
# from RECL.models import db, Link, Usluga

# импорты для загрузки файлов - начало
from flask_wtf.file import FileField, FileAllowed, FileRequired
# импорты для загрузки файлов - конец

password_length = 2


# Форма для создания таблицы прайсов
class PriceForm(FlaskForm):
    name_price_table = StringField("Заголовок таблицы")
    comments_table = TextAreaField("Комментарии к таблице")
    row_table = IntegerField('Количество строк в прайсе (row_table)', validators=[InputRequired()])
    col_table = IntegerField('Количество столбцов в прайсе (col_table)', validators=[InputRequired()])
    submit = SubmitField('Создать таблицу')





