import elasticsearch
import datetime
import sqlite3
from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import DataRequired
from recommendation import milkpowder, diaper, toy, snack


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

lat = 37.5835642
lng = 127.02895470000001

diseases = {
    0: ['BCG(결핵 예방접종)(결핵 예방접종)', 'HBV(B형간염 예방접종)'],
    1: ['HBV(B형간염 예방접종)'],
    2: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)'],
    4: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)'],
    5: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)'],
    6: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)', 'HBV(B형간염 예방접종)'],
    7: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)', 'HBV(B형간염 예방접종)'],
    8: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)', 'HBV(B형간염 예방접종)'],
    9: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)', 'HBV(B형간염 예방접종)'],
    10: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)', 'HBV(B형간염 예방접종)'],
    11: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'IPV(폴리오 예방접종)', 'PCV(폐구균 예방접종)', 'HBV(B형간염 예방접종)'],
    12: ['Hib(뇌수막염 예방접종)', 'MMR(홍역, 유행성 이하선염, 풍진 예방접종)', 'PCV(폐구균 예방접종)', 'JE(일본뇌염 예방접종)', 'VAR(수두 예방접종)'],
    13: ['Hib(뇌수막염 예방접종)', 'MMR(홍역, 유행성 이하선염, 풍진 예방접종)', 'PCV(폐구균 예방접종)', 'JE(일본뇌염 예방접종)', 'VAR(수두 예방접종)'],
    14: ['Hib(뇌수막염 예방접종)', 'MMR(홍역, 유행성 이하선염, 풍진 예방접종)', 'PCV(폐구균 예방접종)', 'JE(일본뇌염 예방접종)', 'VAR(수두 예방접종)'],
    15: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'Hib(뇌수막염 예방접종)', 'MMR(홍역, 유행성 이하선염, 풍진 예방접종)', 'PCV(폐구균 예방접종)', 'JE(일본뇌염 예방접종)', 'VAR(수두 예방접종)'],
    16: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'JE(일본뇌염 예방접종)'],
    17: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'JE(일본뇌염 예방접종)'],
    18: ['DTaP(디프테리아, 백일해, 파상풍 예방접종)', 'JE(일본뇌염 예방접종)'],
    19: ['JE(일본뇌염 예방접종)'],
    20: ['JE(일본뇌염 예방접종)'],
    21: ['JE(일본뇌염 예방접종)'],
    22: ['JE(일본뇌염 예방접종)'],
    23: ['JE(일본뇌염 예방접종)']
}


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


def diseaseSearch(type=None, lat=None, lon=None):
    if type == 'BCG(결핵 예방접종)(결핵 예방접종)':
        searchIndex = 'disease_bcg_v2'
    elif type == 'HBV(B형간염 예방접종)':
        searchIndex = 'disease_hbv_v2'
    elif type == 'DTaP(디프테리아, 백일해, 파상풍 예방접종)':
        searchIndex = 'disease_dtap_v2'
    # elif type == 'Hib(뇌수막염 예방접종)':
    elif 'Hib' in type:
        searchIndex = 'disease_hib_v2'
    elif type == 'MMR(홍역, 유행성 이하선염, 풍진 예방접종)':
        searchIndex = 'disease_mmr_v2'
    elif type == 'PCV(폐구균 예방접종)':
        searchIndex = 'disease_pcv_v2'
    elif type == 'JE(일본뇌염 예방접종)':
        searchIndex = 'disease_je_v2'
    elif type == 'VAR(수두 예방접종)':
        searchIndex = 'disease_var_v2'
    elif type == 'IPV(폴리오 예방접종)':
        searchIndex = 'disease_ipv_v2'

    doc = es_client.search(index=searchIndex, body={
        "query": {
            "bool": {
                "filter": {
                    "geo_distance": {
                        "distance": "3km",
                        "location": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
            }
        }
    }, size=20)

    return doc


def user_recommendation_diaper(brand_term=None):
    doc = es_client.search(index='diaper', body={
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "title": brand_term
                    }
                }
            }
        }
    }, size=1)

    return doc


def user_recommendation_milkpowder(brand_term=None):
    doc = es_client.search(index='milkpowder', body={
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "title": brand_term
                    }
                }
            }
        }
    }, size=1)

    return doc


def user_recommendation_snack(brand_term=None):
    doc = es_client.search(index='snack', body={
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "title": brand_term
                    }
                }
            }
        }
    }, size=1)

    return doc


