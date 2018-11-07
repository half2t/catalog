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
def Add():
    if request.method == 'GET':
        categories = session.query(Categorie).all()
        return render_template('NewCategorie.html', categories=categories)
    if request.method == 'POST':
        categorie = Categorie(name=request.form['categoriename'])
        session.add(categorie)
        session.commit()
        return redirect(url_for('Add'))
    
    
# Delete Categorie
@app.route('/NewCateogrie', methods=['GET','Delete'])
def Delete():
    if request.method == 'GET':
        categories = session.query(Categorie).all()
        return render_template('NewCategorie.html', categories=categories)
    if request.method == 'POST':
        categorie = Categorie(name=request.form['categoriename'])
        session.add(categorie)
        session.commit()
        return redirect(url_for('Add'))


# Return List of categories as Json
@app.route('/CategoriesJSON')
def CategoriesJSON():
    categories = session.query(Categorie).all()
    return jsonify(categories=[i.serialize for i in categories])
    

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)