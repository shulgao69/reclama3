# from flask import Flask
# import flask_security

# import datetime
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import JSON

# from sqlalchemy.orm.collections import InstrumentedList as _InstrumentedList

# from sqlalchemy import text

# from flask_security import Security

# https://question-it.com/questions/6537146/flask-sqlalchemy-filtr-po-kolichestvu-obektov-otnoshenij
# from sqlalchemy.sql.expression import func
from sqlalchemy import select, func


# from transliterate import translit


# from flask_login import UserMixin
# from RECL import login_manager
# from flask_security SQLAlchemyUserDatastore
# from flask_admin import BaseView, expose
# from flask_security.utils import hash_password
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask import redirect, session
# from flask_admin.contrib.sqla import ModelView

# from wtforms import SubmitField, SelectField, HiddenField, BooleanField, StringField, \
#     PasswordField, IntegerField, validators, DateField, DateTimeField

# from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
#
# from flask_migrate import Migrate

db = SQLAlchemy()


# b = timedelta(days=45, hours=45, minutes=45)
# print('b=', b, 'type(b)=', type(b))

# a = datetime(2022, 8, 05, 10, 32, 24, 34574)
# a = datetime(2022, 8, 5, 10, 00)
# print('a=', a, a.year, a.month, a.day, a.hour, a.minute, a.second, a.microsecond)

# c = a+b
# print('c=', c, 'type(c)=', type(c))



# ****** МОДЕЛИ ДЛЯ РАЗМЕЩЕНИЯ ЭЛЕМЕНТОВ - начало

# Модель для определения БАЗОВОЙ ЛОКАЦИИ элемента (все стр., первая стр, раздел, услуга и тп) - начало
class BaseLocationElement(db.Model):
    __tablename__ = 'base_location_elements'
    id = db.Column(db.Integer, primary_key=True)
    name_base_location = db.Column(db.String(255), nullable=False, unique=True)
    comment_base_location = db.Column(db.String(255), nullable=False, unique=True)
    code = db.Column(db.String(255), nullable=False, unique=True)
    places = db.relationship("PlaceElement", back_populates="base_location")
    def __repr__(self):
        return self.name_base_location
# Модель для определения БАЗОВОЙ ЛОКАЦИИ элемента - конец


# Модель для определения БАЗОВОЙ ПОЗИЦИИ элемента (шапка, тело, подвал) - начало
class BasePositionElement(db.Model):
    __tablename__ = 'base_position_elements'
    id = db.Column(db.Integer, primary_key=True)
    name_base_position = db.Column(db.String(255), nullable=False, unique=True)
    comment_base_position = db.Column(db.String(255), nullable=False, unique=True)
    code = db.Column(db.String(255), nullable=False, unique=True)
    places = db.relationship("PlaceElement", back_populates="base_position")
    def __repr__(self):
        return self.name_base_position
# Модель для определения БАЗОВОЙ ПОЗИЦИИ элемента (шапка, тело, подвал) - конец


# Модель для определения горизонтальной ПОЗИЦИИ элемента - начало
class HorizontalPositionElement(db.Model):
    __tablename__ = 'horizontal_positions'
    id = db.Column(db.Integer, primary_key=True)
    name_horizontal_position = db.Column(db.String(255), nullable=False, unique=True)
    comment_horizontal_position = db.Column(db.String(255), nullable=False, unique=True)
    code = db.Column(db.String(255), nullable=False, unique=True)
    # positions = db.relationship("PositionElement", back_populates="horizontal_position")

    def __repr__(self):
        return self.name_horizontal_position
# Модель для определения горизонтальной ПОЗИЦИИ элемента - конец
#
# Модель для определения вертикальной ПОЗИЦИИ элемента - начало
class VerticalPositionElement(db.Model):
    __tablename__ = 'vertical_positions'
    id = db.Column(db.Integer, primary_key=True)
    name_vertical_position = db.Column(db.String(255), nullable=False, unique=True)
    comment_vertical_position = db.Column(db.String(255), nullable=False, unique=True)
    code = db.Column(db.String(255), nullable=False, unique=True)
    # positions = db.relationship("PositionElement", back_populates="vertical_position")

    def __repr__(self):
        return self.name_vertical_position
# Модель для определения вертикальной ПОЗИЦИИ элемента - конец


# Модель для определения ПОЗИЦИИ(координаты) элемента  - начало
# в зависимости от горизонтальной позиции и вертикальной позиций
class PositionElement(db.Model):
    __tablename__ = 'position_elements'
    id = db.Column(db.Integer, primary_key=True)
    # name_position = db.Column(db.String(255), nullable=False, unique=True)
    # comment_position = db.Column(db.String(255))

    # places = db.relationship("PlaceElement", back_populates="position")

    # horizontal_position = db.relationship("HorizontalPositionElement", back_populates="positions")
    horizontal_position = db.relationship("HorizontalPositionElement")
    horizontal_position_id = db.Column(db.Integer, db.ForeignKey("horizontal_positions.id"))
    #
    # # vertical_position = db.relationship("VerticalPositionElement", back_populates="positions")
    vertical_position = db.relationship("VerticalPositionElement")
    vertical_position_id = db.Column(db.Integer, db.ForeignKey("vertical_positions.id"))
    #

    # Конструкция __table_args__ задает дополнительные свойства класса
    # В данном случае с помощью db.UniqueConstraint мы указываем, что в классе SettingAdmin
    # одной модели и одной роли соответствует единственная строка.

    __table_args__ = (db.UniqueConstraint('horizontal_position_id', 'vertical_position_id', name='_horizontal_vertical'),
                     )

    @hybrid_property
    def name_position(self):
        # name_position = 'По гориз.: '+str(self.horizontal_position)+\
        #                         '. '+ 'По вертик.: '+str(self.vertical_position)
        name_position = str(self.vertical_position)+' - '+str(self.horizontal_position)
        return name_position

    @hybrid_property
    def alias_position(self):
        alias_position = str(self.vertical_position.code)+'-'+str(self.horizontal_position.code)
        return alias_position


    @hybrid_property
    def comment_position(self):
        # comment_position = 'по гориз.: '+str(self.horizontal_position.comment_horizontal_position)+\
        #                         '; по вертик.: '+ str(self.vertical_position.comment_vertical_position)
        comment_position = str(self.vertical_position.comment_vertical_position)+\
                           ' (код - '+self.vertical_position.code+'). '+\
                           str(self.horizontal_position.comment_horizontal_position)+\
                           ' (код - '+self.horizontal_position.code+')'

        return comment_position


    def __repr__(self):
        return self.name_position
# Модель для определения ПОЗИЦИИ элемента - конец


# Модель для определения ШИРИНЫ элемента - начало
class WidthElement(db.Model):
    __tablename__ = 'width_elements'
    id = db.Column(db.Integer, primary_key=True)
    width_element = db.Column(db.String(255), nullable=False, unique=True)
    comment_width_element = db.Column(db.String(255), nullable=False, unique=True)
    def __repr__(self):
        return self.width_element
# Модель для определения ШИРИНЫ элемента - конец


# Модель для определения ВЫСОТЫ элемента - начало
class HeightElement(db.Model):
    __tablename__ = 'height_elements'
    id = db.Column(db.Integer, primary_key=True)
    height_element = db.Column(db.String(255), nullable=False, unique=True)
    comment_height_element = db.Column(db.String(255), nullable=False, unique=True)
    def __repr__(self):
        return self.height_element
# Модель для определения ВЫСОТЫ элемента - конец


# Модель для определения КОНТЕЙНЕРА элемента- начало
class ContainerElement(db.Model):
    __tablename__ = 'container_elements'
    id = db.Column(db.Integer, primary_key=True)
    name_container_element = db.Column(db.String(255), nullable=False, unique=True)
    comment_container_element = db.Column(db.String(255), nullable=False, unique=True)
    code = db.Column(db.String(255), nullable=False, unique=True)
    # all_locations_this_container = db.relationship("PlaceElement", back_populates="container_element")
    def __repr__(self):
        return self.name_container_element
