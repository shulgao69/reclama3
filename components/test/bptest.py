# from flask_wtf import FlaskForm
# from wtforms import SubmitField, HiddenField, SelectField, BooleanField, StringField
# from wtforms import PasswordField, IntegerField, validators, TextAreaField, TextField
# from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo
# from wtforms.validators import ValidationError
# from RECL.models import db, Link, Usluga

# импорты для загрузки файлов - начало
from flask_wtf.file import FileField, FileAllowed, FileRequired
# импорты для загрузки файлов - конец

from flask import Blueprint, jsonify, render_template, url_for, redirect, request
from RECL.models import Usluga, Link, Order, User, Role, roles_users, UploadFileMy
from RECL.components.test.forms import TestForm
from RECL.models import db


# - test_bp - экземпляр класса Blueprint, кот. импортируем в __init__.py приложения RECL
#  (from test.blueprinttest import test_bp), а затем регистрируем Блюпринт
#  test_bp из файла bptest.py   app.register_blueprint(test_bp, url_prefix='/testprefix'),
#  где url_prefix='/testprefix' - это то, что будет добавляться в url после домена
#  и перед путями указанными в роутах Блюпринта
#
# - 'test' - название папки в которой находится Блюпринт? В других местах у меня это не так!!!
# (например в папке admin  в файлах ...py у меня зарегистрированы разные блюпринты)
# Наверное все-таки это:
# (название(псевдоним) блюпринта, которое потом используется при формировании
# url_for(test.имя-функции в роуте этого блюпринта),

# -  template_folder='templates/test' - # название папки (templates или (templates/test))
# внутри папки Блюпринта(в нашем случае test), где находятся файлы представлений Блюпринта.

# ВНИМАНИЕ!
# Если роут Блюпринта обращается к html - файлу (в нашем случае test.html),
# а в папках templates и приложения и Блюпринта есть файлы с одинаковым именем (test.html)
# то отображаться будет файл из папки templates приложения RECL, а не Блюпринта, так как
# Блюпринт имеет более слабый приоритет
# Если роут обращается к файлу, которого нет в template_folder='templates' Блюпринта,\
# но есть в папке templates приложения, то отразиться этот файл!
# Чтобы избежать  переопределений и используют дополнительную папку
# внутри папки templates папку /test внутри Блюпринта
# (см https://flask.palletsprojects.com/en/1.1.x/blueprints/)
# - static_folder='static' - название папки (static) внутри папки Блюпринта(в нашем случае test),
# в которой находятся папки CSS JS images, относящиеся к данному Блюпринту

test_bp = Blueprint('test', __name__, template_folder='templates/test/', static_folder='static')

# В итоге файл test.html  из папки components/test/templates/test - (components/test/templates/test/test.html)
# отобразиться по адресу /testprefix/testroute/, где
# 1) testprefix - это url_prefix из  app.register_blueprint(test_bp, url_prefix='/testprefix')
# из __init__.py нашего приложения
# 2) testroute - это роут из @test_bp.route('/testroute/')(см. ниже)
# эти 1) и 2) имена можно давать любые!!!! (мы такие присвоили для понимания)


