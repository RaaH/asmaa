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

#mdb-schema x.mdb | perl -wpe 's%^DROP TABLE %DROP TABLE IF EXISTS %i;s%Memo/Hyperlink%TEXT%i;s%(Byte|(\w+ )?Integer)%INTEGER%i;s%\s*\(\d+\)\s*(,?[ \t]*)$%${1}%;s%(\s+TEXT)%${1} DEFAULT NULL%;s%(\s+INTEGER)%${1} DEFAULT 0%;' | sqlite3 x.db

import sqlite3
import os
import os.path
import re
from subprocess import Popen,PIPE

schema_fix_del=re.compile('\(\d+\)')
schema_fix_text=re.compile('Memo/Hyperlink',re.I)
schema_fix_int=re.compile('(Boolean|Byte|Byte|Numeric|Replication ID|(\w+ )?Integer)',re.I)

sqlite_cols_re=re.compile("\((.*)\)",re.M | re.S)
no_sql_comments=re.compile('^--.*$',re.M)
# main is called 0bok and cat is called 0cat in the individual files
#SELECT min(book.id),((book.sora)<<18)+((book.aya)<<9)+book.na as ayat_id FROM b%d as book WHERE ayat_id>%d GROUP BY ayat_id;
schema={
  'main':"bkid INTEGER PRIMARY KEY, bk TEXT, thwab INTEGER, shortname TEXT, cat INTEGER, betaka TEXT, inf TEXT, bkord INTEGER DEFAULT -1, authno INTEGER DEFAULT 0, auth_death INTEGER DEFAULT 0,islamshort INTEGER DEFAULT 0, is_tafseer INTEGER DEFAULT 0, is_sharh INTEGER DEFAULT 0",
  'men': "id INTEGER PRIMARY KEY, arrname TEXT, isoname TEXT, dispname TEXT",
  'shorts': "ramz TEXT, nass TEXT",
  'mendetail': "spid INTEGER PRIMARY KEY, manid INTEGER, bk INTEGER, id INTEGER, talween TEXT",
  'shrooh': "matnid INTEGER, sharhid INTEGER",
  'cat':"id INTEGER PRIMARY KEY, name Text, catord INTEGER, lvl INTEGER",
  'book':"id INTEGER PRIMARY KEY, nass TEXT, part INTEGER DEFAULT 0, page INTEGER DEFAULT 0, hno INTEGER DEFAULT 0, sora INTEGER DEFAULT 0, aya INTEGER DEFAULT 0, na INTEGER DEFAULT 0",
  'toc': "id INTEGER, tit TEXT, lvl INTEGER DEFAULT 1, sub INTEGER DEFAULT 0"
}

#schema={'main':"bkid INTEGER PRIMARY KEY, bk TEXT, cat INTEGER, betaka TEXT, inf TEXT, bkord INTEGER, authno INTEGER, auth TEXT, authinf TEXT, max INTEGER, nosr INTEGER, comp INTEGER, islamshort INTEGER, tafseernam TEXT, idx INTEGER, archive INTEGER, iso TEXT, nidx INTEGER, onum INTEGER, over INTEGER, bver INTEGER, seal TEXT, aseal TEXT, oauth INTEGER, pdf INTEGER, nosel INTEGER, notaf INTEGER, vername TEXT, blnk TEXT, oauthver INTEGER, lng TEXT, higrid TEXT,AD INTEGER, pdfcs INTEGER",
#  'men': "id INTEGER PRIMARY KEY, arrname TEXT, isoname TEXT, dispname TEXT",
#  'mendetail': "spid INTEGER PRIMARY KEY, manid INTEGER, bk INTEGER, id INTEGER, talween TEXT",
#  'shorts': "bk INTEGER, ramz TEXT, nass TEXT",
#  'shrooh': "matn TEXT, matnid TEXT, sharh TEXT, sharhid TEXT",
#  'com': "com TEXT, bk INTEGER, id INTEGER",
#  'cat':"id INTEGER PRIMARY KEY, name Text, catord INTEGER, lvl INTEGER",
#  'book':"id INTEGER PRIMARY KEY, nass TEXT, part INTEGER, page INTEGER, hno INTEGER, sora INTEGER, aya INTEGER,  na INTEGER, seal TEXT",
#  'toc': "id INTEGER, tit TEXT, lvl INTEGER, sub INTEGER"
#}
# TODO: add Men MenDetail Shorts Shrooh com 
table_cols=dict(map(lambda tb: (tb,map(lambda i: i.split()[0],schema[tb].split(','))), schema.keys()))
table_col_defs=dict(map(lambda tb: (tb,dict(map(lambda i: (i.strip().split()[0],i.strip()),schema[tb].split(',')))), schema.keys()))