# Модель для определения КОНТЕЙНЕРА элемента - конец

# Модель для определения КОЛ-ВА КОЛОНОК, в кот. будет размещен элемент- начало
class ColumnElement(db.Model):
    __tablename__ = 'column_elements'
    id = db.Column(db.Integer, primary_key=True)
    column_element = db.Column(db.String(255), nullable=False, unique=True)
    comment_column_element = db.Column(db.String(255), nullable=False, unique=True)
    code = db.Column(db.String(255), nullable=False, unique=True)
    # place = db.relationship("PlaceElement", back_populates="column_element")
    def __repr__(self):
        return self.column_element
# Модель для определения КОЛ-ВА КОЛОНОК, в кот. будет размещен элемент - конец

# Модель для определения ПРИОРИТЕТА размещения- начало
class PriorityElement(db.Model):
    __tablename__ = 'priority_elements'
    id = db.Column(db.Integer, primary_key=True)
    priority_element = db.Column(db.Integer, unique=True)
    comment_priority_element = db.Column(db.String(255), nullable=False)
    # place = db.relationship("PlaceElement", back_populates="priority_element")

    # Внимание!!! Если возвращала просто self.priority_element - тип был Integer
    # и почему-то возникала ошибка в админке при попытке создать запись в таблице PlaceElement
    # Поэтому сделала str(self.priority_element)
    def __repr__(self):
        return str(self.priority_element)
# Модель для определения ПРИОРИТЕТА размещения - конец


# Ассоциативная таблица Карусели - Локации - начало
# carouseles_place_elements_association = db.Table(
#     "carouseles_place_elements",
#     db.Column("carousel_id", db.Integer, db.ForeignKey("carouseles.id")),
#     db.Column("place_element_id", db.Integer, db.ForeignKey("place_elements.id")),
# )
# Ассоциативная таблица Карусели - Локации - конец


# Модель для определения местоположения загружаемых элементов - начало
class PlaceElement(db.Model):
    __tablename__ = 'place_elements'
    id = db.Column(db.Integer, primary_key=True)

    base_location = db.relationship("BaseLocationElement")
    base_location_id = db.Column(db.Integer, db.ForeignKey("base_location_elements.id"), nullable=False)

    base_position = db.relationship("BasePositionElement")
    base_position_id = db.Column(db.Integer, db.ForeignKey("base_position_elements.id"), nullable=False)

    position = db.relationship("PositionElement")
    position_id = db.Column(db.Integer, db.ForeignKey("position_elements.id"), nullable=False)

    container_element = db.relationship("ContainerElement")
    container_element_id = db.Column(db.Integer, db.ForeignKey("container_elements.id"), nullable=False)

    column_element = db.relationship("ColumnElement")
    column_element_id = db.Column(db.Integer, db.ForeignKey("column_elements.id"))

    __table_args__ = (db.UniqueConstraint('base_location_id', 'base_position_id',
                                          'position_id', 'container_element_id', 'column_element_id',
                                          name='_place_element_relation'),
                      )
    # carouseles = db.relationship(
    #     "Carousel", secondary=carouseles_place_elements_association, back_populates="place_elements"
    # )

    @hybrid_property
    def comment_place_element(self):
        comment_place_element = 'Баз. позиция: '+ str(self.base_position.comment_base_position)+\
                                ' (код - '+str(self.base_position.code)+\
                                '). Баз. локация: '+str(self.base_location.comment_base_location)+\
                                ' (код - '+str(self.base_location.code)+\
                                '). '+str(self.position.comment_position)+\
                                '. '+str(self.container_element.comment_container_element)+\
                                ' (код - '+str(self.container_element.code)+\
                                '). '+str(self.column_element.comment_column_element)+\
                                ' (код - '+str(self.column_element.code)+')'
        return comment_place_element


    @hybrid_property
    def code_place_element(self):
        code_place_element = str(self.base_position.code)+\
                                '/'+ str(self.position.alias_position)+\
                                '/'+str(self.base_location.code)+\
                                '/'+str(self.container_element.code)+\
                                '/'+str(self.column_element.code)
        return code_place_element

    @hybrid_property
    def name_place_element(self):
        name_place_element = 'Место: '+str(self.base_position.code)\
                              +'/'+ str(self.position.alias_position)\
                              +'/'+str(self.base_location)\
                              +'/'+str(self.column_element.code)\
                              +'/'+str(self.container_element.code)
        return name_place_element

    def __repr__(self):
        return self.name_place_element
# Модель для определения местоположения загружаемых элементов - конец


# Модель для определения возможных размеров в зависимости от местоположения и модели - начало
class PlaceModelElement(db.Model):
    __tablename__ = 'place_model_elements'
    id = db.Column(db.Integer, primary_key=True)

    # Внимание! Здесь задала ForeignKey не id а name_model, тк ListModel.name_model unique-True и может служить ключом!!!
    # (Оставила название кот. было раньше name_model_id (хотя использую ключ не id а name_model)
    # тк не получалась миграция (переименовать желательно чтобы путаницы не было))
    # Если этого ограничения нет не использовать так как будет ошибка!!!
    # Это сделала для удобства фильтрации в админке class MyPlaceCarousel(SpecificView): по слову Carousel, а не по id
    # https://question-it.com/questions/3511025/filtratsija-znachenij-stolbtsov-v-flask-admin-s-otnosheniem-odin-ko-mnogim
    # https://progi.pro/ispolzovanie-foreignkey-v-modelyah-sqlalchemy-v-pythonflask-342165
    # name_model_id = db.Column(db.Integer, db.ForeignKey("list_models.id"))

    name_model = db.relationship("ListModel")
    name_model_id = db.Column(db.String, db.ForeignKey("list_models.name_model"), nullable=False)

    place_element = db.relationship("PlaceElement")
    place_element_id = db.Column(db.Integer, db.ForeignKey("place_elements.id"), nullable=False)

    width_element = db.relationship("WidthElement")
    width_element_id = db.Column(db.Integer, db.ForeignKey("width_elements.id"))

    height_element = db.relationship("HeightElement")
    height_element_id = db.Column(db.Integer, db.ForeignKey("height_elements.id"), nullable=False)

    # place_carousels = db.relationship("PlaceCarousel")
    # place_carousels_id = db.Column(db.Integer, db.ForeignKey('place_carousels.id'))

    __table_args__ = (db.UniqueConstraint('place_element_id', 'name_model_id',
                                          'width_element_id', 'height_element_id',
                                          name='_model_place_size'),
                      )

    def __repr__(self):
        return str(self.name_model)+'. ' + str(self.place_element)+'. '+str(self.width_element)+'*'+str(self.height_element)
        # return str(self.name_model)+'. ' + str(self.place_element.name_place_element)+'. w-'+str(self.width_element)+', h-'+str(self.height_element)
# Модель для определения возможных местоположений и размеров в зависимости от модели - конец


# # Ассоциативная таблица Карусели - Места Карусели - начало
# carouseles_place_carousels_association = db.Table(
#     "carouseles_place_carousels",
#     db.Column("place_carousel_id", db.Integer, db.ForeignKey("place_carousels.id")),
#     db.Column("carousel_id", db.Integer, db.ForeignKey("carouseles.id")) )
# # Ассоциативная таблица Карусели - Места Карусели - конец


