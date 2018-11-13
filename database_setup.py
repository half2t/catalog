#!/usr/bin/env python2


from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Categorie(Base):
    __tablename__ = "categorie"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    items = relationship("Item", cascade="all,delete", backref="categorie")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by
        }


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=False)
    created_by = Column(String(100), nullable=False)
    categorie_id = Column(Integer, ForeignKey('categorie.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'categori_id': self.categorie_id,
            'categorie_name': self.categorie.name,
            'created_by': self.created_by
        }


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
