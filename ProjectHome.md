a simple python orm for mysql, postgresql,sqlite3,mongodb,
run sina app engine, gae, and more.

Example:
```
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
mAnimal = Animal(type='y')
aid = mAnimal.save()

mCow = Cow(name = 'yoyoyouyoyoyy', animal = aid )
cid = mCow .save()

#获取数据
animal = mAnimal.get(1)
print animal

#获取关联的 Cow
print animal.cows()


```