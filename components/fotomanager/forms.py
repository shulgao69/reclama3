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
# см также https://docs-python.ru/packages/veb-frejmvork-flask-python/rasshirenie-flask-wtf/
from flask_wtf.file import FileField, FileAllowed, FileRequired
# импорты для загрузки файлов - конец

password_length = 2



# Форма для удаления файла из миниатюр - не понадобилась, но пока оставлю
class DeleteFormFromMini(FlaskForm):
    secure_name_photo = HiddenField('Имя фото в базе')
    origin_name_photo = HiddenField('Исходное имя фото')
    dir_uploads = HiddenField('Полная директория загрузки фото')
    dir_usluga = HiddenField('Директория услуги')
    dir_menu = HiddenField('Директория меню')
    submit_delete_form_from_mini = SubmitField('Удалить')

# Форма для редактирования файла из миниатюр
class EditFormFromMini(FlaskForm):
    secure_name_photo = HiddenField('Имя фото в базе', [InputRequired()])
    origin_name_photo = HiddenField('Исходное имя фото', [InputRequired()])
    dir_uploads = HiddenField('Полная директория загрузки фото', [InputRequired()])
    dir_usluga = HiddenField('Директория услуги', [InputRequired()])
    dir_menu = HiddenField('Директория меню', [InputRequired()])
    # про render_kw задает высоту поля(строки)
    #  см: https://stackoverflow.com/questions/7979548/how-to-render-my-textarea-with-wtforms
    # в самой форме это поле можно вытянуть за правй нижний угол
    comments = TextAreaField("Сопроводительный текст", render_kw={"rows": 4, "cols": 1})
    title = StringField("Заголовок услуги")
    hidden_comments = HiddenField("Сопроводительный текст")
    hidden_title = HiddenField("Заголовок услуги")
    submit_edit_form_from_mini = SubmitField('Редактировать')
    submit_save_form_from_mini = SubmitField('Сохранить')

# Форма для удаления файла (cм в views.py)
class DeleteForm(FlaskForm):
    form_delete_name = HiddenField('DeleteFormName')
    menu = SelectField('Раздел:', validators=[DataRequired()], id='select_menu_for_delete')
    usluga = SelectField('Услуга:', validators=[DataRequired()], id='select_usluga_for_delete')
    names_files_for_delete = SelectField('Файлы для удаления:', validators=[DataRequired()], id='select_files_for_delete')
    delete_file = FileField('Выберите файл для удаления')
    submit_delete_form = SubmitField('Удалить файл')



# ******-->
# Выбор из выпадающего списка и обновление другого списка в формах
# class Choice2, FormChoice2(form_name='FormChoice2Name') и
# @app.route('/_get_usl_choice1_admin/')
# def _get_usl_choice1_admin():
# Полностью основано на https://stackoverflow.com/questions/41232105/populate-wtforms-select-field-using-value-selected-from-previous-field
# Заменены переменные, названия функций, также в choice1.html добавлен
# <script src="https://code.jquery.com/jquery-3.2.1.min.js"
#       integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
#       crossorigin="anonymous">
#      </script>!!!

class FormChoice2(FlaskForm):
    # Cкрытое поле HiddenField заданное явно можно исключить.
    # Оно нужно чтобы иметь возможность, если это необходимо, передавать неизменяемую
    # пользователем информацию. Часто используют когда форма в форме
    # и ее нужно назвать чтобы не запутаться
    # У нас дополнительная проверка при запросе POST
    # (точно не знаю зачем, возможно, чтобы формы не были перехвачены в процессе запроса?)
    # но это можно убрать!!! Я оставлю пока
    #  к скрытым полям относиться и CRFToken он по умолчанию задается и прописывается в файле HTML
    form_name = HiddenField('FormChoice2Name')
    menu = SelectField('Раздел:', validators=[DataRequired()], id='select_menu')
    usluga = SelectField('Услуга:', validators=[DataRequired()], id='select_usluga')
    # photo = FileField('Выбор фото', validators=[FileRequired()])
    comments = TextAreaField("Сопроводительный текст")
    title = StringField("Заголовок фото")
    photo = FileField('Выбрать фото для загрузки', validators=[FileRequired()])
    submit = SubmitField('Загрузить')

# Выбор из выпадающего списка и обновление другого списка в формах -  конец
# ******-->


# ******-->
# Выбор из выпадающего списка и обновление другого списка в формах
# class Choice1, FormChoice1(form_name='FormChoice1Name') и
# @app.route('/_get_usl_choice1_admin/')
# def _get_usl_choice1_admin():
# Полностью основано на https://stackoverflow.com/questions/41232105/populate-wtforms-select-field-using-value-selected-from-previous-field
# Заменены переменные, названия функций, также в choice1.html добавлен
# <script src="https://code.jquery.com/jquery-3.2.1.min.js"
#       integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
#       crossorigin="anonymous">
#      </script>!!!

class FormChoice1(FlaskForm):
    # Cкрытое поле HiddenField заданное явно можно исключить.
    # Оно нужно чтобы иметь возможность, если это необходимо, передавать неизменяемую
    # пользователем информацию. Часто используют когда форма в форме
    # и ее нужно назвать чтобы не запутаться
    # У нас дополнительная проверка при запросе POST
    # (точно не знаю зачем, возможно, чтобы формы не были перехвачены в процессе запроса?)
    # но это можно убрать!!! Я оставлю пока
    #  к скрытым полям относиться и CRFToken он по умолчанию задается и прописывается в файле HTML

    form_name = HiddenField('FormChoice1Name')
    menu = SelectField('Menu:', validators=[DataRequired()], id='select_menu')
    usluga = SelectField('Usluga:', validators=[DataRequired()], id='select_usluga')
    submit = SubmitField('Выбрать')

# Выбор из выпадающего списка и обновление другого списка в формах -  конец
# ******-->


# **** Загрузка фото в админке отдельной кнопкой
# https://docs-python.ru/packages/veb-frejmvork-flask-python/rasshirenie-flask-wtf/
class PhotoFormAdmin(FlaskForm):
    # Теоретически есть встроенный валидатор FileAllowed(['jpg', 'png'], "Images only!")]
    # для проверки расширений загружаемых файлов, но он почему-то не работает
    # Как утверждается он работает и без FlaskUpload, но у меня нет.
    # Попробовать через FlaskUpload!!!!
    # photo = FileField('Фото', validators=[FileRequired(), FileAllowed(['jpg', 'png'], "Images only!")])
    photo = FileField('Фото', FileRequired())
    submit = SubmitField('Загрузить файл')
# **** Загрузка фото в админке отдельной кнопкой - конец



# ******* Вариант2 - выбор из выпадающего списка- попытка
# Основано на https://www.youtube.com/watch?v=I2dJuNwlIH0-->
# Но не получилось(10.08.21)
# пока оставить и пропробовать позже (см LoadPhotoWithChoice2 в admin/init.py-->
# class PhotoFormAdmin2(FlaskForm):
#     form_name = HiddenField('LoadPhotoWithChoice2')
#     menu = SelectField('menu', choices=[])
#     usluga = SelectField('usluga', choices=[])
#     # ***** Вариант2 - конец




