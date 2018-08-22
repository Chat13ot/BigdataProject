import elasticsearch
import json
from flask import Flask, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

app = Flask(__name__)
es_client = elasticsearch.Elasticsearch('localhost:9200')


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'ICIS'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False


db = SQLAlchemy(app)


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255))
    babyName = db.Column(db.String(255))
    birthDate = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    # 입력받을 사용자 정보는 여기다 추가하면됨.


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/shop-grid')
def shop_grid():
    return render_template('shop-grid.html')


@app.route('/search', methods=['POST'])
def search():
    titles = []
    imgs = []
    prices = []

    search_term = request.form['search']
    doc = es_client.search(index='_all', body={
        "query": {
            "match_phrase": {
                "title": search_term
            }
        }
    }, size=999)

    resultCount = len(doc['hits']['hits'])

    # for i in range(resultCount):
    #     print(json.dumps(doc['hits']['hits'][i]['_source'], ensure_ascii=False, indent=2))

    for i in range(resultCount):
        titles.append(doc['hits']['hits'][i]['_source']['title'])

    for i in range(resultCount):
        imgs.append(doc['hits']['hits'][i]['_source']['img'])

    for i in range(resultCount):
        prices.append(str(doc['hits']['hits'][i]['_source']['price']) + '원')

    return render_template('shop-grid.html', titles=titles, imgs=imgs, prices=prices)


if __name__ == '__main__':
    app.run()
