# -*- coding: utf-8 -*-
import sqlite3
import os.path
from Asmaa.ThwabShamelaImport import shamela3_import, schema

class ThwabBook:
    
    def __import(self):
        self.__cn=sqlite3.connect(':memory:', isolation_level=None)
        try: shamela3_import(self.__cn, self.__fn, self.__book_id)
        except OSError: print "mdbtools are not installed"; raise
    
    def __load(self):
        if self.__fn[-4:] in ('.bok','.mdb') : 
            self.__import(); 
            return
        self.__cn = sqlite3.connect(self.__fn, isolation_level=None)
    
    def __init__(self, book,bkid=-1):
        self.__book_id=bkid
        r=[]
        if type(book) == sqlite3.Connection: filename = None
        elif os.path.exists(book): filename=book
        else: raise IndexError
        self.__fn = filename
        if filename: self.__load()
        self.c = self.__cn.cursor()
        try: r = self.c.execute("SELECT bkid,thwab,betaka,bk FROM main WHERE bkid>=%d ORDER BY bkid DESC LIMIT 1" % bkid).fetchone()
        except sqlite3.DatabaseError: self.c.close(); self.__cn.close(); raise IndexError
        if not r: raise IndexError
        elif r[1]!=2: raise TypeError
        else: self.__book_id=r[0]
        self.__cn.row_factory=sqlite3.Row
        self.__c=self.__cn.cursor()
        self.bk = r[3]
    
    def export(self, fn, progress=None):
        self.__c.execute('ATTACH ? as f',(fn,))
        self.__c.execute("BEGIN TRANSACTION;")
        main_tb=['main']+filter(lambda x: x not in ['main','cat','book','toc'],schema.keys()) # make sure main is the first
        for i in main_tb:
            self.__c.execute('CREATE TABLE IF NOT EXISTS f.%s (%s)' % (i,schema[i]))
        self.__c.execute('CREATE TABLE IF NOT EXISTS f.titles (%s)' % (schema['toc']))
        self.__c.execute('CREATE TABLE IF NOT EXISTS f.pages (%s)' % (schema['book']))
        for i in main_tb:
            self.__c.execute("INSERT INTO f.%s SELECT * FROM main.%s" % (i,i))
        self.__c.execute("INSERT INTO f.titles SELECT * FROM main.t%d" % (self.__book_id))
        self.__c.execute("INSERT INTO f.pages SELECT * FROM main.b%d" % (self.__book_id))
        self.__c.execute("END TRANSACTION;")
        self.__cn.commit()
        self.__c.execute('DETACH f')
        self.__c.close()
        self.c.close()
        self.__cn.close()
