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

#��orm��ע��model    
register(Animal, Cow)

#����db
Animal().create()
Cow().create()

#��������
mAnimal = Animal(type='333333333333333333333333')
mAnimal.save()

#��ȡ����
animals = mAnimal.get(1)
print animals

