from flask import Blueprint, jsonify, redirect, session, request, render_template, abort, url_for
from flask import has_app_context, flash, current_app
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, MultipleFileField
from wtforms import PasswordField, IntegerField, validators, TextAreaField
# from wtforms import TextField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
# from wtforms.validators import ValidationError
# from RECL.models import db, Link, Usluga
import json

from wtforms import PasswordField, IntegerField, validators, FieldList, FormField, TextAreaField
# импорты для загрузки файлов - начало
from flask_wtf.file import FileField, FileAllowed, FileRequired
# импорты для загрузки файлов - конец

# Импорт, необходимый для создания уникального имени загружаемого файла по времени загрузки
import datetime
from datetime import datetime

# Импорт, необходимый для перехвата предупреждений при задании form_edit_rules
import warnings


from RECL.models import db
# from RECL.models import UploadFileMy, Usluga, Link, Order, User, Role, roles_users, ListModel, \
#     SettingAdmin, UploadFileMy, PriceTable, Carousel, PlaceElement, BaseLocationElement, \
#     BasePositionElement, PositionElement, PlaceCarousel, PlaceModelElement
from RECL.models import *


# from RECL.__init__ import app

from RECL.components.carouselmanager.forms import CreateCarouselForm, UploadCarouselForm, \
    EditTextSlaidForm, ReplaceSlaidForm, AddSlaidForm, ProbaForm

import os

from flask_security import login_required, roles_required, roles_accepted
from sqlalchemy.dialects.postgresql import JSON

# импорты для загрузки файлов - начало
# from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from sqlalchemy.dialects.postgresql import JSON
# импорты для загрузки файлов - конец

carousel_manager = Blueprint('carousel_manager_bp', __name__, template_folder='templates/carouselmanager/', static_folder='static')

