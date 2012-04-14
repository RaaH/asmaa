# -*- coding: utf-8 -*-
import Asmaa.fuzzy as fuzzy
import bisect
import sqlite3



class AsmaaBook:

    def __init__(self,book, id):
        #self.current_id=-1
        self.search_tokens=[]
        self.search_text=''
       # self.search_is_fuzzy=0
        self.search_pos=-1
        self.is_tafseer=0
       # self.is_sharh=0
       # self.shorts=0
        self.book = book
        self.shorts=0
        self.shorts_init()
        self.cn = sqlite3.connect(self.book,isolation_level = None)
        self.cn.create_function('fuzzy_normalize',1,fuzzy.normalize)
        self.cn.create_function('expand_shorts',1,self.expand_shorts)
        self.cr = self.cn.cursor()
        self.cr1 = self.cn.cursor()
        self.cr2 = self.cn.cursor()
        self.cr1.execute("select * from main")
        r1=self.cr1.fetchone()
        self.book_id = r1[0]
        self.betaka = r1[5]
        self.is_tafseer = r1[11]
        self.is_sharh = r1[12]
        self.shorts = r1[10]
        self.book_name = r1[1]
        self.cr2.execute("select id from pages")
        self.lds = len(self.cr2.fetchall())
        self.cr1.close()
        self.cr2.close()
        self.h = {}
        
    def shorts_init(self):
        self.shorts2=[]
        if self.shorts < 2: self.shorts2 = []; return
        self.shorts2=map(lambda i,j:(i,'\n'+j+'\n'),self.cr1.execute('SELECT ramz, nass FROM shorts').fetchall())

    def expand_shorts(self, txt):
        for i,j in self.shorts2: txt=txt.replace(i,j)
        return txt
    
    def get_text_body(self, book, page_id):
        if page_id > self.lds : page_id = 1
        self.book = book
        self.cr.execute("select id,expand_shorts(nass) as text,part,page,hno,sora,aya,na from pages where id=%d limit 1" % (page_id)) # id,nass,part,page,hno,sora,aya,na
        r = self.cr.fetchone()
        return r
    
    def next_page(self,current_id):
        self.current_id = current_id
        if self.current_id == self.lds: return None
        elif self.current_id == -1: self.current_id = 1
        self.current_id += 1
        return self.get_text_body(self.book,self.current_id), self.current_id
    
    def first_page(self):
        self.current_id=1
        return self.get_text_body(self.book,self.current_id), self.current_id
    
    def previous_page(self,current_id):
        self.current_id = current_id
        if self.current_id < 2: return None
        self.current_id -= 1
        return self.get_text_body(self.book,self.current_id), self.current_id
    
    def last_page(self):
        self.current_id = self.lds
        return self.get_text_body(self.book,self.current_id), self.current_id  
   
    def go_to_page(self,page,part):
        self.cr.execute("select id from pages where part=%d and page=%d" % (part,page)) # id
        ff = self.cr.fetchone()[0]
        return ff
    
    def page_quran(self, sora,aya):
        self.cr.execute("""SELECT id FROM pages WHERE sora=%d AND %d<=aya+na """% (sora,aya))
        pr=self.cr.fetchone()
        try: return pr[0]
        except: return 1
        
    def get_toc(self):
        self.cr.execute("select rowid,id,tit,lvl,sub from titles ORDER BY id,sub")
        self.toc_list =   self.cr.fetchall()
        self.en = enumerate(self.toc_list)
        self.rv = reversed(list(self.en))
        for i,j in self.rv: self.h[j[1]] = j # i is used to keep the order only
        self.toc_ids = self.h.keys() 
        self.toc_ids.sort()
        self.toc_uniq = self.h.values()
        self.toc_uniq.sort()
        return self.toc_list
    
    def get_headers_in_page_id(self,pid):
        """return tuples in the form of (level,text) for the headers in page id pid"""
        l = []
        i = bisect.bisect(self.toc_ids,pid)
        try :
            k = self.toc_uniq[i-1][0]-1
        except :
            k = 0
        for j in self.toc_list[k:]:
            if j[1] != pid: break
            l.append((j[3]-1,j[2],))
        return l
    
    def page_id_for_aya(self, sora,aya, last_rowid=-1):
        """return page_id and titile for aya"""
        self.cr.execute("""SELECT id,sora,aya,na FROM pages WHERE rowid>%d AND sora>=%d AND aya>=%d LIMIT 1"""% ( last_rowid, sora,aya))
        pr=self.cr.fetchone()
        if not pr: return None
        if pr[1] != sora or pr[2] != aya:
            rr = self.toc_uniq[bisect.bisect(self.toc_ids, pr[0]-1)-1]
            return rr[1],"%s:%s" % (pr[1],pr[2])
        if pr[3] > 1: return pr[0],"%d:%d-%d" % (pr[1],pr[2],pr[2]+pr[3]-1)
        return pr[0],"%d:%d" % (pr[1],pr[2])
    
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
        self.cr.execute("""SELECT book.id FROM pages AS book WHERE %s %s LIMIT %d """ % (condition, order, limit), l)
        a=self.cr.fetchall()
        r=[]
        for i in a:
            j=i[0]
            k=bisect.bisect(self.toc_ids,j)-1
            if k<0: k=0
            try: h=self.toc_uniq[k]
            except: h = [1,1,'......']
            r.append((j, h[2]))
            self.search_pos=j
        return r
    
    def exit(self,*a):
        del self.l
        del self.j
        del self.h
        del self.en
        del self.rv
        del self.toc_list
        del self.toc_ids
        del self.toc_uniq
        self.cr.close()
        self.cn.close()
        
            
