# -*- coding: utf-8 -*-
"""
NOTE: From this code I think I can write something reasonable for the client library!
"""

#TODO: Are the c-extensions installed when using PyCharm????



import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    #Base.metadata.create_all(engine) 

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % \
           (self.name, self.fullname, self.password)

engine = create_engine('sqlite:///test.db')

Session = sessionmaker(bind=engine)
#If defined later:
#   Session.configure(bind=engine)

session = Session()

print engine


           
           
ed_user = User(name='ed', fullname='Ed Jones', password='edspassword') 




print ed_user      
session.add(ed_user)
session.commit()