# -*- coding: utf-8 -*-
import os.path

class ThwabConf(dict):
    def __init__(self,argv):
        self.p = os.path.expanduser('~/.asmaa')
        self.v = os.path.expanduser('~/')
        try: os.makedirs(self.p+'/memoir', 0777)
        except: pass
        try: os.makedirs(self.p+'/background', 0777)
        except: pass
        try: os.system('cp icons/face.jpg '+self.p+'/background')
        except: pass
        
        dict.__init__(self)
        self.__confs=['fontq','fontn','fonta','fontc','colorqf','colornf','coloraf','colorcf','colormf',
                      'colorqb','colornb','colorcb','colorsb','quran','path','start','tb','tr','sv','sh','pho','lb','mx','ka','ev','fi','ad']
        self['argv']=argv
        self['exe']=argv[0]
        self['exedir']=os.path.dirname(argv[0])
        self['datadir']=os.path.join(os.path.dirname(argv[0]),'..','share','asmaa')
        self['fontq']="28"
        self['fontn']="Simplified Naskh 24"
        self['fonta']="Simplified Naskh Bold 32"
        self['fontc']="KacstOne 15"
        self['colorqb']="#FDFDD7"
        self['colornb']="#FDFDD7"
        self['colorcb']="#F9F0CF"
        self['colorsb']='#FFFF80'
        self['colorqf']="#204000"
        self['colornf']='#0B0C8D'
        self['coloraf']="#860915"
        self['colormf']="#EC430A"
        self['colorcf']='#162116'
        self['quran']='1'
        self['path']='/home/hs/مكتبة أسماء/'
        self['start']=0
        self['tb']='0'
        self['tr']='0' # a تعديل الخط
        self['sv']='700'
        self['sh']='1000'
        self['pho']='icons/face.jpg'
        self['lb']='0'
        self['mx']='0'
        self['ka']='1' # a عرض قائمة الكتب
        self['ev']='0' # a الضغط على الخلفية
        self['fi']='1'
        self['ad']='4'
        self['conffile']=os.path.expanduser('~/.asmaa/asmaa.cfg')
        self['confdir']=os.path.dirname(self['conffile'])
        if not os.path.exists(self['datadir']): self['datadir']=self['exedir']
        if not os.path.exists(self['conffile']): self.save()
        else: self.load()

    def save(self):
        if not os.path.exists(self['confdir']):
            try: os.mkdir(os.path.expanduser(self['confdir']))
            except: raise
        try: f=open(self['conffile'],'w+')
        except: raise
        f.write('\n'.join(map(lambda i: i+'='+str(self[i]),self.__confs)))
        f.close()

    def load(self):
        try: f=open(self['conffile'],'r')
        except IOError: return
        s=f.read(); f.close()
        for l in s.split('\n'):
            l=l.strip()
            if not l: continue
            v=l.split('=',1)
            if not v or len(v)!=2 or not v[1] or v[0] not in self.__confs: continue
            self[v[0]]=v[1]
          
    def get_filename(self,fn):
        return os.path.join(self['datadir'],fn)


