import re
import email_validator

from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, MultipleFileField
from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
from wtforms import PasswordField, IntegerField, validators, TextAreaField
# from wtforms import TextField
from wtforms.validators import InputRequired, Length, NumberRange, Email, DataRequired, EqualTo, Regexp
# from wtforms.validators import ValidationError
# from RECL.models import db, Link, Usluga

# импорты для загрузки файлов - начало
from flask_wtf.file import FileField, FileAllowed, FileRequired
# импорты для загрузки файлов - конец


# Форма для получения исходных данных для создания спецификации статусов карточки услуг
class Specification(FlaskForm):
    days = IntegerField("Дней", [InputRequired(), NumberRange(min=0, max=366)], render_kw={'autofocus': True })
    hours = IntegerField("Часов", [InputRequired(), NumberRange(min=0, max=23)], render_kw={'autofocus': True})
    minutes = IntegerField("Минут", [InputRequired(), NumberRange(min=0, max=59)], render_kw={'autofocus': True})
    role = SelectField("Роль", validators=[DataRequired()], render_kw={'autofocus': True})
    status_card_id = HiddenField('статус карты услуг (id)')
    submit = SubmitField('Сохранить')

# Форма для получения исходных данных для создания формы карусели(кол-во фото, имя, директория загрузки)
class CreateCardUslugaForm(FlaskForm):
    name_card_usluga = StringField("Имя карточки услуг",
                                   [InputRequired()],
                                #    [InputRequired(),
                                #     Regexp("^[a-zA-Zа-яА-Я0-9]+[a-zA-Zа-яА-Я0-9\s_-]+$",
                                #           message='Имя может содержать только буквы, цифры, тире, дефис, а также пробелы'),
                                # Length(min=1, max=60)],
                                   render_kw={'autofocus': True })
    # comments = TextAreaField("Сопроводительный текст")
    comments =CKEditorField("Сопроводительный текст")
    # Regexp("^[a-zA-Z]+$", - только латинские буквы
    # message='Имя директории загрузки должно быть задано латинскими буквами'),
    # Regexp("^[a-zA-Z0-9]+[a-zA-Z0-9_-]+$" - только латинские буквы, цифры или _ -(кроме первого символа)
    # dir_photos убрала тк сделала автоматическое создание директории по имени карточки услуги
    # dir_photos = StringField("Директория для загрузки изображений",
    #                            [InputRequired(),
    #                             Regexp("^[a-zA-Z0-9]+[a-zA-Z0-9_-]+$",
    #                                    message='Имя директории должно состоять из латинских букв, цифр, а также нижнего подчеркивания или тире(кроме первого символа)'),
    #                             Length(min=1, max=60)],
    #                            render_kw={'autofocus': True, 'placeholder': "Латинские буквы, не более 30"})
    # number_foto = SelectField('Количество изображений в карточке услуг:', choices = [(i+1, i+1) for i in range(-1, 20)], validators=[DataRequired()])
    # active = BooleanField(default=True)
    # arhive = BooleanField(default=False)
    # photo = FileField('Загрузите фото для карусели', render_kw={'multiple': True})
    menu = SelectField('Раздел:', validators=[DataRequired()], id='select_menu')
    usluga = SelectField('Услуга:', validators=[DataRequired()], id='select_usluga')
    type_production = SelectField('Тип производства:', validators=[DataRequired()])
    submit_create = SubmitField('Следующий шаг')


class UploadFoto(FlaskForm):
    title = StringField("Заголовок фото", render_kw={'autofocus': True})
    comments = TextAreaField("Текст фото")
    photo = FileField('Фото')
    submit_upload = SubmitField('Загрузить фото')
    submit_end = SubmitField('Добавить прайсы')
    submit_add = SubmitField('Добавить фото')

