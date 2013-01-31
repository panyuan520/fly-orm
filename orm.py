import os

config_1 = {
            'database':{
                      'type':'postgresql',
                      'user':'postgres',
                      'passwd':'postgres',
                      'db':'test',
                      'port':5433,
                      'host':'localhost',
                      'charset':'utf8'
                      }
        }

config_2 = {
            'database':{
                      'type':'sqlite3',
                      'user':'',
                      'passwd':'',
                      'db':'model.db',
                      'port':'',
                      'host':'localhost',
                      'charset':'utf8'
                      }
        }


config_3 = {
            'database':{
                      'type':'postgresql',
                      'user':'postgres',
                      'passwd':'postgres',
                      'db':'model',
                      'port':5433,
                      'host':'localhost',
                      'charset':'utf8'
                      }
        }
        
config_4 = {
            'database':{
                      'type':'mongodb',
                      'user':'',
                      'passwd':'',
                      'db':'model',
                      'port':'',
                      'host':'localhost',
                      'charset':'utf8'
                      }
        }
        
config = config_1
        
class ForeignKey(object):

    def __init__(self, model, *args, **kwargs):
        self.pk = None
        self.foreignModel = model
        self.table, self.column = self.foreignModel.split('.')
        self.primary_key = kwargs.get('primary_key', self.column)
    
    def format(self):
        return ' int'
        
    def get_key(self):
        return self.primary_key
        
    def __set__(self, key, value):
        setattr(self, key, value)
        
    def __call__(self):
        return globals()[self.table]().filter(**{self.column:self.pk})
        
        
class Relation(object):

    def __init__(self, model, *args, **kwargs):
        self.pk = None
        self.relationModel = model
        self.primary_key = kwargs.get('primary_key', 'id')
        self.table, self.column = self.relationModel.split('.')
    
    def get_key(self):
        return self.primary_key
    
    def __set__(self, key, value):
        setattr(self, key, value) 
    
    def __call__(self):
        return globals()[self.table]().filter(**{self.column:self.pk})
    
    
class MysqlBase(object):
    def __init__(self, *args, **kwargs):
        import MySQLdb
        import MySQLdb.cursors
        self.__tablename__ = None
        self.objectManager = {}
        self.connection = MySQLdb.connect(
                            host        = config['database']['host'], 
                            user        = config['database']['user'],
                            passwd      = config['database']['passwd'], 
                            db          = config['database']['db'], 
                            port        = config['database']['port'],
                            charset     = config['database']['charset'],
                            cursorclass = MySQLdb.cursors.DictCursor
                        )
        self.cursor = self.connection.cursor()
        
    def save(self):
        sql = "insert into "+self.__tablename__+" ("+",".join(self.objectManager.keys())+") values ("+",".join(["'%s'" % i for i in self.objectManager.values()])+")"  
        self.execute(sql)   
            
    def filter(self, *args, **kwargs):
        query = ''
        if args and len(args) > 0:
            query += "and".join([i for i in args]) if len(args) > 1 else " ".join([i for i in args])
        if kwargs and len(kwargs) > 0:
            if query:
                query += ' and '
            query += " and".join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()]) if len(kwargs) > 1 \
                                                    else  " ".join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()])
        if query:
            print "select * from "+self.__tablename__+" where "+ query +""
            self.cursor.execute("select * from "+self.__tablename__+" where "+ query +"")
            return self.cursor.fetchall()
        
    def get(self, id):
        self.cursor.execute("select * from "+self.__tablename__+" where id=%s" % id)
        return self.cursor.fetchone()
        
    def all(self):
        self.cursor.execute("select * from "+self.__tablename__+"")
        return self.cursor.fetchall()
    
    def create(self):
        sql = []
        for key in dir(self):
            if isinstance(getattr(self, key), (Field, ForeignKey)):
                sql.append(key + getattr(self, key).format())
        sql = ",".join(sql)
        sql = "CREATE TABLE %s (%s)" % (self.__tablename__, sql)
        self.execute(sql) 
        
    def delete(self, *args, **kwargs):
        sql = "delete from "+self.__tablename__+" where "+" ".join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()])+""
        self.execute(sql) 
    
    def execute(self, sql):
        self.cursor.execute(sql)
        
    def primary_key(self, sql):
        return sql +" auto_increment PRIMARY KEY"  

