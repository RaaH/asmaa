# -*- coding: utf-8 -*-
import sqlite3
import Asmaa.fuzzy as fuzzy
import bisect

class AsmaaSh:

    def __init__(self):
        "None"
    
    def search(self,text, is_fuzzy=0, pos=-1, direction=1 ,limit=10000):
        if pos!=self.search_pos or text!=self.search_text: self.search_pos=pos; pos-=1
        else: self.search_pos=pos
        self.search_text=text
        self.search_is_fuzzy=is_fuzzy
        if is_fuzzy:
            s='''fuzzy_normalize(book.nass) LIKE ? ESCAPE "|"'''
            text=fuzzy.normalize(text)
        else: s='''book.nass LIKE ? ESCAPE "|"'''
        self.search_tokens=fuzzy.tokenize_search(text)
    
        l=map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
        if len(l)<1: return []
        
        condition=' AND '.join([s]*len(l))
        if direction<0: order="ORDER BY book.rowid DESC"; op="<"
        else: order=""; op=">"
        if pos>=0: condition='book.id %s %d AND %s' % (op,pos,condition)
        self.__c.execute("""SELECT book.id FROM b%d AS book WHERE %s %s LIMIT %d """ % (self.__book_id, condition, order, limit), l)
        #c.execute("""SELECT book.id, toc.tit FROM b2023 AS book left JOIN t2023 AS toc USING ( id ) where %s group by book.id limit %d,%d;""" % (condition,limit*page,limit))
        a=self.__c.fetchall()
        r=[]
        for i in a:
            j=i[0]
            k=bisect.bisect(self.__toc_ids,j)-1
            if k<0: k=0
            try: h=self.__toc_uniq[k]
            except: h = [1,1,'......']
            r.append((j, h[2]))
            self.search_pos=j
        return r
    
    def sh_all_nass(self):
        "None"  
                  
    def sh_all_anawin(self):
        "None"
        
    def sh_all_quran(self):
        "None"
        
    def sh_cr_nass(self,text, is_fuzzy=0):
        if is_fuzzy:
            s = '''fuzzy_normalize(book.nass) LIKE ? ESCAPE "|"'''
            text=fuzzy.normalize(text)
        else: s = '''book.nass LIKE ? ESCAPE "|"'''
        self.search_tokens=fuzzy.tokenize_search(text)
        l = map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
        if len(l) < 1: return []
        condition = ' AND '.join([s]*len(l))
        self.cr.execute("""SELECT book.id FROM pages AS book WHERE %s""" % (condition), l)
        a = self.cr.fetchall()
        r = []
        for i in a:
            j = i[0]
            try: h = self.sh_get_title(j)
            except: h = '......'
            r.append((j, h))
        return r
        
    def sh_cr_quran(self):
        "None"
        
    def sh_cr_nass_sup(self,text, is_fuzzy=0, pos=-1, direction=1 ,limit=10000):
        if is_fuzzy:
            s = '''fuzzy_normalize(book.nass) LIKE ? ESCAPE "|"'''
            text=fuzzy.normalize(text)
        else: s = '''book.nass LIKE ? ESCAPE "|"'''
        self.search_tokens=fuzzy.tokenize_search(text)
        l = map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
        if len(l) < 1: return []
        condition = ' AND '.join([s]*len(l))
        if direction < 0: 
            orde = "ORDER BY book.rowid DESC" 
            op = "<"
        else: 
            order = ""
            op = ">"
        if pos >= 0: condition = 'book.id %s %d AND %s' % (op,pos,condition)
        self.cr.execute("""SELECT book.id FROM pages AS book WHERE %s %s LIMIT %d """ % (condition, order, limit), l)
        a = self.cr.fetchall()
        r = []
        for i in a:
            j = i[0]
            k = bisect.bisect(self.toc_ids,j)-1
            if k < 0: k = 0
            try: h = self.toc_uniq[k]
            except: h = [1,1,'......']
            r.append((j, h[2]))
            self.search_pos = j
        return r
        
    def sh_cr_quran_sup(self): 
        "None"  
        
    def sh_in_nataidj(self): 
        "None"
        
    def sh_get_title(self,i): 
        gg = int(i)+1
        op = " < "
        self.condi = 'id %s %d' % (op,gg)
        self.cr.execute('select tit from titles where %s' % (self.condi))
        tit = self.cr.fetchone()
        return str(tit[0]) 
        
         