# Создать карусель - начало
@carousel_manager.route('/create/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def render_create_carousel():
    form_create = CreateCarouselForm()

    if form_create.validate_on_submit() and form_create.submit_create.data:
        name_carousel=form_create.name_carousel.data
        dir_carousel = form_create.dir_carousel.data
        number_foto = form_create.number_foto.data
        all_name_carousel = {item.name_carousel for item in Carousel.query.all()}
        all_dir_carousel = {item.dir_carousel for item in Carousel.query.all()}
        if name_carousel in all_name_carousel:
            message_name = 'Такое имя карусели уже существует! Пожалуйста задайте другое имя.'
            return render_template('create_carousel.html',
                                   form_create=form_create,
                                   message_name=message_name
                                   )
        if dir_carousel in all_dir_carousel:
            message_dir = 'Такая директория уже существует! Пожалуйста задайте другую директорию.'
            return render_template('create_carousel.html',
                                   form_create=form_create,
                                   message_dir=message_dir
                                   )

        return redirect(url_for('carousel_manager_bp.render_upload_carousel',
                                name_carousel=name_carousel,
                                dir_carousel=dir_carousel,
                                number_foto=number_foto)
                                )

    # print('form.photo(id=1)=', form.photo(id=1), type(form.photo(id=1)))    #
    # print('str(form.photo(id=1))=', str(form.photo(id=1)), type(str(form.photo(id=1))))
    # выдаст str(form.photo)= <input id="photo" multiple name="photo" type="file">
    # где multiple задан в форме в render_kw={'multiple': True},
    # а id по умолчанию принимает значение=имя поля), но можно в форме задать другое id
    # print('str(form.photo_all)=', str(form.photo_all))

    return render_template('create_carousel.html',
                           form_create=form_create,
                           )
# Создать карусель - конец


# Загрузить фото карусели - начало
@carousel_manager.route('/upload/<number_foto>/<name_carousel>/<dir_carousel>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def render_upload_carousel(number_foto, name_carousel, dir_carousel):
    dict_all_foto_carousel_name = []

    # class UploadCarouselForm(FlaskForm): перенесла в forms.py
    class CarouselForm(FlaskForm):
        all_photo = FieldList(FormField(UploadCarouselForm), min_entries=int(number_foto))
        submit_carousel = SubmitField('Загрузить фото')

    form_uploads_carousel = CarouselForm()

    if form_uploads_carousel.validate_on_submit() and form_uploads_carousel.submit_carousel.data:

        # Формируем путь загрузки карусели
        # Для получения конфигурации можно использовать app.config['UPLOAD_PATH'] но тогда нужно делать импорт
        # from RECL.__init__ import app а это порождает разные ошибки (при миграциях и тд)  тк циклический импорт
        # поэтому используем current_app.config['UPLOAD_PATH'], импортируя from flask import current_app
        # так как при обращении к блюпринту приложение уже создано и соответственно уже существует его контекст
        # path_carousel = app.config['UPLOAD_CAROUSEL']+dir_carousel - так в блюпринтах не делать!!!
        path_carousel = current_app.config['UPLOAD_CAROUSEL'] + dir_carousel

        if not os.path.isdir(path_carousel):
            os.makedirs(path_carousel)

        for i in range(len(form_uploads_carousel.all_photo.data)):
            filename = str(i) + '_' + secure_filename(form_uploads_carousel.all_photo.data[i]['photo'].filename)
            # print('filename', i, filename)

             # п.2 Присоединяем безопасное имя файла к пути загрузки
            file_path = os.path.join(path_carousel, filename)

            # п.3 Сохраняем в выбранное место файл с безопасным именем
            form_uploads_carousel.all_photo.data[i]['photo'].save(file_path)

            # Тоже самое (то есть п.1-3) можно записать в одну строку так:
            # form_uploads_carousel.all_photo.data[i]['photo'].save(os.path.join(app.config['UPLOAD_CAROUSEL'], secure_filename(form_uploads_carousel.all_photo.data[i]['photo'].filename)))

            dict_car = {}
            dict_car['title_foto_carousel']=form_uploads_carousel.all_photo.data[i]['title_foto_carousel']
            dict_car['text_foto_carousel']=form_uploads_carousel.all_photo.data[i]['text_foto_carousel']
            dict_car['photo']=filename

            dict_all_foto_carousel_name.append(dict_car)


        # serialized_dict_all_foto_carousel_name=json.dumps(dict_all_foto_carousel_name, ensure_ascii=False)
        # print('serialized_dict_all_foto_carousel_name1=', serialized_dict_all_foto_carousel_name)
        # print('type(serialized_dict_all_foto_carousel_name)=', type(serialized_dict_all_foto_carousel_name))
        date_create = str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')
        carousel = Carousel(name_carousel=name_carousel,
                            dir_carousel=dir_carousel,
                            number_foto=number_foto,
                            dict_all_foto_carousel_name = dict_all_foto_carousel_name,
                            active = False,
                            arhive = False,
                            date_create=date_create
                            )

        db.session.add(carousel)
        db.session.commit()

        return redirect(url_for('carousel_manager_bp.show_carousel', id=carousel.id))

    return render_template('upload_carousel.html',
                           form_uploads_carousel=form_uploads_carousel,
                           name_carousel=name_carousel,
                           dir_carousel=dir_carousel,
                           number_foto=number_foto
                           )
# Загрузить фото карусели - конец


# Показать карусель - начало
@carousel_manager.route('/show_carousel/<int:id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def show_carousel(id):
    carousel = Carousel.query.get(id)
    dict_all_foto_carousel_name=carousel.dict_all_foto_carousel_name
    return render_template('show_carousel.html', dict_all_foto_carousel_name=dict_all_foto_carousel_name, carousel=carousel)
# Показать карусель - конец


# Показать все карусели - начало
@carousel_manager.route('/show_all_carousel/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def show_all_carousel():
    # Сортировка по дате
    form_proba=ProbaForm()
    carousels = Carousel.query.order_by(Carousel.date_create.desc()).all()
    return render_template('show_all_carousel.html', carousels=carousels, form_proba=form_proba)
# Показать все карусели - конец


# Удалить карусель (все фото из файловой системы и запись в базе данных)- начало
@carousel_manager.route('/delete/<int:id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def delete_carousel(id):
    carousel = Carousel.query.filter_by(id=id).first()

    # Получаем все места размещения данной карусели
    carousel_places = PlaceCarousel.query.filter(PlaceCarousel.carousel_id==id)

    # Удаляем все полученные места размещения данной карусели
    for place in carousel_places:
        db.session.delete(place)

    # Формируем путь для удаления содержимого карусели (нам надо удалить директорию со всем содержимым)
    # см. https://question-it.com/questions/1532255/kak-udalit-udalit-papku-kotoraja-ne-pusta
    path_carousel = current_app.config['UPLOAD_CAROUSEL'] + carousel.dir_carousel

    # Удаляем все файлы изображений в этой директории
    for i in os.listdir(path_carousel):
        os.remove(os.path.join(path_carousel, i))

    # Удаляем саму директорию(уже пустую) - если пытаться удалять не пустую - ошибка
    os.rmdir(path_carousel)
    flash('Карусель во всех местах размещения удалена')

    # удаляем запись карусели в базе данных
    db.session.delete(carousel)

    # Применяем удаления мест карусели и самой карусели в базе
    db.session.commit()
    return redirect(url_for('carousel_manager_bp.show_all_carousel'))

# Удалить карусель (все фото из файловой системы и запись в базе данных) - конец


# Выбор местоположения карусели из разрешенных вариантов - начало
@carousel_manager.route('/place_carousel/<int:id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def place_carousel(id):
    carousel = Carousel.query.get(id)
    places_model_size=PlaceModelElement.query.filter(PlaceModelElement.name_model.has(name_model='Carousel')).all()
    base_positions = BasePositionElement.query.order_by(BasePositionElement.id).all()
    return render_template('place_carousel.html',
                           carousel=carousel,
                           base_positions=base_positions,
                           places_model_size=places_model_size
                           )
# Выбор местоположения карусели из разрешенных вариантов - конец


# Сохранить местоположение карусели после выбора из разрешенных вариантов - начало
@carousel_manager.route('/save_place_carousel/<int:carousel_id>/<int:place_model_size_id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def save_place_carousel(place_model_size_id, carousel_id):
    # print('place_model_size_id=', place_model_size_id)
    # print('carousel_id=', carousel_id)
    place=PlaceCarousel.query.filter(PlaceCarousel.carousel.has(Carousel.id==carousel_id)).filter(PlaceCarousel.place_model_element.has(PlaceModelElement.id==place_model_size_id)).first()
    if place:
        place_carousel=[]
        new_place=False
        flash('Такое местоположение у данной карусели уже задано')
    else:
        new_place=True
        place_carousel=PlaceCarousel(place_model_element_id=place_model_size_id, carousel_id=carousel_id, priority_element_id=1)
        db.session.add(place_carousel)
        db.session.commit()
    return render_template('save_place_carousel.html',
                           place_carousel=place_carousel,
                           new_place=new_place,
                           place_model_size_id=place_model_size_id,
                           carousel_id=carousel_id
                           )
# Сохранить местоположение карусели после выбора из разрешенных вариантов - конец

# Удалить выбранную локацию(местоположение) карусели - начало
@carousel_manager.route('/delete_place_carousel/<int:place_carousel_id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def delete_place_carousel(place_carousel_id):
    place_carousel=PlaceCarousel.query.filter_by(id=place_carousel_id).first()

    db.session.delete(place_carousel)
    db.session.commit()
    return redirect(url_for('carousel_manager_bp.show_all_carousel'))
# Удалить выбранную локацию(местоположение) карусели - конец


# Сделать карусель активной(неактивной) - начало
@carousel_manager.route('/active_carousel/<int:carousel_id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def active_carousel(carousel_id):
    carousel=Carousel.query.get(carousel_id)
    if carousel.active:
        carousel.active=False
    else:
        carousel.active=True
    db.session.add(carousel)
    db.session.commit()
    return redirect(url_for('carousel_manager_bp.show_all_carousel'))
# Сделать карусель активной(неактивной) - конец


# Редактировать выбранную карусель - начало
@carousel_manager.route('/edit_carousel/<int:carousel_id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def edit_carousel(carousel_id):
    carousel=Carousel.query.get(carousel_id)
    spisok_foto_carousel=carousel.dict_all_foto_carousel_name
    # print('spisok_foto_carousel=', spisok_foto_carousel)

    # db.session.add(carousel)
    # db.session.commit()
    return render_template('edit_carousel.html',
                           carousel=carousel,
                           spisok_foto_carousel=spisok_foto_carousel
                           )
# Редактировать выбранную карусель - конец


# Удалить выбранный слайд карусели - начало
@carousel_manager.route('/delete_slaid_carousel/<int:carousel_id>/<int:slaid_number>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def delete_slaid_carousel(carousel_id, slaid_number):

    carousel=Carousel.query.get(carousel_id)
    slaid_carousel=carousel.dict_all_foto_carousel_name[slaid_number]

    # Формируем путь для удаления редактируемого слайда карусели
    # см. https://question-it.com/questions/1532255/kak-udalit-udalit-papku-kotoraja-ne-pusta

    # Это путь карусели
    path_carousel = current_app.config['UPLOAD_CAROUSEL'] + carousel.dir_carousel

    # Это путь слайда
    path_slaid_carousel = current_app.config['UPLOAD_CAROUSEL'] + carousel.dir_carousel+'/'+carousel.dict_all_foto_carousel_name[slaid_number]['photo']

    # удаляем  слайд (если он есть)
    # https://pythononline.ru/osnovy/kak-udalit-fayly-python
    if os.path.isfile(path_slaid_carousel):
        os.remove(path_slaid_carousel)

    # Формируем список фото без удаленного фото
    spisok_foto_carousel=[]
    for i in carousel.dict_all_foto_carousel_name:
        if i != slaid_carousel:
            spisok_foto_carousel.append(i)
    carousel.dict_all_foto_carousel_name=spisok_foto_carousel

    carousel.number_foto=carousel.number_foto - 1

    if carousel.number_foto == 0:
        places_carousel=PlaceCarousel.query.filter_by(carousel_id=carousel_id).all()

        # удаляем места размещения карусели
        if places_carousel:
            for place_carousel in places_carousel:
                db.session.delete(place_carousel)

        db.session.delete(carousel)
        db.session.commit()

        # удаляем пустую папку т.к. carousel.number_foto == 0
        os.rmdir(path_carousel)

        return redirect(url_for('carousel_manager_bp.show_all_carousel'))
    else:
        db.session.add(carousel)
        db.session.commit()
        return redirect(url_for('carousel_manager_bp.edit_carousel',
                           # carousel=carousel,
                           # spisok_foto_carousel=spisok_foto_carousel,
                            carousel_id=carousel_id))
# Удалить выбранный слайд карусели - конец


# Добавить слайд карусели - начало
@carousel_manager.route('/add_slaid_carousel/<int:carousel_id>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def add_slaid_carousel(carousel_id):
    form_add_slaid = AddSlaidForm()

    # 1 - Выбрать карусель  для редактирования - начало
    carousel=Carousel.query.get(carousel_id)
    # 1 - Выбрать карусель  для редактирования - конец

    # 2 - принять данные из формы
    if form_add_slaid.validate_on_submit() and form_add_slaid.submit_add_slaid.data:

        # Формируем путь для удаления редактируемого слайда карусели
        # см. https://question-it.com/questions/1532255/kak-udalit-udalit-papku-kotoraja-ne-pusta

        # 3 -  Получить путь карусели - начало
        path_carousel = current_app.config['UPLOAD_CAROUSEL'] + carousel.dir_carousel
        # 3 -  Получить путь карусели - конец

        # 4 - записать новый файл в папку п.3 - начало

        # slaid_number задаем для удобства и включаем в безопасное имя файла - можно и не задавать
        slaid_number=len(carousel.dict_all_foto_carousel_name)

        # Получаем безопасное имя файла
        filename = str(slaid_number) + '_' + secure_filename(form_add_slaid.photo.data.filename)

        #  Присоединяем безопасное имя файла к пути загрузки
        file_path = os.path.join(path_carousel, filename)

        #  Сохраняем в выбранное место файл с безопасным именем
        form_add_slaid.photo.data.save(file_path)

        # 4 - записать новый файл в папку п.3 - конец


        # 5 - создать новый список словарей dict_all_foto_carousel_name - начало
        spisok_foto_carousel=[]
        slaid_carousel_new={}
        for i in carousel.dict_all_foto_carousel_name:
            spisok_foto_carousel.append(i)

        slaid_carousel_new['title_foto_carousel']=form_add_slaid.title_foto_carousel.data
        slaid_carousel_new['text_foto_carousel']=form_add_slaid.text_foto_carousel.data
        slaid_carousel_new['photo']=filename
        spisok_foto_carousel.append(slaid_carousel_new)

        carousel.dict_all_foto_carousel_name=spisok_foto_carousel
        # 5 - создать новый список словарей dict_all_foto_carousel_name - конец

        # Изменим количество слайдов в карусели, т к добавился новый слайд
        carousel.number_foto=carousel.number_foto + 1

        # 6 - сохранить новый dict_all_foto_carousel_name в базу - начало
        db.session.add(carousel)
        db.session.commit()
        # 6 - сохранить новый dict_all_foto_carousel_name в базу - конец

        return redirect(url_for('carousel_manager_bp.edit_carousel',
                                spisok_foto_carousel=spisok_foto_carousel,
                               carousel_id=carousel_id)
                           )

    return render_template('add_slaid_carousel.html',
                           carousel=carousel,
                           # slaid_number=slaid_number,
                           # slaid_carousel=slaid_carousel,
                           form_add_slaid=form_add_slaid
                           )
# Добавить слайд карусели - конец



# Заменить выбранный слайд карусели - начало
@carousel_manager.route('/replace_slaid_carousel/<int:carousel_id>/<int:slaid_number>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def replace_slaid_carousel(carousel_id, slaid_number):
    form_replace_slaid = ReplaceSlaidForm()

    # 1 - Выбрать карусель и слайд для редактирования - начало
    carousel=Carousel.query.get(carousel_id)
    slaid_carousel=carousel.dict_all_foto_carousel_name[slaid_number]
    # 1 - Выбрать карусель и слайд для редактирования - конец

    # 2 - принять данные
    if form_replace_slaid.validate_on_submit() and form_replace_slaid.submit_edit_slaid.data:

        # Формируем путь для удаления редактируемого слайда карусели
        # см. https://question-it.com/questions/1532255/kak-udalit-udalit-papku-kotoraja-ne-pusta

        # 3 -  Получить путь карусели - начало
        path_carousel = current_app.config['UPLOAD_CAROUSEL'] + carousel.dir_carousel
        # print('path_carousel=', path_carousel)
        # 3 -  Получить путь карусели - конец

        # 4 - записать новый файл в папку п.3 - начало
        # Получаем безопасное имя файла
        filename = str(slaid_number) + '_' + secure_filename(form_replace_slaid.photo.data.filename)
        # print('filename=', filename)
        #  Присоединяем безопасное имя файла к пути загрузки
        file_path = os.path.join(path_carousel, filename)
        # print('file_path=', file_path)
        #  Сохраняем в выбранное место файл с безопасным именем
        form_replace_slaid.photo.data.save(file_path)
        # 4 - записать новый файл в папку п.3 - конец

        # 5 - удалить старый файл из папки п.3 - начало
        # Это путь редактируемого слайда
        path_slaid_carousel = current_app.config['UPLOAD_CAROUSEL'] + carousel.dir_carousel+'/'+carousel.dict_all_foto_carousel_name[slaid_number]['photo']
        # print('path_slaid_carousel=', path_slaid_carousel)
        # print('os.path.isfile(path_slaid_carousel)=', os.path.isfile(path_slaid_carousel))

        # удаляем редактируемый слайд (если он есть)
        # https://pythononline.ru/osnovy/kak-udalit-fayly-python
        if os.path.isfile(path_slaid_carousel):
            os.remove(path_slaid_carousel)
        # os.remove(path_slaid_carousel)
        # 5 - удалить старый файл из папки п.3 - конец

        # 6 - создать новый список словарей dict_all_foto_carousel_name - начало
        spisok_foto_carousel=[]
        slaid_carousel_new={}
        for i in carousel.dict_all_foto_carousel_name:
            if i != slaid_carousel:
                spisok_foto_carousel.append(i)
            else:
                slaid_carousel_new['title_foto_carousel']=form_replace_slaid.title_foto_carousel.data
                slaid_carousel_new['text_foto_carousel']=form_replace_slaid.text_foto_carousel.data
                slaid_carousel_new['photo']=filename
                spisok_foto_carousel.append(slaid_carousel_new)
        carousel.dict_all_foto_carousel_name=spisok_foto_carousel
        # print('carousel.dict_all_foto_carousel_name=', carousel.dict_all_foto_carousel_name)
        # 6 - создать новый dict_all_foto_carousel_name - конец

        # 7 - сохранить новый dict_all_foto_carousel_name в базу - начало
        db.session.add(carousel)
        db.session.commit()
        # 7 - сохранить новый dict_all_foto_carousel_name в базу - конец

        return redirect(url_for('carousel_manager_bp.edit_carousel',
                               carousel_id=carousel_id)
                           )

    return render_template('replace_slaid_carousel.html',
                           carousel=carousel,
                           slaid_number=slaid_number,
                           slaid_carousel=slaid_carousel,
                           form_replace_slaid=form_replace_slaid
                           )
# Заменить выбранный слайд карусели - конец


# Редактировать выбранный слайд карусели - начало
@carousel_manager.route('/edit_text_slaid_carousel/<int:carousel_id>/<int:slaid_number>/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def edit_text_slaid_carousel(carousel_id, slaid_number):
    form_edit_text_slaid = EditTextSlaidForm()

    # 1 - Выбрать карусель и слайд для редактирования - начало
    carousel=Carousel.query.get(carousel_id)
    slaid_carousel=carousel.dict_all_foto_carousel_name[slaid_number]
    # 1 - Выбрать карусель и слайд для редактирования - конец

    # 2 - принять данные
    if form_edit_text_slaid.validate_on_submit() and form_edit_text_slaid.submit_edit_slaid.data:

        # 3 - создать новый список словарей dict_all_foto_carousel_name - начало
        spisok_foto_carousel=[]
        slaid_carousel_new={}
        for i in carousel.dict_all_foto_carousel_name:
            if i != slaid_carousel:
                spisok_foto_carousel.append(i)
            else:
                slaid_carousel_new['title_foto_carousel']=form_edit_text_slaid.title_foto_carousel.data
                slaid_carousel_new['text_foto_carousel']=form_edit_text_slaid.text_foto_carousel.data
                slaid_carousel_new['photo']=slaid_carousel['photo']
                spisok_foto_carousel.append(slaid_carousel_new)
        carousel.dict_all_foto_carousel_name=spisok_foto_carousel
        # 3 - создать новый dict_all_foto_carousel_name - конец

        # 4 - сохранить новый dict_all_foto_carousel_name в базу - начало
        db.session.add(carousel)
        db.session.commit()
        # 4 - сохранить новый dict_all_foto_carousel_name в базу - конец

        return redirect(url_for('carousel_manager_bp.edit_carousel',
                               carousel_id=carousel_id)
                           )

    return render_template('edit_text_slaid_carousel.html',
                           carousel=carousel,
                           slaid_number=slaid_number,
                           slaid_carousel=slaid_carousel,
                           form_edit_text_slaid=form_edit_text_slaid
                           )

# Редактировать выбранный слайд карусели - конец







    # # photo_all = form.photo_all.data
    # if photo_all:
    #     for foto in photo_all:
    #         print('foto=', foto)
    # names = form.photo_all.name
    # print ('names=', names)
    # tt = request.files.getlist(form.photo_all.name)
    # if tt:
    #     print ('tt=', tt)
    #     for picture_upload in tt:
    #             picture_contents = picture_upload.stream.read()
    #             # print('picture_contents=', picture_contents)
    #             print('type(picture_contents)=', type(picture_contents))
    # # form class with static fields
    # class MyForm(FlaskForm):
    #     name = StringField('Имя карусели')
    #     submit = SubmitField('Загрузить')
    #     submit_add = SubmitField('Добавить следующее фото')
    # record = {'key-pole-1': 'photo-1', 'key-pole-2': 'photo-2', 'key-pole-3': 'photo-3'}
    #
    # # add dynamic fields
    # for key, value in record.items():
    #     setattr(MyForm, key, StringField(value))
    #
    # formnew = MyForm()

    # <form method="POST" action="/admin/carousel/create/" enctype="multipart/form-data">
    #     {{ form.csrf_token }}
    #     <h5 class="text-left pl-2 mt-4">
    #     Форма formnew = MyForm() из carousel.py
    #     </h5>
    #     <div>
    #         {{ formnew.name.label }}
    #     </div>
    #     <div>
    #         {{ formnew.name(class="container-fluid") }}
    #     </div>
    #
    #     {% for key, value in record.items() %}
    #     <div>key: {{ key }}</div>
    #     <div>value: {{ value }}</div>
    #      <div>formnew|attr(key):{{ formnew|attr(key)() }}</div>
    #      {{ formnew.submit_add(class="form-control my-3 btn-success btn-block") }}
    #     {% endfor %}
    #     {{ formnew.submit(class="form-control my-3 btn-success btn-block") }}
    #     </form>