# Модель для определения возможных местоположений каруселей - начало
class PlaceCarousel(db.Model):
    __tablename__ = 'place_carousels'
    id = db.Column(db.Integer, primary_key=True)

    carousel = db.relationship("Carousel", back_populates='place_carousel')
    carousel_id=db.Column(db.Integer, db.ForeignKey("carouseles.id"), nullable=False)

    place_model_element = db.relationship("PlaceModelElement")
    place_model_element_id=db.Column(db.Integer, db.ForeignKey("place_model_elements.id"), nullable=False)

    priority_element = db.relationship("PriorityElement")
    priority_element_id = db.Column(db.Integer, db.ForeignKey("priority_elements.id"), nullable=False)

    # *** Пока оставить!! - начало
    # Попытка задать фильтрацию по определенному критерию - не удалась.
    # Нужно было для админки при создании мест моделей с размерами(например) чтобы не просматривать все варианты,
    # а только определенные модели
    # Реализовала в админке через form_args, но этот вар. надо разбирать, он много где нужен!!
    # # place_model_element = db.relationship("PlaceModelElement",
    # #                                       primaryjoin="and_(PlaceCarousel.id==PlaceModelElement.place_carousels_id, "
    # #                     "PlaceModelElement.name_model_id==12)")
    #  # place_model_element = db.relationship("PlaceModelElement", primaryjoin="and_(PlaceModelElement.name_model_id==12)")
    # place_model_element_id = db.Column(db.Integer, db.ForeignKey("place_model_elements.id"),nullable=False)
    # *** Пока оставить!! - конец

#     carousel = db.relationship("Carousel", secondary=carouseles_place_carousels_association, back_populates="place_carousel")
#     carousel_id = db.Column(db.Integer, db.ForeignKey("carouseles.id"))

    __table_args__ = (db.UniqueConstraint('priority_element_id', 'place_model_element_id', 'carousel_id',
                       name='_carousel_place_model_element'),
                      )

    @hybrid_property
    def base_location(self):
        base_location = str(self.place_model_element.place_element.base_location.name_base_location)
        return base_location

    @hybrid_property
    def base_position(self):
        base_position = str(self.place_model_element.place_element.base_position.name_base_position)
        return base_position

    @hybrid_property
    def vertical_position(self):
        vertical_position = str(self.place_model_element.place_element.position.vertical_position.name_vertical_position)
        return vertical_position

    @hybrid_property
    def horizontal_position(self):
        horizontal_position = str(self.place_model_element.place_element.position.horizontal_position.name_horizontal_position)
        return horizontal_position

    @hybrid_property
    def container_element(self):
        container_element = str(self.place_model_element.place_element.container_element.name_container_element)
        return container_element

    @hybrid_property
    def column_element(self):
        column_element = str(self.place_model_element.place_element.column_element.column_element)
        return column_element

    @hybrid_property
    def comment_place_element(self):
        comment_place_element = str(self.place_model_element.place_element.comment_place_element)
        return comment_place_element


    def __repr__(self):
        return str(self.place_model_element)

# ****** МОДЕЛИ ДЛЯ РАЗМЕЩЕНИЯ ЭЛЕМЕНТОВ - конец


# ***** Модель для записи данных в процессе загрузки изображения в карусель - начало
class Carousel(db.Model):
    __tablename__ = 'carouseles'
    id = db.Column(db.Integer, primary_key=True)
    name_carousel = db.Column(db.String(255), nullable=False, unique=True) # Имя карусели
    dir_carousel = db.Column(db.String(255), nullable=False, unique=True) # Директория загрузки
    number_foto = db.Column(db.Integer) # Кол-во фото
    date_create = db.Column(db.String(255))  # Дата создания
    dict_all_foto_carousel_name = db.Column(JSON) # Список словарей всех имен фото с подписями, текстом
    active = db.Column(db.Boolean, default=False) # активная карусель или нет
    arhive = db.Column(db.Boolean, default=False) # в архиве или нет

    place_carousel = db.relationship("PlaceCarousel", back_populates='carousel')

    # place_carousel = db.relationship("PlaceCarousel",
    #                                  secondary=carouseles_place_carousels_association,
    #                                  back_populates='carousel'
    #                                  )

    def __repr__(self):
        return 'Карусель: ' + self.name_carousel
# ***** Модель для записи данных в процессе загрузки изображения в карусель - конец


# ***** Модель для записи данных в таблицы прайсов - начало
class PriceTable(db.Model):
    __tablename__ = 'price_tables'
    id = db.Column(db.Integer, primary_key=True)
    # Имя таблицы прайса
    name_price_table = db.Column(db.String(255), nullable=False, unique=True)
    # количество строк в таблице
    row_table = db.Column(db.Integer, nullable=False)
     # количество столбцов(колонок) в таблице
    col_table = db.Column(db.Integer, nullable=False)
    # Как я поняла при записи в базу в поле db.Column(JSON) (например списка)
    # сериализация происходит  автоматически (встроена) и не надо делать специально json.dumps(имя списка)
    # а вот при извлечении этих данных из базы надо сделать json.loads????(...данные из поля) так как в базе JSON формат
    # https://python-scripts.com/json
    # https://question-it.com/questions/83190/stolbets-postgresql-json-ne-sohranjaet-simvol-utf-8
    # https://ru.stackoverflow.com/questions/1047189/Не-могу-избавиться-от-юникода-в-json-dumps
    # https://ru.stackoverflow.com/questions/606885/Как-json-данные-u0413-u0440-преобразовать-в-русский-текст

    # Для прайса теоретически моно было задать сразу тип Numeric (десятичные дроби)
    # Я сделала так потому, что
    # 1) в таблице первая строка и первый столбец это текст!!!
    # 2) В роуте (там где переход по ссылке на заказ) проверяю цена или строка в других ячейках
    # Тк хотела дать возможность написать в ячейке например Цена по запросу или что-то другое

    value_table = db.Column(JSON)

    # Потом убрать -это относится к фотоманагер - начало
    card_uslugi_id = db.Column(db.Integer, db.ForeignKey("upload_files.id"))
    card_uslugi = db.relationship('UploadFileMy', back_populates="price")
    # Потом убрать - конец

    card_usluga_id = db.Column(db.Integer, db.ForeignKey("cards_uslugs.id"))
    card_usluga = db.relationship('CardUsluga', back_populates="prices")
    arhive = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)

    # в каких заказах присутствует
    order_items = db.relationship("OrderItem", back_populates='price')


    def __repr__(self):
        return self.name_price_table+'(id '+str(self.id)+')'
# ***** Модель для записи данных в таблицы прайсов - конец


# Модель для записи данных в процессе загрузки изображения (загрузчик Choice2 в админке):
# - путь загрузки (формируется при выборе раздела и услуги),
# - имя(берется исходное имя загружаемого файла),
# - безопасное имя(преобразуется с помощью функции secure_filename с добавлением времени создания(до секунд)
# что(по замыслу) обеспечивает уникальное имя
#  - расширение, размер и т.д.
# Подразумевается, что данную модель НЕЛЬЗЯ! использовать для загрузки файлов через админ-панель,
#  так как в ней не установлены зависимости с разделами и услугами и, соответственно,
# при ручной записи произвольных путей загрузки не будут учтены пути загрузки по умолчанию,
# будут возникать ошибки, путаница и тд
# Модель отображаем в админке только для просмотра инфо загруженных файлов и общего представления
class UploadFileMy(db.Model):
    __tablename__ = 'upload_files'
    id = db.Column(db.Integer, primary_key=True)

    # *** То что не понадобится тк в модели CardUsluga будет отношение с услугой - начало
    # Раздел(меню сайта)
    menu = db.Column(db.String(255), nullable=False)
    # Директория Раздела(меню сайта) для загрузки
    dir_menu = db.Column(db.String(255), nullable=False)
    # Директория выбранной Услуги выбранного Раздела(меню сайта) для загрузки
    dir_usluga = db.Column(db.String(255), nullable=False)
    # *** То что не понадобится тк в модели CardUsluga будет отношение с услугой - конец

    # *** То что будет в модели Photo - начало
    # Исходное имя загружаемого файла
    origin_name_photo = db.Column(db.String(255), nullable=False)
    # Безопасное имя загружаемого файла
    secure_name_photo = db.Column(db.String(255), nullable=False)
    # Полная Директория для загрузки (общая директория загрузки + дир. раздела + дир услуги)
    dir_uploads = db.Column(db.String(255), nullable=False, default='/static/images/uploads/')
    # Расширение файла
    file_ext = db.Column(db.String(255), nullable=False)
    # Размер файла
    file_size = db.Column(db.Integer)
    # Заголовок фото
    title = db.Column(db.String(255))
    # Сопроводительный текст к фото
    comments = db.Column(db.Text)
    # *** То что будет в модели Photo - конец

    # *** То что будет в модели CardUsluga - начало
    price = db.relationship('PriceTable', back_populates="card_uslugi")
    # Услуга выбранного Раздела(меню сайта)-будет но с отношением
    usluga = db.Column(db.String(255), nullable=False)
    # *** То что будет в модели CardUsluga - конец

    def __repr__(self):
        if self.secure_name_photo and self.title:
            return self.secure_name_photo + '('+self.title + ')'
        elif self.secure_name_photo and not self.title:
            return self.secure_name_photo


