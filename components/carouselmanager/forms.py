import re
import email_validator

from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, MultipleFileField
from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
from wtforms import PasswordField, IntegerField, validators, TextAreaField
# from wtforms import TextField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo, Regexp
# from wtforms.validators import ValidationError
# from RECL.models import db, Link, Usluga

# импорты для загрузки файлов - начало
from flask_wtf.file import FileField, FileAllowed, FileRequired
# импорты для загрузки файлов - конец


# Форма для получения исходных данных для создания формы карусели(кол-во фото, имя, директория загрузки)
class DeleteCarouselForm(FlaskForm):
    name_carousel = StringField("Имя карусели", [InputRequired()])
    dir_carousel = StringField("Директория загрузки", [InputRequired()])
    number_foto = SelectField('Количество изображений в карусели:', choices = [(i+1, i+1) for i in range(0, 20)], validators=[DataRequired()])
    # active = BooleanField(default=True)
    # arhive = BooleanField(default=False)
    # photo = FileField('Загрузите фото для карусели', render_kw={'multiple': True})
    submit_create = SubmitField('Следующий шаг')



# Форма для получения исходных данных для создания формы карусели(кол-во фото, имя, директория загрузки)
class CreateCarouselForm(FlaskForm):
    name_carousel = StringField("Имя карусели", [InputRequired()], render_kw={'autofocus': True })
    dir_carousel = StringField("Директория загрузки",
                               [InputRequired(),
                                Regexp("^[a-zA-Z]+$",
                                       message='Имя директории загрузки должно быть задано латинскими буквами'),
                                Length(min=1, max=8)],
                               render_kw={'placeholder': "Латинские буквы, не более 8"})
    number_foto = SelectField('Количество изображений в карусели:', choices = [(i+1, i+1) for i in range(0, 20)], validators=[DataRequired()])
    # active = BooleanField(default=True)
    # arhive = BooleanField(default=False)
    # photo = FileField('Загрузите фото для карусели', render_kw={'multiple': True})
    submit_create = SubmitField('Следующий шаг')

# Форма (составная из двух классов UploadCarouselForm и CarouselForm)
# для получения исходных данных для создания формы карусели(кол-во фото, имя, директория загрузки)
# CarouselForm перенесла в carousel.py, тк не знаю как здесь задать параметр min_entries=int(number_foto)
class UploadCarouselForm(FlaskForm):
    title_foto_carousel = StringField("Заголовок фото")
    text_foto_carousel = StringField("Текст фото")
    photo = FileField('Фото', [DataRequired()])
    class Meta:
        csrf = False

# class CarouselForm(FlaskForm):
#     all_photo = FieldList(FormField(UploadCarouselForm), min_entries=int(number_foto))
#     submit_carousel = SubmitField('Загрузить фото')

# Форма для редактирования слайда в карусели
class EditTextSlaidForm(FlaskForm):
    title_foto_carousel = StringField("Заголовок слайда")
    text_foto_carousel = TextAreaField("Текст слайда")
    submit_edit_slaid = SubmitField('Сохранить изменения')

# Форма для редактирования слайда в карусели
class ReplaceSlaidForm(FlaskForm):
    title_foto_carousel = StringField("Заголовок слайда")
    text_foto_carousel = TextAreaField("Текст слайда")
    photo = FileField('Загрузить слайд', [DataRequired()])
    submit_edit_slaid = SubmitField('Сохранить изменения')

# Форма для добавления слайда в карусели
class AddSlaidForm(FlaskForm):
    title_foto_carousel = StringField("Заголовок слайда")
    text_foto_carousel = TextAreaField("Текст слайда")
    photo = FileField('Загрузить слайд', [DataRequired()])
    submit_add_slaid = SubmitField('Добавить')


    # Форма для добавления слайда в карусели
class ProbaForm(FlaskForm):
    choose = SelectField("Сортировать", choices = ['По названию', 'по дате'])
    submit_proba = SubmitField('выбрать')