#!/usr/bin/env python2


from flask import Flask, render_template, request, session
from flask import redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categorie, Item, User
import hashlib

app = Flask(__name__)
app.secret_key = "mohamed%$#^&^%$ahmed@@#||L?>"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbsession = DBSession()


# Home Page
@app.route('/')
@app.route('/index')
def index():
    categories = dbsession.query(Categorie).all()
    return render_template('index.html', categories=categories)


@app.route('/Items/<int:categorie_id>')
def Items(categorie_id):
    categorie = dbsession.query(Categorie).filter_by(id=categorie_id).one()
    items = dbsession.query(Item).filter_by(categorie_id=categorie_id).all()
    return render_template('Items.html', categorie=categorie, items=items)


# Registration
@app.route('/Registration', methods=['GET', 'POST'])
def Registration():
    if request.method == 'GET':
        return render_template('Registration.html')
    if request.method == 'POST':
        user = dbsession.query(User).filter_by(
                username=request.form['username']).first()
        if user:
            flash('This username already exsists!')
            return redirect(url_for('Registration'))
        hash_object = hashlib.md5(request.form['passwd'].encode())
        user = User(name=request.form['fullname'],
                    username=request.form['username'],
                    passwd=hash_object.hexdigest())
        dbsession.add(user)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('Login'))


# Login
@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        session.pop('UserId', None)
        session.pop('Name', None)
        return render_template('Login.html')
    if request.method == 'POST':
        hash_object = hashlib.md5(request.form['passwd'].encode())
        user = dbsession.query(User).filter_by(
                username=request.form['username'],
                passwd=hash_object.hexdigest()).first()
        if user:
            session['UserId'] = user.id
            session['Name'] = user.name
            return redirect(url_for('AddCategorie'))
        else:
            flash('Incorrect username or password!')
            return redirect(url_for('Login'))


# Logout
@app.route('/Logout')
def Logout():
    session.pop('UserId', None)
    session.pop('Name', None)
    return redirect(url_for('index'))


# Insert new Categorie
@app.route('/NewCateogrie', methods=['GET', 'POST'])
def AddCategorie():
    if not session.get('UserId'):
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categories = dbsession.query(Categorie).filter_by(
                created_by=session['UserId']).all()
        return render_template('NewCategorie.html', categories=categories)
    if request.method == 'POST':
        categorie = dbsession.query(Categorie).filter_by(
                name=request.form['categoriename']).first()
        if categorie:
            flash('This categorie already exsist!')
            return redirect(url_for('AddCategorie'))
        categorie = Categorie(name=request.form['categoriename'],
                              created_by=session['UserId'])
        dbsession.add(categorie)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddCategorie'))


# Insert new Item
@app.route('/NewItem/<int:categorie_id>', methods=['GET', 'POST'])
def AddItem(categorie_id):
    if not session.get('UserId'):
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categorie = dbsession.query(Categorie).filter_by(id=categorie_id).one()
        items = dbsession.query(Item).filter_by(
                categorie_id=categorie_id).all()
        return render_template('CategorieItems.html', categorie=categorie,
                               items=items)
    if request.method == 'POST':
        item = Item(name=request.form['itemname'],
                    description=request.form['description'],
                    categorie_id=categorie_id)
        dbsession.add(item)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddItem', categorie_id=categorie_id))


# Edit Categorie
@app.route('/EditCateogrie/<int:categorie_id>', methods=['GET', 'POST'])
def EditCategorie(categorie_id):
    if not session.get('UserId'):
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categorie = dbsession.query(Categorie).filter_by(
                id=categorie_id, created_by=session['UserId']).one()
        return render_template('EditCategorie.html', categorie=categorie)
    if request.method == 'POST':
        categorie = dbsession.query(Categorie).filter_by(id=categorie_id).one()
        categorie.name = request.form['categoriename']
        dbsession.add(categorie)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddCategorie'))


# Edit Item
@app.route('/EditItem/<int:item_id>', methods=['GET', 'POST'])
def EditItem(item_id):
    if not session.get('UserId'):
        return redirect(url_for('Login'))
    if request.method == 'GET':
        item = dbsession.query(Item).filter_by(id=item_id).one()
        return render_template('EditItem.html', item=item)
    if request.method == 'POST':
        item = dbsession.query(Item).filter_by(id=item_id).one()
        item.name = request.form['itemname']
        item.description = request.form['item_description']
        dbsession.add(item)
        dbsession.commit()
        flash('Operation completed successfully')
        return redirect(url_for('AddItem', categorie_id=item.categorie_id))


# Delete Categorie
@app.route('/DeleteCategorie/<int:categorie_id>')
def DeleteCategorie(categorie_id):
    if not session.get('UserId'):
        return redirect(url_for('Login'))
    categorie = dbsession.query(Categorie).filter_by(id=categorie_id).one()
    items = dbsession.query(Item).filter_by(categorie_id=categorie_id).all()
    if items:
        for item in items:
            dbsession.delete(item)
    dbsession.commit()
    dbsession.delete(categorie)
    dbsession.commit()
    flash('Operation completed successfully')
    return redirect(url_for('AddCategorie'))


# Delete Item
@app.route('/DeleteItem/<int:item_id>')
def deleteItem(item_id):
    if not session.get('UserId'):
        return redirect(url_for('Login'))
    item = dbsession.query(Item).filter_by(id=item_id).one()
    categorie_id = item.categorie_id
    dbsession.delete(item)
    dbsession.commit()
    flash('Operation completed successfully')
    return redirect(url_for('AddItem', categorie_id=categorie_id))


# Return List of categories as Json
@app.route('/CategoriesJSON')
def CategoriesJSON():
    categories = dbsession.query(Categorie).all()
    return jsonify(categories=[i.serialize for i in categories])


# Return List of items as Json
@app.route('/ItemsJSON/<int:categorie_id>')
def ItemsJSON(categorie_id):
    items = dbsession.query(Item).filter_by(categorie_id=categorie_id).all()
    return jsonify(items=[i.serialize for i in items])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