# Ассоциативная таблица Пользователи - Роли
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))
# Для Flask-login (и Flask-Security которая использует Flask-login)
#  требуется модель User со следующими свойствами:
# имеет метод is_authenticated (), кот. возвращает True, если пользователь предоставил действительные учетные данные
# имеет метод is_active (), кот. возвращает True, если учетная запись пользователя активна
# имеет метод is_anonymous (), кот. возвращает True, если текущий пользователь является анонимным.
# имеет метод get_id (), кот., учитывая экземпляр пользователя, возвращает уникальный идентификатор для этого объекта
# Класс UserMixin обеспечивает реализацию этих свойств.
# Это причина, по кот. вы можете вызвать, например, is_authenticated, чтобы проверить
# правильность предоставленных учетных данных, вместо того, чтобы писать метод, чтобы сделать это самостоятельно.

# Модель Пользователь
# В этой модели храняться все пользователи (и покупатели услуг и персонал)
# Покупателем (заказчиком услуг) может быть пользователь с ролью и без
# Сотрудник - только пользователь с ролью. В зависимости от роли - разные доступы и возможности
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)    # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html#

    # у нас email это логин
    email = db.Column(db.String(255), nullable=False, unique=True)  # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html#

    password = db.Column(db.String(255), nullable=False)    # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html#

    # Нужен для блокировки пользователя при необходимости (например если сотрудник уволен
    # и ему нужно отключить доступ (эта возможность должна быть доступна только суперадмину например)
    active = db.Column(db.Boolean)    # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html#

    # С данными времени нужно разобраться - как правильно (часовые пояса например и тп)
    # Обратить внимание на default=datetime.utcnow. При входе в редактирование юзера давала ошибку
    # Поэтому исключила created_on и updated_on из return в def form_edit_rules в class MyUser(SpecificView)

    # Дата и время создания user
    # По гринвичу - created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    # Местное время
    created_on = db.Column(db.DateTime(), default=datetime.now)

    # updated_on - обновляется дата при изменении данных user -  работает.
    # При изменении данных в админке дату меняет а время другое указывает.Разбираться!!
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    # подтверждение - зачем?-разобраться!!
    confirmed_at = db.Column(db.DateTime())     # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html#

    user_first_name = db.Column(db.String()) # Имя
    user_middle_name = db.Column(db.String()) # Отчество
    user_last_name = db.Column(db.String()) # Фамилия

    # телефоны пользователя
    phones = db.relationship('Phone', back_populates='user')

    # роли пользователя (может быть несколько)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users'))

    # Если включить lazy='dynamic' то при отображении в админке модель Роли давала ошибку!!!
    # так как Дополнительный аргумент lazy указывает на способ выполнения  запроса.
    # Этот режим указывает не выполнять запрос, пока явно об этом не попросили. Разбираться!!!
    # https://stackoverflow.com/questions/29874142/backref-lazy-dynamic-does-not-support-object-population-eager-loading-cann
    # # https://habr.com/ru/post/230643/
    #  roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    # Заказы пользователя (как потребителя услуг)(собственные заказы)
    # 2 связи в модели к одной таблице Order без foreign_keys="[Order.user_id]" дают ошибку!!!
    # https: // docs.sqlalchemy.org / en / 14 / orm / join_conditions.html
    # https: //translated.turbopages.org/proxy_u/en-ru.ru.b9952bcd-636b3a4a-a31a33bd-74722d776562/https/stackoverflow.com/questions/7548033/how-to-define-two-relationships-to-the-same-table-in-sqlalchemy

    # orders = db.relationship('Order', back_populates='user')
    # orders = db.relationship('Order', foreign_keys="Order.user_id")
    orders = db.relationship('Order', foreign_keys="Order.user_id", back_populates='user')

    # За какие заказы отвечает как сотрудник(в каких заказах является главным менеджером)
    # orders_manager = db.relationship('Order', back_populates='manager_person')
    # orders_manager = db.relationship('Order', foreign_keys="Order.manager_person_id")
    orders_manager = db.relationship('Order', foreign_keys="Order.manager_person_id", back_populates='manager_person')

    # За какие элементы заказа отвечает (в данный момент?)
    orders_items = db.relationship('OrderItem', back_populates='staff_actual_status_person')

    # Плательщики пользователя (например организация, физ лицо - может быть несколько)
    payers = db.relationship('Payer', back_populates='user')

    def __repr__(self):
        return self.email


# Модель плательщик - 08.11.22 - дорабатывать - сделана пока для пробы
# В Payer хранить связь с юзером и общую инфо (какую? наименование? ИНН?) для юриков и физиков(ИП?)
# Специфичную инфо в отдельных таблицах для физиков и юриковю
# Отдельные таблицы для адресов сделать - думать как
class Payer(db.Model):
    __tablename__ = 'payers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates='payers')
    payer_status = db.Column(db.String(80))
    payer_info = db.Column(JSON)
    name = db.Column(db.String(), nullable=False)
    def __repr__(self):
        return self.name

# Модель Роли
class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True) # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html видео https://youtu.be/wDBiMtKIBs0#
    name = db.Column(db.String(80), unique = True, nullable=False) # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html  видео https://youtu.be/wDBiMtKIBs0#
    description = db.Column(db.String(255))
    # users = db.relationship("User", back_populates='roles')
    # users = db.relationship('User', secondary=roles_users, backref=db.backref('roles'))
    # users = db.relationship('User', secondary=roles_users, backref=db.backref('roles', lazy='dynamic'))

    # устанавливаем отношение между ролью и настройками
    # это отношение один ко многим - одна модель и у нее несколько настроек (для разных ролей)
    setting = db.relationship("SettingAdmin", back_populates="role")

    # statuses_cards_uslugs = db.relationship("StatusCardUsluga", back_populates='role_responsible')

    orders = db.relationship('Order', back_populates='manager_role')

    # Эта функция позволяет отразить в админке в частности не объект SQLalchemy (например <Role1>),
    # а имя (name)(например admin)
    def __repr__(self):
        return self.name


# Модель Список таблиц(моделей)
class ListModel(db.Model):
    __tablename__ = 'list_models'
    id = db.Column(db.Integer, primary_key=True) # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html видео https://youtu.be/wDBiMtKIBs0#
    name_model = db.Column(db.String(80), unique = True, nullable=False) # Минимум для использования Flask-Security https://pythonhosted.org/Flask-Security/models.html  видео https://youtu.be/wDBiMtKIBs0#

    # устанавливаем отношение между списком моделей и настройками
    # это отношение один ко многим - одна модель и у нее несколько настроек (для разных ролей)
    setting = db.relationship("SettingAdmin", back_populates="model")

    # statuses = db.relationship("Status", back_populates="model_name")

    # Эта функция позволяет отразить в админке в частности не объект SQLalchemy (например <Role1>),
    # а имя (name_model)(например User)
    def __repr__(self):
        return self.name_model