# Форма для редактирования заголовка и сопроводительного текста фото
class EditFormNameTextCards(FlaskForm):

    name_card_usluga = StringField("Заголовок карточки услуги", [InputRequired(),
                                   Regexp("^[a-zA-Zа-яА-Я0-9]+[a-zA-Zа-яА-Я0-9\s_-]+$",
                                          message='Имя может содержать только буквы, цифры, тире, дефис, а также пробелы'),
                                Length(min=1, max=60)],
                                   render_kw={'autofocus': True})
    # про render_kw задает высоту поля(строки)
    #  см: https://stackoverflow.com/questions/7979548/how-to-render-my-textarea-with-wtforms
    # в самой форме это поле можно вытянуть за правый нижний угол
    comments = CKEditorField("Сопроводительный текст", render_kw={"rows": 4, "cols": 1})
    submit = SubmitField('Сохранить изменения')


# Форма для редактирования заголовка и сопроводительного текста фото
class EditFormPhotoCards(FlaskForm):
    # про render_kw задает высоту поля(строки)
    #  см: https://stackoverflow.com/questions/7979548/how-to-render-my-textarea-with-wtforms
    # в самой форме это поле можно вытянуть за правый нижний угол
    comments = TextAreaField("Сопроводительный текст", render_kw={"rows": 4, "cols": 1})
    title = StringField("Заголовок услуги")
    submit = SubmitField('Сохранить изменения')



# Форма для получения исходных данных для создания формы карусели(кол-во фото, имя, директория загрузки)
# class DeleteCarouselForm(FlaskForm):
#     name_carousel = StringField("Имя карусели", [InputRequired()])
#     dir_carousel = StringField("Директория загрузки", [InputRequired()])
#     number_foto = SelectField('Количество изображений в карусели:', choices = [(i+1, i+1) for i in range(0, 20)], validators=[DataRequired()])
#     # active = BooleanField(default=True)
#     # arhive = BooleanField(default=False)
#     # photo = FileField('Загрузите фото для карусели', render_kw={'multiple': True})
#     submit_create = SubmitField('Следующий шаг')


# class UploadTestForm(FlaskForm):
#     title = StringField("Заголовок фото ", render_kw={'class': "form-control pb-2", 'autofocus': True})
#     comments = TextAreaField("Текст фото ", render_kw={'class': "form-control pb-2"})
#     photo = FileField('Фото ', render_kw={'class': "container-fluid pb-2"})
#     class Meta:
#         csrf = False
#     # submit = SubmitField('Сохранить')
#
# class PhotosForm(FlaskForm):
#         all_photo = FieldList(FormField(UploadTestForm), min_entries=3, name='Фото карточки услуг')
#         submit = SubmitField('Загрузить фото')



# Форма (составная из двух классов UploadCarouselForm и CarouselForm)
# для получения исходных данных для создания формы карусели(кол-во фото, имя, директория загрузки)
# CarouselForm перенесла в carousel.py, тк не знаю как здесь задать параметр min_entries=int(number_foto)
# class UploadFoto(FlaskForm):
#     title = StringField("Заголовок фото")
#     comments = TextAreaField("Текст фото")
#     photo = FileField('Фото', [DataRequired()])
#     class Meta:
#         csrf = False

# class CarouselForm(FlaskForm):
#     all_photo = FieldList(FormField(UploadCarouselForm), min_entries=int(number_foto))
#     submit_carousel = SubmitField('Загрузить фото')

# Форма для редактирования слайда в карусели
# class EditTextSlaidForm(FlaskForm):
#     title_foto_carousel = StringField("Заголовок слайда")
#     text_foto_carousel = TextAreaField("Текст слайда")
#     submit_edit_slaid = SubmitField('Сохранить изменения')

# Форма для редактирования слайда в карусели
# class ReplaceSlaidForm(FlaskForm):
#     title_foto_carousel = StringField("Заголовок слайда")
#     text_foto_carousel = TextAreaField("Текст слайда")
#     photo = FileField('Загрузить слайд', [DataRequired()])
#     submit_edit_slaid = SubmitField('Сохранить изменения')

# Форма для добавления слайда в карусели
# class AddSlaidForm(FlaskForm):
#     title_foto_carousel = StringField("Заголовок слайда")
#     text_foto_carousel = TextAreaField("Текст слайда")
#     photo = FileField('Загрузить слайд', [DataRequired()])
#     submit_add_slaid = SubmitField('Добавить')


