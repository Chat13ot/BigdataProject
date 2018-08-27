import elasticsearch
import json
from flask import Flask, request, redirect, session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import DataRequired
import datetime


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

class User(db.Model, UserMixin):
    seq = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    babyName = db.Column(db.String(255), nullable=False)
    birthDate = db.Column(db.Date, nullable=False)


class Role(db.Model, RoleMixin):
    seq = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    milkpowder = db.Column(db.String(100))
    diaper = db.Column(db.String(100))
    toy = db.Column(db.String(100))
    snack = db.Column(db.String(100))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class UserForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    babyName = StringField('babyName', validators=[DataRequired()])
    birthDate = DateField('birthDate', format="%m/%d/%Y", validators=[DataRequired()])

totalnums = []
titles = []
imgs = []
prices = []
urls = []
pageCount = 0

def productView(type=None):
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
    doc = es_client.search(index='_all', body={
        "query": {
            "match_phrase": {
                "title": search_term
            }
        }
    }, size=240)

    return doc

@app.route('/')
def index():

    # doc_diaper = productView('diaper')
    # totalnums.append(doc_diaper['hits']['total'])
    #
    # doc_milkpowder = productView('milkpowder')
    # totalnums.append(doc_milkpowder['hits']['total'])
    #
    # doc_snack = productView('snack')
    # totalnums.append(doc_snack['hits']['total'])
    #
    # doc_toy = productView('toy')
    # totalnums.append(doc_toy['hits']['total'])
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


@app.route('/register', methods=['POST','GET'])
def register():
    userform = UserForm()

    if request.method == 'POST':

        # User DB에 넣기
        user = User()
        user.id = userform.id._value()
        user.password = userform.password._value()
        user.babyName = userform.babyName._value()
        birthDate = userform.birthDate._value().split('/')

        user.birthDate = datetime.date(int(birthDate[2]), int(birthDate[0]), int(birthDate[1]))
        print(user.id + user.password + user.babyName)
        db.session.add(user)
        db.session.commit()
        return render_template('preference.html', user = user.id)

    return render_template('register.html', form=userform)

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

@app.route('/prefer', methods=['POST','GET'])
def prefer():

    if request.method == 'POST':
        user_id = request.form['user_id']
        milkpowder = request.form['milkpowder']
        diaper = request.form['diaper']
        toy = request.form['toy']
        snack = request.form['snack']

        print(user_id, milkpowder, diaper, toy, snack)

        role = Role()
        role.user_id = user_id
        role.milkpowder = milkpowder
        role.diaper = diaper
        role.toy = toy
        role.snack = snack

        db.session.add(role)
        db.session.commit()

        return redirect('/')

    return render_template('preference.html')


@app.route("/regVisitor", methods=["POST"])
def regVisitor():
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    print('lat: {0}, lng: {1}'.format(lat,lng))


@app.route('/login/11', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        userId = request.form['id']
        pwd = request.form['password']
        if len(userId) == 0 or len(pwd) == 0:
            return userId+', '+pwd+' 로그인 정보를 제대로 입력하지 않았습니다.'
        else:
            session['logFlag'] = True
            session['userId'] = userId

            user_pre= Role.query.filter_by(user_id=session['userId']).first()

            u_birthDate = User.query.filter_by(id=session['userId']).first().birthDate
            y = u_birthDate.year
            m = u_birthDate.month
            d = u_birthDate.day
            birth = datetime.datetime(y,m,d)
            now=datetime.datetime.now()

            u_age = int((now-birth).days /30)
            u_milkpowder = user_pre.milkpowder
            u_diaper = user_pre.diaper
            u_toy = user_pre.toy
            u_snack = user_pre.snack

            ## 로그인되어있는 유저정보
            session['user_age'] = u_age
            session['user_milkpowder'] = u_milkpowder
            session['user_diaper'] = u_diaper
            session['user_toy'] = u_toy
            session['u_sanck'] = u_snack

            print(u_age)
            return render_template('index.html', id=session['userId'])

    app.secret_key = 'sample_secreat_key'


    return render_template('login.html')


@app.route('/user', methods=['GET'])
def getUser():
    if session.get('logFlag') != True:
        return '잘못된 접근입니다.'

    userId = session['userId']
    user_age = session['user_age']
    user_milkpowder = session['user_milkpowder']
    user_diaper = session['user_diaper']
    user_toy = session['user_toy']
    u_sanck = session['u_sanck']

    global user_info
    user_info= [userId, user_age, user_milkpowder, user_diaper, user_toy, u_sanck]
    return '[USER INFORMATION] USER ID : {0}'.format(user_info)

@app.route('/logout')
def logout():
    session['userId'] = 0
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