# Модель Настройки CRUD админ. панели
class SettingAdmin(db.Model):
    __tablename__ = 'setting_admin'
    id = db.Column(db.Integer, primary_key=True)
    # name_setting = db.Column(db.String(80), unique = True, nullable=False, autoincrement=True)
    # name_setting = db.Column(db.String(80), unique = True, nullable=False)

    # Персональные настройки для определенной роли и определенной модели
    can_create = db.Column(db.Boolean)
    can_edit = db.Column(db.Boolean)
    can_delete = db.Column(db.Boolean)
    can_export = db.Column(db.Boolean)
    export_max_rows = db.Column(db.Integer)
    # Персональные настройки для определенной роли и определенной модели - конец

    # устанавливаем отношение между ролями и настройками
    # это отношение один ко многим - одна роль и у нее несколько настроек (для разных моделей)
    # Причем для создания настройки нужно обязательно выбрать и роль и модель.
    # Это задается с помощью nullable=False в role_id и model_id
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", back_populates="setting")

    # устанавливаем отношение между списком моделей и настройками
    # это отношение один ко многим - одна модель и у нее несколько настроек (для разных ролей)
    # Причем для создания настройки нужно обязательно выбрать и роль и модель.
    # Это задается с помощью nullable=False в role_id и model_id
    model_id = db.Column(db.Integer, db.ForeignKey("list_models.id"), nullable=False)
    model = db.relationship("ListModel", back_populates="setting")

    # Конструкция __table_args__ задает дополнительные свойства класса
    # В данном случае с помощью db.UniqueConstraint мы указываем, что в классе SettingAdmin
    # одной модели и одной роли соответствует единственная строка. Например:
    # роли - admin и модели - User соответствует единственная! строка настройки
    # роли - admin и модели - Menu соответствует другая единственная! строка
    # При этом собственно настройка (то есть разрешения, которые задаются другими столбцами)
    # может совпадать с другой настройкой

    __table_args__ = (db.UniqueConstraint('role_id', 'model_id', name='_role_model'),
                     )

    @hybrid_property
    def name_setting(self):
        name_setting = str(self.role)+ '_'+ str(self.model)
        return name_setting

    # Эта функция позволяет отразить в админке в частности не объект SQLalchemy (например <Role1>),
    # а значение name_setting (имя настройки в частности)
    def __repr__(self):
        return self.name_setting


# Модель Главное меню
class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    # Название раздела(меню) на русском
    title = db.Column(db.String, nullable=False, unique=True)
    # Путь в URL и одновременно название директории для загрузки файлов
    # (Этот параметр задается в роуте)
    link = db.Column(db.String, unique=True)

    # Комментарии к пункту меню
    comments_1 = db.Column(db.Text)
    comments_2 = db.Column(db.Text)
    comments_3 = db.Column(db.Text)
    comments_4 = db.Column(db.Text)

    # Связь с услугами
    # uslugs = db.relationship("Usluga", back_populates='punkt_menu', cascade="all,delete")
    # uslugs = db.relationship("Usluga", back_populates='punkt_menu', cascade=False)
    uslugs = db.relationship("Usluga", back_populates='punkt_menu')



    # Эта функция позволяет отразить в админке в частности не объект SQLalchemy (например <Link1>),
    # а имя(title) (например Полиграфия)
    def __repr__(self):
        return self.title


    # Создадим счетчик кол-ва услуг - начало!
    # Он нужен чтобы в админке не перечислять все услуги(их может быть много), а указать только их количество
    # https://translated.turbopages.org/proxy_u/en-ru.ru.a8edd97f-62d92535-0d2a131f-74722d776562/https/stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # В ссылке указаны 2 способа (один в модели(ответ), второй прямо в админке - оба работают!!!)
    # для этого способа нужны импорты
    # from sqlalchemy.ext.hybrid import hybrid_property
    # from sqlalchemy import select, func
    @hybrid_property
    def count_uslugs_in_model(self):
        return len(self.uslugs)

    @count_uslugs_in_model.expression
    def count_uslugs_in_model(cls):
        return select([func.len(Usluga.id)]).where(Usluga.punkt_menu_id == cls.id).label('count_uslugs_in_model')
    # Создадим счетчик кол-ва услуг - конец!
    

# Модель Список всех продуктов(услуг) (связан с главным меню Link)
class Usluga(db.Model):
    __tablename__ = 'uslugs'
    id = db.Column(db.Integer, primary_key=True)
    # Название услуги (На русском)
    title = db.Column(db.String, nullable=False, unique=True)
    # Путь в URL и одновременно название директории для загрузки файлов
    # (Надо запретить на кириллице создавать!!! на 25.10.21 не сделано это)
    link = db.Column(db.String, unique=True)

    # Комментарии к услуге
    comments_1 = db.Column(db.Text)
    comments_2 = db.Column(db.Text)
    comments_3 = db.Column(db.Text)
    comments_4 = db.Column(db.Text)

    # Связь с меню (разделами)
    punkt_menu_id = db.Column(db.Integer, db.ForeignKey('links.id'), nullable=False)
    punkt_menu = db.relationship("Link", back_populates='uslugs')

    cards_usluga = db.relationship("CardUsluga", back_populates='usluga')
    # cards_usluga = db.relationship("CardUsluga", back_populates='usluga', cascade="all,delete")
    # cards_usluga = db.relationship("CardUsluga", back_populates='usluga', cascade=False)


    # Создадим счетчик кол-ва карточек услуг - начало!
    # Он нужен чтобы в админке не перечислять все услуги(их может быть много), а указать только их количество
    # https://translated.turbopages.org/proxy_u/en-ru.ru.a8edd97f-62d92535-0d2a131f-74722d776562/https/stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # https://stackoverflow.com/questions/36203908/flask-admin-sort-on-one-to-many-counted-field
    # В ссылке указаны 2 способа (один в модели(ответ), второй прямо в админке - оба работают!!!)
    # для них нужны импорты
    # from sqlalchemy.ext.hybrid import hybrid_property
    # from sqlalchemy import select, func
    @hybrid_property
    def count_cards_uslugs_in_model(self):
        return int(len(self.cards_usluga))

    @count_cards_uslugs_in_model.expression
    def count_cards_uslugs_in_model(cls):
        return select([func.len(CardUsluga.id)]).where(CardUsluga.usluga_id == cls.id).label('count_cards_uslugs_in_model')
    # Создадим счетчик кол-ва карточек услуг - конец!


    def __repr__(self):
        return self.title

# Модель тип производства
# От типа производства будут зависеть промежуточные статусы карт.
# У разного типа производства они могут быть разные
# можно задать тип например Стандарт
# (и задать набор промежуточных статусов карт с этим типом производства)
# А в карточке услуг задать этот тип производства по умолчанию например.
class TypeProduction(db.Model):
    __tablename__ = 'types_productions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    cards_uslugs = db.relationship("CardUsluga", back_populates='type_production')
    statuses_intermediate = db.relationship("StatusIntermediate", back_populates='type_production')
    def __repr__(self):
        return self.name

