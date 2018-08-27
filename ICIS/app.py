import elasticsearch
import datetime
import sqlite3
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import DataRequired
from sqlite3 import Error


app = Flask(__name__)
es_client = elasticsearch.Elasticsearch('localhost:9200')

app.secret_key = 'icis secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'ICIS'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['WTF_CSRF_SECRET_KEY'] = 'icissecrete'


db = SQLAlchemy(app)


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    seq = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    babyName = db.Column(db.String(255), nullable=False)
    birthDate = db.Column(db.Date, nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    # 입력받을 사용자 정보는 여기다 추가하면됨.


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class UserForm(Form):
    id = StringField('id', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    babyName = StringField('babyName', validators=[DataRequired()])
    birthDate = DateField('birthDate', validators=[DataRequired()])


totalnums = []
titles = []
imgs = []
prices = []
urls = []
pageCount = 0

diseases = {
    0: ['BCG', 'HBV'],
    1: ['HBV'],
    2: ['DTaP', 'Hib', 'IPV', 'PCV'],
    4: ['DTaP', 'Hib', 'IPV', 'PCV'],
    5: ['DTaP', 'Hib', 'IPV', 'PCV'],
    6: ['DTaP', 'Hib', 'IPV', 'PCV', 'HBV'],
    7: ['DTaP', 'Hib', 'IPV', 'PCV', 'HBV'],
    8: ['DTaP', 'Hib', 'IPV', 'PCV', 'HBV'],
    9: ['DTaP', 'Hib', 'IPV', 'PCV', 'HBV'],
    10: ['DTaP', 'Hib', 'IPV', 'PCV', 'HBV'],
    11: ['DTaP', 'Hib', 'IPV', 'PCV', 'HBV'],
    12: ['Hib', 'MMR', 'PCV', 'JE', 'VAR'],
    13: ['Hib', 'MMR', 'PCV', 'JE', 'VAR'],
    14: ['Hib', 'MMR', 'PCV', 'JE', 'VAR'],
    15: ['DTaP', 'Hib', 'MMR', 'PCV', 'JE', 'VAR'],
    16: ['DTaP', 'JE'],
    17: ['DTaP', 'JE'],
    18: ['DTaP', 'JE'],
    19: ['JE'],
    20: ['JE'],
    21: ['JE'],
    22: ['JE'],
    23: ['JE']
}


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def select_task(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT birthDate FROM user WHERE id=?", (id,))

    row = cur.fetchone()

    return row


def productView(type=None):
    if type == 'activity':
        doc = es_client.search(index=type, body={
            "query": {
                "bool": {
                    "must_not": [
                        {
                            "match": {
                                "title": "."
                            }
                        }
                    ]
                }
            }
        }, size=240)
    else:
        doc = es_client.search(index=type, body={
            "query": {
                "bool": {
                    "must_not": [
                        {
                            "match": {
                                "title": "."
                            }
                        }
                    ]
                }
            }
            , "sort": [
                {
                    "rating": {
                        "order": "desc"
                    }
                }
            ]
        }, size=240)

    return doc


def productSearch(search_term=None):
    doc = es_client.search(index=['diaper', 'milkpowder', 'snack', 'toy'], body={
        "query": {
            "match_phrase": {
                "title": search_term
            }
        }
    }, size=240)

    return doc


@app.route('/preference', methods=['POST','GET'])
def insert():
    userform = UserForm(FlaskForm)
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        babyName = request.form['babyName']
        birthDate = request.form['birthDate'].split('-')

        print(id, password, babyName, birthDate)

        # User DB에 넣기
        user = User()
        user.id = id
        user.password = password
        user.babyName = babyName
        user.birthDate = datetime.date(int(birthDate[0]), int(birthDate[1]), int(birthDate[2]))

        db.session.add(user)
        db.session.commit()

        return render_template('preference.html')

    # if request.method == 'POST':
    #     print('post!!!!!!!!!1')
    #     if userform.validate_on_submit():
    #         print(userform)
    #         print('된다!!!')
    #     else:
    #         print(userform)
    #         print(userform.id._value())
    #         print(userform.password._value())
    #         print(userform.babyName._value())
    #         print(userform.birthDate._value())


    # if form.validate_on_submit():
    #     print(form)
    #     return render_template('index.html')


@app.route('/')
def index():
    doc_diaper = productView('diaper')
    totalnums.append(doc_diaper['hits']['total'])

    doc_milkpowder = productView('milkpowder')
    totalnums.append(doc_milkpowder['hits']['total'])

    doc_snack = productView('snack')
    totalnums.append(doc_snack['hits']['total'])

    doc_toy = productView('toy')
    totalnums.append(doc_toy['hits']['total'])

    db = "/Users/keith_lee/PycharmProjects/ICIS/ICIS/user.db"
    conn = create_connection(db)

    with conn:
        birthDate = select_task(conn, 'asdf')

    print(birthDate[0])

    return render_template('index.html')


@app.route('/shop-grid')
def shop_grid():
    return render_template('shoplist_diaper.html')


@app.route('/search/<page>', methods=['GET', 'POST'])
def search(page=None):
    pageIndex = int(page)

    if request.method == 'POST':
        search_term = request.form['search']

        doc = productSearch(search_term)

        resultCount = len(doc['hits']['hits'])

        global titles
        global imgs
        global prices
        global urls
        titles = []
        imgs = []
        prices = []
        urls = []

        for item in doc['hits']['hits']:
            titles.append(item['_source']['title'])
            imgs.append(item['_source']['img'])
            prices.append(str(item['_source']['price']) + '원')
            urls.append(item['_source']['link'])

        global pageCount
        if resultCount % 12 == 0:
            pageCount = int(resultCount / 12)
        else:
            pageCount = int(resultCount / 12) + 1

        print(pageCount)

        return render_template('searchresult.html',
                               titles=titles[12 * (pageIndex-1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex-1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex-1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex-1): 12 * pageIndex],
                               currentpage=pageIndex-1,
                               totalnum=totalnums,
                               pageCount=pageCount)

    else:
        return render_template('searchresult.html',
                               titles=titles[12 * (pageIndex - 1):12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1):12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1):12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1):12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount)


@app.route('/register', methods=['POST', 'GET'])
def register():
    userform = UserForm(FlaskForm)

    if request.method == 'GET':
        if userform.validate_on_submit():
            print('응어차피get안써')

        return render_template('register.html', form=userform)

    else: ## method = 'POST'
        if userform.validate_on_submit():
            return render_template('preference.html')

        print(userform.id._value())
        print(userform.birthDate._value())

        return render_template('register.html', form=userform)


@app.route('/prefer')
def prefer():
    return render_template('preference.html')


@app.route('/products/diaper/<page>')
def productList_diaper(page=None):
    pageIndex = int(page)

    global titles
    global imgs
    global prices
    global urls

    titles = []
    imgs = []
    prices = []
    urls = []

    doc_diaper = productView('diaper')

    for item in doc_diaper['hits']['hits']:
        titles.append(item['_source']['title'])
        imgs.append(item['_source']['img'])
        prices.append(str(item['_source']['price']) + '원')
        urls.append(item['_source']['link'])

    resultCount = len(doc_diaper['hits']['hits'])
    global pageCount
    if resultCount % 12 == 0:
        pageCount = int(resultCount / 12)
    else:
        pageCount = int(resultCount / 12) + 1

    return render_template('shoplist_diaper.html',
                           titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                           imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                           prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                           urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                           currentpage=pageIndex - 1,
                           totalnum=totalnums,
                           pageCount=pageCount)


@app.route('/products/milkpowder/<page>')
def productList_milkpowder(page=None):
    pageIndex = int(page)

    global titles
    global imgs
    global prices
    global urls

    titles = []
    imgs = []
    prices = []
    urls = []

    doc_milkpowder = productView('milkpowder')

    for item in doc_milkpowder['hits']['hits']:
        titles.append(item['_source']['title'])
        imgs.append(item['_source']['img'])
        prices.append(str(item['_source']['price']) + '원')
        urls.append(item['_source']['link'])

    resultCount = len(doc_milkpowder['hits']['hits'])
    global pageCount
    if resultCount % 12 == 0:
        pageCount = int(resultCount / 12)
    else:
        pageCount = int(resultCount / 12) + 1

    return render_template('shoplist_milkpowder.html',
                           titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                           imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                           prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                           urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                           currentpage=pageIndex - 1,
                           totalnum=totalnums,
                           pageCount=pageCount)


@app.route('/products/snack/<page>')
def productList_snack(page=None):
    pageIndex = int(page)

    global titles
    global imgs
    global prices
    global urls

    titles = []
    imgs = []
    prices = []
    urls = []

    doc_snack = productView('snack')

    for item in doc_snack['hits']['hits']:
        titles.append(item['_source']['title'])
        imgs.append(item['_source']['img'])
        prices.append(str(item['_source']['price']) + '원')
        urls.append(item['_source']['link'])

    resultCount = len(doc_snack['hits']['hits'])
    global pageCount
    if resultCount % 12 == 0:
        pageCount = int(resultCount / 12)
    else:
        pageCount = int(resultCount / 12) + 1

    return render_template('shoplist_snack.html',
                           titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                           imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                           prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                           urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                           currentpage=pageIndex - 1,
                           totalnum=totalnums,
                           pageCount=pageCount)


@app.route('/products/toy/<page>')
def productList_toy(page=None):
    pageIndex = int(page)

    global titles
    global imgs
    global prices
    global urls

    titles = []
    imgs = []
    prices = []
    urls = []

    doc_toy = productView('toy')

    for item in doc_toy['hits']['hits']:
        titles.append(item['_source']['title'])
        imgs.append(item['_source']['img'])
        prices.append(str(item['_source']['price']) + '원')
        urls.append(item['_source']['link'])

    resultCount = len(doc_toy['hits']['hits'])
    global pageCount
    if resultCount % 12 == 0:
        pageCount = int(resultCount / 12)
    else:
        pageCount = int(resultCount / 12) + 1

    return render_template('shoplist_toy.html',
                           titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                           imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                           prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                           urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                           currentpage=pageIndex - 1,
                           totalnum=totalnums,
                           pageCount=pageCount)


@app.route('/activity/<page>')
def activityList(page=None):
    pageIndex = int(page)

    global titles
    global imgs
    global prices
    global urls

    titles = []
    imgs = []
    prices = []
    urls = []

    doc_activity = productView('activity')

    for item in doc_activity['hits']['hits']:
        titles.append(item['_source']['title'])
        imgs.append(item['_source']['image'])
        prices.append(item['_source']['cost'])
        urls.append(item['_source']['link'])

    resultCount = len(doc_activity['hits']['hits'])
    global pageCount
    if resultCount % 12 == 0:
        pageCount = int(resultCount / 12)
    else:
        pageCount = int(resultCount / 12) + 1

    return render_template('activitylist.html',
                           titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                           imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                           prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                           urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                           currentpage=pageIndex - 1,
                           totalnum=totalnums,
                           pageCount=pageCount)


if __name__ == '__main__':
    app.run()
