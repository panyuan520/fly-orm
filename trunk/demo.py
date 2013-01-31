#!/usr/bin/env python
# -*- coding: utf-8 -*-
from orm import *

class Animal(Model):

    __tablename__ = 'animal'
    
    id    = Field('int', primary_key = True)
    type  = Field('str', length = 30)
    cows  = Relation('Cow.animal', primary_key = 'id')
    
class Cow(Model):
    __tablename__ = 'cow' 
    
    id      =  Field('int', primary_key = True)
    name    =  Field('str', length=30, default = '342342')
    time    =  Field('datetime')
    animal  =  ForeignKey('Animal.id', primary_key = 'id')

#在orm里注册model    
register(Animal, Cow)

mAnimal = Animal()
mCow = Cow()
'''
#创建db
Animal().create()
Cow().create()
'''
a = Animal(type = 'p')
aid = a.save()
print 'aid', aid
c = Cow(name = 'yoyoyouyoyoyy', animal = aid)
cid = c.save()
print 'cid', cid
print "mAnimal", aid, mAnimal.get(aid)
print 'mCow', cid, mCow.get(cid)

