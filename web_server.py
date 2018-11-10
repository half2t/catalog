#!/usr/bin/env python2


from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categorie, Item

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
    items = session.query(Item).all()
    return render_template('index.html')


# Insert new Categorie
@app.route('/NewCateogrie', methods=['GET','POST'])
def AddCategorie():
    if request.method == 'GET':
        categories = session.query(Categorie).all()
        return render_template('NewCategorie.html', categories=categories)
    if request.method == 'POST':
        categorie = Categorie(name=request.form['categoriename'],created_by=55)
        session.add(categorie)
        session.commit()
        return redirect(url_for('AddCategorie'))
    
    
# Insert new Item
@app.route('/NewItem/<int:categorie_id>', methods=['GET','POST'])
def AddItem(categorie_id):
    if request.method == 'GET':
        categorie = session.query(Categorie).filter_by(id=categorie_id).one()
        items = session.query(Item).filter_by(categori_id=categorie_id).all()
        return render_template('CategorieItems.html', categorie=categorie,
                               items=items)
    if request.method == 'POST':
        item = Item(name=request.form['itemname']
        , description=request.form['description'], categori_id=categorie_id)
        session.add(item)
        session.commit()
        return redirect(url_for('AddItem', categorie_id=categorie_id))
    
 
# Delete Categorie
@app.route('/DeleteCategorie/<int:categorie_id>')
def DeleteCategorie(categorie_id):
    categorie = session.query(Categorie).filter_by(id=categorie_id).one()
    items = session.query(Item).filter_by(categori_id=categorie_id).all()
    for item in items:
     session.delete(item)
    session.commit()
    session.delete(categorie)
    session.commit()
    return redirect(url_for('AddCategorie'))


# Delete Item
@app.route('/DeleteItem/<int:item_id>')
def deleteItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    categorie_id = item.categori_id
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
    items = session.query(Item).filter_by(categori_id=categorie_id).all()
    return jsonify(items=[i.serialize for i in items])
    

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)