# Модель Статусы карточек
# стандартный набор статусов, общий для всех карточек услуг
# вес задавать так - 0, 1000, 2000 (Пока так) Нужно для того, чтобы потом сортировать в соответствии с основными
# статусами? Складывать вес основного статуса и промежуточного для сортировки?
class StatusCard(db.Model):
    __tablename__ = 'statuses_card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    # вес статуса
    weight = db.Column(db.Integer, nullable=False)
    # описание статуса
    description = db.Column(db.String(), nullable=False)
    # какие промежуточные статусы соответствуют
    statuses_intermediate = db.relationship("StatusIntermediate", back_populates='status_card')
    specification = db.relationship("SpecificationStatusCard", back_populates='status_card')

    def __repr__(self):
        return self.name


# Модель Промежуточные статусы (зависят от статуса карт и типа производства)
# вес задавать так - 1-999 (Пока так) Нужно для того, чтобы потом сортировать в соответствии с основными статусами?
# Складывать вес основного статуса и промежуточного для сортировки?
class StatusIntermediate(db.Model):
    __tablename__ = 'statuses_intermediate'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    # вес статуса
    weight = db.Column(db.Integer, nullable=False)
    # описание статуса
    description = db.Column(db.String(), nullable=False)

    # основной статус карточки
    status_card_id = db.Column(db.Integer, db.ForeignKey('statuses_card.id'))
    status_card = db.relationship("StatusCard", back_populates='statuses_intermediate')

    # тип производства
    type_production_id = db.Column(db.Integer, db.ForeignKey('types_productions.id'))
    type_production = db.relationship('TypeProduction', back_populates="statuses_intermediate")

    specification_intermediate = db.relationship("SpecificationStatusIntermediate", back_populates='status_intermediate')

    def __repr__(self):
        return self.name


# Модель Карточка услуги
class CardUsluga(db.Model):
    __tablename__ = 'cards_uslugs'
    id = db.Column(db.Integer, primary_key=True)
    name_card_usluga = db.Column(db.String(255), nullable=False, unique=True) # Имя карточки услуги
    comments = db.Column(db.Text)
    dir_photos = db.Column(db.String(255), unique=True) # Директория размещения фото карточки услуги
    usluga_id = db.Column(db.Integer, db.ForeignKey('uslugs.id'), nullable=False)
    usluga = db.relationship("Usluga", back_populates='cards_usluga')
    photos = db.relationship("Photo", back_populates='card_usluga', cascade="all,delete")
    prices = db.relationship('PriceTable', back_populates="card_usluga")
    # statuses_card_usluga = db.relationship("StatusCardUsluga", back_populates='card_usluga', cascade="all,delete")
    arhive = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)

    # в каких заказах присутствует
    order_items = db.relationship("OrderItem", back_populates='card_usluga')

    # тип производства (для последующего определения промежуточных статусов)
    type_production_id=db.Column(db.Integer, db.ForeignKey('types_productions.id'))
    type_production=db.relationship('TypeProduction', back_populates="cards_uslugs")

    # роли и нормативы времени в зависимости от карты услуг и статуса карт
    specification = db.relationship("SpecificationStatusCard", back_populates='card_usluga', cascade="all, delete")

    # роли и нормативы времени в зависимости от карты услуг и промежуточного статуса карт
    specification_intermediate = db.relationship("SpecificationStatusIntermediate", back_populates='card_usluga', cascade="all, delete")

    def __repr__(self):
        return self.name_card_usluga + ' (id '+str(self.id)+')'


    # Создадим счетчик кол-ва фото в карточке услуги - начало!
    # Он нужен чтобы в админке не перечислять все фото(их может быть много), а указать только их количество
    # https://stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # https://stackoverflow.com/questions/36203908/flask-admin-sort-on-one-to-many-counted-field
    # В ссылке указаны 2 способа (один в модели(ответ), второй прямо в админке - оба работают!!!)
    # для них нужны импорты
    # from sqlalchemy.ext.hybrid import hybrid_property
    # from sqlalchemy import select, func
    @hybrid_property
    def count_photos_in_card_usluga(self):
        return len(self.photos)

    @count_photos_in_card_usluga.expression
    def count_photos_in_card_usluga(cls):
        return select([func.len(Photo.id)]).where(Photo.card_usluga_id == cls.id).label('count_photos_in_card_usluga')
        # return len(Photo.query.filter(Photo.card_usluga_id == cls.id).all())
    # Создадим счетчик кол-ва фото в карточке услуг - конец!


    # Создадим счетчик кол-ва прайсов в карточке услуги - начало!
    # Он нужен чтобы в админке не перечислять все прайсы(их может быть много), а указать только их количество
    # https://translated.turbopages.org/proxy_u/en-ru.ru.a8edd97f-62d92535-0d2a131f-74722d776562/https/stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # https://stackoverflow.com/questions/36203908/flask-admin-sort-on-one-to-many-counted-field
    # В ссылке указаны 2 способа (один в модели(ответ), второй прямо в админке - оба работают!!!)
    # для них нужны импорты
    # from sqlalchemy.ext.hybrid import hybrid_property
    # from sqlalchemy import select, func
    @hybrid_property
    def count_prices_in_card_usluga(self):
        return len(self.prices)

    @count_prices_in_card_usluga.expression
    def count_prices_in_card_usluga(cls):
        return select([func.len(PriceTable.id)]).where(PriceTable.card_usluga_id == cls.id).label('count_prices_in_card_usluga')
        # return len(Photo.query.filter(Photo.card_usluga_id == cls.id).all())
    # Создадим счетчик кол-ва прайсов в карточке услуг - конец!

    @hybrid_property
    def punkt_menu_card_usluga(self):
        return self.usluga.punkt_menu


# Модель Спецификация статусов карт (для карточек услуг)
# задает норматив времени и роль ответственного для уник.набора: карточка услуг-статус карточек
class SpecificationStatusCard(db.Model):
    __tablename__ = 'specifications_statuses_cards'
    id = db.Column(db.Integer, primary_key=True)

    card_usluga_id = db.Column(db.Integer, db.ForeignKey('cards_uslugs.id'), nullable=False)
    card_usluga = db.relationship("CardUsluga", back_populates='specification')

    status_card_id = db.Column(db.Integer, db.ForeignKey('statuses_card.id'), nullable=False)
    status_card = db.relationship("StatusCard", back_populates='specification')

#     # Конструкция __table_args__ задает дополнительные свойства класса
#     # В данном случае с помощью db.UniqueConstraint мы указываем, что в классе SpecificationStatusCard
#     # одной карточке услуги и одному статусу карт соответствует единственная строка.
#     # При этом остальные параметры могут совпадать

    __table_args__ = (db.UniqueConstraint('card_usluga_id', 'status_card_id',  name='_card_usluga_status'),
                     )

#     # роль, ответственная (responsible) за этап работы (статус)
    role_responsible_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role_responsible = db.relationship("Role")

#   Норматив времени на статус
    days_norma = db.Column(db.Integer, default=0)
    hours_norma = db.Column(db.Integer, default=0)
    minutes_norma = db.Column(db.Integer, default=0)

    # Данные (@hybrid_property) в админке показывает но не могу задать сортировку
    # column_sortable_list - дает ошибку, поэтому в админке этот столбец в сортирвку не включила
    # https://stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # В ссылке указаны 2 способа (один в модели(см. ответ), второй  в админке - оба работают!!!)
    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html#correlated-subquery-relationship-hybrid

    # Пыталась добавить к @hybrid_property def standard(self): (после)  @standard.expression
    # чтобы добиться возможности сортировки в flask-admin но ничего не получилось.
    # Разбираться!!
    # @normativ.expression
    # def normativ(cls):
    #     return func.str(cls.days_norma)+' дн. '+ str(cls.hours_norma)+' ч. '+str(cls.minutes_norma) + ' мин.'

    @hybrid_property
    def normativ(self):
        return str(self.days_norma)+' дн. '+ str(self.hours_norma)+' ч. '+str(self.minutes_norma) + ' мин.'

    def __repr__(self):
        # return 'Статус - ' + str(self.status)+' (карточка услуги '+ str(self. card_usluga)+')'
        return str(self.status_card)