#def sqlite_get_cols(cn,tb, istemp=False):
#  if istemp: tmpstr="temp_"
#  else: tmpstr=""
#  r=cn.execute('SELECT sql FROM sqlite_"+tmpstr+"master where type="table" and tbl_name=? limit 1',(tb,)).fetchone()[0]
#  return map(lambda a: a.split()[0].lower(),sqlite_cols_re.search(r).group(1).split(','))

def schema_get_cols(r):
  return map(lambda i: i.split()[0],sqlite_cols_re.search(no_sql_comments.sub('',r)).group(1).split(','))



def sqlite_get_cols(cn,tb):
  return map(lambda a: a[0].lower(), cn.execute('select * from '+tb+' limit 0').description )

# FIXME: should we call mdb-ver 'test.bok' if it return non zero ?
def identify_file(ifile):
  if ifile.endswith('.th'): return (0,{},[-1])
  try: p=Popen(['mdb-tables', '-1',ifile], 0, stdout=PIPE)
  except OSError: raise
  try: tables=p.communicate()[0].strip().split('\n')
  except OSError: raise
  r=p.returncode; del p;
  if r!=0: raise TypeError
  tables.sort()
  tb=dict(map(lambda s: (s.lower(),s), tables))
  if 'book' in tables and 'title' in tables: return (2,tb,[])
  bkid=map(lambda i:int(i[1:]),filter(lambda i: i[0]=='b' and i[1:].isdigit(),tables))
  bkid.sort()
  return (3,tb,bkid)
# to get the schema of the table type 'SELECT sql FROM sqlite_master where type="table" and tbl_name="Main" limit 1'
# CREATE INDEX IF NOT EXISTS MyIndexName on MyTable (Col1,Col2)

def get_schema(ifile):
  bkid=[]
  tables=[]
  p=Popen(['mdb-schema', ifile],0,stdout=PIPE)
  (cin, cout) = (p.stdin, p.stdout)
  for l in cout:
    l=l.strip().lower()
    if l.startswith('create table '):
      if l[13]=='b':
        if l[13:]=="book": continue
        elif l[14:].isdigit(): bkid.append(l[14:]); continue
      elif l[13]=='t':
        if l[13:]=="title" or l[14:].isdigit(): continue
      tables.append(l[13:])
  #print "BkId",bkid
  #print "Tables",tables
  return tables, bkid
  # add IF EXISTS to DROP TABLE
  #if l.startswith('DROP TABLE'): l="DROP TABLE IF EXISTS "+l[11:] # 11=len('DROP TABLE')+1
  #l=l.replace('Memo/Hyperlink','TEXT')
  #l=l.replace('Byte','INTEGER')

def __shamela3_insert_or_replace(c,sql_cmd):
  """Internal function used by shamela3_import"""
  if sql_cmd[0].startswith('INSERT INTO '): sql_cmd[0]='INSERT OR IGNORE INTO '+sql_cmd[0][12:]
  cmd=''.join(sql_cmd)
  c.executescript(cmd)

def __shamela3_fix_insert(c,sql_cmd,prefix="OR IGNORE INTO tmp_"):
  """Internal function used by shamela3_import"""
  if prefix and sql_cmd[0].startswith('INSERT INTO '): sql_cmd[0]='INSERT INTO '+prefix+sql_cmd[0][12:]
  cmd=''.join(sql_cmd)
  #print cmd
  c.executescript(cmd)

