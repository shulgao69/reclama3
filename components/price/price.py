import json

from flask import Blueprint, redirect, url_for, session
from flask import request, render_template, current_app

from flask_wtf import FlaskForm

from flask_security import login_required, roles_required, roles_accepted

from sqlalchemy import and_, or_

from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField, IntegerField
from wtforms import validators, PasswordField, FieldList, FormField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo

from RECL.components.price.forms import PriceForm

from RECL.models import db
from RECL.models import Usluga, Link, Order, User, Role, roles_users, UploadFileMy, PriceTable

#  модуль используем для перевода строки в десятичное число
from decimal import Decimal


# Создаем блюпринт управления прайсами- создание, редактирование, копирование, удаление таблиц прайсов

price_blueprint = Blueprint('price_bp', __name__, template_folder='templates/price/', static_folder='static')

# *** Вынесем в отдельную функцию создание сложной формы прайса
# (для сокращения кода), т.к эта форма используется несколько раз
# Хотела вынести в файл forms.py, но не знаю как в форму передать параметры row_table, col_table
# вне функции

def create_form_price(row_table, col_table):

    # **** Создание формы с FieldList(FormField...) - начало
    # Создала класс формы здесь а не в forms.py так как в форму передаются параметры row_table, col_table
    # 1) https://prettyprinted.com/tutorials/how-to-use-fieldlist-in-flask-wtf
    # Данная сложная форма нужна для передачи id каждого поля. Если просто в цикле jinja одно поле повторять
    # то передаются значения одинаковые(как я поняла)
    # RowForm создает форму с количеством строк = row_table(передаем через параметр min_entries=row_table)
    # ColForm создает окончат. форму с кол-вом столбцов = col_table(передаем в параметр min_entries=col_table)
    # а каждый столбец повторяет количество строк заданных в  RowForm
    # 2) При валидации этой формы ColForm form.validate_on_submit() возникали ошибки:
    # Mycol: {'csrf_token': ['The CSRF token is missing.']}
    # Mycol: {'row': [{'csrf_token': ['The CSRF token is missing.']}], 'csrf_token': ['The CSRF token is missing.']}
    # Нашла такой вариант
    # https://stackoverflow.com/questions/15649027/wtforms-csrf-flask-fieldlist
    # Насколько я поняла нужно отключить csrf_token в родительских формах,
    # т.к.мы не можем его передать в HTML так как форма составная
    # Но не использовать ListForm и RowForm самостоятельно!!! (Так как csrf_token отключен и это опасно!!)
    #  Отключение с помощью: class Meta:  csrf = False
    # Если отключаем в ListForm и RowForm(class Meta: csrf = False) то ошибки уходят:
    # Mycol: {'row': [{'csrf_token': ['The CSRF token is missing.']}]}
    # Mycol: {'row': [{'csrf_token': ['The CSRF token is missing.']}], 'csrf_token': ['The CSRF token is missing.']}


    # Составная форма
    class ListForm(FlaskForm):
        # эта строка задает одинаковую надпись (то что в кавычках) перед каждой ячейкой таблицы
        # Если внутри кавычек ничего - то перед ячейкой ничего,
        # если внутри скобок вообще убрать кавычки, то перед каждой ячейкой будет по умолчанию
        # название данного поля. У нас это pole.
        # Я задаю пустые кавычки, чтобы сэкономить место при создании таблицы
        pole = StringField('')
        # если убрать (class Meta: csrf = False) - то ошибка при form.validate_on_submit()
        # Mycol: {'row': [{'csrf_token': ['The CSRF token is missing.']}]}
        class Meta:
            csrf = False

    class RowForm(FlaskForm):
        row = FieldList(FormField(ListForm), name='строка', min_entries=row_table)
        # если убрать (class Meta: csrf = False) - то ошибка при form.validate_on_submit()
        # Mycol: {'row': [{'csrf_token': ['The CSRF token is missing.']}]}
        class Meta:
            csrf = False

    class ColForm(FlaskForm):
        name_price_table = StringField('Имя таблицы прайса', [InputRequired()])
        mycol = FieldList(FormField(RowForm), min_entries=col_table)
        submit = SubmitField('Сохранить изменения')

    # Возвращает сложную форму
    return(ColForm())

 # **** Создание формы с FieldList(FormField...) - конец


