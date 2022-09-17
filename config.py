
import os

from os.path import join, dirname, realpath

db_path = os.environ.get('DATABASE_URL')
# Позже нужно сгенерировать хороший секретный ключ - см пояснения внизу
secret_key = os.environ.get("SECRET_KEY")
flaskapp = os.environ.get("FLASK_APP")


class Config:
    DEBUG = False
    FLASK_APP=flaskapp
    SECRET_KEY= secret_key
    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 16

class DevelopConfig:
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@127.0.0.1:5432/datarecl3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PASSWORD_MIN_LENGTH = 2
    PASSWORD_MAX_LENGTH = 10
    FLASK_ADMIN_FLUID_LAYOUT = True

    # CSRF_ENABLED активирует предотвращение поддельных межсайтовых запросов
    # нужен при работе с формами
    # см https://habr.com/ru/post/194062/
    CSRF_ENABLED = True

    # SECRET_KEY используется для создания криптографического токена,
    # кот. используется при валидации формы. Использовать секретный ключ кот. сложно подобрать!
    # см https://habr.com/ru/post/194062/ и степик
    SECRET_KEY= "randomstring"

    # Настройки для загрузки файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif', 'tif']
    # Директория для загрузки фото услуг (в корне)
    UPLOAD_PATH = join(dirname(realpath(__file__)), 'static/images/uploads/')
    CARDS_USLUGS_UPLOAD_PATH = join(dirname(realpath(__file__)), 'static/images/cards_uslugs/')
    # # UPLOAD_FOLDER = 'static/uploads/'
    # Директория для загрузки фото карусели (в корне)
    UPLOAD_CAROUSEL = join(dirname(realpath(__file__)), 'static/images/carousel/')
    # Настройки для загрузки файлов -  конец

    # Flask-Admin - задаем тему оформления.

    # Если FLASK_ADMIN_SWATCH нe определена то тема default
    # Значение переменной FLASK_ADMIN_SWATCH - это название папки с темой в каталоге
    # env/Lib/site-packages/flask-admin/static/bootstrap/bootstrap4(или 3,2)/swatch/темы

    # FLASK_ADMIN_SWATCH = 'cerulean'
    # FLASK_ADMIN_SWATCH = 'darkly'

    # +
    # FLASK_ADMIN_SWATCH = 'default'
    # FLASK_ADMIN_SWATCH = 'flatly'
    # FLASK_ADMIN_SWATCH = 'journal'
    # FLASK_ADMIN_SWATCH = 'litera'
    # FLASK_ADMIN_SWATCH = 'lumen'
    # FLASK_ADMIN_SWATCH = 'lux'
    # FLASK_ADMIN_SWATCH = 'materia'
    # FLASK_ADMIN_SWATCH = 'minty'
    # FLASK_ADMIN_SWATCH = 'pulse'
    # FLASK_ADMIN_SWATCH = 'sandstone'
    # FLASK_ADMIN_SWATCH = 'simplex'
    # FLASK_ADMIN_SWATCH = 'sketchy'
    # FLASK_ADMIN_SWATCH = 'slate'
    # FLASK_ADMIN_SWATCH = 'solar'

    # +
    # FLASK_ADMIN_SWATCH = 'spacelab'
    # FLASK_ADMIN_SWATCH = 'superhero'

    # +
    # FLASK_ADMIN_SWATCH = 'united'
    # FLASK_ADMIN_SWATCH = 'yeti'

    # Flask-Security
    # значения переменных нужно брать более сложные (где-то см как лучше генерировать)
    # и в рабочем проекте задавать через os.environ.get

    SECURITY_PASSWORD_SALT = 'salt'
    SECURITY_PASSWORD_HASH = 'bcrypt'


    # https://ploshadka.net/flask-delaem-avtorizaciju-na-sajjte/
    ################
    # Flask-Security
    ################

    # URLs
    SECURITY_URL_PREFIX = "/"
    SECURITY_LOGIN_URL = "/login/"
    SECURITY_LOGOUT_URL = "/logout/"
    # SECURITY_POST_LOGIN_VIEW = "/admin/"
    SECURITY_POST_LOGOUT_VIEW = "/admin/"
    SECURITY_POST_REGISTER_VIEW = "/admin/"

    # Включает регистрацию
    SECURITY_REGISTERABLE = True
    SECURITY_REGISTER_URL = "/register/"
    SECURITY_SEND_REGISTER_EMAIL = False

    # Включет сброс пароля
    SECURITY_RECOVERABLE = True
    SECURITY_RESET_URL = "/reset/"
    SECURITY_SEND_PASSWORD_RESET_EMAIL = True

    # Включает изменение пароля
    SECURITY_CHANGEABLE = True
    SECURITY_CHANGE_URL = "/change/"
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False



# Как генерировать хорошие секретные ключи
# стр. 22 https://buildmedia.readthedocs.org/media/pdf/flask-russian-docs/latest/flask-russian-docs.pdf
# Проблемой случайных значений является то, что трудно сказать, что действительно
# является является случайным. А секретный ключ должен быть настолько случайным,
# насколько это возможно. У вашей операционной системы есть способы для
# генерации достаточно случайных значений на базе криптографического случайного
# генератора, который может быть использован для получения таких ключей:
# >>> import os
# >>> os.urandom(24)
# '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
# Просто возьмите, скопируйте/вставьте это в ваш код, вот и готово.