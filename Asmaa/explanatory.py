# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import sqlite3
import gtk, pango, re
import Asmaa.fuzzy as fuzzy
import itertools
from Asmaa.othman import Othman


gtk.widget_set_default_direction(gtk.TEXT_DIR_RTL)
def fuzz(text):
    wasl = u'\u0671'
    mdda = u'\u0653'
    alif_k = u'\u0670'
    skon = u'\u06e1'
    sli = u'\u06d6'
    text0 = re.sub(sli,u'',text)
    text1 = re.sub(wasl,u'ا',text0)
    text2 = re.sub(skon+"|"+mdda,u'',text1)
    text3 = re.sub(alif_k,u'ا',text2)
    return  text3

def dlg(text_dl):
    md1 = gtk.MessageDialog(parent = None, flags = gtk.DIALOG_MODAL,
                    type = gtk.MESSAGE_INFO,
                     message_format = text_dl)
    md1.add_button("أغلق", gtk.RESPONSE_CLOSE)
    md1.run()
    md1.destroy()

def populate_popup(view, menu):
    menu.hide_all()
    buff = view.get_buffer()
    if buff.get_has_selection():
        ddd = buff.get_selection_bounds()
        ddj = buff.get_text(ddd[0],ddd[1],True)
    f7 = gtk.MenuItem('نسخ')
    #   f7.connect('activate',ok_k)
    menu.prepend(f7)
    f7.set_sensitive(False)
    c4 = gtk.SeparatorMenuItem()
    menu.prepend(c4)
    f1 = gtk.MenuItem("تفسير آية")
    menu.prepend(f1)
    f1.set_sensitive(False)
    f2 = gtk.MenuItem("شرح مفردة")
    menu.prepend(f2)
    f2.set_sensitive(False)
    f3 = gtk.MenuItem("ترجمة راوٍ")
    menu.prepend(f3)
    f3.set_sensitive(False)
    if buff.get_has_selection():
        f1.set_sensitive(True)
        f2.set_sensitive(True)
        f3.set_sensitive(True)
        f7.set_sensitive(True)
    f1.connect("activate",lambda *a: Explanatory(u"تفسير آية",ddj))
    f2.connect("activate",lambda *a: Explanatory(u"شرح مفردة",ddj))
    f3.connect("activate",lambda *a: Explanatory(u"ترجمة راوٍ",ddj))
    f1.show()
    f2.show()
    f3.show()
    f7.show()
    c4.show()    

class Explanatory(gtk.Window):
    
    def tooltip_toc(self, widget, x, y, keyboard_tip, tooltip):
        if not widget.get_tooltip_context(x, y, keyboard_tip):
            return False
        else:
            model, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)

            value = model.get(iter, 1)
            tooltip.set_markup(" %s" %value[0])
            widget.set_tooltip_row(tooltip, path)
            return True
        
    
        
# a التفسير---------------------------------------------------------

    def page_quran(self, sora,aya):
        c = sqlite3.connect('data/meyasser',isolation_level=None)
        c1 = c.cursor()
        c1.execute("""SELECT id FROM pages WHERE sora=%d AND %d<=aya+na """% (sora,aya))
        pr=c1.fetchone()
        try: return pr[0]
        except: return 1
        
    def tafsir(self,nass):
        text = '"'+nass+'"'
        j = 0 
        __cn = sqlite3.connect('data/quran.db', isolation_level=None)
        __c=__cn.cursor()
        _c=__cn.cursor()
        __cn.create_function('fuzzy_normalize',1,fuzzy.normalize)
        s='''fuzzy_normalize(imlai) LIKE ? ESCAPE "|"'''
        text=fuzz(fuzzy.normalize(text))
        self.search_tokens=fuzzy.tokenize_search(text)
        l=map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
        if len(l)<1: return []
        self.condition=' AND '.join([s]*len(l))  
        __c.execute("""SELECT id FROM Quran WHERE %s""" % (self.condition), l)
        a = __c.fetchall()
        if len(a) == 0 : dlg('لاتوجد نتائج');return
        for s in range(len(a)):
            while (gtk.events_pending()): gtk.main_iteration()
            gt = a[s][0]
            isr = (gt/512)+1
            iya = gt-((isr-1)*512)
            g1= self.page_quran(isr , iya+1)
            j = j+1
            _c.execute("""SELECT sura_name FROM suranames""")
            b = _c.fetchall()
            g2 = str(b[isr-1][0])
            self.store.append([g1,g2,None,None,None,None,None,None])
            self.modtf(self.store[0][0])
            
    
    def modtf(self,idm):
        cn_r = sqlite3.connect('data/meyasser',isolation_level=None)
        cr_r = cn_r.cursor()
        cr_r.execute("""SELECT nass,sora,aya,na FROM pages WHERE id=%s""" % (idm))
        n_mef = cr_r.fetchall()
        try: sora,aya,na=n_mef[0][1],n_mef[0][2],n_mef[0][3]
        except: sora=0
        if sora>0 and sora<115:
            self.q=' '.join(self.othman.get_ayat(sora,aya,aya+na))
        self.display("\nـــــــــــــــــــ\n"+n_mef[0][0]+"\n",None)
        self.show_all()
        