# when Tb and tb refers to table names but the second is lower case and it has no numbers like t41 could be toc
def sqlite_table_from_mdb(c, ifile, Tb,tb, prefix='tmp_'):
  """create sqlite table from mdb table adding missing cols when needed"""
  pipe=Popen(['mdb-schema', '-S','-T', Tb, ifile], 0, stdout=PIPE,env={'MDB_JET3_CHARSET':'cp1256'})
  r=pipe.communicate()[0]
  cmd=schema_fix_text.sub('TEXT',schema_fix_int.sub('INETEGER',schema_fix_del.sub('',r))).lower()
  cmd=cmd.replace('create table ','create temp table '+prefix)
  cmd=cmd.replace('drop table ','drop table if exists '+prefix)
  cols=schema_get_cols(cmd)
  missing=filter(lambda i: not i in cols,table_cols[tb])
  missing_def=', '.join(map(lambda i: table_col_defs[tb][i],missing))
  if missing_def: cmd=cmd.replace('\n)',','+missing_def+'\n)')
  #print cmd
  c.executescript(cmd)

def shamela3_import_table(c, mark, ifile, tb, tb_prefix="tmp_", is_ignore=0,is_replace=0):
  pipe=Popen(['mdb-export', '-R',';\n'+mark,'-I',ifile, tb], 0, stdout=PIPE,env={'MDB_JET3_CHARSET':'cp1256'})
  sql_cmd=[]
  prefix=""
  if is_ignore: prefix="OR IGNORE INTO "
  elif is_replace: prefix="OR REPLACE INTO "
  prefix+=tb_prefix
  for l in pipe.stdout:
    if l==mark: __shamela3_fix_insert(c,sql_cmd,prefix); sql_cmd=[]
    else: sql_cmd.append(l)
  if len(sql_cmd): __shamela3_fix_insert(c,sql_cmd,prefix); sql_cmd=[]
  del pipe

def insert_from_temp(c, Tb,tb, where=None, prefix="tmp_"):
  #print 'CREATE TABLE IF NOT EXISTS %s (%s)' % (Tb,schema[tb])
  c.execute('CREATE TABLE IF NOT EXISTS %s (%s)' % (Tb,schema[tb]))
  cols=', '.join(table_cols[tb])
  cmd='INSERT INTO %s (%s) SELECT %s FROM %s' % (Tb,cols,cols ,prefix+Tb)
  if where: cmd+=' WHERE '+where
  #print cmd
  c.execute(cmd)

