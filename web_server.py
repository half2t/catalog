#!/usr/bin/env python2


from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categorie, Item, User
import hashlib

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Home Page
@app.route('/')
@app.route('/index')
def index():
    categories = session.query(Categorie).all()
    return render_template('index.html', categories=categories)


@app.route('/Items/<int:categorie_id>')
def Items(categorie_id):
    categorie = session.query(Categorie).filter_by(id=categorie_id).one()
    items = session.query(Item).filter_by(categorie_id=categorie_id).all()
    return render_template('Items.html', categorie=categorie, items=items)


# Registration
@app.route('/Registration', methods=['GET','POST'])
def Registration():
    if request.method == 'GET':
        return render_template('Registration.html')
    if request.method == 'POST':
        hash_object = hashlib.md5(request.form['passwd'].encode())
        user = User(name=request.form['fullname'], 
                    username=request.form['username'], 
                    passwd=hash_object.hexdigest())
        session.add(user)
        session.commit()
        return redirect(url_for('Login'))
    
# Login  
@app.route('/Login', methods=['GET','POST'])
def Login():
    if request.method == 'GET':
        return render_template('Login.html')
    if request.method == 'POST':
        hash_object = hashlib.md5(request.form['passwd'].encode())
        user = session.query(User).filter_by(username=request.form['username'],
                            passwd=hash_object.hexdigest()).first()
        if user:
          resp = make_response(redirect(url_for('AddCategorie')))
          resp.set_cookie('user_cookie', user.id)
          return resp
        else:
            return redirect(url_for('Login'))
        
        
# Logout
@app.route('/Logout')
def Logout():
    resp = make_response(redirect(url_for('Login')))
    resp.set_cookie('user_cookie', '', expires=0)
    return resp


# Insert new Categorie
@app.route('/NewCateogrie', methods=['GET','POST'])
def AddCategorie():
    user_cookie = request.cookies.get('user_cookie')
    if user_cookie is None:
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categories = session.query(Categorie).filter_by(
                created_by=user_cookie).all()
        return render_template('NewCategorie.html', categories=categories)
    if request.method == 'POST':
        categorie = Categorie(name=request.form['categoriename']
        ,created_by=user_cookie)
        session.add(categorie)
        session.commit()
        return redirect(url_for('AddCategorie'))
    
    
# Insert new Item
@app.route('/NewItem/<int:categorie_id>', methods=['GET','POST'])
def AddItem(categorie_id):
    user_cookie = request.cookies.get('user_cookie')
    if user_cookie is None:
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categorie = session.query(Categorie).filter_by(id=categorie_id).one()
        items = session.query(Item).filter_by(categorie_id=categorie_id).all()
        return render_template('CategorieItems.html', categorie=categorie,
                               items=items)
    if request.method == 'POST':
        item = Item(name=request.form['itemname']
        , description=request.form['description'], categorie_id=categorie_id)
        session.add(item)
        session.commit()
        return redirect(url_for('AddItem', categorie_id=categorie_id))
    
    
# Edit Categorie
@app.route('/EditCateogrie/<int:categorie_id>', methods=['GET','POST'])
def EditCategorie(categorie_id):
    user_cookie = request.cookies.get('user_cookie')
    if user_cookie is None:
        return redirect(url_for('Login'))
    if request.method == 'GET':
        categorie = session.query(Categorie).filter_by(id=categorie_id,
                                 created_by=user_cookie).one()
        return render_template('EditCategorie.html', categorie=categorie)
    if request.method == 'POST':
        categorie = session.query(Categorie).filter_by(id=categorie_id).one()
        categorie.name = request.form['categoriename']
        session.add(categorie)
        session.commit()
        return redirect(url_for('AddCategorie'))
    
    
# Edit Item
@app.route('/EditItem/<int:item_id>', methods=['GET','POST'])
def EditItem(item_id):
    user_cookie = request.cookies.get('user_cookie')
    if user_cookie is None:
        return redirect(url_for('Login'))
    if request.method == 'GET':
        item = session.query(Item).filter_by(id=item_id).one()
        return render_template('EditItem.html', item=item)
    if request.method == 'POST':
        item = session.query(Item).filter_by(id=item_id).one()
        item.name = request.form['itemname']
        item.description = request.form['item_description']
        session.add(item)
        session.commit()
        return redirect(url_for('AddItem', categorie_id=item.categorie_id))
    
 
# Delete Categorie
@app.route('/DeleteCategorie/<int:categorie_id>')
def DeleteCategorie(categorie_id):
    user_cookie = request.cookies.get('user_cookie')
    if user_cookie is None:
        return redirect(url_for('Login'))
    categorie = session.query(Categorie).filter_by(id=categorie_id).one()
    items = session.query(Item).filter_by(categorie_id=categorie_id).all()
    for item in items:
     session.delete(item)
    session.commit()
    session.delete(categorie)
    session.commit()
    return redirect(url_for('AddCategorie'))


# Delete Item
@app.route('/DeleteItem/<int:item_id>')
def deleteItem(item_id):
    user_cookie = request.cookies.get('user_cookie')
    if user_cookie is None:
        return redirect(url_for('Login'))
    item = session.query(Item).filter_by(id=item_id).one()
    categorie_id = item.categorie_id
    session.delete(item)
    session.commit()
    return redirect(url_for('AddItem', categorie_id=categorie_id))


# Return List of categories as Json
@app.route('/CategoriesJSON')
def CategoriesJSON():
    categories = session.query(Categorie).all()
    return jsonify(categories=[i.serialize for i in categories])


# Return List of items as Json
@app.route('/ItemsJSON/<int:categorie_id>')
def ItemsJSON(categorie_id):
    items = session.query(Item).filter_by(categorie_id=categorie_id).all()
    return jsonify(items=[i.serialize for i in items])
    

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)