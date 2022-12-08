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

from pathlib import Path
import re
from transliterate import translit

# Импорт, необходимый для создания уникального имени загружаемого файла по времени загрузки
import datetime
from datetime import datetime, timedelta
import time


# Импорт, необходимый для перехвата предупреждений при задании form_edit_rules
import warnings


from RECL.models import db
# from RECL.models import UploadFileMy, Usluga, Link, Order, User, Role, roles_users, ListModel, \
#     SettingAdmin, UploadFileMy, PriceTable, Carousel, PlaceElement, BaseLocationElement, \
#     BasePositionElement, PositionElement, PlaceCarousel, PlaceModelElement
from RECL.models import *


# from RECL.__init__ import app

from RECL.components.card_usluga.forms import CreateCardUslugaForm, UploadFoto, EditFormPhotoCards,\
    EditFormNameTextCards, Specification
# from RECL.components.fotomanager.forms import  DeleteForm, FormChoice1, PhotoFormAdmin, FormChoice2, DeleteFormFromMini,
# from RECL.components.fotomanager.forms import EditFormFromMini

import os

# Модуль shutil используем для удаления папки с со всеми файлами
 # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
import shutil

from flask_security import login_required, roles_required, roles_accepted
from sqlalchemy.dialects.postgresql import JSON

# импорты для загрузки файлов - начало
# from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from sqlalchemy.dialects.postgresql import JSON
# импорты для загрузки файлов - конец

card_usluga_blueprint = Blueprint('card_usluga_bp', __name__, template_folder='templates/card_usluga/', static_folder='static')


# Удалить спецификацию промежуточного статуса карточки услуг
@card_usluga_blueprint.route('/edit_intermediate_specification/<int:card_usluga_id>/<int:status_card_id>/<int'
                             ':specification_id>/', methods=['GET',
                                                                                                          'POST'])