# Модель Спецификация промежуточных статусов карт для карточек услуг
# задает временной норматив и роль ответственного
# для уникального набора: карточка услуг-промежуточный статус карточек
class SpecificationStatusIntermediate(db.Model):
    __tablename__ = 'specifications_statuses_intermediate'
    id = db.Column(db.Integer, primary_key=True)

    card_usluga_id = db.Column(db.Integer, db.ForeignKey('cards_uslugs.id'), nullable=False)
    card_usluga = db.relationship("CardUsluga", back_populates='specification_intermediate')

    status_intermediate_id = db.Column(db.Integer, db.ForeignKey('statuses_intermediate.id'), nullable=False)
    status_intermediate = db.relationship("StatusIntermediate", back_populates='specification_intermediate')

#     # Конструкция __table_args__ задает дополнительные свойства класса
#     # В данном случае с помощью db.UniqueConstraint мы указываем, что в классе SpecificationStatusIntermediate
#     # одной карточке услуги и одному статусу карт соответствует единственная строка.
#     # При этом остальные параметры могут совпадать

    __table_args__ = (db.UniqueConstraint('card_usluga_id', 'status_intermediate_id',  name='_card_usluga_status_intermediate'),
                     )

#     # роль, ответственная (responsible) за этап работы (статус)
    role_responsible_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role_responsible = db.relationship("Role")

#   Норматив времени на статус
    days_norma = db.Column(db.Integer, default=0)
    hours_norma = db.Column(db.Integer, default=0)
    minutes_norma = db.Column(db.Integer, default=0)

    # Данные (@hybrid_property) в админке показывает но не могу задать сортировку
    # column_sortable_list - дает ошибку, поэтому в админке этот столбец в сортирвку не включила
    # https://stackoverflow.com/questions/39895123/custom-and-sortable-column-in-flask-admin
    # В ссылке указаны 2 способа (один в модели(см. ответ), второй  в админке - оба работают!!!)
    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html#correlated-subquery-relationship-hybrid

    # Пыталась добавить к @hybrid_property def standard(self): (после)  @standard.expression
    # чтобы добиться возможности сортировки в flask-admin но ничего не получилось.
    # Разбираться!!
    # @normativ.expression
    # def normativ(cls):
    #     return func.str(cls.days_norma)+' дн. '+ str(cls.hours_norma)+' ч. '+str(cls.minutes_norma) + ' мин.'


    @hybrid_property
    def normativ(self):
        return str(self.days_norma)+' дн. '+ str(self.hours_norma)+' ч. '+str(self.minutes_norma) + ' мин.'

    def __repr__(self):
        # return 'Статус - ' + str(self.status)+' (карточка услуги '+ str(self. card_usluga)+')'
        return str(self.status_card)

# Модель Действия персонала (например позвонить, написать,)
class StaffAction(db.Model):
    __tablename__ = 'staff_actions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def __repr__(self):
        return str(self.name)

# Модель Цель действия (например согласовать макет, уточнить данные)
class GoalAction(db.Model):
    __tablename__ = 'goals_actions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def __repr__(self):
        return str(self.name)

# Модель Метод действия (например письмо, встреча, звонок)
class MethodAction(db.Model):
    __tablename__ = 'methods_actions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def __repr__(self):
        return str(self.name)

# Модель Результат действия (например макет согласован, данные уточнены)
class ResultAction(db.Model):
    __tablename__ = 'results_actions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def __repr__(self):
        return str(self.name)


# Модель Заказы
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    # номер заказа
    number = db.Column(db.String, nullable=False, unique=True)

    # Дата и время создания заказа
    # order_create = db.Column(db.DateTime(), default=datetime.now.replace(microsecond=0))
    # order_create = db.Column(db.DateTime(), default=str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)))
    # order_create = db.Column(db.DateTime(microsecond=0), default=datetime.now )
    date_create = db.Column(db.DateTime(), default=datetime.now )

    # Дата и время полного выполнения заказа (всех позиций заказа)
    date_end = db.Column(db.DateTime())

    # Роль менеджера заказа (ответственный за весь заказ (назначает ответственных?))
    manager_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    manager_role = db.relationship("Role", back_populates='orders')

    # 2 связи в модели к одной таблице User без foreign_keys="[Order.manager_person_id]" и [Order.user_id] дают ошибку!!!
    # https: // docs.sqlalchemy.org / en / 14 / orm / join_conditions.html
    # https: //translated.turbopages.org/proxy_u/en-ru.ru.b9952bcd-636b3a4a-a31a33bd-74722d776562/https/stackoverflow.com/questions/7548033/how-to-define-two-relationships-to-the-same-table-in-sqlalchemy

    # Ответственный за заказ (персона)
    # Персону планируем выбирать из списка юзеров с ролью manager_role, которую определяем ранее
    manager_person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    manager_person = db.relationship("User", foreign_keys="[Order.manager_person_id]")

    # заказчик услуг (покупатель)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User",  foreign_keys="[Order.user_id]")

    # Прогресс выполнения заказа - это статусы заказа(из статусов карточки услуги)
    # с фактическим временем исполнения
    # Сделать отдельную таблицу!
    # progress = db.Column(JSON)

    progresses = db.relationship("ProgressOrder", back_populates='order', cascade="all, delete")

    order_actions = db.relationship("ActionOrder", back_populates='order', cascade="all, delete")

    # Элементы заказа
    # order_items = db.relationship("OrderItem", back_populates='order', cascade="all,delete")
    order_items = db.relationship("OrderItem", back_populates='order', cascade="all, delete")

    # данные заказа поступившие по ссылке в прайсе карточки услуги с сайта
    # прайсы и параметры карточки услуг могут меняться, поэтому в заказе нужно зафиксировать данные,
    # на момент когда пользователь подтверждает заказ на сайте
    # order_parameters = db.Column(JSON)

    def __repr__(self):
        return '№ ' + self.number


# Модель Элементы заказа
# Содержит параметры по каждой заказанной услуге
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)

    # К какому заказу относится
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship("Order", back_populates='order_items')

    card_usluga_id = db.Column(db.Integer, db.ForeignKey('cards_uslugs.id'))
    card_usluga = db.relationship("CardUsluga", back_populates='order_items')

    price_id = db.Column(db.Integer, db.ForeignKey('price_tables.id'))
    price = db.relationship("PriceTable", back_populates='order_items')

    gorizontal_position_price_i = db.Column(db.Integer)
    vertical_position_price_j = db.Column(db.Integer)

    # Если карточка услуг и прайс не в архиве и активны на момент заказа True
    # (иначе нельзя заказать), после заказа если предложение стало не актуально
    # (или архив или не активно) - False
    actual_offer = db.Column(db.Boolean, default=True)

    # Актуальный статус элемента заказа
    # actual_status_id = db.Column(db.Integer, db.ForeignKey('statuses_cards_uslugs.id'))
    # actual_status = db.relationship("StatusCardUsluga", back_populates='order_item')

    date_create_actual_status = db.Column(db.DateTime())

    # Ответственный за актуальнй статус
    staff_actual_status_person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    staff_actual_status_person = db.relationship("User", back_populates='orders_items')

    # Прогресс выполнения элемента заказа (статус, ответственный - роль,
    # ответственный - персона, дата создания, дата окончания, отклонение от норматива)
    # progress = db.Column(JSON)

    # Прогресс выполнения элемента заказа - это статусы карт из элементов заказа(из статусов карт)
    # с фактическим временем исполнения

    progresses = db.relationship("ProgressOrderItem", back_populates='order_item')

    def __repr__(self):
        return 'id '+str(self.id)


# # Модель Статусы заказов
# Общий набор статусов для всех заказов
class StatusOrder(db.Model):
    __tablename__ = 'statuses_orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    weight = db.Column(db.Integer, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return str(self.name)


