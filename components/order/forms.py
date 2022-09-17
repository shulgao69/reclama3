
from flask_wtf import FlaskForm

from wtforms import SubmitField, SelectField, HiddenField, BooleanField, StringField, \
    PasswordField, IntegerField, validators, DateField, DateTimeField, TelField, RadioField
from wtforms.validators import InputRequired, Length, Email, DataRequired, EqualTo, Regexp, ValidationError

# импорты для загрузки файлов - начало
from flask_wtf.file import FileField, FileAllowed, FileRequired
# from werkzeug.utils import secure_filename
# импорты для загрузки файлов - конец

# Задавала длину пароля для валидации, так как не могла импортировать данные из конфига,
# но позже (см ниже) все получилось, поэтому закоммитила
# password_length = 2

# *** Получение данных для валидации (PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH) из файла config.py - начало
# Следующие импорты нужны для того чтобы загрузить данные из корневого файла config.py
# и затем использовать для получения значения
# app.config['PASSWORD_MIN_LENGTH'] и app.config['PASSWORD_MAX_LENGTH']
# Если же попытаться  сделать такой импорт
# from RECL.__init__ import app
# а затем получать значение app.config['PASSWORD_MIN_LENGTH']
# то выдает ошибку импорта app. В блюпринте админки такой импорт почему-то ошибки не дает! Разобраться!!
# НЕ ЗАБЫТЬ ПОМЕНЯТЬ ПОТОМ (при запуске на продакшн)
# app.config.from_object(DevelopConfig) на app.config.from_object(Config)!!!
from flask import Flask
from RECL.config import DevelopConfig, Config
app = Flask(__name__)
app.config.from_object(DevelopConfig)
# *** Получение данных для валидации (PASSWORD_MIN_LENGTH) из корневого файла config.py - конец

# *** Форма заявки (Application) - начало
class ApplicationForm(FlaskForm):

    # СМ регулярные выражения!!!
    # стр Word про регулярки на рабочем столе
    # https://qna.habr.com/q/84360 (Юрий Лобанов
    # https://www.google.ru/search?q=%D1%80%D0%B5%D0%B3%...)

    # Регулярное выражение для валидации номера телефона:(Ориентировано на российские мобильные + городские с кодом из 3 цифр (например, Москва).)
    # https://habr.com/ru/post/110731/
    # вар1
    # user_phone = TelField("Телефон", [InputRequired(), Regexp("^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$", message='Неверный формат телефона...')])

    # вар2
    # Regexp("^((8|\+7)[\- ]?)?(\(?\d{3,4}\)?[\- ]?)?[\d\- ]{5,10}$"
    # https://qna.habr.com/q/84360 Алексей @kerner Автор вопроса

    # Я написала свою регулярку!!!
    # ^(\+)?(7|8)?(\s)*?(\-)?(\()?\d{3,5}(\))?(\s)*?(\-)?\d{1,3}(\s)*?(\-)?\d{2}(\s)*?(\-)?\d{2}(\s)*$
    # Внимание!! К ней нужно доп. проверку (в валидаторе) на кол-во цифр в номере не более 11(с 7 или 8)
    # (7(8)9998886655)  не менее 10 т.к. в регулярке задано максимальное количество 13(специально!)
    # тк формат номеров может быть разный и соответственно люди могут его набирать по разному
    # (см ниже и стр Word про регулярки на рабочем столе)

    # В словаре render_kw={....} можно задать атрибуты поля,
    # которые (если не используется Flask-wtform) можно задать в теге <input>
    # перечень этих атрибутов см например http://htmlbook.ru/html/input
    # Какие из этих атрибутов будут работать - не знаю, не все проверяла
    # Такие работают - проверяла:
    # 'autofocus': True/False, 'placeholder': "name@mail.ru",
    # disabled': True/False, 'readonly': True/False
    # у нас это - автофокус (autofocus': True) и placeholder (образец заполнения поля (подсказка))
    # если например задать 'disabled': True или 'readonly': True то поле будет не активным.
    # Но тогда если задать валидатор InputRequired то все время будет ругаться
    # что поле должно быть заполнено. Поэтому внимательно с render_kw
    # user_phone = TelField("Введите телефон",
    #                       [InputRequired(), Regexp("^(\+)?(7|8)?(\s)*?(\-)?(\()?\d{3,5}(\))?(\s)*?(\-)?\d{1,3}(\s)*?(\-)?\d{2}(\s)*?(\-)?\d{2}(\s)*$",
    #                                                message='Неверный формат телефона...')],
    #                       render_kw={'autofocus': True, 'placeholder': "+7(___)___-__-__" })
    # Пока оставляю 'placeholder': "+7(___)___-__-__" но подумать стоит ли задавать образец для пользователя
    # может быть это будет усложнять для тех у кого например городской номер и шаблон тогда у них другой

    user_phone = TelField("Введите телефон",
                          [InputRequired(message='Номер не введен')],
                          render_kw={'autofocus': True, 'placeholder': "+7(___)___-__-__" }
                          )

    user_first_name = StringField("Введите имя", [InputRequired()],
                            render_kw={'autofocus': True, 'placeholder': "Имя" }
                            )

    user_surname = StringField("Введите фамилию", [InputRequired()],
                            render_kw={'autofocus': True, 'placeholder': "Фамилия" }
                            )

    # Подтверждение что user - юридическое лицо
    user_organization = RadioField("Плательщик", [InputRequired()], default='value_one', choices=[('value_one', 'юридическое лицо'),
                          ('value_two', 'индивидуальный предприниматель'), ('value_three', 'частное лицо')])

    # Согласие на обработку персональных данных
    user_consent = BooleanField("Согласен на обработку персональных данных", default=True)


    submit = SubmitField('Сохранить')

    # *** задаю свой валидатор. он добавиться к имеющимся в списке в поле формы - начало
    # проверяю введенный пользователем тел., кот. уже провалидирован с помощью Regexp из поля user_phone
    # на общее кол-во цифр (отметая все прочие символы(скобки, пробелы, + и тп))
    # https://www.cyberforum.ru/python-beginners/thread1881698.html (Ennjin 103 / 81 / 54 Регистрация: 25.11.2016 Сообщений: 278)
    # их должно быть 11(с7 или 8)или 10(если пользователь ввел без 7 или 8)
    # Можно было задать жестче в Regexp(например Номер телефона(Россия): ^((\+7|7|8)+([0-9]){10})$))
    # или жесткий шаблон для мобильных, но не стала этого специально, оставляя пользователю больше шансов на ошибку при вводе
    # Далее в коде py буду этот тел сохранять в базе в международном формате как +75554443322
    # удаляя все лишние символы или добавляя +7 если задано без него
    # (анализ введенной строки начиная с конца)
    # имя функции при этом должно быть таким: validate_имя валидируемого поля
    def validate_user_phone(form, field):

        if field.data:
            num = [int(i) for i in field.data if i.isdigit()]
            print('num=', num, 'len(num)=', len(num))
            if len(num)>11:
                raise ValidationError('Телефон должен быть не более 11 цифр')
            if len(num)<10:
                raise ValidationError('Телефон должен быть не менее 10 цифр')
    # *** задаю свой валидатор. он добавиться к имеющимся в списке в поле формы - конец



    # order = StringField("Параметры заказа", [InputRequired()])
    # user_id = HiddenField("Пользователь")

# *** Форма заявки (Application) - конец