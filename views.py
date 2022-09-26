# import random
import json
# import flask_security

from flask import session, redirect, request, render_template, url_for, abort

import calendar

# import sys

from flask_migrate import Migrate
# from flask_login import LoginManager
# from flask_login import current_user, login_user, logout_user, login_required
# from werkzeug.security import generate_password_hash, check_password_hash
# from collections import Counter
# from sqlalchemy.dialects.postgresql import JSON
# from flask_security import Security
# from flask_security import SQLAlchemyUserDatastore
from flask_security import login_required, roles_required, roles_accepted, login_user, logout_user
from flask_security import UserMixin, RoleMixin
# from flask_security.decorators import roles_required

# from flask_security.utils import hash_password
# from werkzeug.exceptions import HTTPException

from RECL.__init__ import app, db, login_manager
from RECL.forms import LoginForm, RegistrationForm, OrderFormFromMenu, ConsentForm
# from RECL.forms import PermissionForm
# from RECL.models import Usluga, Link, Order, User, Role, roles_users, UploadFileMy, PriceTable, PlaceElement, \
#     PlaceModelElement, PlaceCarousel, PriorityElement, ColumnElement, ContainerElement, HeightElement, WidthElement, PositionElement, \
#     VerticalPositionElement, HorizontalPositionElement, BasePositionElement, BaseLocationElement

# импортируем ВСЕ модели
from RECL.models import *
from flask import jsonify
# from sqlalchemy.dialects.postgresql import JSON

migrate = Migrate(app, db)

# Setup Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)#
# print(type(user_datastore), type(security))


# Загрузка данных меню и услуг из JSON.
# Использовала когда сделала первоначальную базу в JSON

# with open("links.json", "r", encoding='utf-8') as f:
#    contents = f.read()
#    links = json.loads(contents)
#
# with open("uslugi.json", "r", encoding='utf-8') as f:
#    contents = f.read()
#    uslugi = json.loads(contents)

# Загрузка данных меню и услуг из JSON -  конец

# @login_manager.user_loader
# def load_user(user_id):
#     user = User.query.get(int(user_id))
#     # Данные о пользователе, получаемые с помощью декоратора @login_manager.user_loader
#     # print(user, user.id, user.email, user.password, user.confirmed_at, user.created_on,
#     # load_user, user.is_authenticated, user.is_active, user.is_anonymous, user.get_id())
#     print(user.id)
#     return user



# ****** Загрузка файлов - начало

# Для загрузки файлов можно использовать несколько способов:
# 1. Расширение для загрузки файлов Flask-Uploads(pip install Flask-Uploads) (https://docs-python.ru/packages/veb-frejmvork-flask-python/zagruzka-fajlov-server-flask/)
# 2. Загрузка файлов без Flask-Uploads (https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask)
# 3. Загрузки в админке https://dev-gang.ru/article/flask-admin-zagruzka-faylov-i-obrabotka-formy-v-modeli/
# 4. Загрузка файлов с помощью расширения Flask-WTF
# Здесь используем вар. 2 (Включает все проверки безопасности!!)

# импорты, необходимые для загрузки файлов
import imghdr
import os
from flask import render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
# импорты, необходимые для загрузки файлов - конец

# # *** конфигурации, необходимые для загрузки файлов - начало (перенесла в config)

# ***** UPLOAD_PATH
# Путь загрузки файлов. Обратить внимание:
# В config тоже задан путь UPLOAD_PATH загрузки файлов. Он задает путь от корневых директорий.
# То есть (например) UPLOAD_PATH = RECL/static/uploads/ и загрузка идет туда
# Задав здесь UPLOAD_PATH мы переопределяем его в блюпринте с конечной точкой админ.
# следовательно UPLOAD_PATH = RECL/components/admin/static/images/uploads/
# и все загрузки, в которых используется UPLOAD_PATH
# (в том числе и в функциях, находящихся вне блюпринта админ)
# будет использоваться не определенный в конфиге путь, а переопределенный (у нас в частности в админке)
# так как UPLOAD_PATH глобальная переменная

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

# # *** конфигурации, необходимые для загрузки файлов - конец

# функция, которая выполняет проверку содержимого изображений (для нее нужен import imghdr)
# ее используем при проверке содержимого  изображений при загрузке файлов
# на соответствие расширения реальному содержимому
# и формат jpeg рассматривает как jpg? (Почитать!)
# (https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask)
def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    print('format1=', format)
    if not format:
        print('if not format=', format)
        return None
    print('format1=', format)
    return '.' + (format if format != 'jpeg' else 'jpg')
# функция, которая выполняет проверку содержимого изображений - конец

# Перехват ошибки Большой файл. - работает!!!
# Для этого в config.py задан MAX_CONTENT_LENGTH
# Но мы сделали блюпринт ошибок errors и зададим перехват большого файла там, поэтому здесь отключим
# Вместо ошибки 413(большой загружаемый файл)
# раньше  Прерывала соединение с сервером! Почему не знаю
# Сейчас - 16.09.21 - работает

# @app.errorhandler(413)
# def too_large(e):
#     return "File is too large1", 413
# Перехват ошибки Большой файл - конец

