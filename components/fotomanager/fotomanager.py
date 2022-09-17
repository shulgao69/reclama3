from flask import Blueprint, jsonify, redirect, session, request, render_template, abort, url_for
from flask import has_app_context, flash, current_app

# Импорт, необходимый для создания уникального имени загружаемого файла по времени загрузки
import datetime
from datetime import datetime

# Импорт, необходимый для перехвата предупреждений при задании form_edit_rules
import warnings


from RECL.models import db
from RECL.models import UploadFileMy, Usluga, Link, Order, User, Role, roles_users, ListModel, \
    SettingAdmin, UploadFileMy, PriceTable
from RECL.models import db

# from RECL.__init__ import app

from RECL.components.fotomanager.forms import  DeleteForm, FormChoice1, PhotoFormAdmin, FormChoice2, DeleteFormFromMini, EditFormFromMini

import os

from flask_security import login_required, roles_required, roles_accepted
from sqlalchemy.dialects.postgresql import JSON

# импорты для загрузки файлов - начало
# from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from sqlalchemy.dialects.postgresql import JSON
# импорты для загрузки файлов - конец

foto_manager = Blueprint('foto_manager_bp', __name__, template_folder='templates/fotomanager/', static_folder='static')


# ************** перенесено из components/admin/__init__.py - начало

# ****** Загрузка фото в соответствующий раздел, услугу и директорию - начало
# ****** Choice2
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

