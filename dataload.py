import json

from models import Link, db, Usluga
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@127.0.0.1:5432/datarecl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


# Выгрузила данные в базу. Делала сначала links, а потом uslugi (а links коментировала)
with open("links.json", "r", encoding='utf-8') as f:
    contentlinks = f.read()
    link_menu = json.loads(contentlinks)
    for l in link_menu:
        links = Link(link = l['link'], title = l['title'])
        db.session.add(links)
db.session.commit()

with open("uslugi.json", "r", encoding='utf-8') as f:
    contentuslugi = f.read()
    all_uslugi = json.loads(contentuslugi)
    for u in all_uslugi:
        goal = db.session.query(Link).filter(Link.link == u['punkt_menu']).first()
        usluga = Usluga(link = u['link'], title = u['title'], punkt_menu_id=goal.id)
        db.session.add(usluga)
db.session.commit()




    # for content in contents:
    #     print(content)
    #     category = Category(id = categories["id"], title = categories["title"])
#         db.session.add(category)
# db.session.commit()
#
#
#
#
# with open("uslugi.json", "r", encoding='utf-8') as f:
#    contents = f.read()
#    uslugi = json.loads(contents)
#
#
#
#
#    import csv
#
# from models import Category, db, Meal
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dumpoajnlbgfej:0681e4f8d1092238ad96551fd93183acc14edcea315366f813f6bc3b6896f618@ec2-52-48-65-240.eu-west-1.compute.amazonaws.com:5432/d50i8q61j3c5oq'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# db = SQLAlchemy(app)
#
# with open("delivery_categories.csv", "r", encoding="utf-8") as ff:
#     delivery_categories = csv.DictReader(ff, delimiter=',')
#     for categories in delivery_categories:
#         category = Category(id = categories["id"], title = categories["title"])
#         db.session.add(category)
# db.session.commit()
#
# with open("delivery_items.csv", "r", encoding="utf-8") as f_obj:
#     delivery_items = csv.DictReader(f_obj, delimiter=',')
#
#     for items in delivery_items:
#         meal = Meal(id = items["id"], title = items["title"], price = items["price"],
#                     description = items["description"], picture = items["picture"], categories_id = items["category_id"])
#         db.session.add(meal)
# db.session.commit()