# a الترجمة----------------------------------------------------------
       
    def tardjma(self,nass):
        cn_r = sqlite3.connect('data/rewat',isolation_level=None)
        cn_r.create_function('fuzzy_normalize',1,fuzzy.normalize)
        cr_r = cn_r.cursor()
        text = '"'+nass+'"'
        s='''fuzzy_normalize(name) LIKE ? ESCAPE "|"'''
        text=fuzzy.normalize(text)
        self.search_tokens=fuzzy.tokenize_search(text)
        l=map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
        if len(l)<1: return []
        condition=' AND '.join([s]*len(l))
        cr_r.execute("""SELECT * FROM rewat WHERE %s""" % (condition), l)
        trj = cr_r.fetchall()
        if len(trj) == 0 : dlg('لاتوجد نتائج');return
        self.store.clear()
        self.modtr(trj[0])
        for a in range(len(trj)):
            self.store.append([a,trj[a][1],trj[a][2],trj[a][3],trj[a][4],trj[a][5],trj[a][6],trj[a][7]])
      
    def modtr(self,list):
        text = "الاسم :  "+list[1]+"\n\
"+"المولد :  "+list[6]+"\n\
"+"الوفاة :  "+list[7]+"\n\
"+"الطبقة :  "+list[2]+"\n\
"+"الرواة عنه :  "+list[3]+"\n\
"+"الرتبة عند الحافظ :  "+list[4]+"\n\
"+"الرتبة عند الذهبي :  "+list[5]+"\n                     "
        text = re.sub("F",u'صحابي رضي الله عنه',text)
        text = re.sub("G",u'الثانية ، كبار التابعين',text)
        text = re.sub("H",u'الثالثة ، الوسطى من التابعين',text)
        text = re.sub("I",u'الرابعة ، تلي الوسطى من التابعين',text)
        text = re.sub("J",u'الخامسة ، صغار التابعين',text)
        text = re.sub("K",u'السادسة ، الذين عاصروا صغار التابعين',text)
        text = re.sub("L",u'السابعة ، كبار أتباع التابعين',text)
        text = re.sub("M",u'الثامنة ، الوسطى من أتباع التابعين',text)
        text = re.sub("N",u'التاسعة ، صغار أتباع التابعين',text)
        text = re.sub("O",u'العاشرة ، كبار الآخذين عن تبع الأتباع',text)
        text = re.sub("P",u'الحادية عشرة ، الوسطى من الآخذين عن تبع الأتباع',text)
        text = re.sub("Q",u'الثانية عشرة ، صغار الآخذين عن تبع الأتباع',text)
        text = re.sub("&lt;",u'<',text)
        text = re.sub("&gt;",u'>',text)
        text = re.sub("&quot;",u'"',text)
        text = re.sub("W",u'صلى الله عليه وسلم',text)
        text = re.sub(u"1 :",u'الأولى ،',text)
        self.q =""
        self.display(text,None)
        self.show_all()

# a المفردات------------------------------------------------------------------
           
    def mefrada(self,nass):
        cn_r = sqlite3.connect('data/me3djam',isolation_level=None)
        cn_r.create_function('fuzzy_normalize',1,fuzzy.normalize)
        cr_r = cn_r.cursor()
        text = u''+nass
        s='''fuzzy_normalize(tit) LIKE ? ESCAPE "|"'''
        text = fuzz(fuzzy.normalize(text))
        self.search_tokens = fuzzy.tokenize_search(text)
        l = map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
        if len(l) < 1: return []
        condition = ' OR '.join([s]*len(l))
        cr_r.execute("""SELECT * FROM titles WHERE %s""" % (condition), l)
        mef = cr_r.fetchall()
        if len(mef) == 0 : dlg('لاتوجد نتائج');return
        self.store.clear()
        self.modmf(mef[0][0],mef[0][1])
        for a in range(len(mef)):
            while (gtk.events_pending()): gtk.main_iteration()
            self.store.append([a,mef[a][1],mef[a][0],None,None,None,None,None])

    def modmf(self,idm,index):
        cn_r = sqlite3.connect('data/me3djam',isolation_level = None)
        cr_r = cn_r.cursor()
        cr_r.execute("""SELECT nass FROM pages WHERE id=%s""" % (idm))
        n_mef = cr_r.fetchall()
        self.q = ""
        self.display(n_mef[0][0]+"\n",index)
        self.show_all()
        