class SqliteBase(object):

    def __init__(self, *args, **kwargs):
        import sqlite3 as sqlite
        self.__tablename__ = None
        self.objectManager = {}
        self.connection    = sqlite.connect(config['database']['db'])
        self.connection.row_factory = self.dict_factory
        self.cursor        = self.connection.cursor()
        
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def save(self):
        sql = "insert into "+self.__tablename__+" ("+",".join(self.objectManager.keys())+") values ("+",".join(["'%s'" % i for i in self.objectManager.values()])+")"  
        self.execute(sql)   
            
    def filter(self, *args, **kwargs):
        self.cursor.execute("select * from "+self.__tablename__+" where "+" and".join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()])+"")
        return self.cursor.fetchall()
        
    def get(self, id):
        self.cursor.execute("select * from "+self.__tablename__+" where id=%s" % id)
        return self.cursor.fetchone()
        
    def all(self):
        self.cursor.execute("select * from "+self.__tablename__+"")
        return self.cursor.fetchall()
  
    def delete(self, *args, **kwargs):
        sql = "delete from "+self.__tablename__+" where "+" ".join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()])+""
        self.execute(sql) 
    
    def execute(self, sql):
        self.cursor.execute(sql)
        self.connection.commit()
        
    def primary_key(self, sql):
        return sql + " auto increment PRIMARY KEY"  
           
class PostgresqlBase(object):
    def __init__(self, *args, **kwargs):
        import psycopg2
        import psycopg2.extras
        self.__tablename__ = None
        self.objectManager = {}
        self.connection = psycopg2.connect(
                                        "dbname='%s' user='%s' host='%s' password='%s' port='%s' " % (
                                                                                            config['database']['db'], 
                                                                                            config['database']['user'],
                                                                                            config['database']['host'],
                                                                                            config['database']['passwd'],
                                                                                            config['database']['port']
                                                                                            )
                                        );
        self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        
    def save(self):
        sql = "insert into "+self.__tablename__+" ("+",".join(self.objectManager.keys())+") values ("+",".join(["'%s'" % i for i in self.objectManager.values()])+") RETURNING id"  
        self.execute(sql)
        one = self.cursor.fetchone()
        if len(one) > 0:
            return one.get('id')
            
    def filter(self, *args, **kwargs):
        self.cursor.execute("select * from "+self.__tablename__+" where "+" and".join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()])+"")
        return self.cursor.fetchall()
        
    def get(self, id):
        self.cursor.execute("select * from "+self.__tablename__+" where id=%s" % id)
        return self.cursor.fetchone()
        
    def all(self):
        self.cursor.execute("select * from "+self.__tablename__+"")
        return self.cursor.fetchall()
    
    def create(self):
        sql = []
        for key in dir(self):
            if isinstance(getattr(self, key), (Field, ForeignKey)):
                sql.append(key + getattr(self, key).format())
        sql = ",".join(sql)
        sql = "CREATE TABLE %s (%s)" % (self.__tablename__, sql)
        self.execute(sql) 
        
    def delete(self, *args, **kwargs):
        sql = "delete from "+self.__tablename__+" where "+" ".join(['%s=%s' % (key, value) for key, value in kwargs.iteritems()])+""
        self.execute(sql) 
    
    def execute(self, sql):
        self.cursor.execute(sql) 
        self.connection.commit()
    
    def primary_key(self, sql):
        return " serial PRIMARY KEY"  

class MongoBase(object):
    def __init__(self, *args, **kwargs):
        from pymongo import Connection
        self.__tablename__ = None
        self.objectManager = {}
        self.connection = Connection()
        self.db = self.connection[config['database']['db']]
        
    def save(self):
        self.db[self.__tablename__].insert(self.objectManager) 
            
    def filter(self, *args, **kwargs):
        return self.db[self.__tablename__].find(**kwargs)
        
    def get(self, id):
        data = self.db[self.__tablename__].find(**{'_id':id})
        return data[0] if data.count > 0 else None
        
    def all(self):
        return self.db[self.__tablename__].find()
      
    def delete(self):
        self.db[self.__tablename__].remove()
                    