def edit_intermediate_specification(card_usluga_id, specification_id, status_card_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    specification = SpecificationStatusIntermediate.query.filter(SpecificationStatusIntermediate.id==specification_id).first()
    print('specification =', specification )
    status_card = StatusCard.query.filter(StatusCard.id == status_card_id).first()
    form = Specification()
    form.role.choices = [(role.id, role.name) for role in Role.query.order_by('name').all()]
    if form.validate_on_submit():
        days = form.days.data
        hours = form.hours.data
        minutes = form.minutes.data
        role = form.role.data
        specification.role_responsible_id = role
        specification.days_norma = days
        specification.hours_norma = hours
        specification.minutes_norma = minutes
        db.session.commit()
        return redirect(url_for('card_usluga_bp.intermediate_specifications', card_usluga_id=card_usluga.id, status_card_id=status_card_id))
    return render_template ('edit_intermediate_specification.html',
                            card_usluga=card_usluga,
                            status_card=status_card,
                            specification=specification,
                            form=form
                            )


# Удалить спецификацию промежуточного статуса карточки услуг
@card_usluga_blueprint.route('/delete_intermediate_specification/<int:card_usluga_id>/<int:status_card_id>/<int:specification_id>/', methods=['GET',
                                                                                                          'POST'])
def delete_intermediate_specification(card_usluga_id, specification_id, status_card_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    specification = SpecificationStatusIntermediate.query.filter(SpecificationStatusIntermediate.id==specification_id).first()
    print('specification =', specification )
    db.session.delete(specification)
    db.session.commit()
    return redirect(url_for('card_usluga_bp.intermediate_specifications',
                            card_usluga_id=card_usluga.id,
                            status_card_id=status_card_id)
                    )



# Создать спецификацию промежуточного статуса карточки услуг
@card_usluga_blueprint.route('/create_intermediate_specification/<int:card_usluga_id>/<int:status_card_id>/<int:intermediate_status_id>/', methods=['GET',
                                                                                                          'POST'])
def create_intermediate_specification(card_usluga_id, status_card_id, intermediate_status_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    status_card=StatusCard.query.filter(StatusCard.id == status_card_id).first()
    print('card_usluga_id=', card_usluga_id)
    print('status_card_id=', status_card_id)
    intermediate_status=StatusIntermediate.query.filter(StatusIntermediate.id == intermediate_status_id).first()

    print('intermediate_status_id=', intermediate_status_id)
    form = Specification()
    form.role.choices = [(role.id, role.name) for role in Role.query.order_by('name').all()]
    if form.validate_on_submit():
        days=form.days.data
        hours = form.hours.data
        minutes = form.minutes.data
        role = form.role.data
        specification=SpecificationStatusIntermediate(role_responsible_id=role,
                                              days_norma=days,
                                              hours_norma = hours,
                                              minutes_norma = minutes,
                                              card_usluga_id = card_usluga_id,
                                              status_intermediate_id = intermediate_status_id)
        db.session.add(specification)
        db.session.commit()
        return redirect(url_for('card_usluga_bp.intermediate_specifications', card_usluga_id=card_usluga.id,
                                status_card_id=status_card.id))
    return render_template ('create_intermediate_specification.html',
                             card_usluga=card_usluga,
                            form=form,
                            status_card=status_card,
                            intermediate_status=intermediate_status
                            )



# Задать нормативы (спецификацию) промежуточных статусов
@card_usluga_blueprint.route('/intermediate_specifications/<int:card_usluga_id>/<int:status_card_id>/', methods=['GET', 'POST'])
def intermediate_specifications(card_usluga_id, status_card_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    status_card = StatusCard.query.filter(StatusCard.id == status_card_id).first()

    # спецификация статуса карты
    specification_status_card=SpecificationStatusCard.query.filter(
        SpecificationStatusCard.status_card_id==status_card_id,
        SpecificationStatusCard.card_usluga_id==card_usluga_id).first()

    # норматив статуса в минутах
    normativ=specification_status_card.days_norma * 24 * 60  + specification_status_card.hours_norma * 60 + \
             specification_status_card.minutes_norma

    # Все заданные для карты услуг и выбранного статуса спецификации
    # Сначала ищем те спецификации, которые относятся к данной карточке услуги (filter(...))
    # Затем ДЛЯ СОРТИРОВКИ В ОТНОШЕНИИ списка спецификаций по весу статуса карточки услуг применяем
    # join(SpecificationStatusCard.status_card),
    # а затем указываем сам параметр сортировкм order_by(StatusCard.weight)
    # https://translated.turbopages.org/proxy_u/en-ru.ru.27541e0a - 6389be38-6e5ba418-74722d776562/https/stackoverflow.com/questions/9861990/sqlalchemy-how-to-order-query-results-\order-by-on-a-relationships-field)
    # Пыталась сделать сортировку в отношении с помощью добавления в модель order_by="StatusCard.weight",
    # но почему-то не получилось (пробовала в обе модели добавлять)
    # https://translated.turbopages.org/proxy_u/en-ru.ru.84ff8891-6389c048-e89c4e38-74722d776562/https/stackoverflow.com/questions/49042895/order-by-a-related-table-with-flask-sqlalchemy

    specifications = SpecificationStatusIntermediate.query.join(
        SpecificationStatusIntermediate.status_intermediate).filter(
        SpecificationStatusIntermediate.card_usluga_id == card_usluga_id,
        StatusIntermediate.status_card_id==status_card.id).all()

    # Общее время всех промежуточных спецификаций в минутах
    time_intermediate_specifications=0
    for specification in specifications:
        time_intermediate_specifications +=specification.days_norma*24*60\
                                             +specification.hours_norma*60+specification.minutes_norma


    message1, message2, message3 = '', '', ''

    # Сравним общее время промежуточных спецификаций статуса и нормативом статуса
    if time_intermediate_specifications>normativ:
        message1 = 'Нормативы заданы не верно!'
        message2 = 'Суммарное время нормативов промежуточных статусов не должно превышать норматива статуса!'
        message3 = 'Исправьте значение промежуточных нормативов либо измените норматив основного статуса!'

    # Переведем в дни, часы, минуты и отформатируем результат для передачи на страницу
    days = time_intermediate_specifications // (24 * 60)
    hours = time_intermediate_specifications % (24 * 60) // 60
    minutes = time_intermediate_specifications % 60
    time_intermediate_specifications_format = ("{} дн. {} ч. {} мин.".format(days, hours, minutes))


    # Все промежуточные статусы карт для данного типа производства и для данного статуса
    intermediate_statuses = StatusIntermediate.query.filter(
        StatusIntermediate.type_production_id==card_usluga.type_production_id,
        StatusIntermediate.status_card_id==status_card_id).order_by(
        StatusIntermediate.weight).all()

    # Не заданные статусы карт
    # Удалим те статусы карт из списка статусов у которых есть спецификация для данной карты
    # те создадим список из тех статусов, которые нужно задать
    for specification in specifications:
        if specification.status_intermediate in intermediate_statuses:
            intermediate_statuses.remove(specification.status_intermediate)

    return render_template ('intermediate_specifications.html',
                             card_usluga=card_usluga,
                            status_card=status_card,
                            intermediate_statuses=intermediate_statuses,
                            specifications=specifications,
                            specification_status_card=specification_status_card,
                            message1=message1,
                            message2=message2,
                            message3=message3,
                            time_intermediate_specifications_format=time_intermediate_specifications_format
                            )




# Удалить спецификацию статуса карточки услуг
@card_usluga_blueprint.route('/delete_specification/<int:card_usluga_id>/<int:specification_id>/', methods=['GET',
                                                                                                          'POST'])
def delete_specification(card_usluga_id, specification_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    specification = SpecificationStatusCard.query.filter(SpecificationStatusCard.id==specification_id).first()
    db.session.delete(specification)
    db.session.commit()
    return redirect(url_for('card_usluga_bp.specifications',
                            card_usluga_id=card_usluga.id))


# Создать спецификацию статуса карточки услуг
@card_usluga_blueprint.route('/create_specification/<int:card_usluga_id>/<int:status_card_id>/', methods=['GET',
                                                                                                          'POST'])
def create_specification(card_usluga_id, status_card_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id == card_usluga_id).first()
    status_card=StatusCard.query.filter(StatusCard.id == status_card_id).first()
    form = Specification()
    form.role.choices = [(role.id, role.name) for role in Role.query.order_by('name').all()]
    if form.validate_on_submit():
        days=form.days.data
        hours = form.hours.data
        minutes = form.minutes.data
        role = form.role.data
        specification=SpecificationStatusCard(role_responsible_id=role,
                                              days_norma=days,
                                              hours_norma = hours,
                                              minutes_norma = minutes,
                                              card_usluga_id = card_usluga_id,
                                              status_card_id = status_card_id)
        db.session.add(specification)
        db.session.commit()
        return redirect(url_for('card_usluga_bp.specifications', card_usluga_id=card_usluga.id))
    return render_template ('create_specification.html',
                             card_usluga=card_usluga,
                            form=form,
                            status_card=status_card
                            )


# Редактировать спецификацию статуса карточки услуг
@card_usluga_blueprint.route('/edit_specification/<int:card_usluga_id>/<int:specification_id>/', methods=['GET',
                                                                                                          'POST'])
def edit_specification(card_usluga_id, specification_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    print('card_usluga_id=', card_usluga_id)
    print('card_usluga=', card_usluga)
    specification = SpecificationStatusCard.query.filter(SpecificationStatusCard.id==specification_id).first()
    print('specification=', specification)
    form = Specification()
    form.role.choices = [(role.id, role.name) for role in Role.query.order_by('name').all()]
    if form.validate_on_submit():
        days=form.days.data
        hours = form.hours.data
        minutes = form.minutes.data
        role = form.role.data
        specification.role_responsible_id=role
        specification.days_norma=days
        specification.hours_norma = hours
        specification.minutes_norma = minutes
        db.session.commit()
        return redirect(url_for('card_usluga_bp.specifications', card_usluga_id=card_usluga.id))
    return render_template ('edit_specification.html',
                             card_usluga=card_usluga,
                            form=form,
                            specification=specification
                            )


# Задать нормативы (спецификацию) карточке услуг
@card_usluga_blueprint.route('/specifications/<int:card_usluga_id>/', methods=['GET', 'POST'])
def specifications(card_usluga_id):
    card_usluga = CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()

    # Все заданные для карты услуг спецификации
    # Сначала ищем те спецификации, которые относятся к данной карточке услуги (filter(...))
    # Затем ДЛЯ СОРТИРОВКИ В ОТНОШЕНИИ списка спецификаций по весу статуса карточки услуг применяем
    # join(SpecificationStatusCard.status_card),
    # а затем указываем сам параметр сортировкм order_by(StatusCard.weight)
    # https://translated.turbopages.org/proxy_u/en-ru.ru.27541e0a - 6389be38-6e5ba418-74722d776562/https/stackoverflow.com/questions/9861990/sqlalchemy-how-to-order-query-results-\order-by-on-a-relationships-field)
    # Пыталась сделать сортировку в отношении с помощью добавления в модель order_by="StatusCard.weight",
    # но почему-то не получилось (пробовала в обе модели добавлять)
    # https://translated.turbopages.org/proxy_u/en-ru.ru.84ff8891-6389c048-e89c4e38-74722d776562/https/stackoverflow.com/questions/49042895/order-by-a-related-table-with-flask-sqlalchemy
    specifications = SpecificationStatusCard.query.filter(
            SpecificationStatusCard.card_usluga_id==card_usluga_id).join(
        SpecificationStatusCard.status_card).order_by(StatusCard.weight).all()

    time_specifications = 0
    for specification in specifications:
        time_specifications = time_specifications + specification.days_norma *24 * 60  \
                                            + specification.hours_norma * 60 + specification.minutes_norma
        print('time_specifications=', time_specifications)

    days = time_specifications // (24 * 60)
    print('days=', days)
    hours = time_specifications % (24*60) // 60
    print('hours=', hours)
    minutes = time_specifications % 60
    print('minutes=', minutes)
    time_specifications_format=("{} дн. {} ч. {} мин.".format(days, hours, minutes))


    # Все статусы карт
    statuses_cards = StatusCard.query.order_by(StatusCard.weight).all()

    # Не заданные статусы карт
    # Удалим те статусы карт из списка статусов у которых есть спецификация для данной карты
    # те создадим список из тех статусов, которые нужно задать
    for specification in specifications:
        if specification.status_card in statuses_cards:
            statuses_cards.remove(specification.status_card)

    return render_template('specifications.html',
                             card_usluga=card_usluga,
                            statuses_cards=statuses_cards,
                            specifications=specifications,
                           time_specifications_format=time_specifications_format
                            )



# Деактивировать прайс в карточке услуг
@card_usluga_blueprint.route('/deactiveprice/<int:card_usluga_id>/<int:price_id>/', methods=['GET', 'POST'])
def deactive_price_in_card_usluga(card_usluga_id, price_id):
    price=PriceTable.query.filter_by(id=price_id).first()
    price.active=False
    db.session.commit()
    return redirect (url_for('card_usluga_bp.edit_card_usluga',
                             card_usluga_id=card_usluga_id))


# Активировать прайс в карточке услуг
@card_usluga_blueprint.route('/activeprice/<int:card_usluga_id>/<int:price_id>/', methods=['GET', 'POST'])
def active_price_in_card_usluga(card_usluga_id, price_id):
    price=PriceTable.query.filter_by(id=price_id).first()
    price.active=True
    db.session.commit()
    return redirect (url_for('card_usluga_bp.edit_card_usluga',
                             card_usluga_id=card_usluga_id))


# *** Редактирование заголовка и сопроводительного текста карточки услуг - начало
@card_usluga_blueprint.route('/edit_name_and_text_card/<int:card_usluga_id>/', methods=["GET", "POST"])
def edit_name_and_text_card(card_usluga_id ):
    form = EditFormNameTextCards()
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()

    # print('card_usluga=', card_usluga)
    # print('form.validate_on_submit()=', form.validate_on_submit())

    # # Если запрос POST и форма валидна
    if form.validate_on_submit():

        # Принимаем данные
        name_card_usluga = form.name_card_usluga.data
        comments = form.comments.data

        # Удалим лишние пробелы если есть
        # https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-split/
        # https://tonais.ru/string/zamena-neskolkih-probelov-odnim-python
        name_card_usluga = " ".join(name_card_usluga.split())

        # Сделаем первую заглавную букву в имени карточки услуг
        name_card_usluga=name_card_usluga[0].capitalize()+name_card_usluga[1:]


        # Вносим изменения в данную запись
        card_usluga.name_card_usluga = name_card_usluga
        card_usluga.comments = comments
        # Добавляем в сессии
        db.session.add(card_usluga)
        # Вносим изменения в базу
        db.session.commit()
        # Возвращаемся на страницу с миниатюрами
        return redirect (url_for('card_usluga_bp.edit_card_usluga', card_usluga_id=card_usluga_id))

    return render_template('edit_name_and_text_card.html',
                           form=form,
                           card_usluga=card_usluga
                           )
# ******* Редактирование заголовка и сопроводительного текста карточки услуг - конец


# *** Отправить в архив карточку услуг - начало
# Карточка отправляется в архив вместе с прайсами и фото
@card_usluga_blueprint.route('/send_to_archive_card_usluga/<int:card_usluga_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def send_to_archive_card_usluga(card_usluga_id):
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    card_usluga.arhive=True
    card_usluga.active=False
    if card_usluga.prices:
        for price in card_usluga.prices:
            price.active=False
            price.arhive=True
    if card_usluga.photos:
        for photo in card_usluga.photos:
            photo.arhive=True
    db.session.commit()
    return redirect(url_for('card_usluga_bp.show_cards_uslugs'))
# *** Отправить в архив карточку услу - конец


# *** Активировать карточку услуг - начало
@card_usluga_blueprint.route('/active_card_usluga/<int:card_usluga_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def active_card_usluga(card_usluga_id):
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    card_usluga.active=True
    db.session.commit()
    return redirect(url_for('card_usluga_bp.edit_card_usluga', card_usluga_id=card_usluga.id))
# *** Активировать карточку услуг - конец


# *** Деактивировать карточку услуг - начало
@card_usluga_blueprint.route('/deactive_card_usluga/<int:card_usluga_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def deactive_card_usluga(card_usluga_id):
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    card_usluga.active=False
    db.session.commit()
    return redirect(url_for('card_usluga_bp.edit_card_usluga', card_usluga_id=card_usluga.id))
# *** Деактивировать карточку услуг - конец


# *** Удалить карточку услуг - начало
# Фактическое удаление. Но впоследствии после написания модуля заказов с хранением в базе
# нужно организовать проверку что карточка не находится в заказах
# (и корзинах? в корзинах как проверить?), - никак - удалять
# Удаляется карточка и запись в базе,  сами фото из файловой системы и записи в базе фото
# прайс не удаляется остается в архиве
@card_usluga_blueprint.route('/delete_card_usluga/<int:card_usluga_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def delete_card_usluga(card_usluga_id):

    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()

    # **** удаляем заказы с этой карточкой услуг из корзин пользователей - начало
    # Для этого формируем новый список корзин,
    # в который не включены заказы с удаленным прайсом
    carts_users = session.get('carts_users', [])
    carts_users_new = []
    # print('session.get("carts_users"), [])- 1 = ', session.get('carts_users', []))
    # Перебираем список корзин разных пользователей
    for cart_user in carts_users:
        # Создадим новый словарь конкретного пользователя (включающий id и корзину cart - это список)
        cart_user_new = {}
        cart_user_new['user_id'] = cart_user['user_id']
        cart_user_new['cart'] = []
        # Перебираем корзину конкретного пользователя
        for order_request in cart_user['cart']:
            # Если в корзине есть заказ с удаляемым прайсом то не включаем его в
            # список заказов пользователя (новую корзину)
            # Если в заказе другой прайс (не тот который удаляем) - добавляем
            # в новую корзину пользователя
            if order_request['card_usluga_id'] != card_usluga.id:
                cart_user_new['cart'].append(order_request)
                # print('cart_user_new"= ', cart_user_new, '"carts_users"= ', carts_users)

        if cart_user_new['cart'] != []:
            carts_users_new.append(cart_user_new)

    # print('"carts_users"= ', carts_users)
    session['carts_users'] = carts_users_new
    # print('session.get("carts_users"), [])= - 2', session.get('carts_users', []))
    # **** удаляем заказы с этой карточкой услуг из корзин пользователей - конец


    if card_usluga.prices:
        for price in card_usluga.prices:
            price.active=False
            price.arhive=True
    if card_usluga.photos:
        # Формируем путь для удаления файла
        path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + str(
            card_usluga.usluga.punkt_menu.link) + '/' + str(card_usluga.usluga.link) + '/' + str(card_usluga.dir_photos)
            # print('path_delete=', path_delete)
            # print('os.listdir(path_delete)=', os.listdir(path_delete))    #

        # Удаляем папку со всем содержимым
        # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
        shutil.rmtree(path_delete)

        # Удаляем записи в базе фото
        for photo in card_usluga.photos:
            db.session.delete(photo)

    # Удаляем запись, соответствующую карточке услуги, из базы
    db.session.delete(card_usluga)

    # Вносим изменение в базу
    db.session.commit()

    return redirect(url_for('card_usluga_bp.show_cards_uslugs'))
# *** Удалить карточку услуг - конец


# *** Удаление фото из карточки услуг - начало
@card_usluga_blueprint.route('/delete_photo_from_card_usluga/<int:card_usluga_id>/<int:photo_id>/', methods=["GET", "POST"])
def delete_photo_from_card_usluga(card_usluga_id, photo_id):

    # Выбираем из базы запись, соответствующую id
    delete_photo = Photo.query.filter(Photo.id == photo_id).first()

    # os.listdir см https://docs-python.ru/standart-library/modul-os-python/funktsija-listdir-modulja-os/
    files = os.listdir(path=current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + delete_photo.dir_uploads)
    # print(delete_photo)
    # print(len(files))
    # если удаляемый файл один в папке - удаляем папку со всем содержимым
    # см https://pythonist.ru/udalenie-fajla-poshagovoe-rukovodstvo/
    # Если нет то только этот файл
    try:
        if len(files)==1:
            # Формируем путь для удаления папки
            path_delete=current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + delete_photo.dir_uploads

            # удаляем папку с файлом(единственным в папке)
            shutil.rmtree(path_delete)

            # Удаляем запись, соответствующую удаленному фото, из базы
            db.session.delete(delete_photo)

            # Вносим изменение в базу
            db.session.commit()
        else:
            # Формируем путь для удаления файла
            path_delete = current_app.config['CARDS_USLUGS_UPLOAD_PATH'] + delete_photo.dir_uploads + delete_photo.secure_name_photo
            # print(path_delete)
            os.remove(path_delete)
            flash('Фото успешно удалено')
            # Удаляем запись, соответствующую удаленному фото, из базы
            db.session.delete(delete_photo)

            # Вносим изменение в базу
            db.session.commit()

    except:
        flash('Такой файл уже удален')


    return redirect(url_for('card_usluga_bp.edit_photos_in_card_usluga',
                            card_usluga_id=card_usluga_id))
# *** Удаление фото из карточки услуг - конец


# Редактировать все фото в карточке услуг - начало
@card_usluga_blueprint.route('/edit_photos_in_card_usluga/<int:card_usluga_id>/', methods=['GET', 'POST'])
def edit_photos_in_card_usluga(card_usluga_id):
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    return render_template('edit_photos_in_card_usluga.html',
                           card_usluga=card_usluga
                           )
# Редактировать все фото в карточке услуг - конец


# *** Редактирование заголовка и сопроводительного текста фото - начало
@card_usluga_blueprint.route('/<int:card_usluga_id>/edit_photo_info/<int:photo_id>/', methods=["GET", "POST"])
def edit_photo_info(card_usluga_id, photo_id ):
    form = EditFormPhotoCards()
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    photo = Photo.query.filter(Photo.id == photo_id).first()

    # ***** Принимаем данные из скрытых полей формы, которые запоняются
    # на стр. delete_foto.html автоматически с помощью параметра value
    # например {{ form_edit.secure_name_photo(value= foto.secure_name_photo) }}
    # это нужно для отображения данных картинки для редактирования
    # Если данный параметр на html странице убрать то скажет что не выбрано фото или фото
    # с некоррект.данными(not_foto_for_edit.html) т.к.в форме form_edit заданы проверки [InputRequired()]

    # secure_name_photo = form_edit.secure_name_photo.data
    # origin_name_photo = form_edit.origin_name_photo.data
    # dir_uploads = form_edit.dir_uploads.data
    # dir_usluga = form_edit.dir_usluga.data
    # dir_menu = form_edit.dir_menu.data
    # title = form_edit.hidden_title.data
    # comments = form_edit.hidden_comments.data
    # *****

    # # Если запрос POST и форма валидна
    if form.validate_on_submit():
        # Принимаем уникальное имя
        # secure_name_photo = form.secure_name_photo.data
        # Принимаем измененные данные
        title = form.title.data
        comments = form.comments.data

        # Вносим изменения в данную запись
        photo.title = title
        photo.comments = comments
        # Добавляем в сессии
        # db.session.add(photo)
        # Вносим изменения в базу
        db.session.commit()
        # Возвращаемся на страницу с миниатюрами
        return redirect (url_for('card_usluga_bp.edit_photos_in_card_usluga', card_usluga_id=card_usluga_id))

    # Если запрос не POST а GET и скрытые данные переданные из формы не нулевые,
    # то формируем страницу для редактирования данных
    # else:
    #     if secure_name_photo and origin_name_photo and dir_uploads and dir_usluga and dir_menu:
    #         menu = Link.query.filter(Link.link == dir_menu).first()
    #         usluga = Usluga.query.filter(Usluga.link == dir_usluga).first()
    #         print('comments=', comments)
    #         print('menu, usluga=', menu, usluga)
    #
    #         return render_template('edit_photo_info.html',
    #                             form_edit=form_edit,
    #                             secure_name_photo = secure_name_photo,
    #                             origin_name_photo = origin_name_photo,
    #                             dir_uploads = dir_uploads,
    #                             dir_usluga = dir_usluga,
    #                             dir_menu = dir_menu,
    #                             title = title,
    #                             comments = comments,
    #                             usluga=usluga,
    #                             menu=menu
    #                        )
        # Если запрос не POST а GET но скрытые данные переданные из формы нулевые,
        # или некорректные то формируем страницу где указано что не выбрано фото
        # или данные не корректные (not_foto_for_edit.html)
        # else:
        #     return render_template('not_foto_for_edit.html')

    return render_template('edit_photo_info.html',
                           form=form,
                           card_usluga=card_usluga,
                           photo=photo
                           )
# ******* Редактирование заголовка и сопроводительного текста фото - конец


# Удалить прайс из карточки услуг - начало
@card_usluga_blueprint.route('/delete_price_from_card_usluga/<int:card_usluga_id>/<int:price_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def delete_price_from_card_usluga(card_usluga_id, price_id):
    price=PriceTable.query.filter(PriceTable.id==price_id).first()
    price.card_usluga_id=None
    db.session.commit()
    return redirect(url_for('card_usluga_bp.edit_card_usluga',
                                card_usluga_id=card_usluga_id
                                )
                        )
# Удалить прайс из карточки услуг - конец



# Редактировать карточку услуг - начало
@card_usluga_blueprint.route('/edit_card_usluga/<int:card_usluga_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def edit_card_usluga(card_usluga_id):
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    uslugs=Usluga.query.all()
    menus=Link.query.order_by('title').all()
    session['card_usluga_id']=card_usluga_id

    return render_template('edit_card_usluga.html',
                           card_usluga=card_usluga,
                           uslugs=uslugs,
                           menus=menus
                           )
# Редактировать карточку услуг - конец


# Поменять флаг для показа только архива карточки услуг - начало
@card_usluga_blueprint.route('/show_arhive_cards_uslugs/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_arhive_cards_uslugs():
    session['arhive_cards']=True
    session['not_arhive_cards'] = False
    return redirect(url_for('card_usluga_bp.show_cards_uslugs'))
# Поменять флаг для показа только архива карточки услуг - конец


# Поменять флаг для показа только не архива карточки услуг - начало
@card_usluga_blueprint.route('/show_not_arhive_cards_uslugs/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_not_arhive_cards_uslugs():
    session['arhive_cards']=False
    session['not_arhive_cards'] = True
    return redirect(url_for('card_usluga_bp.show_cards_uslugs'))
# Поменять флаг для показа только не архива карточки услуг - конец


# Поменять флаг для показа всех карточек услуг - начало
@card_usluga_blueprint.route('/show_all_cards_uslugs/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_all_cards_uslugs():
    session['arhive_cards']=True
    session['not_arhive_cards'] = True
    return redirect(url_for('card_usluga_bp.show_cards_uslugs'))
# Поменять флаг для показа всех карточек услуг - конец


# Показать все карточки услуг - начало
@card_usluga_blueprint.route('/show_cards_uslugs/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def show_cards_uslugs():
    arhive_cards = session.get('arhive_cards', True)
    not_arhive_cards = session.get('not_arhive_cards', True)

    # услуги, имеющие карточки услуг
    # usl=Usluga.query.filter(Usluga.cards_usluga.any()).all()
    # print('usl=', usl)

    cards_uslugs = CardUsluga.query.order_by('name_card_usluga').all()

    # Множество услуг для карточек в архиве
    uslugs_list_for_cards_in_arhive= set()
    # Множество разделов меню для карточек в архиве
    menus_list_for_cards_in_arhive = set()
    # Список карточек услуг в архиве
    cards_uslugs_in_arhive = []

    # Множество услуг для карточек НЕ в архиве
    uslugs_list_for_cards_not_in_arhive = set()
    # Множество разделов меню  для карточек НЕ в архиве
    menus_list_for_cards_not_in_arhive = set()
    # Список карточек услуг НЕ в архиве
    cards_uslugs_not_in_arhive = []

    for card in cards_uslugs:
        if card.arhive==True:
            uslugs_list_for_cards_in_arhive.add(card.usluga)
            menus_list_for_cards_in_arhive.add(card.usluga.punkt_menu)
            cards_uslugs_in_arhive.append(card)
        else:
            uslugs_list_for_cards_not_in_arhive.add(card.usluga)
            menus_list_for_cards_not_in_arhive.add(card.usluga.punkt_menu)
            cards_uslugs_not_in_arhive.append(card)

    uslugs_list_for_cards_in_arhive=list(uslugs_list_for_cards_in_arhive)
    menus_list_for_cards_in_arhive = list(menus_list_for_cards_in_arhive)
    uslugs_list_for_cards_not_in_arhive = list(uslugs_list_for_cards_not_in_arhive)
    menus_list_for_cards_not_in_arhive = list(menus_list_for_cards_not_in_arhive)


    session['card_usluga_id'] = ''
    return render_template('show_cards_uslugs.html',
                           menus_not_arhive=menus_list_for_cards_not_in_arhive,
                           uslugs_not_arhive=uslugs_list_for_cards_not_in_arhive,
                           cards_uslugs_not_arhive=cards_uslugs_not_in_arhive,
                           menus_arhive=menus_list_for_cards_in_arhive,
                           uslugs_arhive=uslugs_list_for_cards_in_arhive,
                           cards_uslugs_arhive=cards_uslugs_in_arhive,
                           arhive_cards=arhive_cards,
                           not_arhive_cards=not_arhive_cards

                           # form_edit=form_edit
                           )
# Показать карточки услуг - конец


# роут для выбора из списка услуг по выбору в меню
@card_usluga_blueprint.route('/_get_usl_choice_card_usluga/', methods=['GET', 'POST'])
def _get_usl_choice_card_usluga():
    menu = request.args.get('menu', '01', type=str)
    uslugschoice = [(usluga.id, usluga.title) for usluga in Usluga.query.filter_by(punkt_menu_id=menu).order_by('title').all()]
    # print ('uslugschoice from fotomanager=', uslugschoice)
    return jsonify(uslugschoice)


# Создать карточку услуг - начало
@card_usluga_blueprint.route('/create/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def create_card_usluga():
    form_create_card_usluga=CreateCardUslugaForm()
    form_create_card_usluga.menu.choices = [(menu.id, menu.title) for menu in Link.query.order_by('title').all()]
    form_create_card_usluga.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.order_by('title').all()]
    form_create_card_usluga.type_production.choices = [(type_production.id, type_production.name) for type_production in
                                              TypeProduction.query.order_by('name').all()]
    if form_create_card_usluga.validate_on_submit():
    # if form_create_card_usluga.validate_on_submit() and form_create_card_usluga.name_card_usluga.data:
        name_card_usluga=form_create_card_usluga.name_card_usluga.data
        usluga=form_create_card_usluga.usluga.data
        comments=form_create_card_usluga.comments.data
        type_production=form_create_card_usluga.type_production.data
        # dir_photos = form_create_card_usluga.dir_photos.data

        # Удалим лишние пробелы если есть
        # https://docs-python.ru/tutorial/operatsii-tekstovymi-strokami-str-python/metod-str-split/
        # https://tonais.ru/string/zamena-neskolkih-probelov-odnim-python
        name_card_usluga = " ".join(name_card_usluga.split())

        # Сделаем первую заглавную букву в имени карточки услуг
        name_card_usluga=name_card_usluga[0].capitalize()+name_card_usluga[1:]

        # *** Сформируем путь карточки услуги из имени - начало


        # re.search(r'[^a-zA-Z]', model.link) возвращает объект, если есть несовпадения
        # Если текст полностью соответствует шаблону (у нас латинские буквы) - то выдает None

        # Преобразуем русские буквы в латиницу и переведем в нижний регистр
        dir_photos=translit(name_card_usluga, language_code='ru', reversed=True).lower()


        # **** Проверка на символы типа #$&$^%*&|/ - начало
        # Если символы в строке model.link, заданных юзером не a-zA-Z0-9\s- (регулярка),
        # где \s -символ пробела экранированный
        # тогда удаляем их из model.link и проверяем чтобы не стало пустой строкой
        new_dir_photos=''
        for i in list(dir_photos):
            if re.fullmatch(r'^[a-zA-Z0-9\s-]+$', i):
                new_dir_photos=new_dir_photos + i

        # заменим пробелы на '_' (то есть если заголовок меню из двух слов напрмер)
        new_dir_photos = "_".join(new_dir_photos.split())

        # заменим все '-' на пробелы
        new_dir_photos = " ".join(new_dir_photos.split('-'))

       # заменим пробелы идущие подряд на 1 '-'
        new_dir_photos = "-".join(new_dir_photos.split())


        if len(new_dir_photos)>=1:
            dir_photos=new_dir_photos
        else:
            # Если в заданном юзером пути нет символов, соответствующих шаблону регулярки
            # то в результате преобразований длина пути становится равна 0.
            # Поэтому задаем время загрузки файла в качестве пути загрузки (пока так)
            # для этого импортировали модуль datetime
            # replace(microsecond=0) - чтобы отсечь миллисекунды
            # replace(':', '-') - чтобы заменить : тк может в файловой системе создать проблемы
            uniq_time = 'dir_photos-'+ str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')

            dir_photos=uniq_time
        # **** Проверка на символы типа #$&$^%*&|/ - конец
        # *** Сформируем путь меню из имени - конец

        all_name_card_usluga = {item.name_card_usluga for item in CardUsluga.query.all()}
        if name_card_usluga in all_name_card_usluga:
            message_name_1 = 'Такое имя карточки услуг уже существует!'
            message_name_2 = 'Пожалуйста задайте другое имя.'
            return render_template('create_card_usluga.html',
                                   form_create_card_usluga=form_create_card_usluga,
                                   message_name_1=message_name_1,
                                   message_name_2=message_name_2
                                   )

        all_dir_photos = {item.dir_photos for item in CardUsluga.query.all()}
        if dir_photos in all_dir_photos:
            message_dir_1 = 'Такая директория уже существует!'
            message_dir_2 = 'Пожалуйста задайте другую директорию.'
            return render_template('create_card_usluga.html',
                                   form_create_card_usluga=form_create_card_usluga,
                                   message_dir_1=message_dir_1,
                                   message_dir_2=message_dir_2
                                   )

        card_usluga = CardUsluga(name_card_usluga=name_card_usluga,
                                 usluga_id=usluga,
                                 type_production_id=type_production,
                                 comments=comments,
                                 dir_photos=dir_photos
                                 )

        db.session.add(card_usluga)
        db.session.commit()

        return redirect(url_for('card_usluga_bp.upload_photos_in_card_usluga',
                                card_usluga_id=card_usluga.id
                                )
                        )

    # print('form.photo(id=1)=', form.photo(id=1), type(form.photo(id=1)))    #
    # print('str(form.photo(id=1))=', str(form.photo(id=1)), type(str(form.photo(id=1))))
    # выдаст str(form.photo)= <input id="photo" multiple name="photo" type="file">
    # где multiple задан в форме в render_kw={'multiple': True},
    # а id по умолчанию принимает значение=имя поля), но можно в форме задать другое id
    # print('str(form.photo_all)=', str(form.photo_all))

    session['message_upload']=''
    session['message_add']=''
    return render_template('create_card_usluga.html',
                           form_create_card_usluga=form_create_card_usluga)


# Загрузить фото в карточку услуг - начало
@card_usluga_blueprint.route('/<int:card_usluga_id>/upload/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def upload_photos_in_card_usluga(card_usluga_id):

    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    usluga=card_usluga.usluga
    menu=card_usluga.usluga.punkt_menu
    form=UploadFoto()

    if form.validate_on_submit() and form.photo.data and form.submit_upload.data:
        # Принимаем данные из формы - начало
        photo=form.photo.data
        title=form.title.data
        comments=form.comments.data

        # п.1 задаем время загрузки файла - начало
        # и включаем его (ниже) в имя загружаемого файла (таким образом оно будет уникальным)
        # для этого импортировали модуль datetime
        # replace(microsecond=0) - чтобы отсечь миллисекунды
        # replace(':', '-') - чтобы заменить : так как может в файловой системе создать проблемы
        uniq_time = str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')
        # **** задаем время загрузки файла -  конец

        # п.2 С помощью функции secure_filename делаем имя безопасным!
        # (пояснение https://translate.yandex.ru/translate)
        # Ее нужно использовать всегда, т.к. могут отправить имя, кот.может изменить файловую систему
        # Например имя ДКТ20-11-Фирма Вертикаль-чб.jpg преобразует в 20-11-_-.jpg
        # Но поскольку кириллические символы удаляются, то название например лифт.tif
        # преобразуется в tif Поэтому добавила перед именем время создания
        secure_file_name = uniq_time + '_' + secure_filename(photo.filename)

        # п.3 Формируем часть пути загрузки файла на основе выбранных меню, услуги и card_usluga.dir_photos:
        # директория меню сайта + директория услуги создаются при внесении в базу услуги или пункта меню))
        path_choice=menu.link + '/' + usluga.link + '/' + card_usluga.dir_photos + '/'
        # print('path_choice', path_choice)


        # п.4 Формируем полный путь загрузки файла на основе выбранных меню и услуги:
        # Для получения конфигурации можно использовать app.config['CARDS_USLUGS_UPLOAD_PATH'] но тогда нужно делать импорт
        # from RECL.__init__ import app а это порождает разные ошибки (при миграциях и тд)  тк циклический импорт
        # поэтому используем current_app.config['CARDS_USLUGS_UPLOAD_PATH'], импортируя from flask import current_app
        # так как при обращении к блюпринту приложение уже создано и соответственно уже существует его контекст
        # path_full = app.config['CARDS_USLUGS_UPLOAD_PATH']+path_choice - так в блюпринтах не делать!!!
        path_full = current_app.config['CARDS_USLUGS_UPLOAD_PATH']+path_choice

        # п.5 Если директория не создана - создаем ее
        if not os.path.isdir(path_full):
            os.makedirs(path_full)

        # п.6 Присоединяем безопасное имя файла к пути загрузки
        file_path = os.path.join(path_full, secure_file_name)

        # п.7 Сохраняем в выбранное место файл с безопасным именем
        photo.save(file_path)

        # п.8  Вычислим размер загруженного файла - вариант 1
        # Полученный размер отличается от того, что в проводнике.
        # Так и должно быть!!!! (и в варианте 2 тоже самое!!) Читать про это:
        # https://question-it.com/questions/1398830/python-ospathgetsize-otlichaetsja-ot-len-fread
        # https://translate.yandex.ru/translate?lang=en-ru&url=https%3A%2F%2Fstackoverflow.com%2Fquestions%2F26603698%2Fwhy-does-os-path-getsize-give-me-the-wrong-size&view=c
        # Можно наверное использовать и другой метод -см views.py
        #         @app.route('/upl/', methods=['GET', 'POST'])
        file_size=os.path.getsize(file_path)

        # п.9 Выделим расширение файла
        file_ext = os.path.splitext(file_path)[1]

        # п.10 Запишем параметры загрузки файла в базу
        upload_photo=Photo(card_usluga_id=card_usluga_id,
                           dir_uploads=path_choice,
                           origin_name_photo=photo.filename,
                           secure_name_photo=secure_file_name,
                           file_ext=file_ext,
                           file_size=file_size,
                           title=title,
                           comments=comments
                           )
        db.session.add(upload_photo)
        db.session.commit()
        # session['message_upload']='1Фото успешно загружено.'
        # session['message_add']='1Добавьте следующее фото или перейдите к следующему шагу.'

        return redirect(url_for('card_usluga_bp.upload_photos_success',
                               card_usluga_id=card_usluga.id
                               )
                        )

    if form.validate_on_submit() and not form.photo.data and form.submit_end.data:
        session['message_upload']=''
        session['message_add']=''
        return redirect(url_for('card_usluga_bp.upload_prices_in_card_usluga',
                           card_usluga_id=card_usluga.id
                                )
                        )

    return render_template('upload_photos_in_card_usluga.html',
                           card_usluga=card_usluga,
                           usluga=usluga,
                           menu=menu,
                           form=form,
                           # message_upload=message_upload,
                           # message_add=message_add
                           )
# Загрузить фото в карточку услуг - конец

# Загрузка фото в карточку услуг прошла успешно - начало
@card_usluga_blueprint.route('/<int:card_usluga_id>/upload_success/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def upload_photos_success(card_usluga_id):
    # message_upload = session.get('message_upload')
    # message_add = session.get('message_add')
    # session['message_upload']=''
    # session['message_add']=''

    session['message_upload']='Фото успешно загружено.'
    session['message_add']='Добавьте следующее фото или перейдите к следующему шагу.'

    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    usluga=card_usluga.usluga
    menu=card_usluga.usluga.punkt_menu

    form=UploadFoto()

    if form.validate_on_submit() and form.submit_add.data:

        session['message_upload']=''
        session['message_add']=''
        # message_upload='Фото успешно загружено.'
        # message_add='Добавьте следующее фото или перейдите к следующему шагу.'
        return redirect(url_for('card_usluga_bp.upload_photos_in_card_usluga',
                               card_usluga_id=card_usluga.id
                               )
                        )

    if form.validate_on_submit() and form.submit_end.data:
        session['message_upload']=''
        session['message_add']=''
        return redirect(url_for('card_usluga_bp.upload_prices_in_card_usluga',
                           card_usluga_id=card_usluga.id
                                )
                        )


    return render_template('upload_photos_success.html',
                           card_usluga=card_usluga,
                           usluga=usluga,
                           menu=menu,
                           form=form,
                           # message_upload=message_upload,
                           # message_add=message_add
                           )
# Загрузка фото в карточку услуг прошла успешно - конец


# Страница выбора прайса для загрузки в карточку услуг - начало
@card_usluga_blueprint.route('/<int:card_usluga_id>/upload_price/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def upload_prices_in_card_usluga(card_usluga_id):
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    usluga=card_usluga.usluga
    menu=card_usluga.usluga.punkt_menu
    # desc() - сортировка по убыванию
    # prices=PriceTable.query.order_by(PriceTable.card_usluga_id.desc()).order_by('name_price_table').all()
    # prices = PriceTable.query.filter(PriceTable.active!= False, PriceTable.arhive!= True).order_by(
    #     PriceTable.card_usluga_id.desc()).order_by('name_price_table').all()
    prices = PriceTable.query.filter(PriceTable.arhive != True).order_by(
        PriceTable.card_usluga_id.desc()).order_by('name_price_table').all()
    return render_template('upload_prices_in_card_usluga.html',
                           card_usluga=card_usluga,
                           usluga=usluga,
                           menu=menu,
                           prices=prices
                           )
# Страница выбора прайса для загрузки в карточку услуг - конец


# Добавить выбранный прайс  в карточку услуг - начало
@card_usluga_blueprint.route('/<int:card_usluga_id>/upload_price/<int:price_id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def attach_price_in_card_usluga(card_usluga_id, price_id):
    card_usluga=CardUsluga.query.filter(CardUsluga.id==card_usluga_id).first()
    price=PriceTable.query.filter(PriceTable.id==price_id).first()
    card_usluga.prices.append(price)
    db.session.commit()

    return redirect(url_for('card_usluga_bp.upload_prices_in_card_usluga',
                           card_usluga_id=card_usluga_id
                           )
                    )
# Добавить выбранный прайс  в карточку услуг - конец



    # # class UploadCarouselForm(FlaskForm): перенесла в forms.py
    # class CarouselForm(FlaskForm):
    #     all_photo = FieldList(FormField(UploadCarouselForm), min_entries=int(number_foto))
    #     submit_carousel = SubmitField('Загрузить фото')
    #
    # form_uploads_carousel = CarouselForm()
    #
    # if form_uploads_carousel.validate_on_submit() and form_uploads_carousel.submit_carousel.data:
    #
    #     # Формируем путь загрузки карусели
    #     # Для получения конфигурации можно использовать app.config['UPLOAD_PATH'] но тогда нужно делать импорт
    #     # from RECL.__init__ import app а это порождает разные ошибки (при миграциях и тд)  тк циклический импорт
    #     # поэтому используем current_app.config['UPLOAD_PATH'], импортируя from flask import current_app
    #     # так как при обращении к блюпринту приложение уже создано и соответственно уже существует его контекст
    #     # path_carousel = app.config['UPLOAD_CAROUSEL']+dir_carousel - так в блюпринтах не делать!!!
    #     path_carousel = current_app.config['UPLOAD_CAROUSEL'] + dir_carousel
    #
    #     if not os.path.isdir(path_carousel):
    #         os.makedirs(path_carousel)
    #
    #     for i in range(len(form_uploads_carousel.all_photo.data)):
    #         filename = str(i) + '_' + secure_filename(form_uploads_carousel.all_photo.data[i]['photo'].filename)
    #         # print('filename', i, filename)
    #
    #          # п.2 Присоединяем безопасное имя файла к пути загрузки
    #         file_path = os.path.join(path_carousel, filename)
    #
    #         # п.3 Сохраняем в выбранное место файл с безопасным именем
    #         form_uploads_carousel.all_photo.data[i]['photo'].save(file_path)
    #
    #         # Тоже самое (то есть п.1-3) можно записать в одну строку так:
    #         # form_uploads_carousel.all_photo.data[i]['photo'].save(os.path.join(app.config['UPLOAD_CAROUSEL'], secure_filename(form_uploads_carousel.all_photo.data[i]['photo'].filename)))
    #
    #         dict_car = {}
    #         dict_car['title_foto_carousel']=form_uploads_carousel.all_photo.data[i]['title_foto_carousel']
    #         dict_car['text_foto_carousel']=form_uploads_carousel.all_photo.data[i]['text_foto_carousel']
    #         dict_car['photo']=filename
    #
    #         dict_all_foto_carousel_name.append(dict_car)
    #
    #
    #     # serialized_dict_all_foto_carousel_name=json.dumps(dict_all_foto_carousel_name, ensure_ascii=False)
    #     # print('serialized_dict_all_foto_carousel_name1=', serialized_dict_all_foto_carousel_name)
    #     # print('type(serialized_dict_all_foto_carousel_name)=', type(serialized_dict_all_foto_carousel_name))
    #     date_create = str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')
    #     carousel = Carousel(name_carousel=name_carousel,
    #                         dir_carousel=dir_carousel,
    #                         number_foto=number_foto,
    #                         dict_all_foto_carousel_name = dict_all_foto_carousel_name,
    #                         active = False,
    #                         arhive = False,
    #                         date_create=date_create
    #                         )
    #
    #     db.session.add(carousel)
    #     db.session.commit()
    #
    #     return redirect(url_for('carousel_manager_bp.show_carousel', id=carousel.id))
    #
    # return render_template('upload_carousel.html',
    #                        form_uploads_carousel=form_uploads_carousel,
    #                        name_carousel=name_carousel,
    #                        dir_carousel=dir_carousel,
    #                        number_foto=number_foto
    #                        )
# Загрузить фото в карточку услуг - конец