# Модель Прогресс Заказа
class ProgressOrder(db.Model):
    __tablename__ = 'progresses_orders'
    id = db.Column(db.Integer, primary_key=True)

    # Заказ
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship("Order", back_populates='progresses')

    # Статус заказа (на каком этапе заказа совершены действия)
    status_order_id = db.Column(db.Integer, db.ForeignKey('statuses_orders.id'))
    status_order = db.relationship("StatusOrder")

    # Дата и время создания перехода на другой статус
    date_create = db.Column(db.DateTime(), default=datetime.now)

    # Дата и время окончания статуса
    date_end = db.Column(db.DateTime())

    def __repr__(self):
        return str(self.date_create)+' - ' +str(self.status_order)


# Модель Прогресс Элементов Заказа
class ProgressOrderItem(db.Model):
    __tablename__ = 'progresses_orders_items'
    id = db.Column(db.Integer, primary_key=True)

    # Элементы заказа
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'))
    order_item = db.relationship("OrderItem", back_populates='progresses')

    # Статус карты (на каком этапе заказа совершены действия)
    status_card_id = db.Column(db.Integer, db.ForeignKey('statuses_card.id'))
    status_card = db.relationship("StatusCard")

    intermediate_progresses = db.relationship("ProgressOrderItemIntermediate", back_populates='progress')

    # Дата и время создания статуса
    date_create = db.Column(db.DateTime(), default=datetime.now)

    # Дата и время окончания статуса
    date_end = db.Column(db.DateTime())

    def __repr__(self):
        return str(self.date_create)+' - ' +str(self.status_card)


# Модель Промежуточный Прогресс Элементов Заказа
class ProgressOrderItemIntermediate(db.Model):
    __tablename__ = 'progresses_orders_items_intermediates'
    id = db.Column(db.Integer, primary_key=True)

    # Прогресс по карте элемента заказа
    progress_id = db.Column(db.Integer, db.ForeignKey('progresses_orders_items.id'))
    progress = db.relationship("ProgressOrderItem", back_populates='intermediate_progresses')

    # Статус промежуточный
    status_intermediate_id = db.Column(db.Integer, db.ForeignKey('statuses_intermediate.id'))
    status_intermediate = db.relationship("StatusIntermediate")

    # Дата и время создания статуса
    date_create = db.Column(db.DateTime(), default=datetime.now)

    # Дата и время окончания статуса
    date_end = db.Column(db.DateTime())

    def __repr__(self):
        return str(self.date_create)+' - ' +str(self.status_card)


# Модель Действия персонала по заказу
class ActionOrder(db.Model):
    __tablename__ = 'actions_orders'
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String, nullable=False, unique=True)

    # Заказ
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship("Order", back_populates='order_actions')

    # Статус заказа (на каком этапе заказа совершены действия)
    status_order_id = db.Column(db.Integer, db.ForeignKey('statuses_orders.id'))
    status_order = db.relationship("StatusOrder")
    # Дата и время создания действия
    date_create = db.Column(db.DateTime(), default=datetime.now)

    # Действие
    staff_action_id = db.Column(db.Integer, db.ForeignKey('staff_actions.id'))
    staff_action = db.relationship("StaffAction")

    # Цель действия
    goal_action_id = db.Column(db.Integer, db.ForeignKey('goals_actions.id'))
    goal_action = db.relationship("GoalAction")

    # Метод действия
    method_action_id = db.Column(db.Integer, db.ForeignKey('methods_actions.id'))
    method_action = db.relationship("MethodAction")

    # Результат действия
    result_action_id = db.Column(db.Integer, db.ForeignKey('results_actions.id'))
    result_action = db.relationship("ResultAction")

    def __repr__(self):
        return str(self.date_create)+' Действие: '+str(self.staff_action)+' Результат: '+str(self.result_action)

# Модель Действия персонала по элементу заказа
class ActionOrderItem(db.Model):
    __tablename__ = 'actions_orders_items'
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String, nullable=False, unique=True)

    # Элемент заказа
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'))
    order_item = db.relationship("OrderItem")

    # Статус карты (на каком этапе совершены действия)
    status_card_id = db.Column(db.Integer, db.ForeignKey('statuses_card.id'))
    status_card = db.relationship("StatusCard")

    # Дата и время создания действия
    date_create = db.Column(db.DateTime(), default=datetime.now)

    # Действие
    staff_action_id = db.Column(db.Integer, db.ForeignKey('staff_actions.id'))
    staff_action = db.relationship("StaffAction")

    # Цель действия
    goal_action_id = db.Column(db.Integer, db.ForeignKey('goals_actions.id'))
    goal_action = db.relationship("GoalAction")

    # Метод действия
    method_action_id = db.Column(db.Integer, db.ForeignKey('methods_actions.id'))
    method_action = db.relationship("MethodAction")

    # Результат действия
    result_action_id = db.Column(db.Integer, db.ForeignKey('results_actions.id'))
    result_action = db.relationship("ResultAction")


# Модель Фото
class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)

    card_usluga_id = db.Column(db.Integer, db.ForeignKey('cards_uslugs.id'))
    card_usluga = db.relationship("CardUsluga", back_populates='photos')

    # Полная Директория для загрузки (общая директория загрузки + дир. раздела + дир услуги)
    dir_uploads = db.Column(db.String(255), nullable=False, default='/static/images/cards_uslugs/')

    # Исходное имя загружаемого файла
    origin_name_photo = db.Column(db.String(255), nullable=False)

    # Безопасное имя загружаемого файла
    secure_name_photo = db.Column(db.String(255), nullable=False)

    # Расширение файла
    file_ext = db.Column(db.String(255), nullable=False)

    # Размер файла
    file_size = db.Column(db.Integer)

    # Заголовок фото
    title = db.Column(db.String(255))

    # Сопроводительный текст к фото
    comments = db.Column(db.Text)

    arhive = db.Column(db.Boolean, default=False)

    @hybrid_property
    def photo_card_usluga_usluga(self):
        return self.card_usluga.usluga

    @hybrid_property
    def photo_card_usluga_usluga_punkt_menu(self):
        return self.card_usluga.usluga.punkt_menu


# Модель Телефоны пользователей (User)
# у 1 пользователя может быть несколько тел., у тел. только 1 пользователь
class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates='phones')

    def __repr__(self):
        return str(self.phone)



# Модель для определения РАЗМЕРА элемента - начало
# class SizeElement(db.Model):
#     __tablename__ = 'size_elements'
#     id = db.Column(db.Integer, primary_key=True)
#     # comment_size_element = db.Column(db.String())
#
#     # places = db.relationship("PlaceElement", back_populates="size_element")
#
#     # width_element = db.relationship("WidthElement", back_populates="size_element")
#     width_element = db.relationship("WidthElement")
#     width_element_id = db.Column(db.Integer, db.ForeignKey("width_elements.id"))
#
#     # height_element = db.relationship("HeightElement", back_populates="size_element")
#     height_element = db.relationship("HeightElement")
#     height_element_id = db.Column(db.Integer, db.ForeignKey("height_elements.id"))
#
#     __table_args__ = (db.UniqueConstraint('width_element_id', 'height_element_id', name='_width_height'),
#                      )
#
#     @hybrid_property
#     def name_size_element(self):
#         name_size_element = str(self.width_element)+'x'+ str(self.height_element)
#         return name_size_element
#
#     @hybrid_property
#     def comment_size_element(self):
#         comment_size_element = 'Ширина: '+str(self.width_element.width_element)+\
#                                '. Высота: '+str(self.height_element.height_element)
#         return comment_size_element
#
#
#     def __repr__(self):
#         return self.name_size_element
# Модель для определения РАЗМЕРА  элемента - конец