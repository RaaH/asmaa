# -*- coding: utf-8 -*-
"""
Copyright © 2008, Muayyad Alsadi <alsadi@ojuba.org>

    Released under terms on Waqf Public License.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the latest version Waqf Public License as
    published by Ojuba.org.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    The Latest version of the license can be found on
    "http://www.ojuba.org/wiki/doku.php/waqf/license"

"""
import sqlite3
import fuzzy

tb=['othmani','imlai']
def verse_enumerate(sura,aya=1):
  """return a uniq number used as a primary key that refers to a verse in Quran"""
  return ((sura-1)<<9)+(aya-1)

def sura_aya_from_id(i):
  """return sura and aya corresponding to id"""
  return ((i>>9)+1,(i&511)+1)

def ayat_enumerate(sura,aya=1,ayat=1):
  """return a number that represents sura and aya and number of ayat in Quran"""
  if sura<=0 or aya<=0 or ayat<=0: return 0
  return (sura<<18)+(aya<<9)+ayat # this can't be zero because of ayat>0
def ayat_from_id(i):
  """return sura,aya and ayat corresponding to id"""
  if not i: return (0,0,0)
  return ((i>>18),(i>>9)&511,(i&511))


class Othman:
  def __init__(self,conf):
    self.__cn=sqlite3.connect('data/quran.db')
    self.__cn.create_function('fuzzy_normalize',1,fuzzy.normalize) 
    self.__c=self.__cn.cursor()
    try:
      self.__c.execute("select rowid from quran order by rowid desc limit 1")
      i=self.__c.fetchone()[0]
    except: raise IOError
    if i!=57861: raise TypeError
  def get_aya_n(self,sura):
    self.__c.execute("select 1+id&((1<<9)-1) from quran where id<(?<<9) order by rowid desc limit 1;",(sura,))
    return self.__c.fetchone()[0]
    
  def get_suras_names(self):
    self.__c.execute("select sura_name from SuraNames")
    return map(lambda i: i[0],self.__c.fetchall())

  def get_all_sura_names(self,sura):
    self.__c.execute("select sura_name,other_names from SuraNames where rowid=?",(sura-1,))
    r=self.__c.fetchone()
    R=[r[0]]
    R+=r[1].split(':')
    return R

  def get_ayat(self, sura, aya1, aya2, is_imlai=False):
    self.__c.execute("select %s from quran where id between %d and %d" % (tb[is_imlai==True],verse_enumerate(sura,aya1),verse_enumerate(sura,aya2)) )
    return map(lambda i: i[0],self.__c.fetchall())

  def get_sura(self, sura, is_imlai=False):
    self.__c.execute("select %s from quran where id between %d and %d" % (tb[is_imlai==True],verse_enumerate(sura,1),verse_enumerate(sura+1,1)-1) )
    return map(lambda i: i[0],self.__c.fetchall())

  def search(self,text, is_fuzzy=1, pos=1, direction=1 ,limit=100):
    """return list of aya_ids
    you can do incremental search pass pos=last_pos and limit=1 (direction=1 or -1 for forward and backword search)"""
    self.search_text=text
    self.search_is_fuzzy=is_fuzzy
    self.search_pos=pos
    if is_fuzzy:
      s='''fuzzy_normalize(imlai) LIKE ? ESCAPE "|"'''
      text=fuzzy.normalize(text)
    else: s='''imlai LIKE ? ESCAPE "|"'''
    self.search_tokens=fuzzy.tokenize_search(text)

    l=map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
    if len(l)<1: return []
    
    condition=' AND '.join([s]*len(l))
    condition='id > %d AND %s' % (pos,condition)
    self.__c.execute("""SELECT id FROM Quran WHERE %s""" % (condition), l)
    try: return self.__c.fetchall()[0][0]
    except: return 1