# роут загрузки файлов
@app.route('/upl/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # Загрузка файла
        uploaded_file = request.files['file']
        print('uploaded_file=', uploaded_file)

        # Получила размер загруженного файла ( https://question-it.com/questions/1294264/flask-poluchit-razmer-obekta-requestfiles)
        # Для этого сначала устанавливаем uploaded_file.seek(0, os.SEEK_END)
        # как я поняла??? данная запись uploaded_file.seek(0, os.SEEK_END) ставит курсор
        # в конец файла для того чтобы впоследствии
        # с помощью tell() получить размер файла. Больше ничего не делает
        # http://espressocode.top/python-os-lseek-method/
        # https://question-it.com/questions/2704045/flask-pustye-fajly-pri-zagruzke
        uploaded_file.seek(0, os.SEEK_END)
        print('uploaded_file.seek(0, os.SEEK_END)=', uploaded_file.seek(0, os.SEEK_END))

        uploaded_file_length = uploaded_file.tell()
        print('uploaded_file_length=', uploaded_file_length)
        print("app.config['MAX_CONTENT_LENGTH']=", app.config['MAX_CONTENT_LENGTH'])
      # Проверка имени файла
        filename = secure_filename(uploaded_file.filename)
        print('filename=', filename)
        if filename != '':
            # os.path.splitext(filename)[1] -
            # функция которая ооставляет только расширение с точкой от имени файла
            file_ext = os.path.splitext(filename)[1]
            # print(file_ext)
            # print(validate_image(uploaded_file.stream))
            # Проверяем, что расширение есть в нашем списке
            # и что содержимое соответствует расширению
            # print(app.config['MAX_CONTENT_LENGTH'])
            # print(file_ext)
            print('uploaded_file.stream=', uploaded_file.stream)
            print('validate_image(uploaded_file.stream)=', validate_image(uploaded_file.stream))
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                            file_ext != validate_image(uploaded_file.stream):
                print('file_ext=', file_ext)
                # abort(400)
                # return redirect(url_for('upload_files'))
                return render_template('error-upload.html')
            # Такая ручная проверка не нужна (ниже),
            # сервер автоматически проверяет MAX_CONTENT_LENGTH и должен бросить на ош 413
            # if uploaded_file_length > app.config['MAX_CONTENT_LENGTH']: - не нужно!!!
            # При загрузке файла сервер проверяет размер файла и сравнивает с MAX_CONTENT_LENGTH
            # а затем, если размер больше, должен выдать ошибку 413 (слишком большой файл)
            # Однако в моем случае ошибку не дает, а просто идет сброс соединения с сайтом
            # Такая ошибка и у других встречается.  (https://question-it.com/questions/1471616/flask-sbrasyvaet-soedinenie-vmesto-togo-chtoby-vozvraschat-413-kogda-fajl-slishkom-velik)
            # В этом источнике https://docs-python.ru/packages/veb-frejmvork-flask-python/zagruzka-fajlov-server-flask/
            # говорится что на боевом сервере (а не на сервере разработки) сброса не будет
            # Поэтому пока тупо ограничила размер загружаемого файла 1 Mb (1048576 b) и сравниваю.
            # и перенаправляю на пользовательскую страницу ошибки 413. Причем не через блюпринт,
            # потому что не получается (хотя другие ошибки там ловлю), а через основную папку template
            # Но это нужно изменить впоследствии!!!
            # Сравнивать с app.config['MAX_CONTENT_LENGTH'] не получается так как сервер ловит раньше и
            # дает сброс соединения!
            # if uploaded_file_length > 5*1048576:
            # С 16.09.21 стал работать пререхват ошибки 413 большой файл из блюпринта, поэтому
            # следующие строки отключаю
            # if uploaded_file_length > app.config['MAX_CONTENT_LENGTH']:
            #     # abort(413)
            #     return render_template('error-upload-length.html')
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            print('os.path.join(app.config["UPLOAD_PATH"])=', os.path.join(app.config['UPLOAD_PATH']))
        return redirect(url_for('upload_files'))
    return render_template('upload.html')
# роут загрузки файлов - конец


# @app.route('/static/uploads/<filename>')
# def upload(filename):
#     return send_from_directory(app.config['UPLOAD_PATH'], filename)

# ****** Загрузка файлов - конец


# Роут для создания списка услуг (из модели Usluga) в выпадающем списке
# при выборе в первом выпадающем списке вида услуг(меню сайта Link)
# форма class PhotoFormAdmin, upload-foto-with-choice.html
# class LoadPhotoWithChoice(BaseView):
@app.route('/_get_uslugs/<menu>/', methods=['GET', 'POST'])
def _get_uslugs(menu):
    menu = request.args.get('menu', '01', type=str)
    # print('request.args.get("menu", "01", type=str)=', menu)
    uslugs = [(row.id, row.title) for row in Usluga.query.filter_by(punkt_menu_id=menu).all()]
    # print('uslugs from view=', uslugs)
    # print('jsonify(uslugs)=', jsonify(uslugs))
    return jsonify(uslugs)
    # return uslugs
# # Роут для создания списка услуг - конец

# Роут для создания списка услуг (из модели Usluga) в выпадающем списке
# при выборе в первом выпадающем списке вида услуг(меню сайта Link)
# форма class PhotoFormAdmin2, upload-foto-with-choice2.html
# class LoadPhotoWithChoice2(BaseView):
@app.route('/usluga/<menu>/')
def usluga(menu):
        uslugs = Usluga.query.filter_by(punkt_menu=menu).all()
        print(uslugs)
        uslugaArray = []
        for usluga in uslugs:
            uslugaObj={}
            uslugaObj['id']=usluga.id
            uslugaObj['title']=usluga.title
            uslugaArray.append(uslugaObj)

        return jsonify({'uslugs' : uslugaArray})
# # Роут для создания списка услуг - конец


@app.route('/', methods=['GET','POST']) # Главная страница
def render_main():
    # print('session.get(sum, 1) from render_main=', session.get('sum', 1))

    # это не удалять, тк нужно для проверки согласия на сбор cookies
    # session["cookies_success"] = False
    # print(url_for('render_main'))
    # load_user(user_id)
    # if current_user.is_authenticated:
    #     print(True)
    # print(False)

    links_menu = Link.query.order_by('title').all()
    # calendar.prcal(2022)
    # print(calendar.prcal(2022))


    # *** Блок "Карусели - показ на сайте" - начало
    carousels=Carousel.query.filter(Carousel.active==True).order_by(Carousel.date_create.desc()).all()
    # print('carousels=', carousels)
    carousel_parametrs = {}
    carousels_center = []
    carousels_left = []
    carousels_right = []

    if carousels:
        for carousel in carousels:
            for place in carousel.place_carousel:

               # Здесь base_location и остальные - это гибридные свойства модели PlaceCarousel
               # Они позволят заменить длинный код place.place_model_element.place_element.base_location.name_base_location
               # кот. дает тот же результат что и  place.base_location(например)
                if place.base_location=='FirstPage' or place.base_location=='AllPage':
                    carousel_parametrs['carousel']=carousel
                    carousel_parametrs['place']=place
                    carousel_parametrs['place_id']=place.id
                    carousel_parametrs['base_location']=place.base_location
                    carousel_parametrs['base_position']=place.base_position
                    carousel_parametrs['vertical_position']=place.vertical_position
                    carousel_parametrs['horizontal_position']=place.horizontal_position
                    carousel_parametrs['container_element']=place.container_element
                    carousel_parametrs['column_element']=place.column_element
                    carousel_parametrs['width_element']=place.place_model_element.width_element
                    carousel_parametrs['height_element']=place.place_model_element.height_element

                    if place.horizontal_position=='center':
                        carousels_center.append(carousel_parametrs)
                    if place.horizontal_position=='left':
                        carousels_left.append(carousel_parametrs)
                    if place.horizontal_position=='right':
                        carousels_right.append(carousel_parametrs)

                    carousel_parametrs={}

    # print('carousels_first_page_center=', carousels_first_page_center)
    # print('carousels_first_page_left=', carousels_first_page_left)
    # print('carousels_first_page_right=', carousels_first_page_right)

    # *** Блок "Карусели - показ на сайте" - конец

    return render_template('index.html',
                           # links=links,   для загрузки данных из JSON
                            links_menu=links_menu,
                           carousels_center=carousels_center,
                           carousels_left=carousels_left,
                           carousels_right=carousels_right
                           )

# *** Страница с выбранным пунктом главного меню
# На ней показываем:
# 1) в левом столбце - услуги, принадлежащие пункту меню
# 2) в правом столбце - по одной карточке услуг данной услуги, имеющей фото.
#     То есть если у услуги несколько карточек с фото, то показываем только одну карточку\
#     и только одно ее фото
@app.route('/раздел-<punkt_menu>/')
# Можно с помощью @login_required показывать стр. только для авторизованных пользователей,но мы этого делать не будем!
# @login_required
def render_menu(punkt_menu):
    links_menu = Link.query.order_by('title').all()
    link = Link.query.filter(Link.link == punkt_menu).first()

    if link == None:
        # return render_template("errors/404.html", links_menu=links_menu)
        abort(404)
    else:


        # *** Формирование карточек услуг на стр. с выбранным пунктом меню - начало

        # Выбираем услуги, принадлежащие пункту меню
        uslugs_punkt_menu = Usluga.query.filter(Usluga.punkt_menu_id == link.id).order_by('title').all()

        # Формируем список словарей.
        # Каждый словарь включает в себя:
        # 1) услугу из uslugs_punkt_menu,
        # принадлежащую пункту меню если у нее есть карточки услуг с фото
        # 2) первую карточку услуги с фото (фото показываем потом только одно)

        list_dict_cards = []
        for usluga in uslugs_punkt_menu:
            list_cards_with_photo=[]
            dict_card = {}
            i=0

            # Если услуга имеет карточки
            if usluga.cards_usluga:
                for card in usluga.cards_usluga:
                    if card.arhive==False and card.active==True:

                        # Если карточки имеют фото
                        if card.photos and i<1:
                            i=i+1
                            list_cards_with_photo.append(card)

                if len(list_cards_with_photo)>0:
                    dict_card['usluga']=usluga
                    dict_card['card']=list_cards_with_photo[0]
                    list_dict_cards.append(dict_card)
                    list_cards_with_photo=[]

        # print('list_dict_cards=', list_dict_cards)
        # *** Формирование карточек услуг на стр. с выбранным пунктом меню - конец

    # *** Блок "Карусели - показ на сайте" - начало
    carousels=Carousel.query.filter(Carousel.active==True).order_by(Carousel.date_create.desc()).all()

    carousel_parametrs = {}
    carousels_center = []
    carousels_left = []
    carousels_right = []

    if carousels:
        for carousel in carousels:
            for place in carousel.place_carousel:

               # Здесь base_location и остальные - это гибридные свойства модели PlaceCarousel
                if place.base_location=='Razdel' or place.base_location=='AllPage':
                    # print('carousel1=', carousel, 'place1=', place, 'place.base_location1=', place.base_location, 'place.base_position1=', place.base_position)
                    carousel_parametrs['carousel']=carousel
                    carousel_parametrs['place']=place
                    carousel_parametrs['place_id']=place.id
                    carousel_parametrs['base_location']=place.base_location
                    carousel_parametrs['base_position']=place.base_position
                    carousel_parametrs['vertical_position']=place.vertical_position
                    carousel_parametrs['horizontal_position']=place.horizontal_position
                    carousel_parametrs['container_element']=place.container_element
                    carousel_parametrs['column_element']=place.column_element
                    carousel_parametrs['width_element']=place.place_model_element.width_element
                    carousel_parametrs['height_element']=place.place_model_element.height_element

                    if place.horizontal_position=='center':
                        carousels_center.append(carousel_parametrs)
                    if place.horizontal_position=='left':
                        carousels_left.append(carousel_parametrs)
                    if place.horizontal_position=='right':
                        carousels_right.append(carousel_parametrs)

                    carousel_parametrs={}

    # *** Блок "Карусели - показ на сайте"  - конец

    return render_template("menu.html",
                           punkt_menu=punkt_menu,
                           link=link,
                           links_menu=links_menu,
                           uslugs_punkt_menu=uslugs_punkt_menu,
                           list_dict_cards=list_dict_cards,



                           # uslugi_id_link=uslugi_id_link,
                           # spisok_foto_punkt_menu=spisok_foto_punkt_menu,

                           carousels_center=carousels_center,
                           carousels_left = carousels_left,
                           carousels_right=carousels_right,
                           razdel=True,
                           # links=links,  для загрузки данных из JSON
                           # uslugi=uslugi,  для загрузки данных из JSON
                           )


# Показать карточки услуг в выбранной услуге данного пункта главного меню
# (показываются только карточки, имеющие прайсы)
@app.route('/раздел-<punkt_menu>/услуга-<category>/')
def render_uslugi_link(punkt_menu, category):
    session['order_add_to_cart'] = False
    # print('punkt_menu=', punkt_menu, 'category=', category)

    # кол-во в заказе
    session['sum']=1
    # на заказ услуги в def order_request в блюпринте @order_blueprint.route
    # иначе сохранится то кол-во которое было указано в def order_request ранее
    # Делаем это на этой стр и потом на стр где все карточки услуг (с нее тоже можно будет заказать)
    session['sum']=1
    links_menu = Link.query.order_by('title').all()

    link = Link.query.filter(Link.link == punkt_menu).first()

    usluga = Usluga.query.filter(Usluga.link == category).first()
    # print('usluga_page=', usluga_page, usluga_page.id)
    # cards_uslugs=usluga_page.cards_usluga
    # print('cards_uslugs=', cards_uslugs)

    # Запрос фильтрует те карточки которые принадлежат данной услуге, имеют прайсы и не в архиве
    # cards_uslugs = CardUsluga.query.filter(db.and_(CardUsluga.usluga.has(CardUsluga.usluga_id== usluga.id),
    #                                      CardUsluga.prices.any(), CardUsluga.usluga.has(CardUsluga.arhive==False)
    #                                      )
    #                               ).all()
    # Запрос фильтрует те карточки которые принадлежат данной услуге и не в архиве
    cards_uslugs = CardUsluga.query.filter(db.and_(CardUsluga.usluga.has(CardUsluga.usluga_id == usluga.id),
                                                   CardUsluga.usluga.has(CardUsluga.arhive == False),
                                                   CardUsluga.usluga.has(CardUsluga.active == True)
                                                   )
                                           ).all()
    # print('cards_uslugs=', cards_uslugs)


    if usluga == None:
        # return render_template("errors/404.html", links_menu=links_menu)
        # Происходит пререадресация на стр. 404.html из блюпринта errors
        abort(404)
    else:
        # делаем выборку из базы загрузок фото(UploadFileMy), соответствующих услуге из пункта меню
        # foto_for_usluga - объект запроса из базы
        # type(foto_for_usluga)= <class 'flask_sqlalchemy.BaseQuery'>
        foto_for_usluga = UploadFileMy.query.filter(UploadFileMy.dir_usluga == category)
        spisok_foto_for_usluga = []
        # Создадим словарь, где впоследствии будут храниться данные такой структуры:
        # show_foto_and_prices= {'2021-11-11_15-29-53_20-26--.jpg':
        # {'Прайс1 буклеты': [['str', 'str',....], ['str', 'str',....]],
        # 'Прайс2 буклеты': [['str', 'str',....], ['str', 'str',....]],
        # '2021-11-23_15-20-21_met332.jpg': {}}
        show_foto_and_prices={}
        for foto in foto_for_usluga:
            # Комментарии не удалять!!!
            # foto - это объект <class 'RECL.models.UploadFileMy'> из выборки foto_for_usluga,
            # который с помощью def __repr__(self): в модели class UploadFileMy(db.Model)
            # отображается как  return self.secure_name_photo + '('+self.title + ')' либо
            # return self.secure_name_photo (Например: 2021-11-22_22-25-46_okno3.jpg(Какие-то визитки))
            # secure_name_photo формируется из безопасного имени с добавлением времени загрузки,
            # поэтому можем использовать как уникальный идентификатор
            # foto.price - это коллекция объектов PriceTable прайсов из отношения модели UploadFileMy
            # Например: foto.price= [Прайс 2 визитки, Прайс 1 визитки]
            #           type(foto.price)= <class 'sqlalchemy.orm.collections.InstrumentedList'>
            # foto.price[0] - это один объект PriceTable из коллекции foto.price(если коллекция не пустая),
            #  который отображаеся с помощью def __repr__(self):
            # return self.name_price_table как имя прайса. Например:
            # foto.price[0]= Прайс 2 визитки
            # type(foto.price[0])= <class 'RECL.models.PriceTable'>

            deserialized_price={}
            spisok_foto_for_usluga.append(foto)
            for i in range(len(foto.price)):
                # deserialized_price[foto.price[i].name_price_table]=json.loads(foto.price[i].value_table)
                deserialized_price[foto.price[i].name_price_table]=foto.price[i].value_table

            show_foto_and_prices[foto.secure_name_photo]=deserialized_price


            # *** Формирование карточек услуг на стр. с выбранным пунктом меню - начало
            # Выбираем все карточки у кот. выбранный пункт меню
            # cards_uslugs=CardUsluga.query.filter(CardUsluga.usluga==category).all()
            # print('cards_uslugs=', cards_uslugs)


    # *** Блок "Карусели - показ на сайте" - начало
    carousels=Carousel.query.filter(Carousel.active==True).order_by(Carousel.date_create.desc()).all()

    carousel_parametrs = {}
    carousels_center = []
    carousels_left = []
    carousels_right = []

    if carousels:
        for carousel in carousels:
            for place in carousel.place_carousel:

               # Здесь base_location и остальные - это гибридные свойства модели PlaceCarousel
               # Они позволят заменить длинный код place.place_model_element.place_element.base_location.name_base_location
               # кот. дает тот же результат что и  place.base_location(например)
                if place.base_location=='Usluga' or place.base_location=='AllPage':
                    # print('carousel1=', carousel, 'place1=', place, 'place.base_location1=', place.base_location, 'place.base_position1=', place.base_position)
                    carousel_parametrs['carousel']=carousel
                    carousel_parametrs['place']=place
                    carousel_parametrs['place_id']=place.id
                    carousel_parametrs['base_location']=place.base_location
                    carousel_parametrs['base_position']=place.base_position
                    carousel_parametrs['vertical_position']=place.vertical_position
                    carousel_parametrs['horizontal_position']=place.horizontal_position
                    carousel_parametrs['container_element']=place.container_element
                    carousel_parametrs['column_element']=place.column_element
                    carousel_parametrs['width_element']=place.place_model_element.width_element
                    carousel_parametrs['height_element']=place.place_model_element.height_element

                    if place.horizontal_position=='center':
                        carousels_center.append(carousel_parametrs)
                    if place.horizontal_position=='left':
                        carousels_left.append(carousel_parametrs)
                    if place.horizontal_position=='right':
                        carousels_right.append(carousel_parametrs)

                    carousel_parametrs={}

    # *** Блок "Карусели - показ на сайте" - конец

    return render_template('usluga.html',
                           cards_uslugs=cards_uslugs,
                           links_menu=links_menu,
                           link=link,
                           usluga=usluga,

                            spisok_foto_for_usluga=spisok_foto_for_usluga,
                            show_foto_and_prices=show_foto_and_prices,
                            punkt_menu=punkt_menu,
                            category=category,
                            carousels_center=carousels_center,
                            carousels_left = carousels_left,
                            carousels_right=carousels_right,

                           # links=links, для загрузки данных из JSON
                           # uslugi=uslugi,  для загрузки данных из JSON,
                            )

# *** Показать все карточки услуг - начало
@app.route('/all_cards_uslugs/', methods=['GET', 'POST'])
def all_cards_uslugs():
    links_menu = Link.query.order_by('title').all()

    # filter(CardUsluga.prices.any()) позволяет отфильтровать карточки, у которых есть прайсы
    # по столбцу с отношением. Т.к. я хочу показывать на странице только карточки с прайсами
    cards_uslugs = CardUsluga.query.filter(CardUsluga.prices.any()).order_by('name_card_usluga').all()
    return render_template('all_cards_uslugs.html',
                           links_menu=links_menu,
                           cards_uslugs=cards_uslugs
                           )
# *** Показать все карточки услуг - конец


# *** Все услуги и прайсы - потом убрать!! начало
@app.route('/uslugi/')
def all_uslugi_and_price():
    links_menu = Link.query.order_by('title').all()
    spisok_foto_all = UploadFileMy.query.order_by('menu').all()
    price_without_foto = PriceTable.query.filter(PriceTable.card_uslugi_id == None).all()
    deserialized_price_without_foto={}
    if price_without_foto:
        # print('price_without_foto=', price_without_foto[0])
        # print('price_without_foto.name_price_table=', price_without_foto[0].name_price_table)

        for price in price_without_foto:
            # print('price=', price)
            # print('price.value_table=', price.value_table)
            # print('price.name_price_table=', price.name_price_table)
            # deserialized_price_without_foto[price.name_price_table]=json.loads(price.value_table)
            deserialized_price_without_foto[price.name_price_table]=price.value_table
        # print('deserialized_price_without_foto=', deserialized_price_without_foto)

    spisok_foto_for_usluga = []
    show_foto_and_prices={}
    for foto in spisok_foto_all:
        deserialized_price={}
        spisok_foto_for_usluga.append(foto)
        for i in range(len(foto.price)):
            # deserialized_price[foto.price[i].name_price_table]=json.loads(foto.price[i].value_table)
            deserialized_price[foto.price[i].name_price_table]=foto.price[i].value_table
        show_foto_and_prices[foto.secure_name_photo]=deserialized_price

    # *** Блок "Карусели - показ на сайте" - начало
    carousels=Carousel.query.filter(Carousel.active==True).order_by(Carousel.date_create.desc()).all()

    carousel_parametrs = {}
    carousels_center = []
    carousels_left = []
    carousels_right = []

    if carousels:
        for carousel in carousels:
            for place in carousel.place_carousel:

               # Здесь base_location и остальные - это гибридные свойства модели PlaceCarousel
               # Они позволят заменить длинный код place.place_model_element.place_element.base_location.name_base_location
               # кот. дает тот же результат что и  place.base_location(например)
                if place.base_location=='AllPage':
                    # print('carousel1=', carousel, 'place1=', place, 'place.base_location1=', place.base_location, 'place.base_position1=', place.base_position)
                    carousel_parametrs['carousel']=carousel
                    carousel_parametrs['place']=place
                    carousel_parametrs['place_id']=place.id
                    carousel_parametrs['base_location']=place.base_location
                    carousel_parametrs['base_position']=place.base_position
                    carousel_parametrs['vertical_position']=place.vertical_position
                    carousel_parametrs['horizontal_position']=place.horizontal_position
                    carousel_parametrs['container_element']=place.container_element
                    carousel_parametrs['column_element']=place.column_element
                    carousel_parametrs['width_element']=place.place_model_element.width_element
                    carousel_parametrs['height_element']=place.place_model_element.height_element

                    if place.horizontal_position=='center':
                        carousels_center.append(carousel_parametrs)
                    if place.horizontal_position=='left':
                        carousels_left.append(carousel_parametrs)
                    if place.horizontal_position=='right':
                        carousels_right.append(carousel_parametrs)

                    carousel_parametrs={}
    # *** Блок "Карусели - показ на сайте" - конец

    return render_template('uslugiall.html',
                            links_menu=links_menu,
                            spisok_foto_for_usluga=spisok_foto_for_usluga,
                            show_foto_and_prices=show_foto_and_prices,
                            deserialized_price_without_foto=deserialized_price_without_foto,
                            carousels_center=carousels_center,
                            carousels_left = carousels_left,
                            carousels_right=carousels_right
                            )

# *** Все услуги и прайсы - конец



# Заказать - ссылка в главном меню (потом сделать через блюпринт)
@app.route('/order/', methods=["GET", "POST"])
def render_order():
    err = ""
    links_menu = Link.query.all()
    form = OrderFormFromMenu()

      # *** Блок "Карусели - показ на сайте" - начало
    carousels=Carousel.query.filter(Carousel.active==True).order_by(Carousel.date_create.desc()).all()

    carousel_parametrs = {}
    carousels_center = []
    carousels_left = []
    carousels_right = []

    if carousels:
        for carousel in carousels:
            for place in carousel.place_carousel:

               # Здесь base_location и остальные - это гибридные свойства модели PlaceCarousel
               # Они позволят заменить длинный код place.place_model_element.place_element.base_location.name_base_location
               # кот. дает тот же результат что и  place.base_location(например)
                if place.base_location=='AllPage':
                    # print('carousel1=', carousel, 'place1=', place, 'place.base_location1=', place.base_location, 'place.base_position1=', place.base_position)
                    carousel_parametrs['carousel']=carousel
                    carousel_parametrs['place']=place
                    carousel_parametrs['place_id']=place.id
                    carousel_parametrs['base_location']=place.base_location
                    carousel_parametrs['base_position']=place.base_position
                    carousel_parametrs['vertical_position']=place.vertical_position
                    carousel_parametrs['horizontal_position']=place.horizontal_position
                    carousel_parametrs['container_element']=place.container_element
                    carousel_parametrs['column_element']=place.column_element
                    carousel_parametrs['width_element']=place.place_model_element.width_element
                    carousel_parametrs['height_element']=place.place_model_element.height_element

                    if place.horizontal_position=='center':
                        carousels_center.append(carousel_parametrs)
                    if place.horizontal_position=='left':
                        carousels_left.append(carousel_parametrs)
                    if place.horizontal_position=='right':
                        carousels_right.append(carousel_parametrs)

                    carousel_parametrs={}
    # *** Блок "Карусели - показ на сайте" - конец

    return render_template("order.html",
                           form = form,
                           # links=links,
                           links_menu=links_menu,
                           err=err,
                            carousels_center=carousels_center,
                            carousels_left = carousels_left,
                            carousels_right=carousels_right
                           )



# Профиль пользователя
@app.route('/profil/', methods=["GET", "POST"])
@login_required
def render_profil():
    err = ""
    links_menu = Link.query.all()
    return render_template("profil.html", links_menu=links_menu, err=err)



#
@app.route('/cookies-success/')
def render_cookies_success():
    session["cookies_success"] = True
    print(session.get("cookies_success", False))
    return redirect("/")

# Политика конфиденциальности
@app.route('/politic/', methods=['GET','POST'])
def render_politic():
    return render_template("politic.html")


@app.route('/consent/', methods=['POST'])
def render_consent():
    form = ConsentForm()
    if request.method['POST']:
        current = session.get("i", 0)
        session["i"] = current + 1
        current = session.get("i", 0)
    redirect ("main.html", current=current, form=form)

# Роут страницы Контакты (ссылка на главной стр.)
@app.route('/contacts/')
def render_contacts():
    links_menu = Link.query.all()

     # *** Блок "Карусели - показ на сайте" - начало
    carousels=Carousel.query.filter(Carousel.active==True).order_by(Carousel.date_create.desc()).all()

    carousel_parametrs = {}
    carousels_center = []
    carousels_left = []
    carousels_right = []

    if carousels:
        for carousel in carousels:
            for place in carousel.place_carousel:

               # Здесь base_location и остальные - это гибридные свойства модели PlaceCarousel
               # Они позволят заменить длинный код place.place_model_element.place_element.base_location.name_base_location
               # кот. дает тот же результат что и  place.base_location(например)
                if place.base_location=='AllPage':
                    # print('carousel1=', carousel, 'place1=', place, 'place.base_location1=', place.base_location, 'place.base_position1=', place.base_position)
                    carousel_parametrs['carousel']=carousel
                    carousel_parametrs['place']=place
                    carousel_parametrs['place_id']=place.id
                    carousel_parametrs['base_location']=place.base_location
                    carousel_parametrs['base_position']=place.base_position
                    carousel_parametrs['vertical_position']=place.vertical_position
                    carousel_parametrs['horizontal_position']=place.horizontal_position
                    carousel_parametrs['container_element']=place.container_element
                    carousel_parametrs['column_element']=place.column_element
                    carousel_parametrs['width_element']=place.place_model_element.width_element
                    carousel_parametrs['height_element']=place.place_model_element.height_element

                    if place.horizontal_position=='center':
                        carousels_center.append(carousel_parametrs)
                    if place.horizontal_position=='left':
                        carousels_left.append(carousel_parametrs)
                    if place.horizontal_position=='right':
                        carousels_right.append(carousel_parametrs)

                    carousel_parametrs={}
    # print('carousels_center=', carousels_center)
    # *** Блок "Карусели - показ на сайте" - конец

    return render_template("contacts.html",
                           # links=links,
                           links_menu=links_menu,
                            carousels_center=carousels_center,
                            carousels_left = carousels_left,
                            carousels_right=carousels_right
                           )

# Роут страницы Рекламные позиции (ссылка на главной стр.)
@app.route('/advertising/')
def render_advertising():
    links_menu = Link.query.all()
    return render_template("advertising.html",
                           links_menu=links_menu)



# Этот роут нужен для того, чтобы сбросить данные POST запроса при отправке формы,
# для предотвращения повторной отправки данных при обновлении страницы!!!
# При этом происходит попытка повторного удаления файла кот. уже удален
# На него происходит переадресация из class DeleteFoto если данные формы валидированы и POST запрос
# см админку class DeleteFoto  и форма delete_foto.html
# Этот вариант рабочий, но в проекте используем переадресацию на саму себя (вариант 2),
# поэтому данный роут сделан для примера варианта 1. (и его можно удалить)
@app.route('/sbrosdeletefoto/')
def sbros_deletefoto_from_admin():
    print('роут sbrosdeletefoto ')
    return redirect(url_for('deletefoto.delete_foto'))


# Этот роут нужен для того, чтобы сбросить данные POST запроса при отправке формы,
# для предотвращения повторной отправки данных при обновлении страницы!!!
# Если этого не сделать после загрузки файла и перезагрузки стр. происходит повторная загрузка файла,
# т.к. уникальное имя формируется на основе времени загрузки(до секунды) и они получаются разные.
# А поскольку данные запроса не очищены, то загрузка файлов будет происходить столько раз,
# сколько пользователь обновит стр.
# На него происходит переадресация из class Choice2 если данные формы валидированы и POST запрос
# см админку class Choice2  и форма delete_foto.html
# Этот вариант рабочий, но в проекте используем переадресацию на самого себя (вариант 2),
# поэтому данный роут сделан для примера варианта 1. (и его можно удалить)
@app.route('/sbroschoice2/')
def sbros_choice2_from_admin():
    print('роут sbroschoice2 ')
    return redirect(url_for('choice2.choice2'))



@app.route('/portfolio/')
def render_portfolio():
    title = ['Доставка', 'Контакты']
    region = ['Тверская обл.', 'Московская обл.', 'Ивановская обл.']
    return render_template("portfolio.html", title=title, region=region)

@app.route('/docs-navbar/')
def render_navbar():
    return render_template("docs-navbar.html")


@app.route('/SHPORA/')
def render_shpora():
    title = ['Доставка', 'Контакты']
    region = ['Тверская обл.', 'Московская обл.', 'Ивановская обл.']
    return render_template("SHPORA.html", title=title, region=region)


@app.route('/cookies', methods=['GET','POST'])
def render_cookies():
    return render_template("cookies.html")


# @app.route('/newspaper/')
# def render_newspaper():
#     cnn_paper = newspaper.build('https://www.afanasy.biz/')
#     article = Article('https://www.afanasy.biz/news/society/172369', keep_article_html=True)
#     article.download()
#     article.parse()
#     title = ['Доставка', 'Контакты']
#     region = ['Тверская обл.', 'Московская обл.', 'Ивановская обл.']
#     return render_template("newspaper.html", title=title, region=region, cnn_paper=cnn_paper, article=article)


    # *** вар 2 запроса и дальнейшего отбора - начало
    # было в @app.route('/', methods=['GET','POST']) def render_main():
    # Оставить как пример множественного запроса с отношениями!!!
    # Этот запрос работает (с точки зрения синтаксиса), НО дает НЕ ТОТ результат кот. мы хотели т.к отбирает карусели а не места
    # (с точки зрения логики отбора) Те мы получаем карусели у кот. есть места с name_base_location=='FirstPage',
    # но при этом у той же карус. могут быть места не имеющие name_base_location=='FirstPage',
    # а они все равно попадут в конечный результат. Тогда нам нужно добавить цикл по местам с фильтром name_base_location=='FirstPage',
    # но тогда такой сложный запрос не имеет смысла. И возвращаемся тогда к фильтру Carousel.active==True,
    # а далее if по name_base_location=='FirstPage' те вар 1

    # carousels=Carousel.query.\
    #     filter(Carousel.active==True).\
    #     filter(Carousel.place_carousel.any
    #                          (PlaceCarousel.place_model_element.has
    #                           (PlaceModelElement.place_element.has
    #                            (PlaceElement.base_location.has
    #                             (BaseLocationElement.name_base_location=='FirstPage')))))
    # if carousels:
    #     for carousel in carousels:
    #         for place in carousel.place_carousel:
    #             print('carousel2=', carousel, 'place2=', place, 'place.base_location2=', place.base_location, 'place.base_position2=', place.base_position)
    #
    #             carousel_parametrs['carousel']=carousel
    #             carousel_parametrs['place_id']=place.id
    #             carousel_parametrs['base_location']=place.base_location
    #             carousel_parametrs['base_position']=place.base_position
    #             carousel_parametrs['vertical_position']=place.vertical_position
    #             carousel_parametrs['horizontal_position']=place.horizontal_position
    #             carousel_parametrs['container_element']=place.container_element
    #             carousel_parametrs['column_element']=place.column_element
    #             carousel_parametrs['width_element']=place.place_model_element.width_element
    #             carousel_parametrs['height_element']=place.place_model_element.height_element
    #
    #             if place.horizontal_position=='center':
    #                 carousels_first_page_center.append(carousel_parametrs)
    #             if place.horizontal_position=='left':
    #                 carousels_first_page_left.append(carousel_parametrs)
    #             if place.horizontal_position=='right':
    #                 carousels_first_page_right.append(carousel_parametrs)
    #
    #             carousel_parametrs={}
         # *** вар 2 запроса и дальнейшего отбора - конец










# Перенесла в Blueprint RECL/components
# Разлогинить
# @app.route('/logout/')
# def render_logout():
#     # if session.get("is_auth"):
#     #     session.pop("is_auth")
#     #     session['admin'] = False
#     #     session['role'] = None
#     return redirect('/')


# Авторизация
# @app.route('/login/', methods=["GET", "POST"])
# def render_login():
#     links_menu = Link.query.all()
#     err = ""
#     form = LoginForm()
#     if request.method == "POST":
#         # получаем данные
#         username = form.username.data
#         password = form.password.data
#         # выводим данные
#         return render_template("index.html",
#                                username=username,
#                                password=password,
#                                # links=links,
#                                links_menu=links_menu)
#     return render_template("security/login_user.html",
#                            form = form,
#                            # links=links,
#                            links_menu=links_menu,
#                            err=err)

# # Регистрация
# @app.route('/register/', methods=["GET", "POST"])
# def render_register():
#     links_menu = Link.query.all()
#     print(request.url)
#     print(request.args.get('next'))
#     err = ""
#     form = RegistrationForm()
#     if request.method == "POST":
#         # получаем данные
#         username = form.username.data
#         password = form.password.data
#         user = User.query.filter_by(email=username).first()
#         if user:
#             err = "Пользователь с указанным именем уже существует"
#             return render_template("login.html", err = err, form = form, links_menu=links_menu)
#         # # выводим данные
#         # return render_template("register-save.html",
#         #                        username=username,
#         #                        password=password,
#         #                        # links=links,
#         #                        links_menu=links_menu,
#         #                        err = err)
#         else:
#             if form.validate_on_submit():
#                 user = User(email = username, password = password)
#                 db.session.add(user)
#                 db.session.commit()
#                 return redirect("/")
#             else:
#                 return render_template("register.html", form = form, err = err, links_menu=links_menu)
#     else:
#         return render_template("register.html",
#                                form = form,
#                                # links=links,
#                                links_menu=links_menu,
#                                err=err)


# Перенесла в Blueprint RECL/errors

# # Ошибка 404
# @app.errorhandler(404)
# def render_pageNotFound(error):
#     return render_template("errors/404.html"), 404

# Ошибка 500
# Задокументировала временно, чтобы видеть какие ошибки
# Представление для пользователя, можно дописать чтобы коды ошибки записывались куда-нибудь.
# ЧИТАТЬ ПОДРОБНЕЕ!!!
# https://flask.palletsprojects.com/en/1.1.x/errorhandling/

# @app.errorhandler(Exception)
# def handle_exception(e):
#     # print(e)
#     # print(HTTPException)
#     # pass through HTTP errors
#     if isinstance(e, HTTPException):
#         return e
#     # now you're handling non-HTTP exceptions only
#     return render_template("errors/500.html", e=e), 500

# Перенесла в Blueprint RECL/errors - конец