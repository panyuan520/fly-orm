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

#创建db
Animal().create()
Cow().create()

#保存数据
mAnimal = Animal(type='333333333333333333333333')
mAnimal.save()

#获取数据
animals = mAnimal.get(1)
print animals