@foto_manager.route('/choice/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def choice():
    form = FormChoice2(form_name='FormChoice2Name')
    form.menu.choices = [(menu.id, menu.title) for menu in Link.query.order_by('title').all()]
    form.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.order_by('title').all()]

    # Для вывода сообщения о том что фото успешно загружено - начало
    message = session.get('upload_rezult')
    session['upload_rezult']=False
    # Для вывода сообщения о том что фото успешно загружено - начало

    # if request.method == 'POST':
    # При проверке request.form['form_name'] == 'FormChoice2Name'
    # возникает ошибка 400 - "странный" запрос (у меня Остановлена попытка перенаправления на др. сайт)
    # почему данная проверка в примере - не очень поняла.
    # Заменила ее на проверку form.form_name.data == 'FormChoice2Name'
    # (проверяю дополнительно имя формы из скрытого поля)
    # В принципе проверку на имя формы можно убрать
    # if form.validate_on_submit() and request.form['form_name'] == 'FormChoice2Name':

    # Еще делаем проверку form.photo.data (чтобы была не None)
    # Пока на стр. была одна форма загрузки мы в форме поставили валидатор
    # photo = FileField('Выбор фото', validators=[FileRequired()])
    # чтобы проверить что файл выбран.
    # Поскольку мы делаем на 1 стр. 2 формы при нажатии любой из кнопок отправки
    # происходит прием и обработка на этом роуте, но мы не загрузили имя файл загрузки(например)
    # и он при приеме будет None, поэтому этот валидатор из формы убрали
    # и сделали проверку внутри роута

    if form.validate_on_submit() and form.form_name.data == 'FormChoice2Name' and form.photo.data:
        # print("2-form.form_name.data=", form.form_name.data)
        # print('POST-form.menu.data=', form.menu.data, 'form.usluga.data=', form.usluga.data)
        # flash('menu: %s, usluga: %s' % (form.menu.data, form.usluga.data))
        menu_choice=Link.query.filter_by(id=form.menu.data).first()
        # print('menu_choice=', menu_choice, 'type menu_choice=', type(menu_choice))
        # print('menu_choice.title=', menu_choice.title, 'type menu_choice.title=', type(menu_choice.title))
        # print('menu_choice.link=', menu_choice.link)
        usluga_choice=Usluga.query.filter_by(id=form.usluga.data).first()
        # print('usluga_choice=', usluga_choice)
        # print('usluga_choice.title=', usluga_choice.title)
        # print('usluga_choice.link=', usluga_choice.link)
        # Формируем часть пути загрузки файла на основе выбранных меню и услуги:
        # директория меню сайта + директория услуги (из базы(эти директории (имена директорий) создаются при внесении в базу услуги или пункта меню))
        path_choice=menu_choice.link +'/' + usluga_choice.link +'/'
        # print('path_choice=', path_choice, 'type path_choice=', type(path_choice))

        # Формируем полный путь загрузки файла на основе выбранных меню и услуги:
        # Для получения конфигурации можно использовать app.config['UPLOAD_PATH'] но тогда нужно делать импорт
        # from RECL.__init__ import app а это порождает разные ошибки (при миграциях и тд)  тк циклический импорт
        # поэтому используем current_app.config['UPLOAD_PATH'], импортируя from flask import current_app
        # так как при обращении к блюпринту приложение уже создано и соответственно уже существует его контекст
        # path_full = app.config['UPLOAD_PATH']+path_choice - так в блюпринтах не делать!!!
        path_full = current_app.config['UPLOAD_PATH']+path_choice
        # print('path_full(Директория для загрузки файла)=', path_full)
        # try:
        #     os.makedirs(path_full)
        # except OSError:
        #     print("Создать директорию %s не удалось" %path_full)
        # else:
        #     print("Успешно создана директория %s" %path_full)
        # print('os.path.isdir(path_full)=', os.path.isdir(path_full))
        if not os.path.isdir(path_full):
            os.makedirs(path_full)
            # print('создана новая директория', path_full)
        # else:
        #     print('директория', path_full,'уже существует')


        # ***** загрузка фото и запись в базу
        # Получаем данные из формы:
        # - заголовок услуги
        title = form.title.data

        # - Сопроводительный текст услуги
        comments = form.comments.data

        # - имя файла c расширением
        photo_name = form.photo.data
        # print('photo_name from fotomanager=', photo_name.filename, 'type photo_name=', type(photo_name.filename))

        # **** задаем время загрузки файла - начало
        # и включаем его (ниже) в имя загружаемого файла (таким образом оно будет уникальным)
        # для этого импортировали модуль datetime
        # replace(microsecond=0) - чтобы отсечь миллисекунды
        # replace(':', '-') - чтобы заменить : так как может в файловой системе создать проблемы
        uniq_time = str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')
        # **** задаем время загрузки файла -  конец

        # п.1 С помощью функции secure_filename делаем имя безопасным!
        # (пояснение https://translate.yandex.ru/translate)
        # Ее нужно использовать всегда, т.к. могут отправить имя, кот.может изменить файловую систему
        # Например имя ДКТ20-11-Фирма Вертикаль-чб.jpg преобразует в 20-11-_-.jpg
        # Но поскольку кириллические символы удаляются, то название например лифт.tif
        # преобразуется в tif Поэтому добавила перед именем время создания
        filename = uniq_time + '_' + secure_filename(photo_name.filename)

        # п.2 Присоединяем безопасное имя файла к пути загрузки
        # file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        file_path = os.path.join(path_full, filename)

        # п.3 Сохраняем в выбранное место файл с безопасным именем
        photo_name.save(file_path)

        # Тоже самое (то есть п.1-3) можно записать в одну строку так:
        # photo_name.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(photo_name.filename)))

        # п.4 Вычислим размер загруженного файла - вариант 1
        # Полученный размер отличается от того, что в проводнике.
        # Так и должно быть!!!! (и в варианте 2 тоже самое!!) Читать про это:
        # https://question-it.com/questions/1398830/python-ospathgetsize-otlichaetsja-ot-len-fread
        # https://translate.yandex.ru/translate?lang=en-ru&url=https%3A%2F%2Fstackoverflow.com%2Fquestions%2F26603698%2Fwhy-does-os-path-getsize-give-me-the-wrong-size&view=c
        # Можно наверное использовать и другой метод -см views.py
        #         @app.route('/upl/', methods=['GET', 'POST'])

        file_size=os.path.getsize(file_path)
        # Вычислим размер загруженного файла - вариант 1 - конец

        # п.4 Вычислим размер загруженного файла -  вариант 2
        # (дает тот же результат что и вар 1)
        # Этот вар.работает, но воспользуемся вар.1 (чтобы не импортировать лишнюю библиотеку)
        # from pathlib import Path
        # file_obj = Path(file_path)
        # size = file_obj.stat().st_size
        # print('size=', file_size, 'type size=', type(file_size))
        # Вычислим размер загруженного файла -  вариант 2 - конец

        # п.5 Выделим расширение файла
        name_ext = os.path.splitext(file_path)[1]
        # Выделим расширение файла - конец

        # п.6 Запишем параметры загрузки файла в базу
        upload_file=UploadFileMy(origin_name_photo = photo_name.filename,
                                     secure_name_photo = filename,
                                     menu = menu_choice.title,
                                     dir_menu = menu_choice.link,
                                     usluga = usluga_choice.title,
                                     dir_usluga = usluga_choice.link,
                                     # Часть пути загрузки(меню+услуга)
                                     dir_uploads = path_choice,
                                     # Полный путь загрузки(путь проекта + путь меню+услуга)
                                     # dir_uploads = file_path,
                                     file_ext = name_ext,
                                     file_size = file_size,
                                     title=title,
                                     comments=comments
                                     )
        db.session.add(upload_file)
        db.session.commit()
        success = True

        # Для вывода сообщения о том что фото успешно загружено - продолжение
        session['upload_rezult']= True
        # Для вывода сообщения о том что фото успешно загружено - продолжение - конец
        # Для вывода сообщения о том что фото успешно загружено - конец


        # Данный редирект нужен для сброса данных POST запроса после отправки формы
        # и предотвращения повторной загрузки файла при обновлении страницы
        # Можно сделать 2 вариантами: 1- редирект на отдельный роут(сделала в views.py)
        # return redirect('/sbroschoice2/')
        # 2 вариант(оставим его) - редирект на функцию этой страницы (саму себя)

        return redirect(url_for('foto_manager_bp.choice'))

    return render_template('choice.html', form=form, message=message)

