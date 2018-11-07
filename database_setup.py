#!/usr/bin/env python2


from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Categorie(Base):
    __tablename__ = "categorie"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return serializeable data format"""
        return {            
            'id': self.id,
            'name': self.name,
        }
    
    
class Item(Base):
    __tablename__ = "item"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    categori_id = Column(Integer, ForeignKey('categorie.id'))
    categorie = relationship(Categorie)
    
    
engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