class ObjectManager(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            return None
    
    def __setattr__(self, key, value):
        if value != None: 
            self[key] = value
        
    def __delattr__(self, key):
        if key in self: 
            del self[key]
                
                
class Field(object):

    def __init__(self, *args, **kwargs):
    
        self.types       = args[0]
        self.length      = kwargs.get('length')
        self.not_null    = kwargs.get('not_null')
        self.default     = kwargs.get('default')
        self.primary_key = kwargs.get('primary_key')
        self.callable    = None
        
        if self.types== 'int':
            self.callable = self.valid_int
        elif self.types == 'str':
            self.callable = self.valid_str
        elif self.types == 'datetime':
            self.callable = self.valid_datetime
            
        if config['database']['type'] == 'mysql':
            self.base = MysqlBase()
        elif config['database']['type'] == 'sqlite3':
            self.base = SqliteBase()
        elif config['database']['type'] == 'postgresql':
            self.base = PostgresqlBase()
        elif config['database']['type'] == 'mongodb':
            self.base = MongoBase()
    
    def valid_int(self, value):
        if isinstance(value, int):
            return True
    
    def valid_str(self, value):
        if isinstance(value, str):
            return True
     
    def valid_datetime(self, value):
        import datetime
        if isinstance(self, datetime):
            return True
    
    def format(self):
        sql = None
        if self.types == 'int':
            if config['database']['type'] == 'sqlite3':
                sql = ' INTEGER '
            else:
                sql = ' int '
        elif self.types == 'str':
            sql = ' char'
        elif self.types == 'datetime':
            sql = ' timestamp'
        elif self.types == 'text':
            sql = ' text'
        if self.length and self.types == 'str':
            sql += " ("+str(self.length)+")"
        if self.not_null:
            sql += " NOT NULL"
        if self.default:
            sql += " default '"+self.default+"'"
        if self.primary_key:
            sql = self.base.primary_key(sql)
        return sql
        
    def __call__(self, value):
        return self.callable(value)
          
          
class Model(object):

    def __init__(self, *args, **kwargs):
        if config['database']['type'] == 'mysql':
            self.base = MysqlBase()
        elif config['database']['type'] == 'sqlite3':
            self.base = SqliteBase()
        elif config['database']['type'] == 'postgresql':
            self.base = PostgresqlBase()
        elif config['database']['type'] == 'mongodb':
            self.base = MongoBase()
           
        self.objectManager = ObjectManager()
        for key, value in kwargs.iteritems():
            if isinstance(getattr(self, key), (Field, ForeignKey)):
                print "?", getattr(self, key), value
                #if getattr(self, key)(value):
                self.objectManager[key] = value
                    
        self.base.objectManager = self.objectManager
        self.base.__tablename__ = self.__tablename__
    
    def all(self):
        return self._format_key_object(self.base.all())
        
    def filter(self, *args, **kwargs):
        return self._format_key_object(self.base.filter(*args, **kwargs))
                       
    def get(self, id):
        return self._format_key_object(self.base.get(id))
        
    def save(self):
        return self.base.save() 
                
    def delete(self, *args, **kwargs):
        self.base.delete(*args, **kwargs) 
    
    def create(self):
        sql = []
        for key in dir(self):
            if isinstance(getattr(self, key), (Field, ForeignKey)):
                sql.append(key + getattr(self, key).format())
        sql = ",".join(sql)
        sql = "CREATE TABLE %s (%s)" % (self.__tablename__, sql)
        self.base.execute(sql) 
        
    def _format_key_object(self, data):
        if isinstance(data, dict):
            obj = ObjectManager()
            for modu in dir(self):
                if modu not in data.keys()  and not modu.startswith("_"):
                    get_modu = getattr(self, modu)
                    if isinstance(get_modu, (ForeignKey, Relation, Field)):
                        obj[modu] = get_modu
                        if isinstance(get_modu, (ForeignKey, Relation)):
                            obj[modu].pk = data[obj[modu].get_key()]
            for key, value in data.iteritems():
                obj[key] = value
            return obj
        else:
            result = []
            for i in data:
                obj = ObjectManager()
                for modu in dir(self):
                    if modu not in i.keys() and not modu.startswith("_"):
                        get_modu = getattr(self, modu)
                        if isinstance(get_modu, (ForeignKey, Relation, Field)):
                            obj[modu] = get_modu
                            if isinstance(get_modu, (ForeignKey, Relation)):
                                obj[modu].pk = i[obj[modu].get_key()]
                for key, value in i.iteritems():
                    obj[key] = value
                result.append(obj)
            return result
            
def register(* classs):
    for i in classs:
        globals().update({i.__name__:i})

def ilike_(kwargs):
    if kwargs and len(kwargs) > 0:
        return  " and ".join(["%s like %s" % (k, "'%" + v  + "%'") for k, v in kwargs.iteritems()]) if len(kwargs) > 1 else " ".join(["%s like %s" % (k, "'%" + v + "%'") for k, v in kwargs.iteritems()])


 
