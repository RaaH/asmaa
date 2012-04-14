#! /usr/bin/python
import sys, os, os.path
from distutils.core import setup
from glob import glob

# to install type: 
# python setup.py install --root=/

def no_empty(l):
  return filter(lambda (i,j): j, l)

def recusive_data_dir(to, src, l=None):
  D=glob(os.path.join(src,'*'))
  files=filter( lambda i: os.path.isfile(i), D )
  dirs=filter( lambda i: os.path.isdir(i), D )
  if l==None: l=[]
  l.append( (to , files ) )
  for d in dirs: recusive_data_dir( os.path.join(to,os.path.basename(d)), d , l)
  return l

locales=map(lambda i: ('share/'+i,[''+i+'/asmaa.mo',]),glob('locale/*/LC_MESSAGES'))
data_files=no_empty(recusive_data_dir('share/asmaa', 'asmaa'))
data_files.extend(locales)
setup (name='asmaa', version='1.5',
      description='asmaa library',
      author='Ahmed Raghdi',
      author_email='asmaaarab@gmail.com',
      url='http://www.asmaaarab.wordpress.com/',
      license='Waqf',
      packages=['Asmaa'],
      scripts=['asmaa'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
      data_files=data_files
)