# Извлечь прайс из архива
@price_blueprint.route('/not_arhive_price/<int:id>/', methods=['GET', 'POST'])
def not_arhive_price(id):
    price=PriceTable.query.filter_by(id=id).first()
    price.arhive=False
    db.session.commit()
    return redirect(url_for('price_bp.choose_price'))


# Архивировать прайс
@price_blueprint.route('/arhive_price/<int:id>/', methods=['GET', 'POST'])
def arhive_price(id):
    price=PriceTable.query.filter_by(id=id).first()
    price.arhive=True
    db.session.commit()
    return redirect(url_for('price_bp.choose_price'))


# Деактивировать прайс
@price_blueprint.route('/deactiveprice/<int:id>/', methods=['GET', 'POST'])
def deactive_price(id):
    price=PriceTable.query.filter_by(id=id).first()
    price.active=False
    db.session.commit()
    return redirect(url_for('price_bp.choose_price'))


# Активировать прайс
@price_blueprint.route('/activeprice/<int:id>/', methods=['GET', 'POST'])
def active_price(id):
    price=PriceTable.query.filter_by(id=id).first()
    price.active=True
    db.session.commit()
    return redirect(url_for('price_bp.choose_price'))



# создание копии прайса (ссылки из списка всех прайсов)
@price_blueprint.route('/copyprice/<int:id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def copy_price(id):
    price = PriceTable.query.filter_by(id=id).first()
    row_table=price.row_table
    col_table=price.col_table
    # value_table=json.loads(price.value_table)
    value_table=price.value_table
    err=''

     # Для объявления формы применим функцию, кот. создали сами
    # create_form_price(row_table=row_table, col_table=col_table), объявленную в начале блюпринта.
    # Она возвращает форму ColForm() (т.е.это все равно что form = ColForm())-
    # составную форму от ListForm(FlaskForm) и RowForm(FlaskForm) а ее уже передаем в html
    form = create_form_price(row_table=row_table, col_table=col_table)

    # создали матрицу price_table(список списков) из нулей(если пустую сделать(не 0) то ошибка)
    price_table=[[0]*col_table for _ in range(row_table)]

    # Получим данные по всем прайсам, чтобы сформировать список имен name_spisok
    # для последующей проверки имени, полученного из формы, на уникальность
    names=PriceTable.query.all()
    name_spisok=[]
    for name in names:
        name_spisok.append(name.name_price_table)
        # print('name_spisok=', name_spisok)

    if form.validate_on_submit():
        # Получаем имя прайса из формы
        name_price_table = form.name_price_table.data

        # Проверяем есть ли в списке имен прайсов. Если есть - сообщение 'Такое имя .....
        if name_price_table in name_spisok:
            message = 'Такое имя прайса уже существует. Задайте другое имя'
            return render_template('pricestr.html',
                           form=form,
                           col_table=col_table,
                           row_table=row_table,
                           message=message,
                           err=err
                           )

        # Если имя в списке нет - создаем новый экземпляр класса PriceTable price_copy и заполняем данными из формы
        price_copy = PriceTable()
        price_copy.name_price_table = form.name_price_table.data
        price_copy.row_table=price.row_table
        price_copy.col_table=price.col_table

        # Получили список списков
        mycol = form.mycol.data
        # print('mycol=', mycol, 'type(mycol)=', type(mycol))

        # Заполняем таблицу с нулями данными из формы
        for i in range(len(mycol)):
            for j in range(len(mycol[i]['row'])):
                price_table[j][i]=mycol[i]['row'][j]['pole']
        # print('price_table=', price_table, 'type(price_table)=', type(price_table))

        price_copy.value_table = price_table

        db.session.add(price_copy)
        db.session.commit()

        # Перенаправляем на полный список прайсов
        return redirect(url_for('price_bp.choose_price'))

    # Заполняем форму значениями из выбранного прайса price - начало
    # ВНИМАНИЕ!!! Если этот блок стоит перед if form.validate_on_submit() то данные полученные из формы
    # перезаписываются на те, что были предварительно заполнены!!!
    form.name_price_table.data=price.name_price_table
    for col in range(row_table):
        for row in range(col_table):
            form.mycol[row].row[col].pole.data=value_table[col][row]
    # другой способ(не применяла) populate_obj(obj) см https://wtforms.readthedocs.io/en/2.3.x/forms/
    # если поля формы совпадают с полями модели? не разбиралась
    # Заполняем форму значениями из выбранного прайса - конец

    return render_template('copy_price.html',
                           form=form,
                           id=id
                           )


# удаление прайса
@price_blueprint.route('/deleteprice/<int:id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def delete_price(id):
    price = PriceTable.query.filter_by(id=id).first()
    # print('price.card_usluga=', price.card_usluga)

    # проверяем есть ли в корзине заявки на заказы с этим прайсом
    # Если есть - отправляем прайс в архив (не удаляем). Если нет - удаляем
    cart=session.get('cart', [])
    price_in_cart = False
    for order_reuest in cart:
        if order_reuest['price_id']==id:
            price_in_cart = True
    if price_in_cart == True:
        price.arhive=True
    else:
        db.session.delete(price)
    db.session.commit()

    return redirect(url_for('price_bp.choose_price'))


# редактирования прайса
@price_blueprint.route('/editprice/<int:id>/', methods=['GET', 'POST'])
# @roles_accepted('superadmin')
def edit_price(id):
    message_edit_price=session.get('message_edit_price', '')
    price_success=session.get('price_success', '')

    prices = PriceTable.query.all()
    name_spisok = []
    for price in prices:
        if price.id != id:
            name_spisok.append(price.name_price_table)
    print('name_spisok=', name_spisok)

    price = PriceTable.query.filter_by(id=id).first()
    row_table=price.row_table
    col_table=price.col_table
    # value_table=json.loads(price.value_table)
    value_table=price.value_table

    # Для объявления формы применим функцию, кот. создали сами (см выше)
    # create_form_price(row_table=row_table, col_table=col_table), объявленную в начале блюпринта.
    # Она возвращает форму ColForm() (т.е.это все равно что form = ColForm())-
    # составную форму от ListForm(FlaskForm) и RowForm(FlaskForm) а ее уже передаем в html
    form = create_form_price(row_table=row_table, col_table=col_table)

    # создали матрицу price_table(список списков) из нулей(если пустую сделать(не 0) то ошибка)
    price_table=[[0]*col_table for _ in range(row_table)]
    # print('создали пустую матрицу price_table=', price_table)

    if form.validate_on_submit():

        if form.name_price_table.data in name_spisok:

            session['message_edit_price'] = 'Имя прайса '+ str(form.name_price_table.data) + \
                                            ' уже существует! Задайте другое имя либо сохраните с прежним.'
            # Флаг для показа формы ввода данных. Если button=True- форму аоказывать
            # Если данные сохранены успешно button=False- форму не показывать
            session['price_success'] = False
            return redirect(url_for('price_bp.edit_price', id=price.id))

        else:
            price.name_price_table = form.name_price_table.data

            # Получили список списков
            mycol = form.mycol.data
            # print('mycol=', mycol, 'type(mycol)=', type(mycol))

            # Заполняем таблицу с нулями данными из формы
            for i in range(len(mycol)):
                # for j in range(len(mycol[i]['row'])):
                #     price_table[j][i]=mycol[i]['row'][j]['pole']
                for j in range(len(mycol[i]['row'])):
                    # *** Т.к. в сложной форме параметр поле везде одинаков по типу, то установить
                    # разные типы данных(и соответственно их валидацию) для разных ячеек
                    # не возможною Поэтому решила сделать так:
                    # Первую строку и первый столбец вводим без изменений, как внес пользователь
                    # а остальные ячейки - если число целое - оставляем как есть, если с точкой и числа после нее
                    # тогда переводим в decimal, округляем до 2 знаков после точки и снова преобразуем в строку
                    if i != 0 or j != 0:
                        try:
                            value_i_j = int(mycol[i]['row'][j]['pole'])
                            price_table[j][i] = str(value_i_j)
                        except:
                            try:
                                # Переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                                # и округлим до 2 знаков после запятой
                                # https://www.delftstack.com/howto/python/string-to-decimal-python/
                                value_i_j = round(Decimal(mycol[i]['row'][j]['pole']), 2)
                                price_table[j][i] = str(value_i_j)
                            except:
                                price_table[j][i] = mycol[i]['row'][j]['pole']
                    else:
                        price_table[j][i] = mycol[i]['row'][j]['pole']
                    # ****
            price.value_table = price_table
            db.session.commit()
            session['message_edit_price']='Изменения успешно сохранены'
            session['price_success'] = True

            return redirect(url_for('price_bp.edit_price', id=price.id))

    # Заполняем форму значениями из выбранного прайса - начало
    form.name_price_table.data=price.name_price_table
    for col in range(row_table):
        for row in range(col_table):
            form.mycol[row].row[col].pole.data=value_table[col][row]
    # Заполняем форму значениями из выбранного прайса - конец

    session['message_edit_price']=''
    session['price_success'] = False
    return render_template('edit_price.html',
                           form=form,
                           id=id,
                           price=price,
                           message_edit_price=message_edit_price,
                           price_success=price_success
                           )

# список всех прайсов с ссылкой на страницу редактирования прайса
@price_blueprint.route('/chooseprice/')
# @roles_accepted('superadmin')
def choose_price():
    # prices = PriceTable.query.order_by('name_price_table').all()
    # prices = PriceTable.query.order_by(and_(PriceTable.name_price_table(), PriceTable.arhive())).all()
    # prices = PriceTable.query.order_by(and_(text('name_price_table', 'arhive'))).all()
    prices = PriceTable.query.order_by(PriceTable.arhive, PriceTable.name_price_table, ).all()
    # prices = PriceTable.query.order_by('arhive').all()
    # print('type prices=', type(prices))
    # list_prices = []
    #
    # for price in prices:
    #     dict_price = {}
    #     dict_price['id']=price.id
    #     dict_price['row_table']=price.row_table
    #     dict_price['col_table']=price.col_table
    #     dict_price['name_price_table']=price.name_price_table
    #     # dict_price['value_table']=json.loads(price.value_table)
    #     dict_price['value_table']=price.value_table
    #     dict_price['card_uslugi_id']=price.card_uslugi_id
    #     dict_price['arhive'] = price.arhive
    #     list_prices.append(dict_price)
    # list_prices=prices
    return render_template('choose_price.html',
                           prices=prices
                           )


# Создание страницы формы, где принимаются данные о количестве строк и столбцов
@price_blueprint.route('/priceroute/', methods=['GET', 'POST'])
@roles_accepted('superadmin')
def priceindex():
    form=PriceForm()
    if request.method=='POST':
        # или form.validate_on_submit() - надо протестировать!!!
        col_table=form.col_table.data
        row_table=form.row_table.data
        return redirect(url_for('price_bp.createprice', col_table=col_table, row_table=row_table)
                        )
    # *** request.referrer - позволяет получить адрес ресурса, из которого был получен запрос
    # Используем для того, чтобы сделать сессию пустой
    # (тк в html условие, зависящее от сессии session['card_usluga_id'] в навигационных ссылках)
    # request.referrer.endswith('/admin/')- означает что путь,
    # откуда пришел пользователь заканчивается на  /admin/ (то есть с главной стр администратора)
    # https://docs-python.ru/packages/veb-frejmvork-flask-python/dostup-razlichnym-dannym-zaprosa-flask/
    # https://stackoverflow.com/questions/39777171/how-to-get-the-previous-url-in-flask
    # https://docs-python.ru/packages/veb-frejmvork-flask-python/klass-request/
    if request.referrer.endswith('/admin/'):
        session['card_usluga_id']=''

    return render_template('price.html',
                           form=form
                           )


# Создание страницы формы для ввода данных прайса по заданному ранее количеству строк и столбцов
# Комментарии к def createprice см ниже в Пример использования FieldList(FormField(NameForm(FlaskForm)))
@price_blueprint.route('/pricestr/<int:row_table>/<int:col_table>/', methods=['GET', 'POST'])
def createprice(row_table, col_table):
    row_table=row_table  # количество строк в будущей таблице
    col_table=col_table # количество столбцов(колонок) в будущей таблице

    # Флаг для показа формы ввода данных. Если button=True- форму аоказывать
    # Если данные сохранены успешно button=False- форму не показывать
    button=True

    # Для объявления формы применим свою функцию (см выше) create_form_price(row_table=row_table, col_table=col_table)
    # объявленную в начале блюпринта. Она возвращает ColForm() (т.е.это все равно что form = ColForm())-
    # составную форму от ListForm(FlaskForm) и RowForm(FlaskForm) а ее уже передаем в html
    form = create_form_price(row_table=row_table, col_table=col_table)

    # создали матрицу price_table(список списков) например из нулей(если пустую сделать то ошибка)
    price_table=[[0]*col_table for _ in range(row_table)]



    if form.validate_on_submit():
        name_price_table = form.name_price_table.data

        # Сформируем список имен прайсов для проверки введенного имени прайса на уникальность
        prices = PriceTable.query.all()
        name_spisok = []
        for price in prices:
            name_spisok.append(price.name_price_table)

        if name_price_table in name_spisok:
            message = 'Такое имя прайса уже существует! Задайте другое имя.'
            # Флаг для показа формы ввода данных. Если button=True- форму аоказывать
            # Если данные сохранены успешно button=False- форму не показывать
            button=True
            return render_template('pricestr.html',
                           form=form,
                           col_table=col_table,
                           row_table=row_table,
                           message=message,
                           button=button
                           )
        else:
            # Получили список списков
            mycol = form.mycol.data


            # Заполняем таблицу с нулями данными из формы
            for i in range(len(mycol)):
                for j in range(len(mycol[i]['row'])):
                    # *** Т.к. в сложной форме параметр поле везде одинаков по типу, то установить
                    # разные типы данных(и соответственно их валидацию) для разных ячеек
                    # не возможно Поэтому решила сделать так:
                    # Первую строку и первый столбец вводим без изменений, как внес пользователь
                    # а остальные ячейки:
                    # 1) если строку можно перевести в целое число - тогда эту строку оставляем как есть,
                    # 2) если строку можно перевести в decimal(те строка- числа с точкой и числа после нее)
                    # тогда переводим в decimal, округляем до 2 знаков после точки и снова преобразуем в строку
                    if i !=0 or j !=0:
                        try:
                            value_i_j = int(mycol[i]['row'][j]['pole'])
                            price_table[j][i] = str(value_i_j)

                        except:
                            try:
                                # Переведем в десятичное число с помощью модуля from decimal import Decimal!!!
                                # и округлим до 2 знаков после запятой
                                # https://www.delftstack.com/howto/python/string-to-decimal-python/
                                value_i_j = round(Decimal(mycol[i]['row'][j]['pole']), 2)
                                price_table[j][i] = str(value_i_j)

                            except:
                                price_table[j][i]=mycol[i]['row'][j]['pole']

                    else:
                        price_table[j][i] = mycol[i]['row'][j]['pole']
                    # ****
            # ***Сериализация -  начало
             # Как я поняла при записи в базу в поле db.Column(JSON) (например списка)
            # сериализация происходит  автоматически (встроена) и не надо делать специально json.dumps(имя списка)
            # а вот при извлечении этих данных из базы надо сделать json.loads(...данные из поля) так как в базе JSON формат
            # https://python-scripts.com/json
            # https://question-it.com/questions/83190/stolbets-postgresql-json-ne-sohranjaet-simvol-utf-8
            # https://ru.stackoverflow.com/questions/1047189/Не-могу-избавиться-от-юникода-в-json-dumps
            # https://ru.stackoverflow.com/questions/606885/Как-json-данные-u0413-u0440-преобразовать-в-русский-текст
            # поэтому сериализацию не делаю.
            # Она сделается сама при записи в базу если задано поле как value_table = db.Column(JSON)
            # Но пока не удалять
            # serialized_price_table1 = json.dumps(price_table, ensure_ascii=False)
            # print('serialized_price_table1=', serialized_price_table1, 'type=', type(serialized_price_table1))
            # print (serialized_price_table)
            # ***Сериализация -  конец

            try:
                price = PriceTable(name_price_table = name_price_table,
                                 row_table = row_table,
                                 col_table = col_table,
                                 value_table = price_table
                                )
                print('price.value_table=', price.value_table)
                db.session.add(price)
                db.session.commit()
                price=PriceTable.query.filter(PriceTable.name_price_table==name_price_table).first()
                print('price=', price)
                # Флаг для показа формы ввода данных. Если button=True- форму аоказывать
                # Если данные сохранены успешно button=False- форму не показывать
                button=False
                message_success_1 = 'Данные успешно загружены.'
                message_success_2 = 'Если вам нужно другое кол-во ' \
                                    'строк или столбцов - создайте новый прайс.'
                message_success_3 = 'Если вы хотите отредактировать ' \
                                    'ячейки прайса - перейдите в список прайсов.'
                return render_template('pricestr.html',
                                       form=form,
                                       col_table=col_table,
                                       row_table=row_table,
                                       button=button,
                                       message_success_1=message_success_1,
                                       message_success_2=message_success_2,
                                       message_success_3=message_success_3,
                                       price=price
                                       )

            except:
                message = "Проверьте корректность введенных данных."
                # Флаг для показа формы ввода данных. Если button=True- форму аоказывать
                # Если данные сохранены успешно button=False- форму не показывать
                button = True
                return render_template('pricestr.html',
                                       form=form,
                                       row_table=row_table,
                                       col_table=col_table,
                                       message=message,
                                       button=button
                                       )

    return render_template('pricestr.html',
                           form=form,
                           col_table=col_table,
                           row_table=row_table,
                           button=button
                           )


    # deserialized_price_table = json.loads(serialized_price_table)
    # print('deserialized_price_table=', deserialized_price_table)
    # print('type(deserialized_price_table)=', type(deserialized_price_table))


# **** Пример использования FieldList(FormField(NameForm(FlaskForm))) - начало

# Использование наследуемых форм и FieldList и FormField
# https://prettyprinted.com/tutorials/how-to-use-fieldlist-in-flask-wtf
# min_entries=5 - Количество повторений поля родительской формы
# max_entries=5 - Максимальное число повторений(если min_entries >  max_entrie  то выдаст ошибку)

# pole = TextAreaField('pole', render_kw={'rows': 5, 'cols':4})
# Если задан render_kw={'rows': 5, 'cols':4} то 1 поле будет  иметь 5 строк и 4 столбца
# (единицы измерения не знаю) а не 20 полей в виде таблицы (Для полей ввода текста!!!)


# **Родительская форма
# class ProductForm(FlaskForm):
#     title = StringField('Title')
#     price = IntegerField('Price')
#
# **Дочерняя форма с повторением полей родительской 5 раз
# class InventoryForm(FlaskForm):
#     category_name = StringField('Category Name')
#     products = FieldList(FormField(ProductForm), min_entries=5, max_entries=10)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = InventoryForm()
#     return render_template('index.html', form=form)

# ****Пример использования FieldList(FormField(NameForm(FlaskForm))) - конец

