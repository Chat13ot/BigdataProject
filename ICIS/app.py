import elasticsearch
import json
from flask import Flask, request
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


@app.route('/register', methods=['POST','GET'])
def register():
    userform = UserForm(FlaskForm)

    if request.method == 'GET':
        if userform.validate_on_submit():
            print('응어차피get안써')

        return render_template('register.html', form = userform)

    else: ## method = 'POST'
        if userform.validate_on_submit():
            return render_template('preference.html')

        print(userform.id._value())
        print(userform.birthDate._value())

        return render_template('register.html', form=userform)

@app.route('/prefer')
def prefer():
    return render_template('preference.html')

if __name__ == '__main__':
    app.run()