# ******  Группа роутов для 2 SelectFields с помощью flask и чистого JavaScripts - начало - РАБОТАЕТ ВСЕ!!!
@test_bp.route('/testroute/', methods=['GET', 'POST'])
def testindex():
    # print('test_bp.root_path=', test_bp.root_path)
    # print('test_bp.url_prefix=', test_bp.url_prefix)
    # print('test_bp.url_values_defaults=', test_bp.url_values_defaults)
    # print('test_bp.template_folder=', test_bp.template_folder)
    # print('test_bp.subdomain=', test_bp.subdomain)
    # print('test_bp.static_url_path=', test_bp.static_url_path)
    err = request.args.get('err')

    form = TestForm()
    # Выбираем отсортированный по имени!!!! список для первого селекта (пункт меню)
    # Если не отсортировать, то во втором селекте первоначальный список не будет соответствовать пункту меню
    # т.к. мы изначально там взяли id из первого пункта меню отсортированного списка
    form.menu.choices = [(menu.id, menu.title) for menu in Link.query.order_by('title').all()]

    # Выбираем первый пункт меню из отсортированного по имени!!!! списка
    # Поскольку список для первого селекта мы отсортировали, то этот пункт меню будет первым в списке меню
    links_menu = Link.query.order_by('title').first()

    # Загружаем первоначальный список услуг, который соответствует первому пункту меню.
    # Затем этот список будет меняться в зависимости от выбора пункта меню, а это первоначальная загрузка
    # Если ее не задать, то второй селект(услуги) будет изначально пустой, а подгружаться будет в следствии
    # выбора первого селекта(пункта меню). Но так тоже можно!!
    form.usluga.choices = [(usluga.id, usluga.title) for usluga in Usluga.query.filter(Usluga.punkt_menu_id==links_menu.id).order_by('title').all()]


    # Блок загрузки и выбора файлов взята из Choice2 но не сделана для данной страницы - не удалять!!!
    # if form.validate_on_submit() and form.form_name.data == 'FormChoice2Name' and form.photo.data:
    #     menu_choice2=Link.query.filter_by(id=form.menu.data).first()
    #     usluga_choice2=Usluga.query.filter_by(id=form.usluga.data).first()
    #     path_choice2=menu_choice2.link +'/' + usluga_choice2.link +'/'
    #     path_full = app.config['UPLOAD_PATH']+path_choice2
    #     if not os.path.isdir(path_full):
    #         os.makedirs(path_full)
    #         title = form.title.data
    #         comments = form.comments.data
    #         photo_name = form.photo.data
    #         uniq_filename = str(datetime.now().date()) + '_' + str(datetime.now().time().replace(microsecond=0)).replace(':', '-')
    #         filename = secure_filename(uniq_filename+'_'+photo_name.filename)
    #         file_path = os.path.join(path_full, filename)
    #         photo_name.save(file_path)
    #         file_size=os.path.getsize(file_path)
    #         name_ext = os.path.splitext(file_path)[1]
    #         upload_file=UploadFileMy(origin_name_photo = photo_name.filename,
    #                                  secure_name_photo = filename,
    #                                  menu = menu_choice2.title,
    #                                  dir_menu = menu_choice2.link,
    #                                  usluga = usluga_choice2.title,
    #                                  dir_usluga = usluga_choice2.link,
    #                                  # Часть пути загрузки(меню+услуга)
    #                                  dir_uploads = path_choice2,
    #                                  # Полный путь загрузки(путь проекта + путь меню+услуга)
    #                                  # dir_uploads = file_path,
    #                                  file_ext = name_ext,
    #                                  file_size = file_size,
    #                                  title=title,
    #                                  comments=comments
    #                                  )
    #         db.session.add(upload_file)
    #         db.session.commit()
    #         success = True
    #
    #         return redirect(url_for('choice2.choice2'))

    return render_template('test.html',
                           form=form
                           # links_menu=links_menu,
                           # err=err
                           )

# ******** Роут для 2 Селектов - вариант 1 - работает!!! - начало
@test_bp.route('/testroute/<int:menu>')
def usluga(menu):
    print(menu)
    uslugaObj={}
    uslugs = [{'id': usluga.id, 'title': usluga.title} for usluga in Usluga.query.filter_by(punkt_menu_id=menu).order_by('title').all()]
    print ('uslugs=', uslugs)
    return jsonify({'uslugs': uslugs})
# ******** Роут для 2 Селектов - вариант 1 - работает!!! - конец

# ******** Роут для 2 Селектов - вариант 2 - работает!!! - начало
# @test_bp.route('/testroute/<int:menu>')
# def usluga(menu):
#     print(menu)
#     uslugs = Usluga.query.filter_by(punkt_menu_id=menu).order_by('title').all()
#     uslugaArray = []
#     for usluga in uslugs:
#         uslugaObj = {}
#         uslugaObj['id'] = usluga.id
#         uslugaObj['title'] = usluga.title
#         uslugaArray.append(uslugaObj)#
#     print(uslugaArray)#
#     return jsonify({'uslugs' : uslugaArray})
# ******** Роут для 2 Селектов - вариант 2 - работает!!! - конец

# ******  Группа роутов для 2 SelectFields с помощью flask и чистого JavaScripts - конец