@foto_manager.route('/_get_usl_choice_admin/', methods=['GET', 'POST'])
def _get_usl_choice_admin():
    menu = request.args.get('menu', '01', type=str)
    uslugschoice = [(usluga.id, usluga.title) for usluga in Usluga.query.filter_by(punkt_menu_id=menu).order_by('title').all()]
    # print ('uslugschoice from fotomanager=', uslugschoice)
    return jsonify(uslugschoice)

# Выбор из выпадающего списка с обновлением другого списка, формирование
# пути загрузки файла на основе выбора + загрузка файла + запись в базу - конец
# ******
# ****** Choice2 - конец
# ****** Загрузка фото в соответствующий раздел, услугу и директорию - конец


# ****** Просмотр всех фото миниатюр - начало

@foto_manager.route('/fotomanager/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def manager_foto():
    menu_all = Link.query.all()
    uslugi_all = Usluga.query.all()
    foto_all = UploadFileMy.query.all()
    # print('foto_all from manager_foto=', foto_all)
    # form_delete = DeleteFormFromMini()
    form_edit = EditFormFromMini()
    # print('foto_all 3=', foto_all)
    return render_template('fotomanager.html',
                                   # form_delete=form_delete,
                                   form_edit=form_edit,
                                   menu_all=menu_all,
                                   uslugi_all=uslugi_all,
                                   foto_all=foto_all)

# ****** Просмотр всех фото миниатюр - конец


# ******* Выбрать прайс для добавления к фото из миниатюр - начало
@roles_accepted('superadmin')
@foto_manager.route('/add_price/<int:id>/', methods=["GET", "POST"])
def add_price(id):
    # Выбираем из базы запись, соответствующую id
    foto = UploadFileMy.query.filter(UploadFileMy.id == id).first()
    prices = PriceTable.query.all()
    return render_template('add_price.html',
                           foto = foto,
                           prices = prices
                           )
# ******* Выбрать прайс для добавления к фото из миниатюр - конец


# ******* Выбрать прайс для удаления из карточки услуги(фото) из миниатюр - начало
@roles_accepted('superadmin')
@foto_manager.route('/delete_price/<int:foto_id>/', methods=["GET", "POST"])
def delete_price(foto_id):
    # Выбираем из базы запись, соответствующую id
    foto = UploadFileMy.query.filter(UploadFileMy.id == foto_id).first()
    prices = PriceTable.query.all()
    return render_template('delete_price.html',
                           foto = foto,
                           prices = prices
                           )
# ******* Выбрать прайс для удаления из карточки услуги(фото) из миниатюр - конец


# ******* Прикрепить прайс  к карточке (фото) услуги - начало
@roles_accepted('superadmin')
@foto_manager.route('/attach_price/<int:foto_id>/<int:price_id>/', methods=["GET", "POST"])
def attach_price(foto_id, price_id):
    # print('foto_id=', foto_id, 'price_id=', price_id)
    # Выбираем из базы запись, соответствующую id
    foto = UploadFileMy.query.filter(UploadFileMy.id == foto_id).first()
    prices = PriceTable.query.all()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    foto.price.append(price)
    db.session.commit()
    return redirect(url_for('foto_manager_bp.add_price',
                           id = foto.id))
# ******* Прикрепить прайс  к карточке (фото) услуги - конец


# ******* Открепить прайс от карточки (фото) услуги - начало
@roles_accepted('superadmin')
@foto_manager.route('/detach_price/<int:foto_id>/<int:price_id>/', methods=["GET", "POST"])
def detach_price(foto_id, price_id):
    # print('foto_id=', foto_id, 'price_id=', price_id)
    # Выбираем из базы запись, соответствующую id
    foto = UploadFileMy.query.filter(UploadFileMy.id == foto_id).first()
    # prices = PriceTable.query.all()
    price = PriceTable.query.filter(PriceTable.id == price_id).first()
    foto.price.remove(price)
    db.session.commit()
    return redirect(url_for('foto_manager_bp.delete_price',
                           foto_id = foto.id))
# ******* Открепить прайс от карточки (фото) услуги - конец



# ******* Удаление фото из миниатюр с использованием модального окна
@roles_accepted('superadmin')
@foto_manager.route('/delete_foto/<int:id>/', methods=["GET", "POST"])
def delete_foto(id):
    # print('id=', id)

    # Выбираем из базы запись, соответствующую id
    delete_foto = UploadFileMy.query.filter(UploadFileMy.id == id).first()
    # print('delete_foto1=', delete_foto)
    # print('delete_foto1.id=', delete_foto.id)

    # Формируем путь для удаления файла
    path_delete = current_app.config['UPLOAD_PATH'] + delete_foto.dir_uploads + delete_foto.secure_name_photo
    # print('path_delete=', path_delete)

    try:
        # Удаляем фото из файловой системы
        os.remove(path_delete)
        flash('Фото успешно удалено')

        # Удаляем запись, соответствующую удаленному фото, из базы
        db.session.delete(delete_foto)
        # print('delete_foto2=', delete_foto)
        # print('delete_foto2.id=', delete_foto.id)

        # Вносим изменение в базу
        db.session.commit()

        # Формируем новый список файлов (без удаленных записей, соответствующих удаленным файлам)
        # foto_all = UploadFileMy.query.all()
        # print('foto_all after delete=', foto_all)

    except:
        flash('Такой файл уже удален')
        print('Повторная попытка удаления файла')
        print('delete_foto.id from except=', delete_foto.id)
    
    return redirect(url_for('foto_manager_bp.manager_foto'))



# ******* Редактирование заголовка и сопроводительного текста фото в миниатюрах
# @roles_accepted('superadmin')
@foto_manager.route('/edit_foto_info/', methods=["GET", "POST"])
def edit_foto():
    form_edit = EditFormFromMini()

    # ***** Принимаем данные из скрытых полей формы, которые запоняются
    # на стр. delete_foto.html автоматически с помощью параметра value
    # например {{ form_edit.secure_name_photo(value= foto.secure_name_photo) }}
    # это нужно для отображения данных картинки для редактирования
    # Если данный параметр на html странице убрать то скажет что не выбрано фото или фото
    # с некоррект.данными(not_foto_for_edit.html) т.к.в форме form_edit заданы проверки [InputRequired()]

    secure_name_photo = form_edit.secure_name_photo.data
    origin_name_photo = form_edit.origin_name_photo.data
    dir_uploads = form_edit.dir_uploads.data
    dir_usluga = form_edit.dir_usluga.data
    dir_menu = form_edit.dir_menu.data
    title = form_edit.hidden_title.data
    comments = form_edit.hidden_comments.data
    # *****

    # Если запрос POST и форма валидна
    if form_edit.validate_on_submit() and form_edit.submit_save_form_from_mini.data:
        # Принимаем уникальное имя
        secure_name_photo = form_edit.secure_name_photo.data
        # Принимаем измененные данные
        title = form_edit.title.data
        comments = form_edit.comments.data
        # Выбираем запись из базы с уникальным именем
        foto = UploadFileMy.query.filter(UploadFileMy.secure_name_photo==secure_name_photo).first()
        # Вносим изменения в данную запись
        foto.title = title
        foto.comments = comments
        # Добавляем в сессии
        db.session.add(foto)
        # Вносим изменения в базу
        db.session.commit()
        # Возвращаемся на страницу с миниатюрами
        return redirect (url_for('foto_manager_bp.manager_foto'))

    # Если запрос не POST а GET и скрытые данные переданные из формы не нулевые,
    # то формируем страницу для редактирования данных
    else:
        if secure_name_photo and origin_name_photo and dir_uploads and dir_usluga and dir_menu:
            menu = Link.query.filter(Link.link == dir_menu).first()
            usluga = Usluga.query.filter(Usluga.link == dir_usluga).first()
            print('comments=', comments)
            print('menu, usluga=', menu, usluga)

            return render_template('edit_foto_info.html',
                                form_edit=form_edit,
                                secure_name_photo = secure_name_photo,
                                origin_name_photo = origin_name_photo,
                                dir_uploads = dir_uploads,
                                dir_usluga = dir_usluga,
                                dir_menu = dir_menu,
                                title = title,
                                comments = comments,
                                usluga=usluga,
                                menu=menu
                           )
        # Если запрос не POST а GET но скрытые данные переданные из формы нулевые,
        # или некорректные то формируем страницу где указано что не выбрано фото
        # или данные не корректные (not_foto_for_edit.html)
        else:
            return render_template('not_foto_for_edit.html')
# ******* Редактирование заголовка и сопроводительного текста фото в миниатюрах


# ****** Удаление фото из миниатюр с помощью формы DeleteFormFromMini() - начало
#             РАБОТАЕТ!!!
# Этот кусок был в
# @foto_manager.route('/fotomanager/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
# def manager_foto():
#
#     Отказалась от него и сделал отдельный роут удаления с помощью передачи id фото
#     так проще

# Удаление фото из миниатюр с помощью формы DeleteFormFromMini()
    # Отказалась от этого варианта и перенесла этот кусок (без получения данных из форм)
    # роут felete_foto

    # if form_delete.validate_on_submit() and form_delete.submit_delete_form_from_mini.data:
    # # if form_delete.validate_on_submit():
    #     # Получаем данные для удаления файла из формы(из скрытых полей)
    #     # Эти данные формируются автоматически
    #     secure_name_photo = form_delete.secure_name_photo.data
    #     origin_name_photo = form_delete.origin_name_photo.data
    #     dir_uploads = form_delete.dir_uploads.data
    #     dir_usluga = form_delete.dir_usluga.data
    #     dir_menu = form_delete.dir_menu.data
    #
    #     # Формируем путь для удаления файла
    #     path_delete = current_app.config['UPLOAD_PATH'] + dir_uploads + secure_name_photo
    #
    #     try:
    #         # Выбираем из базы запись, соответствующую удаленному файлу
    #         delete_foto_from_base = UploadFileMy.query.filter(UploadFileMy.secure_name_photo == secure_name_photo).first()
    #
    #
    #         # Удаляем запись, соответствующую удаленному фото, из базы
    #         db.session.delete(delete_foto_from_base)    #
    #
    #         # Вносим изменение в базу
    #         db.session.commit()

    #         # Формируем новый список файлов (без удаленных записей, соответствующих удаленным файлам)
    #         foto_all = UploadFileMy.query.all()
    #
    #         # Удаляем фото из файловой системы
    #         os.remove(path_delete)
    #         flash('Фото успешно удалено')
    #
    #     except:
    #         flash('Такой файл уже удален')
    #         print('Повторная попытка удаления файла')
    #         print('secure_name_photo from except=', secure_name_photo)
    #
    #     # Этот редирект оказался нужен для того, чтобы очистить в браузере данные
    #     # POST запроса, предотвратиь повторную отправку данных при перезагрузке
    #     # страницы и соответственно попытку повторного удаления уже удаленного файла!!!
    #     # Для этого создала простой роут в views.py который просто переадресовывает обратно на
    #     # страницу с формой (то есть на эту же стр.)
    #     # При этом происходит очистка и попытки повторного удаления файла не происходит!!!!
    #
    #     # Можно сделать 2 вариантами: 1- редирект на отдельный роут(сделала в views.py)
    #     # return redirect('/sbrosdeletefoto/')
    #     # 2 вариант(оставим его) - редирект на функцию этой страницы (саму себя)
    #
    #     return redirect(url_for('foto_manager_bp.manager_foto'))

# ****** Удаление фото из миниатюр с помощью формы DeleteFormFromMini() - конец

