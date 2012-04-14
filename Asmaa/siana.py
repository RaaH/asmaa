# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import sqlite3, os.path
import gtk, pango
from Asmaa.conf import ThwabConf
import re


gtk.widget_set_default_direction(gtk.TEXT_DIR_RTL)

def dlg(text_dl):
    md1 = gtk.MessageDialog(parent = None, flags = gtk.DIALOG_MODAL,
                    type = gtk.MESSAGE_INFO,
                     message_format = text_dl)
    md1.add_button("أغلق", gtk.RESPONSE_CLOSE)
    md1.run()
    md1.destroy()

class Siana(gtk.Window):
    
    def hala(self,*args):
        self.progress.set_text('جاري الفحص')
        self.cur.execute('SELECT bk FROM books')
        m1 = self.cur.fetchall()
        m2 = len(m1)
        m4 = [] 
        y  = 0
        while (gtk.events_pending()): gtk.main_iteration()
        while y < (m2):
            fd = m1[y][0]
            m4.append(fd)
            fr2 = self.pathasmaa+'books/'+fd+'.asm'
            if not os.path.exists(fr2):
                self.ls.append([fd+"   يوجد الاسم فقط"])
            j = (float(y)/float(m2))/2.0
            self.progress.set_fraction(j)
            y += 1
        list_n = os.listdir(self.pathasmaa+'books/')
        v = 0
        m3 = len(list_n)
        while v in range(m3):
            gk = u''+re.sub('.[Aa][Ss][Mm]','',list_n[v])
            if gk in m4:
                pass
            else:
                self.ls.append([gk+"   موجود وغير ملحق"])
            if os.path.getsize(self.pathasmaa+'books/'+list_n[v]) == 0:
                self.ls.append([gk+"   كتاب فارغ"])
            j1 = (float(v)/float(m3))+0.5
            self.progress.set_fraction(j1)
            v += 1
        self.progress.set_fraction(1.0)
        self.progress.set_text('انتهى الفحص')
        if len(self.ls) == 0:
            self.ls.append(['جميع البيانات سليمة'])
            
    def islah(self,*args):
        self.progress.set_fraction(0.0)
        self.progress.set_text('جاري عملية الصيانة')
        while (gtk.events_pending()):  gtk.main_iteration()
        self.cur.execute('SELECT bk FROM books')
        m1 = self.cur.fetchall()
        self.cur.execute('SELECT * FROM groups')
        m7 = self.cur.fetchall()
        m2 = len(m1)
        m4 = []
        y  = 0
        while y < (m2):
            fd = m1[y][0]
            m4.append(fd)
            fr2 = self.pathasmaa+'books/'+fd+'.asm'
            if not os.path.exists(fr2):
                self.cur.execute('delete from books where bk = "'+fd+'"')
                self.con.commit()
            y += 1
        list_n = os.listdir(self.pathasmaa+'books/')
        v = 0
        m3 = len(list_n)
        while v in range(m3):
            gk = u''+re.sub('.[Aa][Ss][Mm]','',list_n[v])
            if gk in m4:
                pass
            else:
                rf = u'كتب مسترجعة'
                self.cur.execute('SELECT val FROM groups where grp = "'+rf+'"')
                m5 = self.cur.fetchall()
                if len(m5) == 0:
                    self.cur.execute('INSERT INTO groups VALUES ("'+rf+'","'+'0'+'","'+str(len(m7)+1)+'")')
                    check = self.con.commit()
                self.cur.execute('INSERT INTO books VALUES ("'+gk+'","'+'0'+'","'+'0'+'")')
                check = self.con.commit()
            if os.path.getsize(self.pathasmaa+'books/'+list_n[v]) < 2:
                self.cur.execute('delete from books where bk = "'+gk+'"')
                self.con.commit()
                os.remove(self.pathasmaa+'books/'+list_n[v])
            v += 1 
        self.progress.set_fraction(1.0)
        self.progress.set_text('انتهى الصيانة')
        self.ls.clear()

    def __init__(self, argv = [__file__]):
        gtk.Window.__init__(self)
        self.conf = ThwabConf(argv)
        self.pathasmaa = self.conf['path']
        self.con = sqlite3.connect(self.pathasmaa+'data/book.asmaa',isolation_level = None)
        self.cur = self.con.cursor()
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,10)
        vb.set_border_width(10)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_title('المراقبة')
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file("icons/Configs-24.png")
        self.progress = gtk.ProgressBar()
        self.ls = gtk.ListStore(str)
        vb.pack_start(self.progress, 0,0)
        kh13 = gtk.TreeView()
        sah1 = gtk.TreeViewColumn('نتائج الفحص',gtk.CellRendererText(),text = 0)
        kh13.append_column(sah1)
        kh13.set_model(self.ls)
        kh13.modify_font(pango.FontDescription("KacstOne 13"))
        kh13.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color('#162116'))
        kh13.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color("#F9F0CF"))
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add(kh13)
        self.resize(500,250)
        vb.pack_start(scroll,1,1)
        vb.pack_start(hb,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.destroy())
        hb.pack_end(clo,0,0)
        hal = gtk.Button("الفحص")
        hal.connect('clicked',self.hala)
        hb.pack_start(hal,0,0)
        sia = gtk.Button("صيانة")
        sia.connect('clicked',self.islah)
        hb.pack_start(sia,0,0)
        self.add(vb)
        self.show_all()
        
        
