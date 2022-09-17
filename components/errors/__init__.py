from flask import Blueprint, render_template, make_response
# Следующий импорт нужен для того чтобы загрузить данные из корневого файла config.py
# и затем использовать для получения значения (работает только в контексте запроса)
# max_size_file = current_app.config['MAX_CONTENT_LENGTH'] в ошибке 413 о большом файле
# Если же попытаться  сделать такой импорт
# from RECL.__init__ import app
# а затем для получения значения max_size_file = app.config['MAX_CONTENT_LENGTH']
# то выдает ошибку импорта app. В блюпринте админки такой импорт почему-то ошибки не дает! Разобраться!!
from flask import current_app

# from werkzeug.exceptions import HTTPException

errors_blueprint = Blueprint('errors', __name__, template_folder='templates', static_folder='static')


# Во вьюс работает @app.errorhandler(404)
#  По идее должно работать @errors_blueprint.errorhandler(404) но так не работает
# но работает @errors_blueprint.app_errorhandler(404)
# откуда берется app_errorhandler не знаю ЧИТАТЬ!!!
# помогло;  https://progi.pro/ya-popitalsya-ispolzovat-blueprints-dlya-obrabotki-oshibok-404-v-flask-no-pohozhe-ya-ne-rabotayu-vot-moy-kod-1154224

# Ошибка 404
@errors_blueprint.app_errorhandler(404)
def render_pageNotFound(error):
    return render_template("errors/404.html"), 404

# Ошибка 404 с получением объект внутри представления - начало
# стр.21 https://buildmedia.readthedocs.org/media/pdf/flask-russian-docs/latest/flask-russian-docs.pdf
# Если мы хотим в результате ответа заполучить объект внутри представления, то
# можно использовать функцию make_response(). Для этого сначала сделаем импорты
# from flask import render_template, make_response
# Далее представим, что мы имеем представление:
# @app.errorhandler(404)
# def not_found(error):
#     return render_template('error.html'), 404
# Нужно всего лишь обернуть возвращаемое выражение функцией make_response()
# и получить объект ответа для его модификации, а затем вернуть его:
# @app.errorhandler(404)
# def not_found(error):
#     resp = make_response(render_template('error.html'), 404)
#     resp.headers['X-Something'] = 'A value'
#     return resp

# ** Далее рабочий код - начало
# @errors_blueprint.app_errorhandler(404)
# def render_pageNotFound(error):
#     resp = make_response(render_template("errors/404.html"), 404)
#     resp.headers['X-Something'] = 'A value'
#     print(resp, resp.headers['X-Something'])
#     return resp
# ** Далее рабочий код - конец
# Распечатали ответ в терминале     <Response 29993 bytes [404 NOT FOUND]> A value
# **** Ошибка 404 с получением объект внутри представдения - конец

# Ошибка 400
@errors_blueprint.app_errorhandler(400)
def render_bad_next(error):
    return render_template("errors/400.html"), 400

# Ошибка 413
@errors_blueprint.app_errorhandler(413)
def render_upload_large(error):
    max_size_file = current_app.config['MAX_CONTENT_LENGTH']
    return render_template("errors/413.html", max_size_file=max_size_file), 413

# Ошибка 500
# Задокументировала временно, чтобы видеть какие ошибки
# Представление для пользователя, можно дописать чтобы коды ошибки записывались куда-нибудь.
# ЧИТАТЬ ПОДРОБНЕЕ!!!
# https://flask.palletsprojects.com/en/1.1.x/errorhandling/

# @errors_blueprint.app_errorhandler(Exception)
# def handle_exception(e):
#     # print(e)
#     # print(HTTPException)
#     # pass through HTTP errors
#     if isinstance(e, HTTPException):
#         return e
#     # now you're handling non-HTTP exceptions only
#     return render_template("errors/500.html", e=e), 500
# Ошибка 500 - конец