# a العرض----------------------------------------------------------------------
    
    def display(self,text,index):
        ss_tag = []
        self.buff.set_text(text)
        for tag1 in self.n_tag:
            self.buff.remove_tag(tag1, self.buff.get_start_iter(), self.buff.get_end_iter())
        n_tags=itertools.cycle(self.n_tag)
        for txt1 in [ "الاسم :  ","المولد :  ","الوفاة :  ","الطبقة :  "
                     ,"الرواة عنه :  ","الرتبة عند الحافظ :  ","الرتبة عند الذهبي :  "]:
            tag1=n_tags.next()
            i1=self.buff.get_start_iter()
            r=i1.forward_search(txt1, 0)
            if r: i1,i2=r
            while (r):
                self.buff.apply_tag(tag1,i1,i2)
                r=i2.forward_search(txt1, 0)
                if r: i1,i2=r
        self.n_tag[-1].set_property('font',"KacstOne Bold 17")
        self.n_tag[-1].set_property('foreground',"#660000")
        oi = self.buff.get_text(self.buff.get_start_iter(),self.buff.get_end_iter(),True).split()
        for er in range(len(oi)):
            rr = oi[er]
            if fuzzy.normalize(index) in fuzzy.normalize(rr):
                ss_tag.append(rr)
        for tag2 in self.s_tag:
            self.buff.remove_tag(tag2, self.buff.get_start_iter(), self.buff.get_end_iter())
        i_min,is0=None,None
        s_tags=itertools.cycle(self.s_tag)
        for txt2 in ss_tag:
            tag2=s_tags.next()
            is1=self.buff.get_start_iter()
            rs=is1.forward_search(txt2, 0)
            if rs: is1,is2=rs; is0=is1
            while (rs):
                self.buff.apply_tag(tag2,is1,is2)
                rs=is2.forward_search(txt2, 0)
                if rs: is1,is2=rs
            if is0 and (not i_min or i_min.compare(is0)>0): i_min=is0
        self.sw2.get_vadjustment().set_value(0)
        if i_min:
            while (gtk.events_pending()): gtk.main_iteration();
            self.buff.place_cursor(i_min)   
            m=self.buff.get_insert()
            self.view.scroll_to_mark(m, 0.0,True)
        self.s_tag[-1].set_property('background','#FFFF80')
        self.buff.insert_with_tags(self.buff.get_start_iter(), self.q, self.qr_tag) 
    
    def up0(self,*a):
        mod = self.tree.get_selection()
        ar = mod.get_selected()
        if ar[1]:
            df = self.store.get_path(ar[1])
            df = df[0]
            if df==0: df = df
            else: df = df-1
            i1 = self.store.get_iter(df,)
            self.tree.get_selection().select_iter(i1)
            self.tree.scroll_to_cell((df,))
            self.ok_row()
        
    def down0(self,*a):
        mod = self.tree.get_selection()
        ar = mod.get_selected()
        if ar[1]:
            df = self.store.get_path(ar[1])
            df = df[0]
            if df== len(self.store)-1: df = df
            else: df = df+1
            i1 = self.store.get_iter(df,)
            self.tree.get_selection().select_iter(i1)
            self.tree.scroll_to_cell((df,))
            self.ok_row()
    
    def ok_row(self,*a):
        t_selec = self.tree.get_selection()
        (model, i) = t_selec.get_selected()
        if i :
            r = model.get(i,0)[0]
            if self.tit == "ترجمة راوٍ": self.modtr(self.store[r])
            elif self.tit == "تفسير آية": self.modtf(r)
            elif self.tit == "شرح مفردة":
                r1 = model.get(i,2)[0]
                v = model.get(i,1)[0]
                self.modmf(r1,v)
            
    def __init__(self, tit,nass):
        gtk.Window.__init__(self)
        self.tit = tit
        self.othman=Othman(self)
        self.set_title(tit)
        self.set_default_size(650, 350)
        self.set_keep_above(True)
        hpaned = gtk.HPaned()
        self.store = gtk.ListStore(int,str,str,str,str,str,str,str)
        self.tree = gtk.TreeView()
        self.tree.set_model(self.store)
        column = gtk.TreeViewColumn('النتائج المحتملة', gtk.CellRendererText(),text=1)
        self.tree.append_column(column)
        self.tree.props.has_tooltip = True
        self.tree.connect("query-tooltip", self.tooltip_toc)
        self.view = gtk.TextView()
        self.view.connect_after("populate-popup", populate_popup)
        self.view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.view.set_editable(False)
        self.view.set_right_margin(20)
        self.view.set_left_margin(20)
        self.view.set_cursor_visible(False)
        self.buff = gtk.TextBuffer()
        self.qr_tag=[]
        self.qr_tag=self.buff.create_tag()
        self.n_tag = []
        self.n_tag.append(self.buff.create_tag())
        self.s_tag = []
        self.s_tag.append(self.buff.create_tag())
        self.view.set_buffer(self.buff)
        sw1 = gtk.ScrolledWindow()
        sw1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hpaned.pack1(sw1)
        sw1.add(self.tree)
        self.sw2 = gtk.ScrolledWindow()
        self.sw2.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hpaned.pack2(self.sw2)
        hpaned.set_position(150)
        self.sw2.add(self.view)
        self.set_position(gtk.WIN_POS_CENTER)
        self.view.modify_font(pango.FontDescription("KacstOne 15"))
        self.view.modify_text(gtk.STATE_NORMAL,color=gtk.gdk.Color("#204000"))
        self.view.modify_base(gtk.STATE_NORMAL,color=gtk.gdk.Color('#FFEED1'))
        self.tree.modify_font(pango.FontDescription("KacstOne 13"))
        self.tree.modify_text(gtk.STATE_NORMAL,color=gtk.gdk.Color('#FFFF80'))
        self.tree.modify_base(gtk.STATE_NORMAL,color=gtk.gdk.Color("#204000"))
        self.qr_tag.set_property('paragraph-background',"#F6FFD2")
        self.qr_tag.set_property('foreground','#990000')
        self.qr_tag.set_property('font',"Simplified Naskh 15")
        self.widget = gtk.Button("الرموز")
        im01 = gtk.Image()
        im01.set_from_file('icons/up.png')
        im02 = gtk.Image()
        im02.set_from_file('icons/down.png')
        self.up = gtk.Button()
        self.up.add(im01)
        self.up.connect('clicked',self.up0)
        self.down = gtk.Button()
        self.down.add(im02)
        self.down.connect('clicked',self.down0)
        vb = gtk.VBox(False,10)
        hb1 = gtk.HBox(False,10)
        vb.set_border_width(10)
        clo=gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.destroy())
        hb1.pack_start(self.up,0,0)
        hb1.pack_start(self.down,0,0)
        hb1.pack_end(clo,0,0)
        hb1.pack_end(self.widget,0,0)
        vb.pack_start(hpaned,1,1)
        vb.pack_start(hb1,0,0)
        self.add(vb)
        self.tree.connect("cursor-changed", self.ok_row)
        if tit == "ترجمة راوٍ":
            self.tardjma(nass)
            self.widget.connect("clicked", lambda *a: dlg("""١ - البخاري في صحيحه (خ).
٢ - البخاري في صحيحه معلقا (خت).
٣ - البخاري في الادب المفرد (بخ).
٤ - البخاري في خلق أفعال العباد (عخ).
٥‌ - البخاري في جزء القراءة خلق الامام (ز).
٦ - البخاري في رفع اليدين (ي).
٧ - مسلم في صحيحه (م).
٨ - مسلم في المقدمة (مق).
٩ - أبو داود في سننه (د).
١٠ - أبو داود في المراسيل (مد).
١١ - أبو داود في فضائل الانصار (صد).
١٢ - أبو داود في الناسخ (خد).
١٣ - أبو داود في القدر (قد).
١٤ - أبو داود في التفرد (ف).
١٥‌ - أبو داود في المسائل (ل).
١٦ - أبو داود في مسند مالك (كد).
١٧ - الترمذي في سننه (ت).
١٨ - الترمذي في الشمائل (تم).
١٩ - النسائي في سننه (س).
٢٠ - النسائي في مسند علي (عس).
٢١ - النسائي في عمل اليوم والليلة (سي).
٢٢ - النسائي في مسند مالك (كن).
٢٣ - النسائي في خصائص الامام علي (ص).
٢٤ - ابن ماجة في سننه(ق)."""))
        elif tit == "تفسير آية":
            self.tafsir(nass)
            self.widget.set_sensitive(False)
        elif tit == "شرح مفردة":
            self.mefrada(nass)
            self.widget.connect("clicked", lambda *a: dlg("""1_ ' - ' : الكلمة نفسها
        
2_ ' -ُ ' : عين المضارع مضمومة

3_ ' -َ ' : عين المضارع مفتوحة

4_ ' -ِ ' : عين المضارع مكسورة

5_ ' ج ' : الجمع

6_ ' جج ' : جمع الجمع

7_ ' مع ' : الكلمة معربة

8_ ' مو ' : الكلمة مولدة

9_ ' د ' : الكلمة دخيلة

10_ ' مج ' : أقرها المجمع اللغوي"""))
        if len(self.store) > 0:
            i1 = self.store.get_iter(0,)
            self.tree.get_selection().select_iter(i1)
            