def user_recommendation_toy(brand_term=None):
    doc = es_client.search(index='toy', body={
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "title": brand_term
                    }
                }
            }
        }
    }, size=1)

    return doc


@app.route('/')
def index(session=session):
    global lat
    global lng

    doc_diaper = productView('diaper')
    totalnums.append(doc_diaper['hits']['total'])

    doc_milkpowder = productView('milkpowder')
    totalnums.append(doc_milkpowder['hits']['total'])

    doc_snack = productView('snack')
    totalnums.append(doc_snack['hits']['total'])

    doc_toy = productView('toy')
    totalnums.append(doc_toy['hits']['total'])

    print(lat, lng)

    if len(session) == 0:
        return render_template('index.html')
    else:
        print(session)
        conn = sqlite3.connect('user.db')
        cur = conn.cursor()

        cur.execute("SELECT milkpowder from role where user_id=?", (session['userId'],))
        milksession = cur.fetchone()[0]
        milkpowder_terms = milkpowder(milksession)

        cur.execute("SELECT diaper from role where user_id=?", (session['userId'],))
        diapersession = cur.fetchone()[0]
        diaper_terms = diaper(diapersession)

        cur.execute("SELECT toy from role where user_id=?", (session['userId'],))
        toysession = cur.fetchone()[0]
        toy_term = toy(toysession)

        cur.execute("SELECT snack from role where user_id=?", (session['userId'],))
        snacksession = cur.fetchone()[0]
        snack_term = snack(snacksession)

        rec_milkpowder = user_recommendation_milkpowder(milkpowder_terms)['hits']['hits']
        rec_diaper = user_recommendation_diaper(diaper_terms)['hits']['hits']
        rec_toy = user_recommendation_toy(toy_term)['hits']['hits']
        rec_snack = user_recommendation_snack(snack_term)['hits']['hits']

        milkpowderResult = []
        milkpowderResult.append(rec_milkpowder[0]['_source']['title'])
        milkpowderResult.append(rec_milkpowder[0]['_source']['img'])
        milkpowderResult.append(rec_milkpowder[0]['_source']['price'])
        milkpowderResult.append(rec_milkpowder[0]['_source']['link'])

        diaperResult = []
        diaperResult.append(rec_diaper[0]['_source']['title'])
        diaperResult.append(rec_diaper[0]['_source']['img'])
        diaperResult.append(rec_diaper[0]['_source']['price'])
        diaperResult.append(rec_diaper[0]['_source']['link'])

        toyResult = []
        toyResult.append(rec_toy[0]['_source']['title'])
        toyResult.append(rec_toy[0]['_source']['img'])
        toyResult.append(rec_toy[0]['_source']['price'])
        toyResult.append(rec_toy[0]['_source']['link'])

        snackResult = []
        snackResult.append(rec_snack[0]['_source']['title'])
        snackResult.append(rec_snack[0]['_source']['img'])
        snackResult.append(rec_snack[0]['_source']['price'])
        snackResult.append(rec_snack[0]['_source']['link'])

        u_birthDate = User.query.filter_by(id=session['userId']).first().birthDate
        y = u_birthDate.year
        m = u_birthDate.month
        d = u_birthDate.day
        birth = datetime.datetime(y, m, d)
        now = datetime.datetime.now()
        u_age = int((now - birth).days / 30)

        if 0 <= u_age <= 23:
            diseaseList = diseases[u_age]
            diseaseCount = len(diseaseList)

        diseaseResult = []

        for item in diseaseList:
            diseaseResult.append(diseaseSearch(item, lat, lng))

        lats = []
        lngs = []
        names = []
        numbers = []

        diseaseResult = diseaseResult[0]['hits']['hits'][:20]

        print(len(diseaseResult))
        print(diseaseResult[0])

        for i in range(20):
            lats.append(diseaseResult[i]['_source']['lat'])
            lngs.append(diseaseResult[i]['_source']['lng'])
            names.append(diseaseResult[i]['_source']['name'])
            numbers.append(diseaseResult[i]['_source']['number'])

        return render_template('index.html', id=session['userId'], milkpowderResult=milkpowderResult,
                               diaperResult=diaperResult, toyResult=toyResult, snackResult=snackResult,
                               names=names, numbers=numbers,
                               lats=lats, lngs=lngs, diseaseList=diseaseList, diseaseCount=diseaseCount)




