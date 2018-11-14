#!/usr/bin/env python2


from flask import Flask, render_template, request, session
from flask import redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categorie, Item
from flask_oauth import OAuth
import json

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '59212569067-j9mbu9odf67kchpi8g5d0gcd24odhtso.apps.googleus'
GOOGLE_CLIENT_ID += 'ercontent.com'
GOOGLE_CLIENT_SECRET = 'Ce_r84pKBmnz-eh5v7Sc0A5Q'
REDIRECT_URI = '/oauth2callback'  # Redirect URIs from Google APIs console
oauth = OAuth()
authorize_url = 'https://accounts.google.com/o/oauth2/auth'
scope = 'https://www.googleapis.com/auth/userinfo.email'
access_token_url = 'https://accounts.google.com/o/oauth2/token'
grant_type = 'authorization_code'
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url=authorize_url,
                          request_token_url=None,
                          request_token_params={'scope': scope,
                                                'response_type': 'code'},
                          access_token_url=access_token_url,
                          access_token_method='POST',
                          access_token_params={'grant_type': grant_type},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

app = Flask(__name__)
app.secret_key = "mohamed%$#^&^%$ahmed@@#||L?>"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

MyDbSession = sessionmaker(bind=engine)


@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
        data = json.load(res)
        session['Email'] = data['email']
        session['Name'] = data['name']
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('Login'))
    return redirect(url_for('AddCategorie'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


# Home Page list all available categories
@app.route('/')
@app.route('/index')
def index():
    dbsession = MyDbSession()
    categories = dbsession.query(Categorie).all()
    return render_template('index.html', categories=categories)


# list all available items
@app.route('/Items/<int:categorie_id>')
def Items(categorie_id):
    dbsession = MyDbSession()
    categorie = dbsession.query(Categorie).filter_by(id=categorie_id).one()
    items = dbsession.query(Item).filter_by(categorie_id=categorie_id).all()
    return render_template('Items.html', categorie=categorie, items=items)


# Login
@app.route('/Login')
def Login():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


# Logout
@app.route('/Logout')
def Logout():
    if session:
        session.clear()
    return redirect(url_for('index'))


# Insert new Categorie
@app.route('/NewCateogrie', methods=['GET', 'POST'])
def AddCategorie():
    dbsession = MyDbSession()
    if not session.get('Email'):
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categories = dbsession.query(Categorie).filter_by(
                created_by=session.get('Email')).all()
        return render_template('NewCategorie.html', categories=categories)
    if request.method == 'POST':
        categorie = dbsession.query(Categorie).filter_by(
                name=request.form['categoriename']).first()
        if categorie:
            flash('This categorie already exsist!')
            return redirect(url_for('AddCategorie'))
        categorie = Categorie(name=request.form['categoriename'],
                              created_by=session.get('Email'))
        dbsession.add(categorie)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddCategorie'))


# Insert new Item
@app.route('/NewItem/<int:categorie_id>', methods=['GET', 'POST'])
def AddItem(categorie_id):
    dbsession = MyDbSession()
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categorie = dbsession.query(Categorie).filter_by(
                id=categorie_id, created_by=session.get('Email')).first()
        if categorie is None:
            flash('No data found!')
            return redirect(url_for('AddCategorie'))
        items = dbsession.query(Item).filter_by(
                categorie_id=categorie_id,
                created_by=session.get('Email')).all()
        return render_template('CategorieItems.html', categorie=categorie,
                               items=items)
    if request.method == 'POST':
        item = Item(name=request.form['itemname'],
                    description=request.form['description'],
                    categorie_id=categorie_id, created_by=session.get('Email'))
        dbsession.add(item)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddItem', categorie_id=categorie_id))


# Edit Categorie
@app.route('/EditCateogrie/<int:categorie_id>', methods=['GET', 'POST'])
def EditCategorie(categorie_id):
    dbsession = MyDbSession()
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categorie = dbsession.query(Categorie).filter_by(
                id=categorie_id, created_by=session.get('Email')).first()
        if categorie is None:
            flash('No data found!')
            return redirect(url_for('AddCategorie'))
        return render_template('EditCategorie.html', categorie=categorie)
    if request.method == 'POST':
        categorie = dbsession.query(Categorie).filter_by(
                id=categorie_id, created_by=session.get('Email')).one()
        categorie.name = request.form['categoriename']
        dbsession.add(categorie)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddCategorie'))


# Edit Item
@app.route('/EditItem/<int:item_id>', methods=['GET', 'POST'])
def EditItem(item_id):
    dbsession = MyDbSession()
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('Login'))
    if request.method == 'GET':
        item = dbsession.query(Item).filter_by(
                id=item_id, created_by=session.get('Email')).first()
        if item is None:
            flash('No data found!')
            return redirect(url_for('AddCategorie'))
        return render_template('EditItem.html', item=item)
    if request.method == 'POST':
        item = dbsession.query(Item).filter_by(
                id=item_id, created_by=session.get('Email')).one()
        item.name = request.form['itemname']
        item.description = request.form['item_description']
        dbsession.add(item)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddItem', categorie_id=item.categorie_id))


# Delete Categorie
@app.route('/DeleteCategorie/<int:categorie_id>')
def DeleteCategorie(categorie_id):
    dbsession = MyDbSession()
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('Login'))
    categorie = dbsession.query(Categorie).filter_by(
            id=categorie_id, created_by=session.get('Email')).one()
    dbsession.delete(categorie)
    dbsession.commit()
    flash('Operation completed successfully')
    return redirect(url_for('AddCategorie'))


# Delete Item
@app.route('/DeleteItem/<int:item_id>')
def deleteItem(item_id):
    dbsession = MyDbSession()
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('Login'))
    item = dbsession.query(Item).filter_by(
            id=item_id, created_by=session.get('Email')).one()
    categorie_id = item.categorie_id
    dbsession.delete(item)
    dbsession.commit()
    flash('Operation completed successfully')
    return redirect(url_for('AddItem', categorie_id=categorie_id))


# Return List of categories as Json
@app.route('/CategoriesJSON')
def CategoriesJSON():
    dbsession = MyDbSession()
    categories = dbsession.query(Categorie).filter_by(
            created_by=session.get('Email')).all()
    return jsonify(categories=[i.serialize for i in categories])


# Return categorie as Json
@app.route('/CategorieJSON/<int:categorie_id>')
def CategorieJSON(categorie_id):
    dbsession = MyDbSession()
    categorie = dbsession.query(Categorie).filter_by(
            id=categorie_id, created_by=session.get('Email')).one()
    return jsonify(categorie=categorie.serialize)


# Return List of items as Json
@app.route('/ItemsJSON/<int:categorie_id>')
def ItemsJSON(categorie_id):
    dbsession = MyDbSession()
    items = dbsession.query(Item).filter_by(
            categorie_id=categorie_id, created_by=session.get('Email')).all()
    return jsonify(items=[i.serialize for i in items])


# Return item as Json
@app.route('/ItemJSON/<int:item_id>')
def ItemJSON(item_id):
    dbsession = MyDbSession()
    item = dbsession.query(Item).filter_by(
            id=item_id, created_by=session.get('Email')).one()
    return jsonify(item=item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=8000)