# import sqlite3
# cn=sqlite3.connect('y.db')
# from ThwabShamelaImport import shamela3_import
# shamela3_import(cn, "x.mdb")
def shamela3_import(cn, ifile, bkid=-1, progress=None):
  """import a single book having bkid from shamela3 file ifile into sqlite connection cn"""
  auth_death1,auth_death2,sharh_for=0,0,0
  shortname=''
  v,tables,bkids=identify_file(ifile)
  bk_n=len(bkids)
  # no need to check all tables ['com', 'main', 'men', 'mendetail', 'shorts', 'shrooh']
  if v!=3 or 'main' not in tables.keys() or bk_n<1: raise TypeError # not a shamela3 book
  if bkid==-1:
    if len(bkids)!=1: raise IndexError # no book id is specified and file have more than one book
    else: bkid=bkids[0]

  hashlen=32 # must be divisible by 4
  # some mark to know how and where to cut
  mark="-- CUT HERE STUB (%s) BUTS EREH TUC --\n" % os.urandom(hashlen*3/4).encode('base64')[:hashlen]
  c=cn.cursor()
  c.execute("BEGIN TRANSACTION")
  # FIXME: toc should be direct without temp
  sqlite_table_from_mdb(c, ifile, tables['t'+str(bkid)],'toc')
  shamela3_import_table(c, mark, ifile, 't'+str(bkid))
  sqlite_table_from_mdb(c, ifile, tables['b'+str(bkid)],'book')
  shamela3_import_table(c, mark, ifile, 'b'+str(bkid))
  sqlite_table_from_mdb(c, ifile, tables['main'],'main')
  shamela3_import_table(c, mark, ifile, 'main')
  #c.execute("END TRANSACTION;")
  #cn.commit()
  if 'shrooh' in tables:
    sqlite_table_from_mdb(c, ifile, tables['shrooh'],'shrooh')
    shamela3_import_table(c, mark, ifile, 'shrooh')
    try:
      r=c.execute('SELECT matn,sharh FROM tmp_shrooh WHERE sharh=%d LIMIT 1'% bkid).fetchone()
      if r:
        sharh_for=int(r[0])
        c.execute('UPDATE OR IGNORE tmp_main SET is_sharh=?',(sharh_for,))
    except sqlite3.DatabaseError: pass
    except TypeError: pass
  else:
    c.execute('UPDATE OR IGNORE tmp_main SET is_sharh=0')
  # fix some values like shortname
  try:
    r=c.execute('SELECT tafseernam FROM tmp_main WHERE bkid=%d LIMIT 1' % bkid).fetchone()
    if r: shortname=r[0]
  except sqlite3.DatabaseError: pass
  c.execute('UPDATE OR IGNORE tmp_main SET thwab=2')
  if shortname: c.execute('UPDATE OR IGNORE tmp_main SET shortname=?',(shortname,))
  # and auth_death
  try:
    r=c.execute('SELECT higrid FROM tmp_main WHERE bkid='+str(bkid)).fetchone()
    if r and r[0]: auth_death1=int(r[0])
  except sqlite3.DatabaseError: pass
  except ValueError: pass
  try:
    r=c.execute('SELECT ad FROM tmp_main WHERE bkid='+str(bkid)).fetchone()
    if r and r[0]: auth_death2=int(r[0])
  except sqlite3.DatabaseError: pass
  if auth_death1 and auth_death2 and auth_death1==auth_death2:
    c.execute('UPDATE OR IGNORE tmp_main SET auth_death=?',(auth_death1,))
  
  r=c.execute('SELECT sora FROM tmp_b%d WHERE sora>0 LIMIT 1' % bkid).fetchone()
  if r: c.execute('UPDATE OR IGNORE tmp_main SET is_tafseer=1')
  #c.execute("BEGIN TRANSACTION")
  insert_from_temp(c,'main','main','bkid='+str(bkid))
  if 'shorts' in tables:
    sqlite_table_from_mdb(c, ifile, tables['shorts'],'shorts')
    shamela3_import_table(c, mark, ifile, 'shorts')
    try: r=c.execute('INSERT INTO shorts SELECT ramz,nass FROM tmp_shorts WHERE bk=%d' % bkid)
    except sqlite3.DatabaseError: pass
  else: c.execute('CREATE TABLE short (%s)' % schema['shorts'])
  c.execute('CREATE TABLE shrooh (%s)' % schema['shrooh'])
  insert_from_temp(c,'t'+str(bkid),'toc')
  insert_from_temp(c,'b'+str(bkid),'book')
  for i in ('men','mendetail','shorts'): c.execute('CREATE TABLE IF NOT EXISTS %s (%s)' % (i,schema[i]))
  if sharh_for: c.execute('INSERT INTO shrooh SELECT matnid,sharhid FROM tmp_shrooh WHERE sharh=%d' % bkid)
  c.executescript("DROP TABLE IF EXISTS tmp_main; DROP TABLE IF EXISTS tmp_shrooh; DROP TABLE IF EXISTS tmp_b%d; DROP TABLE IF EXISTS tmp_t%d;" % (bkid,bkid));
  #c.execute("END TRANSACTION;")
  cn.commit()


# update main set bk="درء تعارض العقل والنقل" where bkid=2023
def shamela3_import_single(ifile, ofile, bkid=-1, progress=None, truncate=True):
  """Import Shamela 3 .bok/.mdb files into Thwab SQLite .db file"""
  v,tb,bkids=identify_file(ifile)
  if v!=3 or main not in tb: raise TypeError # no need to check all tables ['com', 'main', 'men', 'mendetail', 'shorts', 'shrooh']
  if bkid!=-1:
    if bkid not in bkids: raise IndexError
  else:
    if len(bkids)==1: bkid=bkids[0]
    else: raise IndexError
  if truncate and os.path.exists(ofile): os.unlink(ofile)
  cn = sqlite3.connect(ofile,isolation_level=None)
  #c=cn.cursor()
  #c.execute("select count(rowid) from Main")
  shamela3_import(cn, ifile, bkid,progress)
  cn.close()

