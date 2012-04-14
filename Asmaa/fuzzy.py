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
import re

#harakat="ًٌٍَُِّْـ".decode('utf-8')
#normalize_tb=dict(map(lambda i: (ord(i),None),list(harakat)))
#normalize_tb[ord('ة'.decode('utf-8'))]=ord('ه'.decode('utf-8'))
#for i in list("ىئإؤأآء".decode('utf-8')):
#  normalize_tb[ord(i)]=ord('ا'.decode('utf-8'))

normalize_tb={
65: 97, 66: 98, 67: 99, 68: 100, 69: 101, 70: 102, 71: 103, 72: 104, 73: 105, 74: 106, 75: 107, 76: 108, 77: 109, 78: 110, 79: 111, 80: 112, 81: 113, 82: 114, 83: 115, 84: 116, 85: 117, 86: 118, 87: 119, 88: 120, 89: 121, 90: 122,
1600: None, 1569: 1575, 1570: 1575, 1571: 1575, 1572: 1575, 1573: 1575, 1574: 1575, 1577: 1607, 1611: None, 1612: None, 1613: None, 1614: None, 1615: None, 1616: None, 1617: None, 1618: None, 1609: 1575}
__sq_re=re.compile('[\s"]')

def normalize(s): return unicode(s).translate(normalize_tb)

def tokenize_search(s):
  '''Take a string and return a list of non-empty tokens, double quotes are group tokens, and double double quotes are escaped
s='abc def' -> ['acb', 'def']
s='abc def "Hello, world!"' -> ['acb', 'def','Hello, world!']
s='abc"def"ghi' -> ['acb', 'def', 'ghi']

s='abc def "He said: ""Hello, world!"""' -> ['abc', 'def', 'He said: "Hello, world!"']
'''
  global __sq_re
  skip,last,t=0,0,1
  l=[]
  for m in __sq_re.finditer(s):
    s1=s[last:m.start()].replace('""','"')
    if s[m.start()]=='"':
      if skip: skip=0; continue
      elif s[m.start():m.start()+2]=='""': skip=1; continue
      elif t==1: t=-1; l.append(s1); last=m.end(); continue
      else: t=1; l.append(s1); last=m.end(); continue
    elif t==-1: continue
    else: t=1; l.append(s1); last=m.end(); continue
  if len(s[last:])>0: l.append(s[last:])
  return filter(lambda a: len(a)>0, l)

def tashkil(s):
    t = []
    for a in len(s):
        for a1 in len(s[a]):
            for a2 in s[a][a1]:
                for a3 in [u'ّ',u'']:
                    for a4 in [u'َ',u'ُ',u'ِ',u'ْ',u'']:
                        for a5 in [u'ً',u'ٌ',u'ٍ',u'']:
                            t.append([a2+a3+a4])
    