# @app.route('/', methods=['POST'])
# def advancedIndex():
#     global lat
#     global lng
#
#     type = request.form['term']
#
#     u_birthDate = User.query.filter_by(id=session['userId']).first().birthDate
#     y = u_birthDate.year
#     m = u_birthDate.month
#     d = u_birthDate.day
#     birth = datetime.datetime(y, m, d)
#     now = datetime.datetime.now()
#     u_age = int((now - birth).days / 30)
#
#     print(len(type))
#
#     if 0 <= u_age <= 23:
#         diseaseList = diseases[u_age]
#         diseaseCount = len(diseaseList)
#
#     diseaseResult = diseaseSearch(type, lat, lng)
#
#     lats = []
#     lngs = []
#     names = []
#     numbers = []
#
#     for item in diseaseResult:
#         lats.append(item['lat'])
#         lngs.append(item['lng'])
#         names.append(item['name'])
#         numbers.append(item['number'])
#
#     return render_template('index.html', id=session['userId'], diseaseList=diseaseList, diseaseCount=diseaseCount,
#                            do=True, lats=lats, lngs=lngs, names=names, numbers=numbers)


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

        if len(session) == 0:
            return render_template('searchresult.html',
                                   titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                                   imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                                   prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                                   urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                                   currentpage=pageIndex - 1,
                                   totalnum=totalnums,
                                   pageCount=pageCount)
        else:
            return render_template('searchresult.html',
                                   titles=titles[12 * (pageIndex-1): 12 * pageIndex],
                                   imgs=imgs[12 * (pageIndex-1): 12 * pageIndex],
                                   prices=prices[12 * (pageIndex-1): 12 * pageIndex],
                                   urls=urls[12 * (pageIndex-1): 12 * pageIndex],
                                   currentpage=pageIndex-1,
                                   totalnum=totalnums,
                                   pageCount=pageCount,
                                   id=session['userId'])

    else:
        if len(session) == 0:
            return render_template('searchresult.html',
                                   titles=titles[12 * (pageIndex - 1):12 * pageIndex],
                                   imgs=imgs[12 * (pageIndex - 1):12 * pageIndex],
                                   prices=prices[12 * (pageIndex - 1):12 * pageIndex],
                                   urls=urls[12 * (pageIndex - 1):12 * pageIndex],
                                   currentpage=pageIndex - 1,
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
                                   pageCount=pageCount,
                                   id=session['userId'])


@app.route('/register', methods=['POST', 'GET'])
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

    if len(session) == 0:
        return render_template('shoplist_diaper.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount)
    else:
        return render_template('shoplist_diaper.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount,
                               id=session['userId'])


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

    if len(session) == 0:
        return render_template('shoplist_milkpowder.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount)
    else:
        return render_template('shoplist_milkpowder.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount,
                               id=session['userId'])


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

    if len(session) == 0:
        return render_template('shoplist_snack.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount)
    else:
        return render_template('shoplist_snack.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount,
                               id=session['userId'])


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

    if len(session) == 0:
        return render_template('shoplist_toy.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount)
    else:
        return render_template('shoplist_toy.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount,
                               id=session['userId'])


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

    if len(session) == 0:
        return render_template('activitylist.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount)
    else:
        return render_template('activitylist.html',
                               titles=titles[12 * (pageIndex - 1): 12 * pageIndex],
                               imgs=imgs[12 * (pageIndex - 1): 12 * pageIndex],
                               prices=prices[12 * (pageIndex - 1): 12 * pageIndex],
                               urls=urls[12 * (pageIndex - 1): 12 * pageIndex],
                               currentpage=pageIndex - 1,
                               totalnum=totalnums,
                               pageCount=pageCount,
                               id=session['userId'])


@app.route('/prefer', methods=['POST', 'GET'])
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

        return render_template('index.html')

    return render_template('preference.html')


@app.route("/regVisitor", methods=["POST"])
def regVisitor():
    global lat
    global lng

    lat = request.form.get("lat")
    lng = request.form.get("lng")
    print('lat: {0}, lng: {1}'.format(lat, lng))
    return None


@app.route('/login/11', methods=['GET', 'POST'])
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

            return redirect('/')

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
    user_info = [userId, user_age, user_milkpowder, user_diaper, user_toy, u_sanck]
    return '[USER INFORMATION] USER ID : {0}'.format(user_info)


@app.route('/logout/11')
def logout():
    session.clear()
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
