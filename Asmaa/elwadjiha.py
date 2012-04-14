#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import os, re, sqlite3
import gtk, gobject, pango
import itertools, cPickle
from Asmaa.explanatory import Explanatory
from Asmaa.AsmaaDB import AsmaaBook
from Asmaa.about import show_about1
from Asmaa.othman import Othman
import Asmaa.fuzzy as fuzzy
from Asmaa.siana import Siana
from Asmaa.conf import ThwabConf

gtk.widget_set_default_direction(gtk.TEXT_DIR_RTL)
(COLUMN_FIXED,COLUMN_N) = range(2)






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

def dlg_res(text_dl):
    md0 = gtk.MessageDialog(parent = None, flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            type = gtk.MESSAGE_WARNING,
                             message_format = text_dl)
    ok_button = md0.add_button("موافق", gtk.RESPONSE_OK)
    cl_button = md0.add_button("أغلق", gtk.RESPONSE_CLOSE)
    def cll(widget,*a):
        global res_dlg
        res_dlg = False
    cl_button.connect('clicked',cll)
    def cb(widget,*a):
        global res_dlg
        res_dlg = True
    ok_button.connect('clicked',cb)
    md0.set_default_response(gtk.RESPONSE_YES)
    md0.run()
    md0.destroy()

def dlg(text_dl):
    md1 = gtk.MessageDialog(parent = None, flags = gtk.DIALOG_MODAL,
                    type = gtk.MESSAGE_INFO,
                     message_format = text_dl)
    md1.add_button("أغلق", gtk.RESPONSE_CLOSE)
    md1.run()
    md1.destroy()
 
def hide_cb(w, *args): w.hide(); return True
    
# class البداية------------------------------------------------------------------
    
class ThwabApplication: 
    
    def do_close(self,*a):
        self.close0()
        gtk.main_quit()
    
    def djadid(self,*args):
        tt = self.notebook.get_n_pages()
        for s in range(tt):
            ui = self.notebook.get_nth_page(s)
            if ui.cnm.get_text() == "جديد الإصدار":
                self.notebook.set_current_page(s)
                return
        self.hr = u"جديد الإصدار"
        qa = "data/new_re"
        dv = warakat(qa)
        self.notebook.append_page(dv, TabLabel(dv,self.hr))
        self.notebook.set_tab_reorderable(dv,True)
        self.notebook.set_current_page(-1)
        ui = self.notebook.get_nth_page(-1)
        ui.cnm.set_text(self.hr)
        if tt == 0:
            self.event_box1.hide_all()
            self.notebook.show_all()
        self.do_win()
        ui.hb.hide_all()
        ui.view.set_editable(False)
        ui.view.set_cursor_visible(False)
        ui.view.modify_font(pango.FontDescription("KacstOne 18"))

    def do_win(self,*a):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        self.win.set_title('مكتبة أسماء ('+ui.cnm.get_text()+')')  
         
    def stop(self,*a):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        try: ui.f0 = len(ui.sto)
        except: return
        
    def __init__(self, argv = [__file__]):
        self.w = None
        self.conf = ThwabConf(argv)
        self.othman = Othman(self.conf)
        self.pathasmaa = self.conf['path']
        self.build_gui()
        if self.conf['start'] == 0:
            self.ch_ph()
            self.conf['start'] = 1
            self.conf.save()
        self.tree0()
        
    def insh(self, *a):
        dialog = gtk.Dialog("ورقة بحث جديدة", None,
                            gtk.DIALOG_DESTROY_WITH_PARENT) 
        add = dialog.add_button('إنشاء', 1)
        close = dialog.add_button('إغلاق', 2)
        ent_wr = gtk.Entry()
        dialog.vbox.pack_end(ent_wr, True, True, 0)
        def new_wrk(widget,*a):
                qq = ent_wr.get_text()
                if qq == '':
                    dlg('أدخل اسما مناسبا في مكانه أولا')
                else :
                    ee = open(self.conf.p+'/memoir/'+qq,'w')
                    ee.write(u'ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ\n')
                    ee.close()
                    self.store_sah.append([qq])
                    ent_wr.set_text('')
                    dlg('تمّ إضافة ورقة بحث')
                    dialog.destroy()
        add.connect("clicked", new_wrk)
        def close0(widget,*a):
            dialog.destroy()
        close.connect("clicked", close0)
        dialog.show_all()
      
    def tree0(self,*args):
        self.store_s.clear()
        self.store_k.clear()
        self.store_kaima1.clear()
        try:
            self.con = sqlite3.connect(self.pathasmaa+'data/book.asmaa',isolation_level = None)
            self.cur = self.con.cursor()
            self.cur1 = self.con.cursor()
            self.cur.execute('SELECT * FROM groups')
            self.fe = self.cur.fetchall()
            y = 0 
            while (gtk.events_pending()): gtk.main_iteration()
            while y in range(len(self.fe)):
                y1 = str(y+1)
                self.cur.execute('SELECT * FROM groups where tar = "'+y1+'"')
                self.fe1 = self.cur.fetchall()
                self.a1 = self.store_k.append(None,[self.fe1[0][0]])
                self.a2 = self.store_s.append( None, (self.fe1[0][0], None) )
                self.store_kaima1.append([self.fe1[0][0]])
                self.dz = str(self.fe1[0][1])
                self.cur.execute('SELECT * FROM books where val = "'+self.dz+'" ORDER BY bk')
                self.fz = self.cur.fetchall()
                x = 0 
                while x in range(len(self.fz)):
                    self.store_k.append(self.a1,[self.fz[x][0]])
                    self.store_s.append( self.a2, (self.fz[x][0],None) )
                    x += 1
                y += 1  
        except: dlg(''' قد يكون القرص الذي به \nالمكتبة غير مضموم !!''')
        
    def bkgs(self,list_p,qw):
        v = qw
        while v in range(len(list_p)+qw):
            while (gtk.events_pending()):gtk.main_iteration()
            bb = gtk.EventBox()
            self.n_p = self.conf.p+'/background/'+list_p[v-qw]
            pixbufanim = gtk.gdk.pixbuf_new_from_file(self.conf.p+'/background/'+list_p[v-qw])
            bb.set_name(self.conf.p+'/background/'+list_p[v-qw])
            scaled_buf = pixbufanim.scale_simple(128,128,gtk.gdk.INTERP_BILINEAR)
            image = gtk.Image()
            bb.add(image)
            image.set_from_pixbuf(scaled_buf)
            self.tab_c.attach(bb,v%3,(v%3)+1,(v/3),(v/3)+1)
            bb.connect("button_press_event",self.jjj)
            bb.show_all()
            v += 1
    def jjj(self,gg,hh):
        f1 = gg.get_name()
        self.conf['pho'] = f1
        self.conf.save()
        self.expose(self.event_box1, self.ev) 
               
    def ch_pho(self,*args):
        w_pho = gtk.Window()
        w_pho.set_title('اختر الخلفية')
        w_pho.set_modal(True)
        self.tab_c = gtk.Table(3,3,True)
        self.tab_c.set_border_width(10)
        self.tab_c.set_row_spacings(10)
        self.tab_c.set_col_spacings(10)
        sco = gtk.ScrolledWindow()
        sco.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sco.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        bf = gtk.Button('إضافة')
        def add_cb(widget, *args):
            add_dlg = gtk.FileChooserDialog("اختر صورة الخلفية",
                                          buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            ff = gtk.FileFilter()
            ff.set_name('png , jpg')
            ff.add_pattern('*.[Pp][Nn][Gg]')
            ff.add_pattern('*.[Jj][Pp][Gg]')
            add_dlg.add_filter(ff)
            add_dlg.set_select_multiple(True)
            add_dlg.run()
            list_a = []
            qw = len(os.listdir(self.conf.p+'/background/'))
            for i in add_dlg.get_filenames():
                os.system('cp "'+i+'" '+self.conf.p+'/background/')
                list_a.append(os.path.basename(i))
            add_dlg.destroy()
            self.bkgs(list_a,qw)
        bf.connect('clicked',add_cb)
        bc = gtk.Button('مسح')
        bc.set_sensitive(False)
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,10)
        vb.set_border_width(10)
        hb.pack_start(bf,0,0)
        hb.pack_start(bc,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: w_pho.destroy())
        hb.pack_end(clo,0,0)
        vb.pack_start(sco,1,1)
        vb.pack_start(hb,0,0)
        sco.add_with_viewport(self.tab_c)
        w_pho.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        w_pho.set_position(gtk.WIN_POS_CENTER)
        list_p = os.listdir(self.conf.p+'/background/')
        w_pho.resize(470,400)
        w_pho.add(vb)
        w_pho.show_all()
        self.bkgs(list_p,0)
   
    def ggg(self,*args):
        self.pathasmaa = self.f_ch_d.get_filename()+'/'
        self.conf['path']=self.pathasmaa
        self.conf.save()
    
        
    def expose(self,widget, ev):
      #  global ev
        self.ev = ev
        g = gtk.gdk.screen_height()
        f = gtk.gdk.screen_width()
        try: pixbuf = gtk.gdk.pixbuf_new_from_file(self.conf['pho'])
        except: pixbuf = gtk.gdk.pixbuf_new_from_file('icons/face.jpg')
        scaled_buf = pixbuf.scale_simple(f,g,gtk.gdk.INTERP_BILINEAR)
        widget.window.draw_pixbuf(widget.style.bg_gc[gtk.STATE_NORMAL], scaled_buf, 0, 0, 0, 0)
        if widget.get_child() != None:
            widget.propagate_expose(widget.get_child(), ev)
        return True 
        
    def ch_ph(self,*args):  
        self.f_ch_d = gtk.FileChooserDialog("مسار الكتب والبيانات الخاصة بالمكتبة",None,
                                gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.f_ch_d.set_current_folder(self.pathasmaa)
        ok_b1 = self.f_ch_d.add_button('موافق', gtk.RESPONSE_OK)
        ok_b1.set_sensitive(False)
        ok_b2 = self.f_ch_d.add_button('أغلق', gtk.RESPONSE_OK)
        def cb1(widget,*a):
            self.ggg()
            self.f_ch_d.destroy()
            self.tree0()
        ok_b1.connect('clicked',cb1)
        def cb2(widget,*a):
            self.f_ch_d.destroy()
        ok_b2.connect('clicked',cb2)
        def lll(widget,*a):
            vvv = self.f_ch_d.get_filename()
            if os.path.exists(vvv+"/data/book.asmaa"):
                ok_b1.set_sensitive(True)
            else: ok_b1.set_sensitive(False)
        self.f_ch_d.connect("selection-changed",lll) 
        self.f_ch_d.run()
        self.f_ch_d.destroy()
        
    def new_lib(self,*args):  
        self.f_ch_n = gtk.FileChooserDialog("مسار الكتب والبيانات للمكتبة المفرّغة",None,
                                gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_OK))
        self.f_ch_n.set_current_folder(self.pathasmaa) 
        ok_button = self.f_ch_n.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        def ggn(widget,*args):
            self.pathasmaa = self.f_ch_n.get_current_folder()+u'/مكتبة أسماء/'
            self.conf['path'] = self.pathasmaa
            self.conf.save()
            os.system('cd '+str(self.f_ch_n.get_current_folder())+'/;tar -xvf /usr/share/asmaa/data/asmaa-library.tar')
        ok_button.connect('clicked', ggn)
        self.f_ch_n.run()
        self.f_ch_n.destroy()
        self.tree0()

    def ch_ph0(self,*args):
        self.ch_ph()

    def card(self,*args):
        global label10
        windo = gtk.Window(gtk.WINDOW_POPUP)
        def sdd(widget,*a):
            windo.destroy()
        windo.connect("destroy", sdd)
        windo.set_position(gtk.WIN_POS_CENTER)
        event_box = gtk.EventBox()
        windo.add(event_box)
        windo.set_border_width(20)
        label10 = gtk.Label()
        i = self.notebook.get_current_page()
        w = self.notebook.get_nth_page(i)
        try: label10.set_text(w.sdb.book_name+"\n\n"+w.sdb.betaka)
        except: return
        label10.modify_font(pango.FontDescription("KacstOne 15"))
        label10.modify_fg(gtk.STATE_NORMAL,color = gtk.gdk.Color("#204000"))
        event_box.add(label10)
        event_box.connect("button_press_event", sdd)
        event_box.realize()
        event_box.modify_bg(gtk.STATE_NORMAL,color = gtk.gdk.Color("#C1E9D4"))
        windo.modify_bg(gtk.STATE_NORMAL,color = gtk.gdk.Color("#C1E9D4"))
        windo.show_all()

# a الخط-------------------------------------------------------------------------
    
    def font(self):
        for s in range(self.notebook.get_n_pages()):
            try:
                ui = self.notebook.get_nth_page(s)
                ui.qr_tag.set_property('paragraph-background',self.colorqb)
                ui.qr_tag.set_property('foreground',self.colorqf)
                ui.qr_tag.set_property('font',"Simplified Naskh "+self.fontq)
                ui.r_tag[-1].set_property('foreground',self.colormf)
                ui.q_tag[-1].set_property('foreground',self.colormf) 
                ui.h_tag[-1].set_property('font',self.fonta)
                ui.h_tag[-1].set_property('foreground',self.coloraf) 
                ui.search_tags_list[-1].set_property("background", self.colorsb) 
                ui.view.modify_font(pango.FontDescription(self.fontn))
                ui.view.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colornf))
                ui.view.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colornb))
                ui.toc.modify_font(pango.FontDescription(self.fontc))
                ui.toc.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcf))
                ui.toc.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcb))
            except: pass

# a فتح كتاب---------------------------------------------------------------------

    def highlight_headers(self,pid):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        i = ui.buffer.get_start_iter()
        for level,txt in ui.sdb.get_headers_in_page_id(pid):
            r = i.forward_search(txt,0)
            if r:
                i1,i2 = r
                if i2: ui.buffer.apply_tag(ui.h_tag[-1],i1,i2); i = i2
        
        for tag1 in ui.r_tag:
            ui.buffer.remove_tag(tag1, ui.buffer.get_start_iter(), ui.buffer.get_end_iter())
        r_tags = itertools.cycle(ui.r_tag)
        
        for txt1 in ['صلى الله عليه وسلم','بسم الله الرحمن الرحيم','بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيم '
                     ,'بِسْمِ اللهِ الرَّحْمَنِ الرَّحِيم','صلى الله عليه و سلم','﴾'
                     ,'﴿']:
            tag1 = r_tags.next()
            i1 = ui.buffer.get_start_iter()
            r = i1.forward_search(txt1, 0)
            if r: i1,i2 = r
            while (r):
                ui.buffer.apply_tag(tag1,i1,i2)
                r = i2.forward_search(txt1, 0)
                if r: i1,i2 = r
    def page_highlight(self):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        try: 
            for tag in ui.search_tags_list:
                ui.buffer.remove_tag(tag, ui.buffer.get_start_iter(), ui.buffer.get_end_iter())
        except: return
        i_min,i0 = None,None
        search_tags = itertools.cycle(ui.search_tags_list)
        ui.search_tokens0 = []
        oi = ui.buffer.get_text(ui.buffer.get_start_iter(),ui.buffer.get_end_iter(),True).split()
        if len(ui.search_tokens) == 1 :
            for er in range(len(oi)):
                if ui.search_tokens == []: return
                ss = ui.search_tokens[0]
                kk = len(ss.split())
                ee = oi[er:er+kk]
                rr = ' '.join(ee)
                if ss in fuzz(fuzzy.normalize(rr)):
                    ui.search_tokens0.append(rr)
        else:
            for er in range(len(oi)):
                for et in range(len(ui.search_tokens)): 
                    if ui.search_tokens[et] in fuzz(fuzzy.normalize(oi[er])) or ui.search_tokens[et] in oi[er]:
                        ui.search_tokens0.append(oi[er])
        for s in ui.search_tokens0:
            tag = search_tags.next()
            i1 = ui.buffer.get_start_iter() 
            r = i1.forward_search(s, 0)
            if r: i1,i2 = r; i0 = i1
            while (r):
                ui.buffer.apply_tag(tag,i1,i2)
                r = i2.forward_search(s, 0)
                if r: i1,i2 = r
            if i0 and (not i_min or i_min.compare(i0) > 0): i_min = i0
        ui.sw0.get_vadjustment().set_value(0)
        if i_min:
            ui.buffer.place_cursor(i_min)   
            m = ui.buffer.get_insert()
            ui.view.scroll_to_mark(m, 0.0,True)
            
    def display_text(self,r,page_id = None,highlight = []):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        if not r: return
        if page_id!= None:
            try: ui.toc_store.foreach(ui.toc_highlight, page_id)
            except: pass
        try: sora,aya,na = r[5],r[6],r[7]
        except: sora = 0
        ui.buffer.set_text(r[1].replace('EX','').replace('{','﴿').replace('}','﴾').\
                           replace('0','٠').replace('1','١').replace('2','٢').\
                           replace('3','٣').replace('4','٤').replace('5','٥‌').\
                           replace('6','٦').replace('7','٧').replace('8','٨').\
                           replace('9','٩').replace('+',''));
        if sora > 0 and sora < 115:
            q = ' '.join(ui.othman.get_ayat(sora,aya,aya+na))
            ui.buffer.insert(ui.buffer.get_start_iter(), u"\nـــــــــــــــــــ\n")
            ui.buffer.insert_with_tags(ui.buffer.get_start_iter(), q, ui.qr_tag)
            for tag1 in ui.q_tag:
                ui.buffer.remove_tag(tag1, ui.buffer.get_start_iter(), ui.buffer.get_end_iter())
            q_tags = itertools.cycle(ui.q_tag)
            for txt1 in ['ٱللَّه','بِٱللَّه','ٱللَّهُمّ','ٱلله','لِلَّه','فَٱللَّه','۝','٠','١','٢','٣','٤','٥','٦','٧','٨','٩','۞']:
                tag1 = q_tags.next()
                i1 = ui.buffer.get_start_iter()
                r = i1.forward_search(txt1, 0)
                if r: i1,i2 = r
                while (r):
                    ui.buffer.apply_tag(tag1,i1,i2)
                    r = i2.forward_search(txt1, 0)
                    if r: i1,i2 = r
        ui.buffer.place_cursor(ui.buffer.get_start_iter())
        ui.sw0.get_vadjustment().set_value(0.0)
        ui.sw0.get_hadjustment().set_value(0.0) 
        ui.current_id = page_id   
    
    def open_bk(self,nbk,idbk,hr):
        fd = nbk
        ri = idbk
        tt = self.notebook.get_n_pages()
        thv = ThwabViewer(self,fd,1)
        if len(self.list_book) == 20: self.list_book.pop(0)
        if hr != "دليل المستخدم" and hr != "القرآن الكريم":
            if hr in self.list_book:
                self.list_book.remove(hr)
            self.list_book.append(hr)
        else: pass
        if hr == "دليل المستخدم":
            for s in range(tt):
                ui = self.notebook.get_nth_page(s)
                if ui.cnm.get_text() == "دليل المستخدم":
                    self.notebook.set_current_page(s)
                    return
        ss = TabLabel(thv,hr)
        self.notebook.append_page(thv, ss)
        self.notebook.set_tab_reorderable(thv,True)
        self.notebook.set_current_page(-1)
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        ui.cnm.set_text(hr)
        if ri > 1 : i = ri
        else: r,i = ui.sdb.first_page()
        r = ui.sdb.get_text_body(nbk,i)
        self.font()
        self.display_text(r,i)
        self.highlight_headers(i)
        ui.n_pg(r)
        if tt == 0:
            self.event_box1.hide_all()
            self.notebook.show_all()
        self.do_win()
        try: 
            output = open(self.pathasmaa+'data/last-books.pkl', 'wb')
            cPickle.dump(self.list_book, output)
            output.close()
        except: pass

# a دليل المستخدم---------------------------------------------------------

    def dalil11( self,*args):
        self.hr = 'دليل المستخدم'
        fd = 'data/dalil'
        nbk = fd
        idbk = 1
        self.open_bk(nbk, idbk,self.hr)
  
# a المفضلة----------------------------------------------------------------
  
    def adfav( self,*a):
        n = self.notebook.get_current_page()
        try: r1 = self.notebook.get_nth_page(n).sds().get_text()
        except: return
        if r1 in ['دليل المستخدم','القرآن الكريم']:
            dlg('لا يمكن إضافة هذا الكتاب إلى المفضلة !')
        else :
            y = open(self.pathasmaa+'data/favorite/'+r1 , 'w')
            y.close()
            dlg('تم إضافة الكتاب إلى المفضلة !')
    
    def fav11( self,*args):
        if not os.path.exists(self.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
        self.store_fav.clear()
        self.wf = gtk.Window()
        self.wf.set_keep_above(True)
        self.wf.set_modal(True)
        self.wf.set_title('الكتب المفضلة')
        self.wf.set_icon_from_file("icons/Fav-Books-24.png")
        self.wf.set_position(gtk.WIN_POS_CENTER)
        self.wf.resize(350,400)
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,10)
        vb.set_border_width(10)
        scof1 = gtk.ScrolledWindow()
        scof1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scof1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        kf1 = gtk.TreeView()
        kf1.set_headers_visible(False)
        list_v = os.listdir(self.pathasmaa+'data/favorite/')
        for v in range(len(list_v)):
            self.store_fav.append([list_v[v]])
        def ok_k(widget,*args):
            if not os.path.exists(self.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
            global hr , fjj ,fhh
            t_selection = kf1.get_selection()
            (model, i) = t_selection.get_selected()
            if not i:
                (p,c) = kf1.get_cursor()
                i = self.store_fav.get_iter(p)
                if not i: return
            r = model.get(i,0)[0]
            r = str(r)
            self.hr = str(r)
            fd = self.pathasmaa+'books/'+r+'.asm'
            fd0 = th.pathasmaa+'data/book.asmaa'
            self.c = sqlite3.connect(fd0,isolation_level = None)
            cr = self.c.cursor()
            cr.execute('select fav from books where bk = "'+self.hr+'"')
            rd = cr.fetchall()
            try: ri = int(rd[0][0])
            except: ri = 1
            self.open_bk(fd, ri,self.hr)
            self.wf.destroy()
        kf1.connect("row-activated", ok_k)
        saf1 = gtk.TreeViewColumn('الكتب',gtk.CellRendererText(),text = 0)
        kf1.append_column(saf1)
        kf1.set_model(self.store_fav)
        kf1.modify_font(pango.FontDescription(self.fontc))
        kf1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcf))
        kf1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcb))
        scof1.add(kf1)
        br = gtk.Button("حذف")
        def rm(widget, *args):
            global res_dlg
            (model1, i1) = kf1.get_selection().get_selected()
            if i1 :
                r1 = model1.get_value(i1,0)
                dlg_res("هل ترغب في حذف الكتاب المحددة من المفضلة ؟")
                if res_dlg == False: return
                else:
                    os.remove(self.pathasmaa+'data/favorite/'+r1)
                    self.store_fav.remove(i1)
                    res_dlg = False
        br.connect('clicked',rm)
        hb.pack_start(br,0,0)
        bc = gtk.Button("مسح")
        def cl(widget, *args):
            global res_dlg
            dlg_res("هل ترغب في حذف جميع الكتب من المفضلة ؟")
            if res_dlg == False: return
            else:
                list_v = os.listdir(self.pathasmaa+'data/favorite/')
                for v in range(len(list_v)):
                    r1 = list_v[v]
                    os.remove(self.pathasmaa+'data/favorite/'+r1)
                self.store_fav.clear()
                res_dlg = False
        bc.connect('clicked',cl)
        vb.pack_start(scof1,1,1)
        hb.pack_start(bc,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.wf.destroy())
        hb.pack_end(clo,0,0)
        vb.pack_start(hb,0,0)
        self.wf.add(vb)
        self.wf.show_all()

# a المصحف------------------------------------------------------------------
  
    def otm(self,*args):
        self.hr = 'القرآن الكريم'
        fd = 'data/koran'
        g = self.conf['quran']
        f = int(g)
        nbk = fd
        idbk = f
        self.open_bk(nbk, idbk,self.hr)
        n = self.notebook.get_current_page()
        self.notebook.get_nth_page(n).sav.set_sensitive(False)
        self.notebook.get_nth_page(n).inc_is_quran.set_active(True)
        self.notebook.get_nth_page(n).inc_is_quran.set_sensitive(False)
        self.notebook.get_nth_page(n).view.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(self.colorqb))

# a خرج التوضيح----------------------------------------------------------------    
    
    def tawdih(self,nass,tit):
        Explanatory(tit,nass)

# a المحفوظات----------------------------------------------------------------    
    
    def sav11( self,*args):
        if not os.path.exists(self.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
        self.store_sav.clear()
        self.cur1.execute('SELECT * FROM kept')
        sav0 = self.cur1.fetchall()
        self.store_fav.clear()
        for a1 in range(len(sav0)):
            self.store_sav.append([sav0[a1][0],sav0[a1][2],sav0[a1][1]])
        self.ws = gtk.Window()
        self.ws.set_modal(True)
        self.ws.set_keep_above(True)
        self.ws.set_icon_from_file("icons/Books-Saved-24.png")
        self.ws.set_title('المواضع المحفوظة')
        self.ws.set_position(gtk.WIN_POS_CENTER)
        self.ws.resize(350,400)
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,10)
        vb.set_border_width(10)
        scos1 = gtk.ScrolledWindow()
        scos1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scos1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        ks1 = gtk.TreeView()
        def ok_k(widget,*args):
            t_selection = ks1.get_selection()
            (model, i) = t_selection.get_selected()
            if not i:
                (p,c) = ks1.get_cursor()
                i = self.store_sav.get_iter(p)
                if not i: return
            self.hr = model.get(i,1)[0]
            ri = int(model.get(i,2)[0])
            fd = self.pathasmaa+'books/'+self.hr+'.asm'
            nbk = fd
            idbk = ri
            self.open_bk(nbk, idbk,self.hr)
            self.ws.destroy()
        ks1.connect("row-activated", ok_k)
        sas1 = gtk.TreeViewColumn('اسم الموضع',gtk.CellRendererText(),text = 0)
        ks1.append_column(sas1)
        sas2 = gtk.TreeViewColumn('الكتاب',gtk.CellRendererText(),text = 1)
        ks1.append_column(sas2)
        ks1.set_model(self.store_sav)
        ks1.modify_font(pango.FontDescription(self.fontc))
        ks1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcf))
        ks1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcb))
        scos1.add(ks1)
        br = gtk.Button("حذف")
        def rm(widget, *args):
            global res_dlg
            (model1, i1) = ks1.get_selection().get_selected()
            if i1 :
                dlg_res(" هل ترغب في حذف الموضع المحدد ؟")
                if res_dlg == False: return
                else:
                    res_dlg = False
                    r1 = model1.get_value(i1,0)
                    self.cur1.execute('delete from kept where nam = "'+r1+'"')
                    check1 = self.con.commit()
                    if (check1 == None):
                        self.store_sav.remove(i1)
        br.connect('clicked',rm)
        hb.pack_start(br,0,0)
        bc = gtk.Button("مسح")
        
        def cl(widget, *args):
            global res_dlg
            dlg_res(" هل ترغب في حذف جميع المواضع ؟")
            if res_dlg == False: return
            else:
                res_dlg = False
                self.cur1.execute('delete from kept')
                check1 = self.con.commit()
                if (check1 == None):
                    self.store_sav.clear()
        bc.connect('clicked',cl)
        vb.pack_start(scos1,1,1)
        hb.pack_start(bc,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.ws.destroy())
        hb.pack_end(clo,0,0)
        vb.pack_start(hb,0,0)
        self.ws.add(vb)
        self.ws.show_all()
    
# a أوراق البحث----------------------------------------------------------------
           
    def awrak_sh( self,*args):
        self.wh = gtk.Window()
        self.wh.set_modal(True)
        self.wh.set_keep_above(True)
        self.wh.set_icon_from_file("icons/Papers-24.png")
        self.wh.set_title('أوراق البحث')
        self.wh.set_position(gtk.WIN_POS_CENTER)
        self.wh.resize(350,400)
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,10)
        vb.set_border_width(10)
        scos1 = gtk.ScrolledWindow()
        scos1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scos1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        kh1 = gtk.TreeView()
        kh1.set_headers_visible(False)
        sah1 = gtk.TreeViewColumn('البحوث',gtk.CellRendererText(),text = 0)
        kh1.append_column(sah1)
        kh1.set_model(self.store_sah)
        kh1.modify_font(pango.FontDescription(self.fontc))
        kh1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcf))
        kh1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcb))
        scos1.add(kh1)
        list_n = os.listdir(self.conf.p+'/memoir/')
        self.store_sah.clear()
        for v in range(len(list_n)):
            self.store_sah.append([list_n[v]])
        br = gtk.Button("حذف")
        def ok_k(widget,*args):
            t_selection = kh1.get_selection()
            (model, i) = t_selection.get_selected()
            if not i:
                (p,c) = kh1.get_cursor()
                i = self.store_sav.get_iter(p)
                if not i: return
            na = model.get(i,0)[0]
            tt = self.notebook.get_n_pages()
            self.hr = "ورقة البحث : "+na
            qa = self.conf.p+'/memoir/'+na
            dv = warakat(qa)
            self.notebook.append_page(dv, TabLabel(dv,self.hr))
            self.notebook.set_tab_reorderable(dv,True)
            self.notebook.set_current_page(-1)
            ui = self.notebook.get_nth_page(-1)
            ui.cnm.set_text(self.hr)
            if tt == 0:
                self.event_box1.hide_all()
                self.notebook.show_all()
            self.do_win()
            self.wh.destroy()
        kh1.connect("row-activated", ok_k)
        def rm(widget, *args):
            global res_dlg
            (model1, i1) = kh1.get_selection().get_selected()
            if i1 :
                dlg_res("هل ترغب في حذف الورقة المحددة ؟")
                if res_dlg == False: return
                else:
                    r1 = model1.get_value(i1,0)
                    os.remove(self.conf.p+'/memoir/'+r1)
                    self.store_sah.remove(i1)
                    res_dlg = False
            
        br.connect('clicked',rm)
        hb.pack_start(br,0,0)
        bc = gtk.Button("مسح")
        def cl(widget, *args):
            global res_dlg
            dlg_res("هل ترغب في حذف جميع أوراق البحث ؟")
            if res_dlg == False: return
            else:
                list_n = os.listdir(self.conf.p+'/memoir/')
                for v in range(len(list_n)):
                    r1 = list_n[v]
                    os.remove(self.conf.p+'/memoir/'+r1)
                self.store_sah.clear()
                res_dlg = False
        bc.connect('clicked',cl)
        vb.pack_start(scos1,1,1)
        hb.pack_start(bc,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.wh.destroy())
        hb.pack_end(clo,0,0)
        vb.pack_start(hb,0,0)
        self.wh.add(vb)
        self.wh.show_all()
    
    def search_special(self, *a):
        self.wv = gtk.Window()
        self.wv.set_modal(True)
        self.wv.set_keep_above(True)
        self.wv.set_title('بحث خاص')
        self.wv.set_position(gtk.WIN_POS_CENTER) 
        ent_wr = gtk.Entry()
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,4)
        vb.set_border_width(10)
        tab_1 = gtk.Table(1,3,True)
        tab_1.set_col_spacings(4)
        vb.pack_start(ent_wr, 0, 0)
        taf = gtk.Button('تفسير')
        def taf0(widget,*a):
            ddj = ent_wr.get_text()
            if ddj == '': return
            self.wv.destroy()
            self.tawdih(ddj,u"تفسير آية")
        taf.connect('clicked',taf0)
        tar = gtk.Button('ترجمة')
        def tar0(widget,*a):
            ddj = ent_wr.get_text()
            if ddj == '': return
            self.wv.destroy()
            self.tawdih(ddj,u"ترجمة راوٍ")
        tar.connect('clicked',tar0)
        mef = gtk.Button('شرح')
        def mef0(widget,*a):
            ddj = ent_wr.get_text()
            if ddj == '': return
            self.wv.destroy()
            self.tawdih(ddj,u"شرح مفردة")
        mef.connect('clicked',mef0)
        tab_1.attach(tar,0,1,0,1)
        tab_1.attach(taf,1,2,0,1)
        tab_1.attach(mef,2,3,0,1)
        hb.pack_start(tab_1,0,0)
        hb.pack_start(gtk.Label('            '),0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.wv.destroy())
        hb.pack_end(clo,0,0)
        vb.pack_start(hb,0,0)
        self.wv.add(vb)
        self.wv.show_all()
        
# a نتائج البحث في الصفحة الحالية----------------------------------------------------------------

    def srh_pg(self,*a):
        rr = self.ent_find.get_text()
        n = self.notebook.get_current_page()
        if n == -1: return
        if len(rr) > 0:
            rr = fuzzy.normalize(rr.strip())
            yy = rr.split()
            kk = len(yy)
            self.notebook.get_nth_page(n).search_tokens = []
            try: oi = self.notebook.get_nth_page(n).buffer.get_text(self.notebook.get_nth_page(n).buffer.get_start_iter(),
                                                               self.notebook.get_nth_page(n).buffer.get_end_iter(),True).split()
            except: return
            if self.inc_is_fuzzy.get_active() == False:
                self.notebook.get_nth_page(n).search_tokens.append(rr)
            else:
                for er in range(len(oi)):
                    for et in range(kk): 
                        if yy[et] in fuzz(fuzzy.normalize(oi[er])) or yy[et] in oi[er]:
                            self.notebook.get_nth_page(n).search_tokens.append(oi[er])
        else: self.notebook.get_nth_page(n).search_tokens = []
        self.page_highlight()
                
# a نتائج البحث في الكتاب الحالي----------------------------------------------------------------
    
    def inc_search_cb(self,text):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        if len(text) > 0:
            text = ' '.join(text.split())
            if self.inc_is_fuzzy.get_active() == True:
                text = u''+text
            else :
                text = '"'+text+'"'
            if self.inc_is_quran.get_active() == True:
                ey = ui.sdb.get_text_body(ui.book_p,ui.current_id)
                qe = ((ey[5]-1)*512)+ey[6]+ey[7]-1
                l = self.search(text,True,True, qe, 1, 1)
                i = l
            else:
                l = self.search(text,False,True, ui.current_id, 1, 1)
                i = l[0][0]
            if not l: return
            r = ui.sdb.get_text_body(ui.book_p,i)
            self.display_text(r,i)
            self.highlight_headers(r[0])
            ui.n_pg(r)
            self.page_highlight()
        else :
            pass
      
    def search(self,text, in_quran, is_fuzzy, pos = -1, direction = 1 ,limit = 10000):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        if in_quran == False: return ui.sdb.search(text, is_fuzzy, pos, direction ,limit)
        else:
            l = ui.othman.search(text, 1,pos, direction,limit)
            ui.sdb.search_tokens.append(fuzzy.normalize(text))
            isr = (l/512)+1
            iya = l-((isr-1)*512)+1
            z = ui.sdb.page_quran(isr , iya)
            return z
      
    def ss_search_cb(self,text,ss_store,quran):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        if len(text) > 0 :
            text = ' '.join(text.split())
            if th.inc_is_fuzzy.get_active() == True:
                text = u''+text
            else :
                text = '"'+text+'"'
            if quran == True:    
                    j = 0 
                    __cn = sqlite3.connect('data/quran.db', isolation_level = None)
                    c = sqlite3.connect('data/koran',isolation_level = None)
                    __c = __cn.cursor()
                    _c = __cn.cursor()
                    sdb = AsmaaBook('data/koran',-1)
                    __cn.create_function('fuzzy_normalize',1,fuzzy.normalize)
                    s = '''fuzzy_normalize(imlai) LIKE ? ESCAPE "|"'''
                    text = fuzzy.normalize(text)
                    ui.sdb.search_tokens = fuzzy.tokenize_search(text)
                    l = map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',ui.sdb.search_tokens)
                    if len(l) < 1: return []
                    self.condition = ' AND '.join([s]*len(l))  
                    __c.execute("""SELECT id FROM Quran WHERE %s""" % (self.condition), l)
                    a = __c.fetchall()
                    for s in range(len(a)):
                        gt = a[s][0]
                        isr = (gt/512)+1
                        iya = gt-((isr-1)*512)
                        g1 = sdb.page_quran(isr , iya+1)
                        j = j+1
                        _c.execute("""SELECT sura_name FROM suranames""")
                        b = _c.fetchall()
                        g2 = str(b[isr-1][0])
                        if len(ss_store) > 0:
                            if g1 != ss_store[-1][1]:
                                ss_store.append([j,g1,g2,"Tip",50.0])
                        else: ss_store.append([j,g1,g2,"Tip",50.0])
            else:
                l = self.search(text,False,True, -1, 1, 10000)
                n = 0
                while n in range(len(l)):
                    ss_store.append([n+1,l[n][0],l[n][1],"Tip",50.0])
                    n += 1
        else :
            pass
                
    def srh_bk(self,quran):
        if self.ent_find.get_text() == "": return
        try: self.wsb.destroy()
        except: pass
        self.wsb = gtk.Window()
        self.wsb.set_keep_above(True)
        self.wsb.set_icon_from_file("icons/Search-Book-24.png")
        self.wsb.set_title('نتائج البحث')
        self.wsb.set_position(gtk.WIN_POS_CENTER)
        self.wsb.resize(350,500)
        self.wsb.set_border_width(10)
        scos1 = gtk.ScrolledWindow()
        scos1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scos1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.ss_store = gtk.ListStore(int,int,str,str,float) # num,id,title,segment,rank
        n = self.notebook.get_current_page()
        text = u""+self.ent_find.get_text()
        try: ww = self.notebook.get_nth_page(n).inc_is_quran.get_active()
        except: return
        if ww == True:
            quran = True
        else:
            quran = self.inc_is_quran.get_active()
        self.ss_search_cb(text,self.ss_store,quran)
        self.ss_list = gtk.TreeView(self.ss_store)
        self.ss_list.modify_font(pango.FontDescription("KacstOne 13"))
        self.ss_list.modify_text(gtk.STATE_NORMAL,color=gtk.gdk.Color('#FFFF80'))
        self.ss_list.modify_base(gtk.STATE_NORMAL,color=gtk.gdk.Color("#204000"))
        cells0 = []; cols0 = []
        cells0.append(gtk.CellRendererText())
        cols0.append(gtk.TreeViewColumn('الرقم', cells0[-1], text = 0))
        cols0[-1].set_expand(False)
        cells0.append(gtk.CellRendererText())
        cols0.append(gtk.TreeViewColumn('العنوان', cells0[-1], text = 2))
        cols0[-1].set_expand(True)
        for i in cols0: self.ss_list.insert_column(i, -1)
        self.ss_list.set_enable_search(True)
        self.ss_list.set_search_column (2)
        self.sw2 = gtk.ScrolledWindow(None,None)
        self.sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw2.add(self.ss_list)
        def ss_cb(widget,*args):
            (model, i) = self.ss_list.get_selection().get_selected()
            if not i:
                (p,c) = self.ss_list.get_cursor()
                i = self.ss_store.get_iter(p)
                if not i: return
            i = model.get(i,1)[0]
            r = self.notebook.get_nth_page(n).sdb.get_text_body(self.notebook.get_nth_page(n).book_p,i)
            self.display_text(r,i)
            self.highlight_headers(r[0])
            self.notebook.get_nth_page(n).search_tokens = self.notebook.get_nth_page(n).sdb.search_tokens
            self.notebook.get_nth_page(n).n_pg(r)
            self.page_highlight()
        self.ss_list.connect("cursor-changed", ss_cb)
        self.wsb.add(self.sw2)
        self.wsb.show_all() 
        
# a نتائج البحث---------------------------------------------------------------- 
  
    def ok_ntaij(self,qa):
        tt = self.notebook.get_n_pages()
        self.hr = 'نتائج : '+qa
        asv = Asmasearch(self)
        self.notebook.append_page(asv, TabLabel(asv,self.hr))
        self.notebook.set_tab_reorderable(asv,True)
        self.notebook.set_current_page(-1)
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        ui.cnm.set_text(self.hr)
        if tt == 0:
            self.event_box1.hide_all()
            self.notebook.show_all()
        self.do_win()
        self.font()
        if qa == "آخر بحث": store = cPickle.load(file(self.pathasmaa+"data/last-search.pkl"))
        else: store = cPickle.load(file(self.pathasmaa+"data/records/"+qa))
        self.notebook.get_nth_page(n).search_tokens = store[-3]
        self.notebook.get_nth_page(n).progress1.hide()
        self.notebook.get_nth_page(n).stp.hide()
        self.metassila = gtk.CheckButton()
        if store[-1] == 0: self.notebook.get_nth_page(n).inc_is_quran.set_active(False)
        elif store[-1] == 1: self.notebook.get_nth_page(n).inc_is_quran.set_active(True)
        self.notebook.get_nth_page(n).l_search.set_text(" عدد النتائج "+str(len(store)-3)) 
        self.notebook.get_nth_page(n).sh_store = store
        for a in range(len(store)-3):
            self.notebook.get_nth_page(n).search_store.append(store[a])
        try:
            i1 = self.notebook.get_nth_page(n).search_store.get_iter(0,)
            self.notebook.get_nth_page(n).toc_selection1.select_iter(i1)
            self.notebook.get_nth_page(n).ss_cb1()
        except: return
            
    def srv( self,*args):
        if not os.path.exists(self.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
        self.wv = gtk.Window()
        self.wv.set_icon_from_file("icons/Saved-Result-24.png")
        self.wv.set_modal(True)
        self.wv.set_keep_above(True)
        self.wv.set_title('نتائج البحث المحفوظة')
        self.wv.set_position(gtk.WIN_POS_CENTER)
        self.wv.resize(350,400)
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,10)
        vb.set_border_width(10)
        scos1 = gtk.ScrolledWindow()
        scos1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scos1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        kh1 = gtk.TreeView()
        kh1.set_headers_visible(False)
        sah1 = gtk.TreeViewColumn('البحوث',gtk.CellRendererText(),text = 0)
        kh1.append_column(sah1)
        kh1.set_model(self.store_sah1)
        kh1.modify_font(pango.FontDescription(self.fontc))
        kh1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcf))
        kh1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(self.colorcb))
        scos1.add(kh1)
        list_n = os.listdir(self.pathasmaa+'data/records/')
        self.store_sah1.clear()
        self.store_sah1.append(["آخر بحث"])
        for v in range(len(list_n)):
            self.store_sah1.append([list_n[v]])
        br = gtk.Button("حذف")
        def ok_k(widget,*args):
            t_selection = kh1.get_selection()
            (model, i) = t_selection.get_selected()
            if not i:
                (p,c) = kh1.get_cursor()
                i = self.store_sav.get_iter(p)
                if not i: return
            qa = model.get(i,0)[0]
            self.wv.destroy()
            self.ok_ntaij(qa)
        kh1.connect("row-activated", ok_k)
        def rm(widget, *args):
            global res_dlg
            (model1, i1) = kh1.get_selection().get_selected()
            if i1 :
                dlg_res(" هل ترغب في حذف النتيجة المحددة ؟")
                if res_dlg == False: return
                else:
                    res_dlg = False
                    r1 = model1.get_value(i1,0)
                    os.remove(self.pathasmaa+'data/records/'+r1)
                    self.store_sah1.remove(i1)
        br.connect('clicked',rm)
        hb.pack_start(br,0,0)
        bc = gtk.Button("مسح")
        def cl(widget, *args):
            global res_dlg
            list_n = os.listdir(self.pathasmaa+'data/records/')
            dlg_res(" هل ترغب في حذف جميع النتائج ؟")
            if res_dlg == False: return
            else:
                res_dlg = False
                for v in range(len(list_n)):
                    r1 = list_n[v]
                    os.remove(self.pathasmaa+'data/records/'+r1)
                self.store_sah1.clear()
                self.store_sah1.append(["آخر بحث"])
        bc.connect('clicked',cl)
        vb.pack_start(scos1,1,1)
        hb.pack_start(bc,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.wv.destroy())
        hb.pack_end(clo,0,0)
        vb.pack_start(hb,0,0)
        self.wv.add(vb)
        self.wv.show_all()
        
    def search_search(self,*args):
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        nm = ui.inc_search1.get_text()
        if nm == "":
            dlg("أدخل نصا للبحث عنه.")
        else:
            self.hr = 'بحث عن : '+nm
            asv = Asmasearch()
            self.notebook.append_page(asv, TabLabel(asv,self.hr))
            self.notebook.set_tab_reorderable(asv,True)
            self.notebook.set_current_page(-1)
            n = self.notebook.get_current_page()
            ui1 = self.notebook.get_nth_page(n)
            self.sh_store = []
            self.notebook.show_all()
            self.event_box1.hide_all()
            ui1.cnm.set_text(self.hr)
            self.metassila = gtk.CheckButton()
            self.metassila.set_active(True)
            self.do_win()
            j = 0
            e = 0
            while e in range(len(ui.search_store)):
                t_id = ui.search_store[e][1]
                t_bok = ui.search_store[e][2]
                s = '''fuzzy_normalize(nass) LIKE ? ESCAPE "|"'''
                text = fuzzy.normalize(nm)
                ui1.search_tokens = fuzzy.tokenize_search(text)
                l = map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',ui1.search_tokens)
                if len(l) < 1: return []
                self.condition = ' AND '.join([s]*len(l))
                fnm = u''+th.pathasmaa+'books/'+t_bok+'.asm'
                __cn = sqlite3.connect(fnm, isolation_level = None)
                c = sqlite3.connect(fnm,isolation_level = None)
                __c = __cn.cursor()
                c1 = c.cursor()
                c1.execute('SELECT bkid FROM main')
                fe1 = c1.fetchall()
                bkid = fe1[0][0]
                __book_id = bkid
                __cn.create_function('fuzzy_normalize',1,fuzzy.normalize)
                self.cond = 'id = %d' % (t_id)
                __c.execute("""SELECT id,part,page FROM pages WHERE %s and %s """ % (self.cond, self.condition), l)
                a = __c.fetchall()
                ui1.l_search.set_text('   عدد النتائج   '+str(j)+'    ')
                ui1.progress1.set_text(t_bok)
                ui1.progress1.set_fraction(float(e+1)/float(len(ui.search_store)))
                if len(a) == 1:
                    g1 = int(a[0][0])
                    try: g2 = int(a[0][1])
                    except: g2 = 1
                    try: g3 = int(a[0][2])
                    except: g3 = 0
                    h = ui.search_store[e][3]
                    j += 1
                    ui1.search_store.append([j,g1,t_bok,h,g2,g3,"Tip",50.0])
                    ui1.sh_store.append([j,g1,t_bok,h,g2,g3,"Tip",50.0])
                    if len(ui1.search_store) == 1:
                        i1 = ui1.search_store.get_iter(0,)
                        ui1.toc_selection1.select_iter(i1)
                        ui1.ss_cb1()
                e += 1
            ui1.l_search.set_text("عدد النتائج "+str(j))   
            ui1.progress1.set_text('انتهى البحث')
            ui1.progress1.set_fraction(1.0)
            ui1.stp.set_sensitive(False)
      
# a اسهم التصفح---------------------------------------------------------------------     

    def s_pg11(self,*args):
        n = self.notebook.get_current_page()
        try: self.notebook.get_nth_page(n).first_page()
        except: pass
    
    def s_pg2(self,*args):
        n = self.notebook.get_current_page()
        try: self.notebook.get_nth_page(n).next_page()
        except: pass
    
    def s_pg1(self,*args):
        n = self.notebook.get_current_page()
        try: self.notebook.get_nth_page(n).previous_page()
        except: pass
    
    def s_pg22(self,*args):
        n = self.notebook.get_current_page()
        try: self.notebook.get_nth_page(n).last_page()
        except: pass

# b تعليق-----------------------------------------------------------------------

    def tooltip_toc(self, widget, x, y, keyboard_tip, tooltip,h):
        if not widget.get_tooltip_context(x, y, keyboard_tip):
            return False
        else:
            model, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)

            value = model.get(iter, h)
            tooltip.set_markup(" %s" %value[0])
            widget.set_tooltip_row(tooltip, path)
            return True

# a تفضيلات------------------------------------------------------------

    def tahakem( self,*args):
        tt = self.notebook.get_n_pages()
        self.hr = "مركز التحكم"
        for s in range(tt):
            ui = self.notebook.get_nth_page(s)
            if ui.cnm.get_text() == "مركز التحكم":
                self.notebook.set_current_page(s)
                return
        dv = Modification(self.hr)
        self.notebook.append_page(dv, TabLabel(dv,self.hr))
        self.notebook.set_tab_reorderable(dv,True)
        self.notebook.set_current_page(-1)
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        ui.cnm.set_text("مركز التحكم")
        if tt == 0:
            self.event_box1.hide_all()
            self.notebook.show_all()
        self.do_win()
        
    def tandim( self,*args):
        if not os.path.exists(self.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
        else:
            if len(self.store_kaima1) == 0: self.tree0()
        self.hr = "تنظيم المكتبة"
        tt = self.notebook.get_n_pages()
        for s in range(tt):
            ui = self.notebook.get_nth_page(s)
            if ui.cnm.get_text() == "تنظيم المكتبة":
                self.notebook.set_current_page(s)
                return
        dv = Organizing(self.hr)
        self.notebook.append_page(dv, TabLabel(dv,self.hr))
        self.notebook.set_tab_reorderable(dv,True)
        self.notebook.set_current_page(-1)
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        ui.cnm.set_text("تنظيم المكتبة")
        if tt == 0:
            self.event_box1.hide_all()
            self.notebook.show_all()
        self.do_win()
        
    def kaima(self,*args):
        if not os.path.exists(self.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
        else:
            if len(self.store_kaima1) == 0: self.tree0()
        if self.conf["ka"] == "1":
            self.hr = "قائمة الكتب"
            tt = self.notebook.get_n_pages()
            for s in range(tt):
                ui = self.notebook.get_nth_page(s)
                if ui.cnm.get_text() == "قائمة الكتب":
                    self.notebook.set_current_page(s)
                    return
            dv = WinBooks(self.hr)
            self.notebook.append_page(dv, TabLabel(dv,self.hr))
            self.notebook.set_tab_reorderable(dv,True)
            self.notebook.set_current_page(-1)
            n = self.notebook.get_current_page()
            ui = self.notebook.get_nth_page(n)
            ui.cnm.set_text("قائمة الكتب")
            if tt == 0:
                self.event_box1.hide_all()
                self.notebook.show()
            self.do_win()
        else:
            WinBooks("قائمة الكتب").wink()
            
    def win_search(self,nass):
        if not os.path.exists(self.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
        else:
            if len(self.store_s) == 0: self.tree0()
        try: self.list_terms = cPickle.load(file(self.pathasmaa+'data/last-terms.pkl'))
        except: self.list_terms = []
        completion03 = gtk.EntryCompletion()
        list_ts = gtk.ListStore(str)
        for a in self.list_terms:
            list_ts.append([a])
        completion03.set_model(list_ts)
        completion03.set_text_column(0)
        self.ent_sh.set_completion(completion03)
        if self.conf['fi'] == '1':
            self.winsearch.connect('delete-event', lambda w,*a: w.hide() or True)
            if self.n_s == 1 :
                self.winsearch.show_all()
                if nass != '':
                    self.ent_sh.set_text(nass)
                return
            else: pass
        self.winsearch.set_icon_from_file("icons/Search-Books-24.png")
        self.winsearch.set_title("بحث")
        self.winsearch.set_modal(True)
        self.winsearch.set_keep_above(True)
        self.winsearch.set_position(gtk.WIN_POS_CENTER)
        self.winsearch.set_border_width(10)
        self.winsearch.resize(700,450)
        self.winsearch.add(SearchView(nass))
        if self.conf['fi'] == '0':
            SearchView('').tas0() 
        self.winsearch.show_all()
           
    def hala(self,*args):
        Siana() 
        
        
    def full0(self, *args):
        if self.ghj == 1:
            self.win.unfullscreen()
            self.fall.set_label('إملإ الشاشة')
            self.ghj = 0
        else:
            self.win.fullscreen()
            self.fall.set_label('غادر ملء الشاشة')
            self.ghj = 1
    
    def toolb0(self, *args):
        if self.stat.get_active() == True:
            self.toolbar.show()
            self.conf['tb'] = '0'
            self.conf.save()
        else:
            self.toolbar.hide()
            self.conf['tb'] = '1'
            self.conf.save()

    def apply_font(self, *args):
        if self.conf['tr'] == '1':
            self.fontq = self.conf['fontq']
            self.fontn = self.conf['fontn']
            self.fonta = self.conf['fonta']
            self.fontc = self.conf['fontc']
            self.colorqf = self.conf['colorqf']
            self.coloraf = self.conf['coloraf']
            self.colornf = self.conf['colornf']
            self.colorcf = self.conf['colorcf']
            self.colormf = self.conf['colormf']
            self.colorqb = self.conf['colorqb']
            self.colornb = self.conf['colornb']
            self.colorcb = self.conf['colorcb']
            self.colorsb = self.conf['colorsb']
        else:
            self.fontq = "28"
            self.fontn = "Simplified Naskh 24"
            self.fonta = "Simplified Naskh Bold 32"
            self.fontc = "KacstOne 15"
            self.colorqf = "#204000"
            self.coloraf = "#860915"
            self.colornf = '#0B0C8D'
            self.colorcf = '#162116'
            self.colormf = "#EC430A"
            self.colorqb = "#FDFDD7"
            self.colornb = "#FDFDD7"
            self.colorcb = "#F9F0CF"
            self.colorsb = '#FFFF80'
            
    def populate_popup(self, view, menu):
        menu.hide_all()
        n = self.notebook.get_current_page()
        ui = self.notebook.get_nth_page(n)
        buff = view.get_buffer()
        if buff.get_has_selection():
            ddd = buff.get_selection_bounds()
            ddj = buff.get_text(ddd[0],ddd[1],True)
        def ok_k(widget,*args):
            qa = menu.get_active()
            qa = qa.get_label()
            qa = qa[16:]
            ddt = ui.fnm
            dds = ddt+u' ('+ui.ent_page.get_text()+'\\'+ui.ent_part.get_text()+u")"
            f = open(self.conf.p+'/memoir/'+qa , 'r')
            sa = f.readlines()
            for q in range(len(sa)):
                if u'ــــــــــــــــــــــــــــــــــــــــــــــــ' in sa[q]:
                    ind = q
            qs = len(sa)-ind
            ta3 = "("+str(qs)+")"+"   "+dds+'\n'
            sa.insert(ind,ddj+"("+str(qs)+")\n")
            sa.append(ta3)
            y = open(self.conf.p+'/memoir/'+qa , 'w')
            y.writelines(sa)
            y.close()
        f5 = gtk.MenuItem('فتح في لسان جديد')
        def op_k(widget,*args):
            hr = ui.fnm
            if hr == "القرآن الكريم": fd = 'data/koran'
            elif hr == "دليل المستخدم": return
            elif hr == "waraka": return
            else: fd = self.pathasmaa+'books/'+hr+'.asm'
            nbk = fd
            idbk = ui.current_id
            th.open_bk(nbk, idbk,hr)
        f5.connect('activate',op_k)
        menu.prepend(f5)
        c2 = gtk.SeparatorMenuItem()
        menu.prepend(c2)
        f0 = gtk.MenuItem(" أنشئ ورقة بحث")
        f0.connect('activate',th.insh)
        menu.prepend(f0)
        c3 = gtk.SeparatorMenuItem()
        menu.prepend(c3)
        list_n = os.listdir(th.conf.p+'/memoir/')
        for v in range(len(list_n)):
            f6 = gtk.MenuItem('نسخ إلى : '+list_n[v])
            f6.connect('activate',ok_k)
            menu.prepend(f6)
            f6.show()
            if buff.get_has_selection():
                f6.set_sensitive(True)
            else: f6.set_sensitive(False)
        f7 = gtk.MenuItem('نسخ')
        def ok_cp(widget,*a):
            self.clipboard.set_text(ddj)
        f7.connect('activate',ok_cp)
        menu.prepend(f7)
        f7.set_sensitive(False)
        c4 = gtk.SeparatorMenuItem()
        menu.prepend(c4)
        f1 = gtk.MenuItem("تفسير آية")
        f1.set_sensitive(False)
        menu.prepend(f1)
        f2 = gtk.MenuItem("شرح مفردة")
        menu.prepend(f2)
        f2.set_sensitive(False)
        f3 = gtk.MenuItem("ترجمة راوٍ")
        menu.prepend(f3)
        f3.set_sensitive(False)
        c5 = gtk.SeparatorMenuItem()
        menu.prepend(c5)
        f4 = gtk.MenuItem("فتح في نافذة البحث")
        f4.set_sensitive(False)
        menu.prepend(f4)
        if buff.get_has_selection():
            f1.set_sensitive(True)
            f2.set_sensitive(True)
            f3.set_sensitive(True)
            f4.set_sensitive(True)
            f7.set_sensitive(True)
        f1.connect("activate",lambda *a: self.tawdih(ddj,u"تفسير آية"))
        f2.connect("activate",lambda *a: self.tawdih(ddj,u"شرح مفردة"))
        f3.connect("activate",lambda *a: self.tawdih(ddj,u"ترجمة راوٍ"))
        f4.connect("activate",lambda *a: self.win_search(ddj))
        menu.connect('move_scroll',ok_k)
        f1.show()
        f2.show()
        f3.show()
        f4.show()
        f5.show()
        f0.show()
        f7.show()
        c2.show()
        c3.show()
        c4.show()
        c5.show()
        if view.get_editable() == True:
            menu.show_all()
            f5.hide()
        
    def toolb1(self, *args):
        if self.conf['tb'] == '0':
            self.toolbar.show()
            self.stat.set_active(True)
        elif self.conf['tb'] == '1':
            self.toolbar.hide()
            self.stat.set_active(False)

    def chgsiz(self, *a):
        ty = self.win.get_size()
        self.conf['sv'] = str(ty[1])
        self.conf['sh'] = str(ty[0])  
        self.conf.save()
        
    def eventbox(self,*a):
        if self.conf['ev'] == "0":
            self.kaima()
        elif self.conf["ev"] == "1":
            SearchView("")
        else: pass
        
    def close0(self,*a):
        tt = self.notebook.get_n_pages()
        s = 0
        while s in range(tt):
            ui = self.notebook.get_nth_page(0)
            ii = self.notebook.get_tab_label(ui)
            ii.close_tab()
            s += 1
        
    def others(self,*a):
        try: os.makedirs(self.pathasmaa+'data/records', 0777)
        except: pass
        try: os.makedirs(self.pathasmaa+'data/favorite', 0777)
        except: pass
        try: os.makedirs(self.pathasmaa+'data/lists', 0777)
        except: pass
        
        self.winsearch = gtk.Window()
        self.ghj = 0
        self.n_s = 0
        self.sto_s = []
        self.list_p = []
        self.lab_ch = gtk.Label()
        self.list_book = []
        self.list_terms = []
        self.store_fav = gtk.ListStore(str)
        self.store_sav = gtk.ListStore(str,str,int)
        self.store_sah = gtk.ListStore(str)
        self.store_sah1 = gtk.ListStore(str)
        self.store_kaima1 = gtk.ListStore(str)
        self.store_s = gtk.TreeStore( gobject.TYPE_STRING,gobject.TYPE_BOOLEAN )
        self.store_k = gtk.TreeStore(str) 
        self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
        self.ent_sh = gtk.Entry()
        
      
    def build_gui(self):
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title('مكتبة أسماء')
        self.win.set_icon_name("asmaa")
        self.win.connect("destroy", self.do_close)
        vv1 = int(self.conf['sv']) 
        hh1 = int(self.conf['sh'])  
        self.win.resize(hh1, vv1)
        self.win.connect('size-request',self.chgsiz)
# a القائمة----------------------------------------------------------
        self.agr = gtk.AccelGroup()
        self.win.add_accel_group(self.agr)
        self.mb = gtk.MenuBar()
        self.filemenu1 = gtk.Menu()
        self.filemenu11 = gtk.Menu()
        self.filemenu5 = gtk.Menu()
        self.filemenu2 = gtk.Menu()
        self.filemenu3 = gtk.Menu()
        self.filemenu4 = gtk.Menu()
        self.filemenu6 = gtk.Menu()
        self.fil = gtk.MenuItem("ملف")
        self.fil.set_submenu(self.filemenu1)
        self.qr1 = gtk.MenuItem("القرآن الكريم")
        self.qr1.connect('activate',self.otm)
        self.book1 = gtk.MenuItem("قائمة الكتب")
        self.book1.connect('activate',self.kaima)
        keyk, modk = gtk.accelerator_parse("F12")
        self.book1.add_accelerator('activate', self.agr, keyk, modk, gtk.ACCEL_VISIBLE)
        self.mfd1 = gtk.MenuItem("الكتب المفضلة")
        self.mfd1.connect('activate',self.fav11)
        self.alama = gtk.MenuItem("المواضع المحفوظة")
        self.alama.connect('activate',self.sav11)
        self.wrk = gtk.MenuItem("أوراق البحث")
        self.wrk.connect('activate',self.awrak_sh)
        self.sas = gtk.MenuItem("نتائج البحث")
        self.sas.connect('activate',self.srv)
        self.T_book1 = gtk.MenuItem("بطاقة عن الكتاب")
        self.T_book1.connect('activate',self.card)
        self.close = gtk.MenuItem("إغلاق كل الألسنة")
        self.close.connect('activate',self.close0)
        self.exit = gtk.MenuItem("خروج")
        self.exit.connect('activate',self.do_close)
        self.sep1 = gtk.SeparatorMenuItem()
        self.sep3 = gtk.SeparatorMenuItem()
        self.filemenu1.append(self.qr1)
        self.filemenu1.append(self.book1)
        self.filemenu1.append(self.mfd1)
        self.filemenu1.append(self.alama)
        self.filemenu1.append(self.wrk)
        self.filemenu1.append(self.sas)
        self.filemenu1.append(self.T_book1)
        self.filemenu1.append(self.sep3)
        self.filemenu1.append(self.close)
        self.filemenu1.append(self.exit)
        self.adds = gtk.MenuItem("تحرير")
        self.adds.set_submenu(self.filemenu11)
        self.crt_m = gtk.MenuItem("إنشاء مكتبة مفرغة")
        self.imp_m = gtk.MenuItem("استيراد كتب")
        self.imp_m.connect('activate',AddBooks)
        self.reg = gtk.MenuItem("إعداد المظهر")
        self.reg.connect('activate',Perference)
        self.ctah = gtk.MenuItem("تنظيم المكتبة")
        self.ctah.connect('activate',self.tandim)
        self.tahakm = gtk.MenuItem("مركز التحكم")
        self.tahakm.connect('activate',self.tahakem)
        self.adf = gtk.MenuItem("إضافة إلى المفضلة")
        self.adf.connect('activate',self.adfav)
        self.adw = gtk.MenuItem("إضافة ورقة بحث")
        self.adw.connect('activate',self.insh)
        self.filemenu11.append(self.adf)
        self.filemenu11.append(self.adw)
        self.chg = gtk.MenuItem("تعيين مسار الكتب")
        self.chg.connect('activate',self.ch_ph)
        self.crt_m.connect('activate',self.new_lib)
        self.filemenu11.append(self.chg)
        self.filemenu11.append(self.crt_m)
        self.filemenu11.append(self.imp_m)
        self.filemenu11.append(self.sep1)
        self.filemenu11.append(self.reg)
        self.filemenu11.append(self.ctah)
        self.filemenu11.append(self.tahakm)
        self.shw = gtk.MenuItem("عرض")
        self.shw.set_submenu(self.filemenu5)
        self.p11 = gtk.MenuItem('الصفحة الأولى')
        self.p11.connect('activate',self.s_pg11)
        key11, mod11 = gtk.accelerator_parse("Home")
        self.p11.add_accelerator('activate', self.agr, key11, mod11, gtk.ACCEL_VISIBLE)
        self.p1 = gtk.MenuItem('الصفحة السابقة')
        self.p1.connect('activate',self.s_pg1)
        key1, mod1 = gtk.accelerator_parse("Page_Up")
        self.p1.add_accelerator('activate', self.agr, key1, mod1, gtk.ACCEL_VISIBLE)
        self.p2 = gtk.MenuItem('الصفحة التالية')
        self.p2.connect('activate',self.s_pg2)
        key2, mod2 = gtk.accelerator_parse("Page_Down")
        self.p2.add_accelerator('activate', self.agr, key2, mod2, gtk.ACCEL_VISIBLE)
        self.p22 = gtk.MenuItem('الصفحة الأخيرة')
        self.p22.connect('activate',self.s_pg22)
        key22, mod22 = gtk.accelerator_parse("End")
        self.p22.add_accelerator('activate', self.agr, key22, mod22, gtk.ACCEL_VISIBLE)
        self.sep = gtk.SeparatorMenuItem() 
        self.fall = gtk.MenuItem('املإ الشاشة')
        self.fall.connect('activate',self.full0)
        keyf, modf = gtk.accelerator_parse("F11")
        self.fall.add_accelerator('activate', self.agr, keyf, modf, gtk.ACCEL_VISIBLE)
        self.sep11 = gtk.SeparatorMenuItem() 
        self.cpho = gtk.MenuItem("تغيير الخلفية")
        self.stat = gtk.CheckMenuItem("شريط الأدوات")
        self.stat.set_active(True)
        self.stat.connect("activate", self.toolb0)
        self.cpho.connect("activate", self.ch_pho)
        self.filemenu5.append(self.p11)
        self.filemenu5.append(self.p1)
        self.filemenu5.append(self.p2)
        self.filemenu5.append(self.p22)
        self.filemenu5.append(self.sep11)
        self.filemenu5.append(self.fall)
        self.filemenu5.append(self.sep)
        self.filemenu5.append(self.cpho)
        self.filemenu5.append(self.stat)
        self.services = gtk.MenuItem("أدوات")
        self.services.set_submenu(self.filemenu3)
        self.hala1 = gtk.MenuItem("فحص البيانات")
        self.hala1.connect('activate',self.hala)
        self.filemenu3.append(self.hala1)
        sep = gtk.SeparatorMenuItem()
        self.find = gtk.MenuItem("البحث")
        self.find_sp = gtk.MenuItem("بحث خاص")
        self.find_sp.connect('activate',self.search_special)
        keys, mods = gtk.accelerator_parse("F3")
        self.find_sp.add_accelerator('activate', self.agr, keys, mods, gtk.ACCEL_VISIBLE)
        self.find_ls = gtk.MenuItem("نتائج آخر بحث")
        self.find_ls.connect('activate',lambda *a: self.ok_ntaij('آخر بحث'))
        self.find.connect('activate',lambda *a: self.win_search(""))
        keys, mods = gtk.accelerator_parse("F2")
        self.find.add_accelerator('activate', self.agr, keys, mods, gtk.ACCEL_VISIBLE)
        self.filemenu3.append(sep)
        self.filemenu3.append(self.find)
        self.filemenu3.append(self.find_sp)
        self.filemenu3.append(self.find_ls)
        self.Help = gtk.MenuItem("مساعدة")
        self.Help.set_submenu(self.filemenu4)
        self.mehtawa = gtk.MenuItem('دليل المستخدم')
        self.new_re = gtk.MenuItem('جديد الإصدار')
        self.about = gtk.MenuItem('لمحة')
        keym, modm = gtk.accelerator_parse("F1")
        self.mehtawa.add_accelerator('activate', self.agr, keym, modm, gtk.ACCEL_VISIBLE)
        self.new_re.connect('activate',self.djadid)
        self.about.connect('activate',show_about1)
        self.mehtawa.connect('activate',self.dalil11)
        self.filemenu4.append(self.mehtawa)
        self.filemenu4.append(self.new_re)
        self.filemenu4.append(self.about)
        self.mb.append(self.fil)
        self.mb.append(self.adds)
        self.mb.append(self.shw)
        self.mb.append(self.services)
        self.mb.append(self.Help)
        self.apply_font()
# a شريط الأدوات----------------------------------------------------------
        self.tab_deros = gtk.Table(84,16,True)
        self.back = gtk.ToolButton(gtk.STOCK_QUIT)
        self.pg = gtk.HBox(False,0)
        self.vb10 = gtk.VBox(False,0)
        self.vb11 = gtk.VBox(False,0)
        self.pgp = gtk.HBox(False,0)
        ig1 = gtk.Image()
        ig1.set_from_file('icons/Previous-24.png')
        ig11 = gtk.Image()
        ig11.set_from_file('icons/First-24.png')
        ig2 = gtk.Image()
        ig2.set_from_file('icons/Next-24.png')
        ig22 = gtk.Image()
        ig22.set_from_file('icons/Last-24.png')
        self.tb1 = gtk.Table(1,5,True)
        im20 = gtk.Image()
        im20.set_from_file('icons/Prefers-24.png')
        im13 = gtk.Image()
        im13.set_from_file('icons/Bitaka-24.png')
        im1 = gtk.Image()
        im1.set_from_file('icons/Books-24.png') 
        im26 = gtk.Image()
        im26.set_from_file('icons/Search-Books-24.png')
        im17 = gtk.Image()
        im17.set_from_file('icons/Search-Book-24.png')
        self.ent_find = gtk.Entry()
        im12 = gtk.Image()
        im12.set_from_file('icons/Books-Saved-24.png')
        im3 = gtk.Image()
        im3.set_from_file('icons/Chamila-24.png')
        im4 = gtk.Image()
        im4.set_from_file('icons/Configs-24.png')
        im14 = gtk.Image()
        im14.set_from_file('icons/Fav-Books-24.png')
        im6 = gtk.Image()
        im6.set_from_file('icons/Quran-24.png')
        im10 = gtk.Image()
        im10.set_from_file('icons/Papers-24.png')
        im11 = gtk.Image()
        im11.set_from_file('icons/Saved-Result-24.png')
        im104 = gtk.Image()
        im104.set_from_file('icons/About-24.png')
        im105 = gtk.Image()
        im105.set_from_file('icons/Help-24.png')
        im205 = gtk.Image()
        im205.set_from_file('icons/center-24.png')
        im304 = gtk.Image()
        im304.set_from_file('icons/exit-24.png')
        self.toolbar = gtk.Toolbar()
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.othm = self.toolbar.insert_item(None,"القرآن العظيم","Private",im6,self.otm,None,0)
        self.alketeb = self.toolbar.insert_item(None,"قائمة الكتب","Private",im1,self.kaima,None,1)
        self.toolbar.insert_space(2)
        self.fav_b = self.toolbar.insert_item(None,"الكتب المفضلة","Private",im14,self.fav11,None,3)
        self.alama = self.toolbar.insert_item(None,"المواضع المحفوظة","Private",im12,self.sav11,None,4)
        self.wrk = self.toolbar.insert_item(None,"أوراق البحث","Private",im10,self.awrak_sh,None,5)
        self.ntj = self.toolbar.insert_item(None,"النتائج المحفوظة","Private",im11,self.srv,None,6)
        self.toolbar.insert_space(7)
        self.pg11 = self.toolbar.insert_item(None,"الصفحة الأولى","Private",ig11,self.s_pg11,None,8)
        self.pg1 = self.toolbar.insert_item(None,"الصفحة السابقة","Private",ig1,self.s_pg1,None,9)
        self.pg2 = self.toolbar.insert_item(None,"الصفحة التالية","Private",ig2,self.s_pg2,None,10)
        self.pg22 = self.toolbar.insert_item(None,"الصفحة الأخيرة","Private",ig22,self.s_pg22,None,11)
        self.toolbar.insert_space(12)
        self.find = self.toolbar.insert_item(None,"البحث في المكتبة","Private",im26,lambda *a: self.win_search(""),None,13)
        self.toolbar.insert_space(14)
        self.findb = self.toolbar.insert_item(None,"البحث في الكتاب الحالي","Private",im17,lambda *a: self.srh_bk(False),None,15)
        self.toolbar.insert_widget(self.ent_find,"أدخل النص المراد البحث عنه\nبحث تفاعلي في الصفحة الحالية\nبحث تسلسلي بالنقر على مفتاح الدخول", "Private",16)
        def sear_ok(widget,*a):
            self.inc_search_cb(self.ent_find.get_text())
        self.ent_find.connect("activate", sear_ok) 
        self.ent_find.connect("key-release-event", self.srh_pg) 
        self.inc_is_fuzzy = gtk.CheckButton()
        self.inc_is_fuzzy.connect("toggled",self.srh_pg)
        self.toolbar.insert_widget(self.inc_is_fuzzy, "بحث ضبابي\nعلّم إذا أردت البحث عن كلمات متفرقة", "Private",17)
        self.inc_is_fuzzy.set_active(False)
        self.inc_is_quran = gtk.CheckButton()
        self.inc_is_quran.set_sensitive(False)
        self.toolbar.insert_widget(self.inc_is_quran,"البحث في النص القرآني\nخيار لكتب التفسير فقط","Private",18)
        self.toolbar.insert_space(19)
        self.c_tahkem = self.toolbar.insert_item(None,"مركز التحكم","Private",im205,self.tahakem,None,20)
        self.w_tandim = self.toolbar.insert_item(None,"تنظيم المكتبة","Private",im4,self.tandim,None,21)
        self.addbk = self.toolbar.insert_item(None,"استيراد كتب الشاملة","Private",im3, AddBooks,None,22)
        self.font_s = self.toolbar.insert_item(None,"إعداد المظهر","Private",im20,Perference,None,23)
        self.toolbar.insert_space(24)
        self.T_book = self.toolbar.insert_item(None,"بطاقة الكتاب","Private",im13,self.card,None,25)
        self.about0 = self.toolbar.insert_item(None,"دليل المستخدم","Private",im105,self.dalil11,None,26)
        self.about0 = self.toolbar.insert_item(None,"عن البرنامج","Private",im104,show_about1,None,27)
        self.toolbar.insert_space(28)
        self.back = self.toolbar.insert_item(None,"خروج","Private",im304,self.do_close,None,29)
        self.toolbar.set_show_arrow(True)
        
      #  self.im5.set_from_pixbuf(scaled_buf)
      #  self.im5.set_scroll_adjustments(None,None)
      #  self.sco5 = gtk.ScrolledWindow(None,None)
     #   self.sco5.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
      #  self.sco5.add_with_viewport(self.im5)
        self.event_box1 = gtk.EventBox()
        #self.event_box1.add(self.sco5)
        self.event_box1.connect('expose_event', self.expose)
        self.event_box1.connect("button_press_event", self.eventbox)
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(2)
        self.notebook.set_scrollable(True)
        def fff(widget,notebook, page):
            ui = self.notebook.get_nth_page(page)
            self.win.set_title('مكتبة أسماء ('+ui.cnm.get_text()+')') 
            try: 
                if ui.sdb.is_tafseer == 1:
                    self.inc_is_quran.set_sensitive(True)
                else: self.inc_is_quran.set_sensitive(False);self.inc_is_quran.set_active(False)
            except: self.inc_is_quran.set_sensitive(False);self.inc_is_quran.set_active(False)
        self.notebook.connect("switch-page",fff)
        def eee(widget,*a):
            tt = self.notebook.get_n_pages()
            if tt == 0:
                self.event_box1.show_all()
                self.notebook.hide_all()
                self.win.set_title('مكتبة أسماء')
        self.notebook.connect("page-removed",eee)
        self.sco = gtk.ScrolledWindow(None,None)
        self.sco.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.tab_deros.attach(self.event_box1,0,16,0,84)
        self.vb10.pack_start(self.mb,0,0)
        self.vb10.pack_start(self.vb11,1,1)
        self.vb11.pack_start(self.toolbar,0,0)
        self.vb11.pack_start(self.tab_deros,1,1)
        self.tab_deros.attach(self.notebook,0,16,0,84)
        self.win.add(self.vb10)
        self.sco.hide()
        self.win.show_all()
        self.toolb1()
        self.win.set_focus(self.ent_find)
        self.others()
        
# class عارض عنوان اللسان-------------------------------------------------------------------

class TabLabel(gtk.HBox):
    close_img = None
    def __init__(self, child,nm):
        self.child = child
        if not self.close_img:
            self.close_img = gtk.Image()
            self.close_img.set_from_file(self.child.ico)
        gtk.HBox.__init__(self,False,0)
        self.close = gtk.Button()
        self.close.set_tooltip_text('أغلق هذه الصفحة')
        self.close.add(self.close_img)
        self.close.set_relief(gtk.RELIEF_NONE)
        self.close.set_focus_on_click(False)
        self.close.connect('clicked',self.close_tab)
        self.set_border_width(0)
        n = th.notebook.get_current_page()
        tab_label = gtk.Label(nm)
        tab_label.set_max_width_chars(18)
        self.set_tooltip_text(nm)
        self.fff = nm
        tab_label.set_ellipsize(pango.ELLIPSIZE_END)
        self.pack_start(tab_label,True,True,0)
        self.pack_start(self.close,False,False,0)
        self.show_all()
    def close_tab(self,*a):
        th.stop()
        i = th.notebook.page_num(self.child)
        w = th.notebook.get_nth_page(i)
        th.notebook.remove_page(i)
        del w
        try:
            i1 = self.child.current_id
            i1 = str(i1)
            self.child.toc_store.clear()
            self.child.sdb.exit()
            del self.child.ll
        except: pass
        if self.child.cnm.get_text() == 'القرآن الكريم':
            th.conf['quran'] = i1
            th.conf.save()
        elif self.child.cnm.get_text() == 'تنظيم المكتبة':
            th.tree0()
        else:
            try:
                fd = th.pathasmaa+'data/book.asmaa'
                self.con = sqlite3.connect(fd,isolation_level = None)
                cur = self.con.cursor()
                cur.execute('UPDATE books SET fav = "'+i1+'" where bk = "'+str(self.fff)+'"')
                self.con.commit()
                self.con.close()
                cur.close()
            except: pass
        if i < 0: return
       
# class عرض الكتاب----------------------------------------------------------------------

class ThwabViewer(gtk.VBox):
  
    def toc_cb(self,*args):
        (model, i) = self.toc_selection.get_selected()
        if i:
            r = self.sdb.get_text_body(self.book_p,model.get(i,1)[0])
            self.n_pg(r)
            th.display_text(r)
            th.highlight_headers(r[0])
            self.current_id = r[0]
        
    def first_page(self,*args):
        r,i = self.sdb.first_page()
        th.display_text(r,i)
        th.highlight_headers(i)
        self.current_id = i
        try:
            npg = str(r[3])
            npt = str(r[2])
        except: 
            npg = "1"
            npt = "1"
        self.ent_page.set_text(npg)
        self.ent_part.set_text(npt) 
    
    def next_page(self,*args):
        r,i = self.sdb.next_page(self.current_id)
        th.display_text(r,i)
        th.highlight_headers(i)
        self.current_id = i
        self.n_pg(r)
    
    def previous_page(self,*args):
        r,i = self.sdb.previous_page(self.current_id)
        th.display_text(r,i)
        th.highlight_headers(i)
        self.current_id = i
        self.n_pg(r)
    
    def last_page(self,*args):
        r,i = self.sdb.last_page()
        th.display_text(r,i)
        th.highlight_headers(i)
        self.current_id = i
        self.n_pg(r)
        
    def n_pg(self,r):
        try:
            npg = str(r[3])
            npt = str(r[2])
        except: 
            npg = "..."
            npt = "..."
        self.ent_page.set_text(npg)
        self.ent_part.set_text(npt)
  
    def toc_highlight(self, model, path, i, page_id):
        pid = model.get(i,1)[0]
        if pid < page_id: 
            self.toc_hl_last = path 
            return False
        elif page_id == 1:
            self.toc_hl_last = (0,) 
            path = self.toc_hl_last
        elif pid > page_id:
            path = self.toc_hl_last
        self.toc.expand_to_path(path)
        self.toc.scroll_to_cell(path)
        self.toc_selection.select_path(path)
        return True 

    def sds(self,*a):
        return self.cnm
    
    def mov_cb(self,r):
        pg = int(self.ent_page.get_text())
        pr = int(self.ent_part.get_text())
        idp = self.sdb.go_to_page(pg, pr)
        r = self.sdb.get_text_body(self.book_p,idp)
        th.display_text(r)
        th.highlight_headers(r[0])
        self.current_id = r[0]
    
    def sav_cb(self,r):    
        fa = self.ent_mark.get_text()
        if fa == '' :
            dlg('أدخل اسما لحفظ هذا الموضع')
        else :
            i = self.current_id
            i = str(i)
            th.cur1.execute('INSERT INTO kept VALUES ("'+fa+'","'+i+'","'+th.hr+'")')
            check = th.con.commit()
            if check == None:
                dlg('تم الحفظ')
                self.ent_mark.set_text('')

    def __init__(self,app,filename,bkid = -1):
        self.othman = Othman(self)
        self.pddn_c,self.pdup_c = 0,0
        self.sdb = AsmaaBook(filename,bkid)
        self.app = app
        self.cnm = gtk.Label()
        self.__build_gui()
        self.show_all()
        self.search_tokens = []
        self.search_tokens0 = []
        self.fnm = self.sdb.book_name
        self.book_p = filename
        self.current_id = None
        self.set_toc_tree()
        if self.fnm == "دليل المستخدم":
            self.ico = 'icons/Help-16.png'
        elif self.fnm == "القرآن الكريم":
            self.ico = 'icons/Quran-16.png'
        else:
            self.ico = 'icons/Book-Open-16.png'
        
    def ch20(self,*args):
        print 'None'
  
    def jame0(self,*args):
        if self.to == 0:
            self.toc.expand_all()
            self.to = 1
        else :
            self.toc.collapse_all()
            self.to = 0
    
    def fah_cb(self,*args):
        if self.fah_v == 0:
            self.hp.set_position(150)
            self.fah_v = 1
        elif self.fah_v == 1:
            self.hp.set_position(0)
            self.fah_v = 0
              
    def __build_gui(self):
        self.to = 1
        self.fah_v = 0
        gtk.VBox.__init__(self, False,0)
        self.view = gtk.TextView()
        self.buffer = self.view.get_buffer()
        self.qr_tag = []
        self.qr_tag = self.buffer.create_tag()
        self.r_tag = []
        self.r_tag.append(self.buffer.create_tag())
        self.q_tag = []
        self.q_tag.append(self.buffer.create_tag())
        self.h_tag = []
        self.h_tag.append(self.buffer.create_tag())
        self.search_tags_list = []
        self.search_tags_list.append(self.buffer.create_tag())
        self.view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.view.set_editable(False)
        self.view.connect_after("populate-popup", th.populate_popup)
        self.view.set_right_margin(20)
        self.view.set_left_margin(20)
        self.view.set_cursor_visible(False)
        self.toc_store = gtk.TreeStore(int,int,str,int,int) # id,title,lvl,sub
        self.toc = gtk.TreeView(self.toc_store)
        self.toc.set_headers_visible(True)
        self.toc.props.has_tooltip = True
        self.toc.connect("query-tooltip", th.tooltip_toc,2)
        self.toc_selection = self.toc.get_selection()
        self.toc.connect("cursor-changed", self.toc_cb)
        cells = []; cols = []
        r = gtk.CellRendererPixbuf()
        cells.append(gtk.CellRendererText())
        cols.append(gtk.TreeViewColumn('الفهرس'))
        cols[-1].pack_start(r,False)
        cols[-1].pack_start(cells[-1],True)
        cols[-1].add_attribute(cells[-1], 'text', 2)
        cols[-1].set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        cols[-1].set_resizable(False)
        cols[-1].set_expand(True)
        for i in cols: self.toc.insert_column(i, -1)
        self.toc.set_enable_search(True)
        self.toc.set_search_column (2)
        toc_selection = self.toc.get_selection ()
        self.toc.set_has_tooltip(True)
        toc_selection.set_mode (gtk.SELECTION_SINGLE)
        r.set_property("pixbuf-expander-closed",gtk.gdk.pixbuf_new_from_file('icons/Book-Close-24.png'))
        r.set_property("pixbuf-expander-open",gtk.gdk.pixbuf_new_from_file('icons/Book-Open-24.png'))
        r.set_property("pixbuf", gtk.gdk.pixbuf_new_from_file('icons/File-24.png'))
        self.sw0 = gtk.ScrolledWindow(None,None)
        self.sw0.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw0.add(self.view)
        self.jame = gtk.ToolButton(gtk.STOCK_REFRESH)
        self.jame.set_tooltip_text('ضم الفهرس وفتحه')
        self.sw1 = gtk.ScrolledWindow(None,None)
        self.sw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw1.add(self.toc)
        self.hb = gtk.HBox(False,0)
        self.fah = gtk.ToolButton(gtk.STOCK_INDEX)
        self.fah.set_tooltip_text('إظهار الفهرس وإخفاؤه استعمل F9')
        keyw, modw = gtk.accelerator_parse("F9")
        self.fah.add_accelerator('clicked', th.agr, keyw, modw, gtk.ACCEL_VISIBLE)
        self.fah.connect("clicked", self.fah_cb)
        self.hb.pack_start(self.jame,0,0)
        self.hb.pack_start(self.fah,0,0) 
        self.hb.show_all()
        self.toc_vb = gtk.VBox(False,0)
        self.tab0 = gtk.Table(1,5,True)
        self.toc_vb.pack_end(self.tab0,False,False,0)
        self.toc_vb.pack_end(self.sw1,True,True,0)
        self.hp = gtk.HPaned()
        self.hp.set_position(1)
        self.c_search = gtk.Entry()
        self.c_search.set_sensitive(False)
        self.ch2 = gtk.ToolButton(gtk.STOCK_FIND)
        self.ch2.set_sensitive(False)
        self.tab0.attach(self.ch2,0,1,0,1)
        self.ch2.connect('clicked',self.ch20)
        self.jame.connect('clicked',self.jame0)
        self.tab0.attach(self.c_search,1,5,0,1)
        self.hp.pack1(self.toc_vb,True,True)
        self.hp.pack2(self.sw0,True,True)
        self.pack_start(self.hp,True,True,0)
        self.pack_start(self.hb,False,False,0)
        self.ent_mark = gtk.Entry()
        self.page_n = gtk.Label('      الصفحة  ')
        self.ent_page = gtk.Entry()
        self.ent_page.set_width_chars(5)
        self.hb.pack_start(self.page_n,0,0) 
        self.hb.pack_start(self.ent_page,0,0)
        self.part_n = gtk.Label('  الجزء  ') 
        self.ent_part = gtk.Entry()
        self.ent_part.set_width_chars(5) 
        self.hb.pack_start(self.part_n,0,0)
        self.hb.pack_start(self.ent_part,0,0) 
        self.mov = gtk.ToolButton(gtk.STOCK_REDO)
        self.mov.set_tooltip_text('الانتقال إلى الصفحة المحددة')
        self.hb.pack_start(self.mov,False,False,2)
        self.mov.connect("clicked", self.mov_cb)
        self.hb.pack_start(gtk.Label('                         '),0,0)
        self.ent_mark.set_width_chars(15)
        self.hb.pack_start(self.ent_mark,0,0)
        self.sav = gtk.ToolButton(gtk.STOCK_SAVE)
        self.sav.set_tooltip_text('حفظ الموضع الحالي')
        self.hb.pack_start(self.sav,False,False,0)
        self.sav.connect("clicked", self.sav_cb)
        self.inc_is_quran = gtk.CheckButton("بحث  في القرآن")
        
    def set_toc_tree(self):
        self.toc_store.clear()
        self.ll = self.sdb.get_toc()
        fff = len(self.ll)
        iters = [None]
        last_iter = None
        last_level = 0
        for i in self.ll:
            level = i[3]
            if level > last_level: iters.append(last_iter)
            elif level < last_level:
                for j in range(last_level-level): iters.pop()
            try :
                last_iter = self.toc_store.append(iters[-1], list(i))
            except :
                pass
            last_level = level
            if fff > 1:
                self.hp.set_position(150)
                self.fah_v = 1
            else:
                self.hp.set_position(0)
                self.fah_v = 0
       
            
            
# class عرض البحث----------------------------------------------------------

class Asmasearch(gtk.VBox):

    def find(self,text,sto_s,metassila,ihdaha,bilharakat,qrn,nss,ans):
        self.sto = sto_s
        if qrn.get_active() == False:
            if bilharakat.get_active() == False:
                if nss.get_active() == True: s = '''fuzzy_normalize(nass) LIKE ? ESCAPE "|"'''
                else: s = '''fuzzy_normalize(tit) LIKE ? ESCAPE "|"'''
                text = fuzzy.normalize(text)
            else: 
                if nss.get_active() == True: s = '''nass LIKE ? ESCAPE "|"'''
                else: s = '''tit LIKE ? ESCAPE "|"'''
            self.search_tokens = fuzzy.tokenize_search(text)
            l = map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
            if len(l) < 1: return []
            if ihdaha.get_active() == False:
                self.condition = ' AND '.join([s]*len(l))
            else :
                self.condition = ' OR '.join([s]*len(l))
            j = 0
            self.f0 = 0
            while self.f0 in range(len(sto_s)):
                fnm = u''+th.pathasmaa+'books/'+sto_s[self.f0]+'.asm'
                while (gtk.events_pending()): gtk.main_iteration()
                __cn = sqlite3.connect(fnm, isolation_level = None)
                c = sqlite3.connect(fnm,isolation_level = None)
                __c = __cn.cursor()
                c1 = c.cursor()
                try:
                    __cn.create_function('fuzzy_normalize',1,fuzzy.normalize)
                    
                    if nss.get_active() == True:
                        __c.execute("select id from pages")
                        ds =  __c.fetchall()
                        lds = len(ds)
                        ll = lds/200
                        tt = lds-(200*ll)
                        fv = 0    
                        while fv in range(ll+1):
                            while (gtk.events_pending()): gtk.main_iteration()
                            o1 = fv*200
                            p1 = (fv+1)*200
                            if fv < ll:
                                self.cond = 'id BETWEEN %s and %d' % (o1,p1)
                            elif fv == ll:
                                self.cond = 'id BETWEEN %s and %d' % (o1,tt)
                            elif fv > ll:
                                self.f0 += 1
                            __c.execute("""SELECT id,part,page FROM pages WHERE %s and %s """ % (self.cond, self.condition), l)
                            a = __c.fetchall()
                            self.l_search.set_text('   عدد النتائج   '+str(j)+'    ')
                            self.progress1.set_text(sto_s[self.f0])
                            self.progress1.set_fraction(float(self.f0+1)/float(len(sto_s)))
                            for rr in range(len(a)):
                                g1 = int(a[rr][0])
                                try: g2 = int(a[rr][1])
                                except: g2 = 1
                                try: g3 = int(a[rr][2])
                                except: g3 = 0
                                gg = int(a[rr][0]+1)
                                op = " < "
                                self.condi = 'id %s %d' % (op,gg)
                                c1.execute('select tit from titles where %s' % (self.condi))
                                __toc = c1.fetchall()
                                try: h = str(__toc[-1][0])
                                except: h = ' '
                                j += 1
                                self.search_store.append([j,g1,sto_s[self.f0],h,g2,g3,"Tip",50.0])
                                self.sh_store.append([j,g1,sto_s[self.f0],h,g2,g3,"Tip",50.0])
                                if len(self.search_store) == 1:
                                    i1 = self.search_store.get_iter(0,)
                                    self.toc_selection1.select_iter(i1)
                                    self.ss_cb1()
                            fv += 1
                        
                    elif ans.get_active() == True:
                        __c.execute("""SELECT id,tit FROM titles WHERE %s """ % (self.condition), l)
                        a = __c.fetchall()
                        self.l_search.set_text('   عدد النتائج   '+str(j)+'    ')
                        self.progress1.set_text(sto_s[self.f0])
                        self.progress1.set_fraction(float(self.f0+1)/float(len(sto_s)))
                        for rr in range(len(a)):
                            g1 = int(a[rr][0])
                            gg = str(a[rr][0])
                            h = a[rr][1]
                            c1.execute('select part,page from pages where id = %d' % (g1))
                            ko = c1.fetchall()
                            g2 = ko[0][0]
                            g3 = ko[0][1]
                            j += 1
                            self.search_store.append([j,g1,sto_s[self.f0],h,g2,g3,"Tip",50.0])
                            self.sh_store.append([j,g1,sto_s[self.f0],h,g2,g3,"Tip",50.0])
                except: self.f0 += 1
                self.f0 += 1
            self.l_search.set_text("عدد النتائج    "+str(j)+'    ')   
            self.progress1.set_text('انتهى البحث')
            self.progress1.set_fraction(1.0)
            self.stp.set_sensitive(False)
        else:
            self.inc_is_quran.set_active(True)
            self.quran.set_text("1")
            self.cnm.set_text(th.hr) 
            th.do_win()
            self.toc1.set_headers_visible(False)      
            j = 0 
            __cn = sqlite3.connect('data/quran.db', isolation_level = None)
            c = sqlite3.connect('data/koran',isolation_level = None)
            __c = __cn.cursor()
            _c = __cn.cursor()
            c1 = c.cursor()
            sdb = AsmaaBook('data/koran',-1)
            __cn.create_function('fuzzy_normalize',1,fuzzy.normalize)
            if bilharakat.get_active() == False:
                s = '''fuzzy_normalize(imlai) LIKE ? ESCAPE "|"'''
                text = fuzzy.normalize(text)
            else: 
                s = '''imlai LIKE ? ESCAPE "|"'''
            self.search_tokens = fuzzy.tokenize_search(text)
            l = map(lambda s: '%'+s.replace('|','||').replace('%','|%')+'%',self.search_tokens)
            if len(l) < 1: return []
            if ihdaha.get_active() == False:
                self.condition = ' AND '.join([s]*len(l))
            else :
                self.condition = ' OR '.join([s]*len(l))   
            __c.execute("""SELECT id FROM Quran WHERE %s""" % (self.condition), l)
            a = __c.fetchall()
            for s in range(len(a)):
                gt = a[s][0]
                isr = (gt/512)+1
                iya = gt-((isr-1)*512)
                g1 = sdb.page_quran(isr , iya+1)
                j = j+1
                _c.execute("""SELECT sura_name FROM suranames""")
                b = _c.fetchall()
                g2 = str(b[isr-1][0])
                self.search_store.append([j,g1,g2,str(iya+1),0,0,"Tip",50.0])
                self.sh_store.append([j,g1,g2,str(iya+1),0,0,"Tip",50.0])
            self.l_search.set_text("    عدد النتائج    "+str(j)+'    ')  
            self.progress1.set_text('انتهى البحث')
            self.progress1.set_fraction(1.0) 
            self.stp.set_sensitive(False)
        self.sh_store.append(fuzzy.tokenize_search(text))
        self.sh_store.append(str(metassila.get_active()))
        if qrn.get_active() == False: self.sh_store.append(0)
        else: self.sh_store.append(1)
        if len(self.search_store)>0:
            output = open(th.pathasmaa+'data/last-search.pkl', 'wb')
            cPickle.dump(self.sh_store, output)
            output.close()

    def stop_cb(self,*args):
        self.f0 = len(self.sto)
        
    def ss_cb1(self,*args):
        (model, i) = self.toc_selection1.get_selected()
        if i:
            self.fnm = self.search_store.get_value(i,2)
            self.c_id = self.search_store.get_value(i,1)
            self.fng = str(self.search_store.get_value(i,5))
            self.fnp = str(self.search_store.get_value(i,4))
            self.book_p = th.pathasmaa+'books/'+self.fnm+'.asm'
            fnq = 'data/koran'
            if self.inc_is_quran.get_active() == True: self.sdb = AsmaaBook(fnq,-1)
            else:
                try: self.sdb = AsmaaBook(self.book_p,-1)
                except: dlg("الكتب غير موصولة");return
            self.ent_page.set_text(self.fng)
            self.ent_part.set_text(self.fnp)
            r = self.sdb.get_text_body(self.book_p,self.c_id)
            th.display_text(r,self.c_id)
            th.font()
            th.page_highlight()
            
    def sds(self,*a):
        return self.cnm  
    def save_search(self,*args):
        nm = self.inc_search1.get_text()
        if nm == "":
            dlg("أدخل الاسم أولا.")
        elif nm in os.listdir(th.pathasmaa+'data/records/'): dlg("يوجد بحث محفوظ بنفس الاسم !!")
        else:
            output = open(th.pathasmaa+"data/records/"+nm, 'wb')
            cPickle.dump(self.sh_store, output)
            output.close()
        self.inc_search1.set_text("")
        
    def first_page(self,*args):
        r,i = self.sdb.first_page()
        th.display_text(r,i)
        try:
            npg = str(r[3])
            npt = str(r[2])
        except: 
            npg = "1"
            npt = "1"
        self.ent_page.set_text(npg)
        self.ent_part.set_text(npt) 
    
    def next_page(self,*args):
        r,i = self.sdb.next_page(self.current_id)
        th.display_text(r,i)
        self.n_pg(r)
    
    def previous_page(self,*args):
        r,i = self.sdb.previous_page(self.current_id)
        th.display_text(r,i)
        self.n_pg(r)
    
    def last_page(self,*args):
        r,i = self.sdb.last_page()
        th.display_text(r,i)
        self.n_pg(r)
        
    def n_pg(self,r):
        try:
            npg = str(r[3])
            npt = str(r[2])
        except: 
            npg = "...."
            npt = "...."
        self.ent_page.set_text(npg)
        self.ent_part.set_text(npt)

    def up0(self,*a):
        mod = self.toc1.get_selection()
        ar = mod.get_selected()
        if ar[1]:
            df = self.search_store.get_path(ar[1])
            df = df[0]
            if df == 0: df = df
            else: df = df-1
            i1 = self.search_store.get_iter(df,)
            self.toc1.get_selection().select_iter(i1)
            self.toc1.scroll_to_cell((df,))
            self.ss_cb1()
        
    def down0(self,*a):
        mod = self.toc1.get_selection()
        ar = mod.get_selected()
        if ar[1]:
            df = self.search_store.get_path(ar[1])
            df = df[0]
            if df == len(self.search_store)-1: df = df
            else: df = df+1
            i1 = self.search_store.get_iter(df,)
            self.toc1.get_selection().select_iter(i1)
            self.toc1.scroll_to_cell((df,))
            self.ss_cb1()
                
    def __init__(self,*args):
        self.search_tokens = []
        self.othman = Othman(self)
        self.sdb = None
        self.current_id = None
        self.ico = 'icons/Search-Books-16.png'
        self.__build_gui1()
        self.show_all()
 
    def __build_gui1(self):
        self.fnm = ''
        self.fng = ''
        self.fnp = ''
        self.sto = []
        self.cnm = gtk.Label()
        self.toc_store = gtk.TreeStore(str)
        self.ent_page = gtk.Entry()
        self.ent_part = gtk.Entry()
        gtk.VBox.__init__(self, False,0)
        self.view = gtk.TextView()
        self.buffer = self.view.get_buffer()
        self.qr_tag = []
        self.qr_tag = self.buffer.create_tag()
        self.r_tag = []
        self.r_tag.append(self.buffer.create_tag())
        self.q_tag = []
        self.q_tag.append(self.buffer.create_tag())
        self.h_tag = []
        self.h_tag.append(self.buffer.create_tag())
        self.search_tags_list = []
        self.search_tags_list.append(self.buffer.create_tag())
        self.view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.view.set_editable(False)
        self.view.connect_after("populate-popup", th.populate_popup)
        self.view.set_right_margin(20)
        self.view.set_left_margin(20)
        self.view.set_cursor_visible(False)
        self.sh_store = []
        self.search_store = gtk.ListStore(int,int,str,str,int,int,str,float) # num,id,book,title,part,page,segment,rank
        self.toc1 = gtk.TreeView(self.search_store)
        self.toc = gtk.TreeView()
        self.toc1.modify_font(pango.FontDescription('KacstOne 10'))
        self.toc_selection1 = self.toc1.get_selection()
        self.toc1.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
        self.toc1.connect("cursor-changed", self.ss_cb1)
        raq = gtk.TreeViewColumn('الرقم',gtk.CellRendererText(),text = 0)
        nass = gtk.TreeViewColumn('النص',gtk.CellRendererText())
        kitab = gtk.TreeViewColumn('الكتاب',gtk.CellRendererText(),text = 2)
        kitab.set_max_width(400)
        kitab.set_resizable(True)
        bab = gtk.TreeViewColumn('الباب',gtk.CellRendererText(),text = 3)
        bab.set_max_width(400)
        bab.set_resizable(True)
        jez = gtk.TreeViewColumn('الجزء',gtk.CellRendererText(),text = 4)
        saf = gtk.TreeViewColumn('الصفحة',gtk.CellRendererText(),text = 5)
        self.toc1.append_column(raq)
        self.toc1.append_column(nass)
        self.toc1.append_column(kitab)
        self.toc1.append_column(bab)
        self.toc1.append_column(jez)
        self.toc1.append_column(saf)
        self.toc1.set_expander_column(kitab)
        self.toc1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcf))
        self.toc1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcb))
        self.toc_selection1.set_mode (gtk.SELECTION_SINGLE)
        self.sw0 = gtk.ScrolledWindow(None,None)
        self.sw0.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.sw0.add(self.view)
        self.sw11 = gtk.ScrolledWindow(None,None)
        self.sw11.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw11.add(self.toc1)
        self.hb1 = gtk.HBox(False,10)
        self.view_vb1 = gtk.VBox(False,0)
        self.view_vb1.pack_start(self.sw0,True,True,0)
        self.view_vb1.pack_start(self.hb1,False,False,0)
        self.hp1 = gtk.VPaned()
        self.hp1.pack1(self.view_vb1,True,True)
        self.hp1.pack2(self.sw11,True,True)
        ty = th.win.get_size()
        te = ty[1]/5*3
        self.hp1.set_position(te)
        self.pack_start(self.hp1,True,True,0)
        self.ch11 = gtk.ToolButton(gtk.STOCK_SAVE)
        self.ch11.set_tooltip_text('حفظ نتائج البحث')
        self.ch11.connect("clicked", self.save_search)
        self.hb1.pack_start(self.ch11,False,False,0)
        self.fi11 = gtk.ToolButton(gtk.STOCK_FIND)
        self.fi11.set_tooltip_text('البحث في نتائج البحث')
        self.hb1.pack_start(self.fi11,False,False,0)
        self.fi11.connect("clicked", th.search_search)
        self.inc_search1 = gtk.Entry() 
        self.inc_search1.set_width_chars(15)
        self.progress1 = gtk.ProgressBar()
        self.hb1.pack_start(self.inc_search1,False,False)
        ig8 = gtk.Image()
        ig8.set_from_file('icons/stp.png')
        self.stp = gtk.ToolButton(ig8)
        self.stp.connect("clicked", self.stop_cb)
        self.hb1.pack_start(self.stp,False,False,0)
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
        self.hb1.pack_start(self.up,0,0)
        self.hb1.pack_start(self.down,0,0) 
        self.l_search = gtk.Label() 
        self.hb1.pack_start(self.l_search,False,False)
        self.hb1.pack_start(self.progress1,1,1)
        self.inc_is_quran = gtk.CheckButton("بحث  في القرآن")
        self.quran = gtk.Label()
   
# class عرض أوراق البحث--------------------------------------------------------

class warakat(gtk.VBox):
    
    def save(self,*a):
        f7 = self.buffer.get_start_iter()
        f8 = self.buffer.get_end_iter()
        y = open(self.faa , 'w')
        va4 = str(self.buffer.get_text(f7,f8,True))
        y.write(va4)
        y.close()
        
    def display(self,qa):
        self.faa = qa
        self.f = open(qa)
        self.sa = self.f.readlines()
        self.sq = ' '.join(self.sa)
        self.buffer.set_text(self.sq)
    
    def __init__(self,qa):
        gtk.VBox.__init__(self, False,0)
        self.ico = 'icons/Papers-16.png'
        self.cnm = gtk.Label()
        self.fnm = "waraka"
        self.search_tokens = []
        self.search_text = gtk.Entry()
        self.view = gtk.TextView()
        self.view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.view.set_right_margin(20)
        self.view.set_left_margin(20)
        self.view.modify_font(pango.FontDescription("Simplified Naskh 15"))
        self.view.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color('#000020'))
        self.view.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color("#fffff8"))
        self.view.connect_after("populate-popup", th.populate_popup)
        self.buffer = self.view.get_buffer()
        self.sw0 = gtk.ScrolledWindow(None,None)
        self.sw0.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw0.add(self.view)
        self.search_tags_list = []
        self.search_tags_list.append(self.buffer.create_tag())
        self.search_tags_list[-1].set_property("background", th.colorsb) 
        self.hb = gtk.HBox(False,0)
        self.bh = gtk.ToolButton(gtk.STOCK_SAVE)
        self.bh.set_tooltip_text('حفظ التغييرات')
        self.hb.pack_start(self.bh,0,0)
        im10 = gtk.Image()
        im10.set_from_file('icons/word.png')
        self.bw = gtk.ToolButton(im10)
        self.bw.set_tooltip_text('افتح مستند في معالج النصوص')
        nm = str(th.hr)+'.odt'
        def new(widget, *a):
            self.f_ch_n = gtk.FileChooserDialog("مسار المستند الجديد",None,
                                gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_OK))
            ok_button = self.f_ch_n.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
            def ggn(widget,*args):
                os.system('cp data/model.odt '+"'"+str(self.f_ch_n.get_current_folder())+"'"+"/"+"'"+nm+"'")
                os.system('cd '+"'"+str(self.f_ch_n.get_current_folder())+"'"+';'+'xdg-open '+"'"+nm+"'")
            ok_button.connect('clicked', ggn)
            self.f_ch_n.run()
            self.f_ch_n.destroy()
        self.bw.connect('clicked',new)
        self.hb.pack_start(self.bw,0,0)
        self.bh.connect('clicked',self.save)
        self.pack_start(self.sw0,1,1)
        font_v = gtk.HScale()
        font_v.set_value_pos(0)
        self.hb.pack_start(gtk.Label('                                         '),1,1)
        self.hb.pack_start(font_v,1,1)
        font_v.set_range(10, 36)
        font_v.set_value(15)
        def on_changed(widget,*a):
            for i in range(10,37):
                val = widget.get_value()
                val = int(val)
                if i == val:
                    self.view.modify_font( pango.FontDescription("Simplified Naskh %d"%i)) 
        font_v.connect("value-changed", on_changed)
        font_v.set_increments(0, 1)
        font_v.set_digits(0)
        self.pack_start(self.hb,0,0)
        self.display(qa)
        self.show_all()
        
# class تنظيم المكتبة-----------------------------------------------------------

class Organizing(gtk.VBox):
    
    def ok2(self,*a):
        self.store_kaima3.clear()
        (model1, i1) = self.kaima1.get_selection().get_selected()
        if i1:
            (p1,c1) = self.kaima1.get_cursor()
            r1 = model1.get_value(i1,0)
            th.cur1.execute('SELECT val FROM groups where grp = "'+r1+'"')
            m0 = th.cur1.fetchall()
            sa = str(m0[0][0])
            th.cur1.execute('SELECT bk FROM books where val = "'+sa+'" ORDER BY bk ')
            m1 = th.cur1.fetchall()
            x = 0 
            while x in range(len(m1)):
                self.store_kaima3.append([m1[x][0],sa])
                x += 1
            self.chajara.set_active(p1[0])
            self.adad_k.set_text("  عدد كل الكتب : "+self.nmb+"   ||   عدد كتب القسم المحدد : "+str(len(m1)))
            self.kaima3.scroll_to_cell((0))
            self.b_view1.set_text("") 
            self.b_view3.set_text("") 
    
    def addks(self,*args):
        th.cur1.execute('SELECT val FROM groups')
        fe5 = th.cur1.fetchall()
        ff1 = str(len(fe5)+1)
        if fe5 == []:
            fw = 1 
        else :
            fw = fe5[-1][0]+1
            print fw , fe5[-1][0]
        fw = str(fw)
        fa = self.en1.get_text() 
        if fa == '' :
            dlg('أدخل اسما مناسبا في مكانه أولا')
        else :
            th.cur1.execute('INSERT INTO groups VALUES ("'+fa+'","'+fw+'","'+ff1+'")')
            check = th.con.commit()
            if check == None:
                th.store_kaima1.append([fa]) 
                self.en1.set_text('')
                self.tr0 = 1
    
    def remks(self,*args):
        global res_dlg
        (model1, i1) = self.kaima1.get_selection().get_selected()
        if i1  : 
            r1 = model1.get_value(i1,0)   
            dlg_res('هل ترغب في حذف هذا القسم\n مع جميع الكتب الموجودة تحته ؟')
            if res_dlg == False: return
            else: 
                th.cur1.execute('select val,tar from groups where grp = "'+r1+'" ')
                in0 = th.cur1.fetchall()
                in1 = str(in0[0][0])
                in2 = str(in0[0][1])
                th.cur1.execute('delete from groups where grp = "'+r1+'"')
                check1 = th.con.commit()
                if (check1 == None):
                    th.cur1.execute('select * from groups')
                    in00 = th.cur1.fetchall()
                    e = 0
                    while e in range(len(in00)):
                        in4 = str(in00[e][0])
                        in3 = str(in00[e][2]-1)
                        th.cur1.execute('UPDATE groups SET tar = "' + in3 + '" WHERE tar > "' +in2+ '"and grp = "'+in4+'"')
                        th.con.commit()
                        e += 1
                    th.store_kaima1.remove(i1)
                    th.cur1.execute('select bk from books where val = "'+in1+'" ')
                    ind0 = th.cur1.fetchall()
                    th.cur1.execute('delete from books where val = "'+in1+'"')
                    check2 = th.con.commit()
                    if (check2 == None):
                        rc = len(ind0)
                        fc = 0
                        self.tr0 = 1
                        while fc in range(rc+1):
                            fy = str(ind0[fc][0])
                            os.remove(th.pathasmaa+'books/'+fy+'.asm')
                            fc += 1
                res_dlg = False
                
    def renks(self,*args):
        (model1, i1) = self.kaima1.get_selection().get_selected()
        if i1:
            fa = self.en1.get_text() 
            if fa == '' :
                dlg('أدخل اسما مناسبا في مكانه أولا')
            else :
                r1 = model1.get_value(i1,0)
                th.cur1.execute('UPDATE groups SET grp = "' + fa + '" WHERE grp = "' +r1+ '"')
                check = th.con.commit()
                if check == None:
                    th.store_kaima1.set_value(i1,0,fa)
                    self.tr0 = 1
                    
    def mvu(self,*args):
        (model1, i1) = self.kaima1.get_selection().get_selected()
        if i1:
            r1 = model1.get_path(i1)
            if r1[0] != 0 :
                d3 = str(model1.get_value(i1,0))
                d1 = str(r1[0]+1)
                d2 = str(r1[0])
                th.cur1.execute('UPDATE groups SET tar = "' + d1 + '" WHERE tar = "' +d2+ '"')
                check = th.con.commit()
                if check == None:
                    th.cur1.execute('UPDATE groups SET tar = "' + d2 + '" WHERE grp = "' +d3+ '"')
                    check1 = th.con.commit()
                    if check1 == None:
                        gg = th.store_kaima1.get_iter((r1[0]-1,))
                        th.store_kaima1.move_before(i1,gg)
                        self.tr0 = 1
                        
    def mvd(self,*args):
        th.cur1.execute('SELECT val FROM groups')
        fe6 = th.cur1.fetchall()
        (model1, i1) = self.kaima1.get_selection().get_selected()
        if i1:
            r1 = model1.get_path(i1)
            if r1[0] < len(fe6)-1 :
                d3 = str(model1.get_value(i1,0))
                d1 = str(r1[0]+1)
                d2 = str(r1[0]+2)
                th.cur1.execute('UPDATE groups SET tar = "' + d1 + '" WHERE tar = "' +d2+ '"')
                check = th.con.commit()
                if check == None:
                    th.cur1.execute('UPDATE groups SET tar = "' + d2 + '" WHERE grp = "' +d3+ '"')
                    check1 = th.con.commit()
                    if check1 == None:
                        gg = th.store_kaima1.get_iter((r1[0]+1,))
                        th.store_kaima1.move_after(i1,gg)
                        self.tr0 = 1
                        
    def rembk(self,*args):
        global res_dlg
        (model1, i1) = self.kaima3.get_selection().get_selected()
        if i1  :
            r1 = model1.get_value(i1,0) 
            r2 = model1.get_value(i1,1) 
            dlg_res('هل ترغب في حذف هذا الكتاب ؟')
            if res_dlg == False: return
            else:
                th.cur1.execute('delete from books where bk = "'+r1+'" and val = "'+r2+'"')
                check1 = th.con.commit()
                if (check1 == None):
                    self.store_kaima3.remove(i1)
                    th.cur1.execute('SELECT bk FROM books where bk = "'+r1+'"')
                    fe7 = th.cur1.fetchall()
                    if len(fe7) == 0:
                        os.remove(th.pathasmaa+'books/'+r1+'.asm')
                        self.tr0 = 1
            res_dlg = False
            
    def renbk(self,*args):
        (model1, i1) = self.kaima3.get_selection().get_selected()
        if i1:
            r1 = model1.get_value(i1,0)
            fa = self.en1.get_text() 
            if fa == '' :
                dlg('أدخل اسما مناسبا في مكانه أولا')
            else :
                th.cur1.execute('UPDATE books SET bk = "' + fa + '" WHERE bk = "' +r1+ '"')
                check = th.con.commit()
                if check == None:
                    os.rename(th.pathasmaa+'books/'+r1+'.asm', th.pathasmaa+'books/'+fa+'.asm')
                    self.store_kaima3.set_value(i1,0,fa)
                    self.tr0 = 1
                    
    def addfav(self,*args):
        (model1, i1) = self.kaima3.get_selection().get_selected()
        if i1:
            r1 = model1.get_value(i1,0)
            y = open(th.pathasmaa+'data/favorite/'+r1 , 'w')
            y.close()
            dlg('تم إضافة الكتاب إلى المفضلة !')
                
    def chn(self,*args):
        global res_dlg
        (model2, i2) = self.kaima3.get_selection().get_selected()
        ss = self.chajara.get_active_text()
        if i2  :
            r2 = model2.get_value(i2,0) 
            r3 = model2.get_value(i2,1) 
            dlg_res('هل ترغب في نقل اسم الكتاب\n إلى قسم '+ss+' ؟')
            if res_dlg == False: return
            else:
                th.cur1.execute('select val from groups where grp = "'+ss+'" ')
                in00 = th.cur1.fetchall()
                in11 = str(in00[0][0])
                th.cur1.execute('SELECT bk FROM books where bk = "'+r2+'" and val = "'+in11+'"')
                fe8 = th.cur1.fetchall()
                if len(fe8) == 0:
                    th.cur1.execute('UPDATE books SET val = "' + in11 + '" WHERE bk = "' +r2+ '" and val = "'+r3+'"')
                    th.con.commit()
                else :
                    th.cur1.execute('delete from books where bk = "'+r2+'" and val = "'+r3+'"')
                    th.con.commit()
                self.store_kaima3.remove(i2)
                self.tr0 = 1
            res_dlg = False
            
    def cop(self,*args):
        global res_dlg
        (model2, i2) = self.kaima3.get_selection().get_selected()
        ss = self.chajara.get_active_text()
        if i2  :
            r2 = model2.get_value(i2,0)  
            dlg_res('هل ترغب في نسخ اسم الكتاب\n في قسم '+ss+' ؟')
            if res_dlg == False: return
            else:
                th.cur1.execute('select val from groups where grp = "'+ss+'" ')
                in00 = th.cur1.fetchall()
                in11 = str(in00[0][0])
                th.cur1.execute('SELECT bk FROM books where bk = "'+r2+'" and val = "'+in11+'"')
                fe8 = th.cur1.fetchall()
                if len(fe8) == 0:
                    th.cur1.execute('INSERT INTO books VALUES ("'+r2+'","'+in11+'",0)')
                    th.con.commit()
                    self.tr0 = 1
            res_dlg = False
            
    def bitaka(self,*a):
        t_selec = self.kaima3.get_selection()
        (model, i) = t_selec.get_selected()
        r = model.get(i,0)[0] 
        fd = th.pathasmaa+'books/'+r+'.asm'
        con = sqlite3.connect(fd,isolation_level = None)
        cur = con.cursor()
        cur.execute('select * from main')
        read = cur.fetchall()
        card_k = read[0][5]
        self.b_view1.set_text(str(card_k)) 
        inf_k = read[0][6]
        self.b_view3.set_text(str(inf_k)) 
    
    def ok_open(self,*a):
        t_selec = self.kaima3.get_selection()
        (model, i) = t_selec.get_selected()
        r = model.get(i,0)[0]
        self.hr = str(r)
        fd = th.pathasmaa+'books/'+r+'.asm'
        fd0 = th.pathasmaa+'data/book.asmaa'
        self.c = sqlite3.connect(fd0,isolation_level = None)
        cr = self.c.cursor()
        cr.execute('select fav from books where bk = "'+self.hr+'"')
        rd = cr.fetchall()
        try: ri = int(rd[0][0])
        except: ri = 1
        th.open_bk(fd, ri,self.hr)   
         
    def sav_bitaka(self,*a):
        global res_dlg
        t_selec = self.kaima3.get_selection()
        (model, i) = t_selec.get_selected()
        if i :
            dlg_res("هل تريد تعديل بيانات الكتاب المحدد ؟")
            if res_dlg == False: return
            else:
                r = model.get(i,0)[0]
                f1 = self.b_view1.get_start_iter()
                f2 = self.b_view1.get_end_iter()  
                bitaka = self.b_view1.get_text(f1,f2,True)
                f3 = self.b_view2.get_start_iter()
                f4 = self.b_view2.get_end_iter()  
                auth = self.b_view2.get_text(f3,f4,True)
                f5 = self.b_view3.get_start_iter()
                f6 = self.b_view3.get_end_iter()  
                info = self.b_view3.get_text(f5,f6,True)
                fd = th.pathasmaa+'books/'+r+'.asm'
                c = sqlite3.connect(fd,isolation_level = None)
                cr = c.cursor()
                cr.execute('UPDATE main SET betaka = "'+bitaka+'",inf = "'+info+'"')
                check = c.commit()
                if check == None: dlg("تم تعديل البيانات")
                res_dlg = False
                
    def __init__(self,qa):
        gtk.VBox.__init__(self,False,5)
        self.ico = 'icons/Configs-16.png'
        self.cnm = gtk.Label()
        tab = gtk.Table(4,9,True)
        tab.set_col_spacings(10)
        tab_1 = gtk.Table(2,9,True)
        tab_1.set_row_spacings(4)
        tab_1.set_col_spacings(4)
        hb = gtk.HBox(False,10)
        hb1 = gtk.HBox(False,10)
        scok1 = gtk.ScrolledWindow()
        scok1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scok1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        self.kaima1 = gtk.TreeView()
        kal = gtk.TreeViewColumn('الأقسام',gtk.CellRendererText(),text = 0)
        self.kaima1.append_column(kal)
        self.kaima1.set_model(th.store_kaima1)
        self.kaima1.modify_font( pango.FontDescription(th.fontc))
        self.kaima1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcf))
        self.kaima1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcb))        
        self.kaima1.connect("cursor-changed", self.ok2)
        self.kaima1.props.has_tooltip = True
        self.kaima1.connect("query-tooltip", th.tooltip_toc,0)
        scok1.add(self.kaima1)
        self.nmb = str(len(os.listdir(th.pathasmaa+'/books/')))
        self.adad_k = gtk.Label("  عدد كل الكتب : "+self.nmb+"   ||   عدد كتب القسم المحدد : ")
        self.adad_k.set_alignment(0,0.5)
        hb.pack_start(self.adad_k,0,0)
        tab.attach(scok1,0,2,0,4)
        scok3 = gtk.ScrolledWindow()
        scok3.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scok3.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        self.kaima3 = gtk.TreeView()
        self.store_kaima3 = gtk.ListStore(str,str)
        kal3 = gtk.TreeViewColumn('الكتب',gtk.CellRendererText(),text = 0)
        self.kaima3.append_column(kal3)
        self.kaima3.set_model(self.store_kaima3)
        self.kaima3.props.has_tooltip = True
        self.kaima3.connect("query-tooltip", th.tooltip_toc,0)
        self.kaima3.modify_font(pango.FontDescription(th.fontc))
        self.kaima3.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcf))
        self.kaima3.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcb))
        self.kaima3.connect("row-activated", self.ok_open)
        self.kaima3.connect("cursor-changed", self.bitaka)
        scok3.add(self.kaima3)
        tab.attach(scok3,2,6,0,4)
        tab_1.attach(gtk.Label('الأقسام   '),0,1,0,1)
        hb1.pack_start(tab_1,0,0)
        tab_1.attach(gtk.Label('الكتب     '),0,1,1,2)
        b1 = gtk.Button('جديد')
        tab_1.attach(b1,1,2,0,1)
        b1.connect('clicked',self.addks)
        self.en1 = gtk.Entry()
        tab_1.attach(self.en1,6,9,0,1)
        b2 = gtk.Button('حذف')
        tab_1.attach(b2,2,3,0,1)
        b2.connect('clicked',self.remks)
        b3 = gtk.Button('تسمية')
        b3.connect('clicked',self.renks)
        tab_1.attach(b3,3,4,0,1)
        b21 = gtk.Button('لأعلى')
        tab_1.attach(b21,4,5,0,1)
        b21.connect('clicked',self.mvu)
        b22 = gtk.Button('لأسفل')
        b22.connect('clicked',self.mvd)
        tab_1.attach(b22,5,6,0,1)
        b5 = gtk.Button('تسمية')
        tab_1.attach(b5,1,2,1,2)
        b5.connect('clicked',self.renbk)
        b4 = gtk.Button('حذف')
        tab_1.attach(b4,2,3,1,2)
        b4.connect('clicked',self.rembk)
        b7 = gtk.Button('تفضيل')
        tab_1.attach(b7,3,4,1,2)
        b7.connect('clicked',self.addfav)
        b6 = gtk.Button('نسخ إلى')
        tab_1.attach(b6,4,5,1,2)
        b61 = gtk.Button('نقل إلى')
        tab_1.attach(b61,5,6,1,2)
        b61.connect('clicked',self.chn)
        b6.connect('clicked',self.cop)
        self.chajara = gtk.ComboBox()
        cell = gtk.CellRendererText()
        self.chajara.pack_start(cell)
        self.chajara.add_attribute(cell, 'text', 0)
        self.chajara.set_wrap_width(1)
        self.chajara.set_model(th.store_kaima1)
        tab_1.attach(self.chajara,6,9,1,2)
        self.noteb = gtk.Notebook() 
        self.noteb.set_scrollable(True)
        self.b_view1 = gtk.TextBuffer()
        self.b_view2 = gtk.TextBuffer()
        self.b_view3 = gtk.TextBuffer()
        sco1 = gtk.ScrolledWindow()
        sco1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sco1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sco2 = gtk.ScrolledWindow()
        sco2.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sco2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sco3 = gtk.ScrolledWindow()
        sco3.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sco3.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.view1 = gtk.TextView(self.b_view1)
        self.view2 = gtk.TextView(self.b_view2)
        self.view3 = gtk.TextView(self.b_view3)
        self.view1.modify_font(pango.FontDescription("KacstOne 13"))
        self.view1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornf))
        self.view1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornb))
        self.view2.modify_font(pango.FontDescription("KacstOne 13"))
        self.view2.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornf))
        self.view2.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornb))
        self.view3.modify_font(pango.FontDescription("KacstOne 13"))
        self.view3.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornf))
        self.view3.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornb))
        self.view1.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.view2.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.view3.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        sco1.add_with_viewport(self.view1)
        sco2.add_with_viewport(self.view2)
        self.b_view2.set_text("لا يمكن تحرير معلومات عن المؤلفين حاليا")
        self.view2.set_editable(False)
        sco3.add_with_viewport(self.view3)
        self.noteb.append_page(sco1,gtk.Label("البطاقة"))
        self.noteb.append_page(sco2,gtk.Label("المؤلف"))
        self.noteb.append_page(sco3,gtk.Label("الكتاب"))
        self.savb = gtk.Button("تعديل البيانات")
        self.savb.connect("clicked",self.sav_bitaka)
        tab.attach(self.noteb,6,9,0,4)
        hb.pack_end(self.savb,0,0)
        self.set_border_width(10)
        self.pack_start(hb,0,0)
        self.pack_start(tab,1,1)
        self.pack_start(hb1,0,0)
        self.show_all() 
   
# class نافذة التفضيلات----------------------------------------------------------------------------        
        
class Perference(gtk.Window):
    
    def __init__(self, *a):
        self.build()        
    
    def cos0(self, *args):
        self.aa.set_sensitive(True)
        self.bq1.set_value(self.rt)
        self.bq2.set_color(color = gtk.gdk.Color(th.conf['colorqf']))
        self.bq3.set_color(color = gtk.gdk.Color(th.conf['colorqb']))
        self.bn1.set_font_name(th.conf['fontn'])
        self.bn2.set_color(color = gtk.gdk.Color(th.conf['colornf']))
        self.bn3.set_color(color = gtk.gdk.Color(th.conf['colornb']))
        self.ba1.set_font_name(th.conf['fonta'])
        self.ba2.set_color(color = gtk.gdk.Color(th.conf['coloraf']))
        self.bc1.set_font_name(th.conf['fontc'])
        self.bc2.set_color(color = gtk.gdk.Color(th.conf['colorcf']))
        self.bc3.set_color(color = gtk.gdk.Color(th.conf['colorcb']))
        self.bm2.set_color(color = gtk.gdk.Color(th.conf['colormf']))
        self.bs3.set_color(color = gtk.gdk.Color(th.conf['colorsb']))
    
    def dfo0(self, *args):
        self.aa.set_sensitive(False)
        self.bq1.set_value(28)
        self.bq2.set_color(color = gtk.gdk.Color("#204000"))
        self.bq3.set_color(color = gtk.gdk.Color("#FDFDD7"))
        self.bn1.set_font_name("Simplified Naskh 24")
        self.bn2.set_color(color = gtk.gdk.Color('#0B0C8D'))
        self.bn3.set_color(color = gtk.gdk.Color("#FDFDD7"))
        self.ba1.set_font_name("Simplified Naskh Bold 32")
        self.ba2.set_color(color = gtk.gdk.Color("#860915"))
        self.bc1.set_font_name("KacstOne 15")
        self.bc2.set_color(color = gtk.gdk.Color('#162116'))
        self.bc3.set_color(color = gtk.gdk.Color("#F9F0CF"))
        self.bm2.set_color(color = gtk.gdk.Color("#EC430A"))
        self.bs3.set_color(color = gtk.gdk.Color('#FFFF80'))  
    
    def tak(self, *args):
        if self.cos.get_active():
            th.conf['fontq'] = str(self.bq1.get_value())[:2]
            th.conf['fontn'] = self.bn1.get_font_name()
            th.conf['fonta'] = self.ba1.get_font_name()
            th.conf['fontc'] = self.bc1.get_font_name()
            th.conf['colorqb'] = self.bq3.get_color().to_string()
            th.conf['colornb'] = self.bn3.get_color().to_string()
            th.conf['colorcb'] = self.bc3.get_color().to_string()
            th.conf['colorsb'] = self.bs3.get_color().to_string()
            th.conf['colorqf'] = self.bq2.get_color().to_string()
            th.conf['colornf'] = self.bn2.get_color().to_string()
            th.conf['coloraf'] = self.ba2.get_color().to_string()
            th.conf['colormf'] = self.bm2.get_color().to_string()
            th.conf['colorcf'] = self.bc2.get_color().to_string()
        else: pass
        if self.dfo.get_active():
            th.conf['tr'] = '0'
        else:
            th.conf['tr'] = '1'
        th.conf.save()
        th.apply_font()
        th.font() 
                       
    def build(self,*args):
        gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
        self.set_icon_from_file("icons/Configs-24.png")
        self.set_title("إعداد المظهر")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_modal(True)
        self.set_keep_above(True)
        self.dfo = gtk.RadioButton(None,'افتراضي')
        self.cos = gtk.RadioButton(self.dfo,'مخصص')
        pho = gtk.Button('الخلفية')
        pho.connect('clicked',th.ch_pho)
        self.aa = gtk.Frame('خيارات')
        v1 = gtk.VBox(False,10)
        h1 = gtk.HBox(False,30)
        tab_1 = gtk.Table(3,2,True)
        tab_1.set_row_spacings(4)
        h4 = gtk.HBox(False,30)
        v2 = gtk.VBox(False,5)
        v3 = gtk.VBox(False,5)
        h11 = gtk.HBox(False,5)
        h12 = gtk.HBox(False,5)
        h13 = gtk.HBox(False,5)
        h14 = gtk.HBox(False,5)
        h15 = gtk.HBox(False,5)
        h21 = gtk.HBox(False,5)
        h22 = gtk.HBox(False,5)
        h23 = gtk.HBox(False,5)
        h24 = gtk.HBox(False,5)
        h25 = gtk.HBox(False,5)
        v1.pack_start(h1,0,0)
        v1.pack_start(h4,0,0)
        h4.pack_start(v2,0,0)
        h4.pack_start(v3,0,0)
        v2.pack_start(h11,0,0)
        v2.pack_start(h12,0,0)
        v2.pack_start(h13,0,0)
        v2.pack_start(h14,0,0)
        v2.pack_start(h15,0,0)
        v3.pack_start(h21,0,0)
        v3.pack_start(h22,0,0)
        v3.pack_start(h23,0,0)
        v3.pack_start(h24,0,0)
        v3.pack_start(h25,0,0)
        self.aa.add(v1)
        v1.set_border_width(10)
        f_nss = gtk.Label('نوع خط النصوص')
        f_nss.set_alignment(0,0.5)
        h1.pack_start(tab_1,0,0)
        tab_1.attach(f_nss,0,1,0,1)
        f_tit = gtk.Label('نوع خط العناوين')
        f_tit.set_alignment(0,0.5)
        tab_1.attach(f_tit,0,1,1,2)
        f_ind = gtk.Label('نوع خط الفهارس')
        f_ind.set_alignment(0,0.5)
        tab_1.attach(f_ind,0,1,2,3)
        adj = gtk.Adjustment(1, 1, 72, 1, 5, 0)
        self.bq1 = gtk.SpinButton(adj, 0, 0)
        self.bq1.set_wrap(True)
        self.rt = int(th.conf['fontq'])
        self.bq1.set_value(self.rt)
        self.bq2 = gtk.ColorButton(color = gtk.gdk.Color(th.colorqf))
        self.bq3 = gtk.ColorButton(color = gtk.gdk.Color(th.colorqb))
        self.bn1 = gtk.FontButton(th.fontn)
        self.bn2 = gtk.ColorButton(color = gtk.gdk.Color(th.colornf))
        self.bn3 = gtk.ColorButton(color = gtk.gdk.Color(th.colornb))
        self.ba1 = gtk.FontButton(th.fonta)
        self.ba2 = gtk.ColorButton(color = gtk.gdk.Color(th.coloraf))
        self.bc1 = gtk.FontButton(th.fontc)
        self.bc2 = gtk.ColorButton(color = gtk.gdk.Color(th.colorcf))
        self.bc3 = gtk.ColorButton(color = gtk.gdk.Color(th.colorcb))
        self.bm2 = gtk.ColorButton(color = gtk.gdk.Color(th.colormf))
        self.bs3 = gtk.ColorButton(color = gtk.gdk.Color(th.colorsb))
        bcl = gtk.Button('تطبيق')
        bcl.connect('clicked',self.tak)
        h12.pack_start(self.bq1,0,0)
        f_qrn = gtk.Label('حجم خط المصحف')
        h12.pack_start(f_qrn,0,0)
        h11.pack_start(self.bq2,0,0)
        c_qrn = gtk.Label('لون خط المصحف')
        h11.pack_start(c_qrn,0,0)
        h21.pack_start(self.bq3,0,0)
        tab_1.attach(self.bn1,1,2,0,1)
        h13.pack_start(self.bn2,0,0)
        h23.pack_start(self.bn3,0,0)
        tab_1.attach(self.ba1,1,2,1,2)
        h14.pack_start(self.ba2,0,0)
        tab_1.attach(self.bc1,1,2,2,3)
        h15.pack_start(self.bc2,0,0)
        h24.pack_start(self.bc3,0,0)
        h25.pack_start(self.bs3,0,0)
        h22.pack_start(self.bm2,0,0)
        c_nss = gtk.Label('لون خط النصوص')
        h13.pack_start(c_nss,0,0)
        c_tit = gtk.Label('لون خط العناوين')
        h14.pack_start(c_tit,0,0)
        c_ind = gtk.Label('لون خط الفهارس')
        h15.pack_start(c_ind,0,0)
        b_qrn = gtk.Label('لون خلفية المصحف')
        h21.pack_start(b_qrn,0,0)
        b_nss = gtk.Label('لون خلفية النصوص')
        h23.pack_start(b_nss,0,0)
        b_ind = gtk.Label('لون خلفية الفهارس')
        h24.pack_start(b_ind,0,0)
        b_srh = gtk.Label('لون تظليل البحث')
        h25.pack_start(b_srh,0,0)
        c_mef = gtk.Label('لون الكلمات المميزة')
        h22.pack_start(c_mef,0,0)
        self.dfo.connect('toggled',self.dfo0,'افتراضي')
        self.cos.connect('toggled',self.cos0,'مخصص')
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,30)
        hb1 = gtk.HBox(False,10)
        vb.set_border_width(10)
        hb.pack_start(self.dfo,0,0)
        hb.pack_start(self.cos,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: self.destroy())
        hb1.pack_start(pho,0,0)
        hb1.pack_end(clo,0,0)
        hb1.pack_end(bcl,0,0)
        vb.pack_start(hb,0,0)
        vb.pack_start(self.aa,1,1)
        vb.pack_start(hb1,0,0)
        if th.conf['tr'] == '1':
            self.cos.set_active(True)
        else:
            self.aa.set_sensitive(False)
            self.dfo.set_active(True)
        self.add(vb)
        self.show_all()     
        
# class نافذة البحث--------------------------------------------------------------

class SearchView(gtk.VBox):
    
    def __init__(self,text):
        if not os.path.exists(th.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
        else:
            if len(th.store_s) == 0: th.tree0()
        self.build(text)
        
    def save_list(self,*a):
        nm = self.ent_list.get_text()
        if nm == "":
            dlg("أدخل الاسم أولا.")
        elif nm in os.listdir(th.pathasmaa+'data/lists/'): dlg("يوجد نطاق محفوظ بنفس الاسم !!")
        else:
            self.add_list()
            if len(self.sto_s) == 0: dlg("لا يوجد أي كتاب محدد !!")
            else:
                output = open(th.pathasmaa+"data/lists/"+nm, 'wb')
                cPickle.dump(self.sto_s, output)
                output.close()
                self.ent_list.set_text("")
                a = (False,nm)
                it = self.store_lists.append()
                self.store_lists.set(it,COLUMN_FIXED, a[COLUMN_FIXED], COLUMN_N, a[COLUMN_N]) 
                 
    def add_list(self,*a):
        self.sto_s = []
        w1 = 0
        while w1 in range(len(th.store_s)):
            tg = th.store_s.get_iter((w1,))
            pg = self.kaima11.get_model().iter_n_children(tg)
            w2 = 0
            while w2 in range(pg):
                if th.store_s[(w1,w2)][1] == True:
                    if th.store_s[(w1,w2)][0] not in self.sto_s:
                        self.sto_s.append(th.store_s[(w1,w2)][0])
                w2 += 1
            w1 += 1
            
    def add_list_all(self,*a):
        self.add_list()
        w1 = 0
        while w1 in range(len(self.store_lists)):
            if self.store_lists[w1][0] == True:
                store = cPickle.load(file(th.pathasmaa+"data/lists/"+self.store_lists[w1][1]))
                self.sto_s.extend(store)
            w1 += 1
        if self.fav_books.get_active() == True:
            list_v = os.listdir(th.pathasmaa+'data/favorite/')
            self.sto_s.extend(list_v)
        
    def find1(self,*a):
        self.add_list_all()
        tc = th.ent_sh.get_text()
        self.hr = 'بحث عن : '+tc
        th.hr = self.hr
        txc = ' '.join(tc.split())
        if tc == '':
            dlg('ادخل النص المراد البحث عنه !')
        else :
            if self.qrn.get_active() == False:
                if not os.path.exists(th.pathasmaa+'books/'): dlg('الكتب غير موصولة');return
                if len(self.sto_s) == 0:
                    dlg('لا يوجد أي كتاب محدد !')
                    return
            
            if self.metassila.get_active() == True:
                if self.metatabika.get_active() == True:
                    text = u'"'+' '+txc+' '+'"'
                else:
                    text = u'"'+txc+'"'
            else :
                if self.metatabika.get_active() == True:
                    text = u'"'+' '+txc+' '+'"'
                else:
                    text = u''+txc
            asv = Asmasearch()
            th.notebook.append_page(asv, TabLabel(asv,self.hr))
            th.notebook.set_tab_reorderable(asv,True)
            th.notebook.set_current_page(-1)
            if th.conf['fi'] == '1':
                th.winsearch.hide()
            else:
                self.tas0()
                th.winsearch.destroy()
            n = th.notebook.get_current_page()
            th.notebook.get_nth_page(n).sh_store = []
            th.notebook.show_all()
            th.event_box1.hide_all()
            ui = th.notebook.get_nth_page(n)
            ui.cnm.set_text(self.hr)
            th.do_win()
            ui.find(text,self.sto_s,self.metassila,self.ihdaha,self.bilharakat,self.qrn,self.nss,self.ans)
            try:
                if len(th.list_terms) == 50: th.list_terms.pop(0)
                if tc in th.list_terms: th.list_terms.remove(tc)
                th.list_terms.append(tc)
                output = open(th.pathasmaa+'data/last-terms.pkl', 'wb')
                cPickle.dump(th.list_terms, output)
                output.close()
            except: pass
            
    def cher1(self,*args):
        self.kaima11.collapse_all()
        (model1, i1) = self.kaima11.get_selection().get_selected()
        tx = self.ent_ch.get_text()
        if tx != '':
            k1 = 0
            while k1 in range(len(th.store_s)):
                q11 = th.store_s.get_iter((k1,))
                hj = th.store_s.iter_n_children(q11)
                k2 = 0
                while k2 in range(hj):
                    f = (k1,k2)
                    i1 = th.store_s.get_iter(f)
                    if tx in model1.get_value(i1,0):
                        self.kaima11.expand_to_path(f)
                        self.kaima11.scroll_to_cell(f)
                        self.kaima11.get_selection().select_iter(i1)
                        break
                    else :
                        k2 += 1
                if tx in model1.get_value(i1,0):
                    break
                k1 += 1
                
    def cher0(self,*args): 
        (model1, i1) = self.kaima11.get_selection().get_selected()
        tx = self.ent_ch.get_text()
        if tx != '':
            if not i1:
                self.cher1(self.ent_ch)
            elif i1 :
                h1 = th.store_s.get_path(i1)
                k11 = h1[0]
                k21 = h1[1]+1
                while k11 in range(len(th.store_s)) :
                    q12 = th.store_s.get_iter((k11,))
                    hj1 = th.store_s.iter_n_children(q12)
                    while k21 in range(hj1):
                        f = (k11,k21)
                        i11 = th.store_s.get_iter(f)
                        if tx in model1.get_value(i11,0):
                            self.kaima11.collapse_all()
                            self.kaima11.expand_to_path(f)
                            self.kaima11.scroll_to_cell(f)
                            self.kaima11.get_selection().select_iter(i11)
                            break
                        k21 += 1
                    if k21 <= (hj1-1):
                        break
                    else:
                        k21 = 0
                        k11 += 1  
                        
    def ok_list(self, cell, path, model):
            it = model.get_iter((int(path),))
            fixed = model.get_value(it, COLUMN_FIXED)
            fixed = not fixed
            model.set(it, COLUMN_FIXED, fixed)  
                             
    def fixed_toggled(self, cell, path, model):
        it = model.get_iter((path),)
        fixed = model.get_value(it, 1)
        if model.iter_has_child(it):
            pp = self.kaima11.get_model().iter_n_children(it)
            d1 = 0
            while d1 in range(pp):
                iter1 = model.get_iter((int(path),d1),)
                fixed1 = model.get_value(iter1, 1)
                fixed1 = not fixed
                model.set(iter1, 1, fixed1)
                d1 += 1
        fixed = not fixed
        model.set(it, 1, fixed)
        
    def t_all(self,*args):
        k1 = 0
        while k1 in range(len(th.store_s)):
            q11 = th.store_s.get_iter((k1,))
            self.kaima11.get_selection().select_iter(q11)
            (mod1, q11) = self.kaima11.get_selection().get_selected()
            hj = th.store_s.iter_n_children(q11)
            k2 = 0
            while k2 in range(hj):
                f = (k1,k2)
                i1 = th.store_s.get_iter(f)
                self.kaima11.get_selection().select_iter(i1)
                (mod11, i1) = self.kaima11.get_selection().get_selected()
                if self.all_bk.get_active() == True:
                    mod11[f][1] = True
                else: mod11[f][1] = False
                k2 += 1
            if self.all_bk.get_active() == True:
                mod1[(k1,)][1] = True
            else: mod1[(k1,)][1] = False
            k1 += 1
            
    def fgh(self,*args):
        (mod11, q1) = self.kaima11.get_selection().get_selected()
        f10 = mod11.get_path(q1)
        if mod11.iter_has_child(q1):
            pp = self.kaima11.get_model().iter_n_children(q1)
            d1 = 0
            while d1 in range(pp):
                mod11[(f10[0],d1)][1] = not mod11[f10][1] 
                d1 += 1
        mod11[f10][1] = not mod11[f10][1]
    
    def tas0(self,*a):
        self.all_bk.set_active(True)
        self.all_bk.set_active(False)
        self.fav_books.set_active(False)
        for w1 in range(len(self.store_lists)):
            if self.store_lists[w1][0] == True: self.store_lists[w1][0] = False
    def tah(self, *args):
        self.store_tah.clear()
        (model1, i1) = self.treeview.get_selection().get_selected()
        r1 = model1.get_value(i1,1)
        w = gtk.Window()
        w.set_modal(True)
        w.set_title('كتب النطاق المحدد')
        w.set_position(gtk.WIN_POS_CENTER)
        w.resize(350,400)
        vb = gtk.VBox(False,10)
        hb = gtk.HBox(False,10)
        vb.set_border_width(10)
        scof1 = gtk.ScrolledWindow()
        scof1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scof1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        kf1 = gtk.TreeView()
        list_v = cPickle.load(file(th.pathasmaa+"data/lists/"+r1))
        for v in range(len(list_v)):
            self.store_tah.append([list_v[v]])
        saf1 = gtk.TreeViewColumn('الكتب',gtk.CellRendererText(),text = 0)
        kf1.append_column(saf1)
        kf1.set_model(self.store_tah)
        kf1.modify_font(pango.FontDescription(th.fontc))
        kf1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcf))
        kf1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcb))
        kf1.set_headers_visible(False)
        scof1.add(kf1)
        br1 = gtk.Button("حذف")
        def rm(widget, *args):
            global res_dlg
            (model1, i1) = kf1.get_selection().get_selected()
            if i1 :
                dlg_res("هل ترغب في حذف الكتاب المحدد من النطاق ؟")
                if res_dlg == False: return
                else:
                    r1 = model1.get_value(i1,0)
                    list_v.remove(r1)
                    self.store_tah.remove(i1)
                    res_dlg = False
        br1.connect('clicked',rm)
        bo = gtk.Button("حفظ")
        def ol(widget, *args):
            output = open(th.pathasmaa+"data/lists/"+r1, 'wb')
            cPickle.dump(list_v, output)
            output.close()
            w.destroy()
        bo.connect('clicked',ol)
        vb.pack_start(scof1,1,1)
        hb.pack_start(br1,0,0)
        clo = gtk.Button("إغلاق")
        clo.connect('clicked',lambda *a: w.destroy())
        hb.pack_end(clo,0,0)
        hb.pack_end(bo,0,0)
        vb.pack_start(hb,0,0)
        w.add(vb)
        w.show_all()
                 
    def build(self,text):
        gtk.VBox.__init__(self,False,10)
        tab_h = gtk.Table(10,10,True)
        tab_h.set_col_spacings(10)
        tab_1 = gtk.Table(3,2,True)
        tab_2 = gtk.Table(4,2,True)
        tab_1.set_border_width(10)
        tab_2.set_border_width(10)
        hb1 = gtk.HBox(False,10)
        hb2 = gtk.HBox(False,10)
        hb3 = gtk.HBox(False,10)
        vb11 = gtk.VBox(False,10)
        vb22 = gtk.VBox(False,5)
        vb33 = gtk.VBox(False,5)
        hb22 = gtk.HBox(False,10)
        hb33 = gtk.HBox(False,5)
        hb44 = gtk.HBox(False,5)
        self.pack_start(hb1,1,1)
        vb11.pack_start(gtk.Label('     '),0,0)
        self.pack_start(hb3,0,0)
        hb1.pack_start(vb11,0,0)
        hb1.pack_start(tab_h,1,1)
        tab_h.attach(vb22,0,6,0,10)
        tab_h.attach(vb33,6,10,0,10)
        vb22.pack_start(hb22,0,0)
        vb33.pack_start(hb33,0,0)
        if th.conf['fi'] == '1':
            th.n_s = 1
        else: th.n_s = 0
        scok1 = gtk.ScrolledWindow()
        scok1.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scok1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC) 
        scoh = gtk.ScrolledWindow()
        scoh.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scoh.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC) 
        self.kaima11 = gtk.TreeView() 
        self.kaima11.set_model(th.store_s)
        scok1.add(self.kaima11)
        rend = gtk.CellRendererText()
        rend1 = gtk.CellRendererToggle()
        rend1.set_property('activatable', True)
        rend1.connect('toggled', self.fixed_toggled, th.store_s)
        column0 = gtk.TreeViewColumn("اختيار", rend1)
        column1 = gtk.TreeViewColumn("القسم", rend, text = 0 )
        column0.add_attribute( rend1, "active", 1)
        self.kaima11.connect( "row-activated", self.fgh)
        self.kaima11.append_column( column0 )
        self.kaima11.append_column( column1 )
        self.nss = gtk.RadioButton(None,'في النصوص')
        tab_1.attach(self.nss,0,2,0,1)
        self.ans = gtk.RadioButton(self.nss,'في العناوين')
        tab_1.attach(self.ans,0,2,1,2)
        self.qrn = gtk.RadioButton(self.ans,'في القرآن')
        tab_1.attach(self.qrn,0,2,2,3)
        def nss0(widget,*args):
            tab_h.set_sensitive(True)
        self.nss.connect('toggled',nss0,'في القرآن')
        def ans0(widget,*args):
            tab_h.set_sensitive(True)
        self.ans.connect('toggled',ans0,'في القرآن')
        def qrn0(widget,*args):
            tab_h.set_sensitive(False)
        self.qrn.connect('toggled',qrn0,'في القرآن')
        vb22.pack_start(scok1,1,1)
        vb22.pack_start(hb2,0,0)
        th.ent_sh.set_text(text)
        ees = gtk.Frame('خيارات البحث')
        ees.add(tab_2)
        ess = gtk.Frame('مجالات البحث')
        vb11.pack_start(ess,0,0)
        vb11.pack_start(ees,0,0)
        ess.add(tab_1)
        self.all_bk = gtk.CheckButton('جميع الكتب')
        hb2.pack_start(self.all_bk,0,0)
        self.fav_books = gtk.CheckButton('الكتب المفضلة')
        hb2.pack_start(self.fav_books,0,0)
        self.all_bk.connect('toggled',self.t_all)
        self.metatabika = gtk.CheckButton('متطابقة')
        tab_2.attach(self.metatabika,0,2,0,1)
        self.metassila = gtk.CheckButton('عبارة متصلة')
        tab_2.attach(self.metassila,0,2,1,2)
        self.ihdaha = gtk.CheckButton('إحداها (أو)')
        tab_2.attach(self.ihdaha,0,2,2,3)
        self.bilharakat = gtk.CheckButton('بالحركات')
        tab_2.attach(self.bilharakat,0,2,3,4)
        self.ent_ch = gtk.Entry()
        ch = gtk.ToolButton(gtk.STOCK_FIND)
        ch.set_tooltip_text("بحث عن كتاب")
        ch.connect('clicked',self.cher0)
        self.ent_ch.connect("key-release-event", self.cher1)
        ig0 = gtk.Image()
        ig0.set_from_file('icons/Search-Books-24.png')
        cher_g = gtk.Button("البحث")
        cher_g.set_image(ig0)
        hb3.pack_start(cher_g,0,0)
        hb3.pack_start(th.ent_sh,1,1)
        cher_g.connect('clicked',self.find1)
        th.ent_sh.connect("activate", self.find1)   
        tas = gtk.Button('تصفير')
        tas.connect('clicked',self.tas0)
        tas.set_tooltip_text("صفّر جميع الكتب من التعليم")
        col = gtk.Button('ضمّ')
        def col0(widget,*a):
            self.kaima11.collapse_all()
        col.connect('clicked',col0)
        hb22.pack_start(col,0,0)
        hb22.pack_start(tas,0,0)
        hb22.pack_end(self.ent_ch,0,0)
        hb22.pack_end(ch,0,0)
        scok4 = gtk.ScrolledWindow()
        scok4.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.store_lists = gtk.ListStore(gobject.TYPE_BOOLEAN,gobject.TYPE_STRING)
        scok4.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        for a in os.listdir(th.pathasmaa+'data/lists/'):
            a = (False,a)
            it = self.store_lists.append()
            self.store_lists.set(it,COLUMN_FIXED, a[COLUMN_FIXED], COLUMN_N, a[COLUMN_N])
        self.treeview = gtk.TreeView(self.store_lists)
        self.treeview.set_rules_hint(True)
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.ok_list, self.store_lists)
        column1 = gtk.TreeViewColumn('o', renderer, active = COLUMN_FIXED)
        column1.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column1.set_fixed_width(25)
        self.treeview.append_column(column1)
        column2 = gtk.TreeViewColumn('النطاق', gtk.CellRendererText(),text = COLUMN_N)
        column2.set_sort_column_id(COLUMN_N)
        self.treeview.append_column(column2)
        scok4.add(self.treeview)
        sav_list = gtk.ToolButton(gtk.STOCK_SAVE)
        sav_list.set_tooltip_text("حفظ نطاق البحث المحدد حالياً")
        sav_list.connect('clicked',self.save_list)
        hb44.pack_start(sav_list,0,0)
        self.ent_list = gtk.Entry()
        hb44.pack_start(self.ent_list,0,0)
        vb33.pack_start(scok4,1,1)
        vb33.pack_start(hb44,0,0)
        be = gtk.Button("تحرير")
        self.store_tah = gtk.ListStore(str)
        be.connect('clicked',self.tah)
        br = gtk.Button("حذف")
        def rm(widget, *args):
            global res_dlg
            dlg_res("هل ترغب في حذف ال نطاق المحدد ؟")
            if res_dlg == False: return
            else:
                (model1, i1) = self.treeview.get_selection().get_selected()
                r1 = model1.get_value(i1,1)
                os.remove(th.pathasmaa+'data/lists/'+r1)
                self.store_lists.remove(i1)
                res_dlg = False
        br.connect('clicked',rm)
        bc = gtk.Button("مسح")
        def cl(widget, *args):
            global res_dlg
            dlg_res("هل ترغب في حذف جميع نطاقات البحث ؟")
            if res_dlg == False: return
            else:
                list_n = os.listdir(th.pathasmaa+'data/lists/')
                for v in range(len(list_n)):
                    r1 = list_n[v]
                    os.remove(th.pathasmaa+'data/lists/'+r1)
                self.store_lists.clear()
                res_dlg = False
        bc.connect('clicked',cl)
        hb33.pack_end(bc,0,0)
        hb33.pack_end(br,0,0)
        hb33.pack_end(be,0,0)
        tab_h.show_all()
        self.show_all()
        self.set_focus_child(self.ent_ch)
        
# class نافذة قائمة الكتب-----------------------------------------------------------------------

class WinBooks(gtk.Table):
    
    def __init__(self,*a):
        self.ico = "icons/Books-16.png"
        self.cnm = gtk.Label()
        self.build()
   
    def cherch(self,*a):
        self.tree_k.collapse_all()
        (model1, i1) = self.tree_k.get_selection().get_selected()
        tx = self.ent_search.get_text()
        if tx != '':
            k1 = 0
            while k1 in range(len(th.store_k)):
                q11 = th.store_k.get_iter((k1,))
                hj = th.store_k.iter_n_children(q11)
                k2 = 0
                while k2 in range(hj):
                    f = (k1,k2)
                    i1 = th.store_k.get_iter(f)
                    if tx in model1.get_value(i1,0):
                        self.tree_k.expand_to_path(f)
                        self.tree_k.scroll_to_cell(f)
                        self.tree_k.get_selection().select_iter(i1)
                        break
                    else :
                        k2 += 1
                if tx in model1.get_value(i1,0):
                    break
                k1 += 1
    def cherch0(self,*a): 
        (model1, i1) = self.tree_k.get_selection().get_selected()
        tx = self.ent_search.get_text()
        if tx != '':
            if not i1:
                self.cherch(self.ent_search)
            elif i1 :
                h1 = th.store_k.get_path(i1)
                k11 = h1[0]
                k21 = h1[1]+1
                while k11 in range(len(th.store_k)) :
                    q12 = th.store_k.get_iter((k11,))
                    hj1 = th.store_k.iter_n_children(q12)
                    while k21 in range(hj1):
                        f = (k11,k21)
                        i11 = th.store_k.get_iter(f)
                        if tx in model1.get_value(i11,0):
                            self.tree_k.collapse_all()
                            self.tree_k.expand_to_path(f)
                            self.tree_k.scroll_to_cell(f)
                            self.tree_k.get_selection().select_iter(i11)
                            break
                        k21 += 1
                    if k21 <= (hj1-1):
                        break
                    else:
                        k21 = 0
                        k11 += 1  
    
    def wink(self,*a):
        self.ka1 = gtk.Window()
        self.ka1.set_icon_from_file("icons/Books-24.png")
        self.ka1.resize(450,600)
        def close_win0(widget,*a):
            self.ka1.destroy()
            WinBooks("قائمة الكتب").destroy()
        self.ka1.connect('destroy',close_win0)
        self.ka1.set_title("الكتب")
        self.ka1.set_position(gtk.WIN_POS_CENTER)
        self.ka1.set_border_width(10)
        self.ka1.set_modal(True) 
        self.ka1.set_keep_above(True)
        self.ka1.add(self) 
        self.ka1.show()                           
# a اختيار كتاب-------------------------------------------------------------
    
    def btk(self,r):
        r = str(r)
        th.hr = str(r)
        fd = th.pathasmaa+'books/'+r+'.asm'
        th.con = sqlite3.connect(fd,isolation_level = None)
        cur = th.con.cursor()
        cur.execute('select * from main')
        read = cur.fetchall()
        self.card_k = read[0][5]
        self.text_inf_b.set_text(str(self.card_k))
        
    def ok_k1(self,*args):
        t_selection = self.tree_k.get_selection()
        (model, i) = t_selection.get_selected()
        if i:
            (p,c) = self.tree_k.get_cursor()
            if len(p) == 2:
                r = model.get(i,0)[0]
                self.btk(r)
            else:
                pass   
                 
    def ok_k(self,*args):
        t_selection = self.tree_k.get_selection()
        (model, i) = t_selection.get_selected()
        self.sdf = th.store_k.get_path(i)
        self.tx = self.ent_search.get_text()
        if i:
            (p,c) = self.tree_k.get_cursor()
            if len(p) == 2:
                r = model.get(i,0)[0]
                r = str(r)
                th.hr = str(r)
                fd = th.pathasmaa+'books/'+r+'.asm'
                fd0 = th.pathasmaa+'data/book.asmaa'
                self.c = sqlite3.connect(fd0,isolation_level = None)
                cr = self.c.cursor()
                cr.execute('select fav from books where bk = "'+th.hr+'"')
                rd = cr.fetchall()
                try: ri = int(rd[0][0])
                except: ri = 1
                if th.conf['ka'] == '1': self.destroy()
                else: self.ka1.destroy()
                th.open_bk(fd, ri,th.hr)
                th.list_p = []
                th.list_p.append(p)
                th.list_p.append(self.tx)
                th.list_p.append(self.card_k)
            else:
                if self.tree_k.row_expanded(p[0]):
                    self.tree_k.collapse_row(p[0])
                else: self.tree_k.expand_row(p[0],False) 
    def show1(self,*a):
        if th.conf['ka'] == '0':
            if th.conf['lb'] == '1':
                self.last.set_active(True)
                self.scok5.hide_all()
                self.scok4.show_all()
            else:
                self.ifo.set_active(True)
                self.scok4.hide_all()
                self.scok5.show_all()
        elif th.conf['ka'] == '1':
            self.show_all()
            self.ifo.hide()
            self.last.hide() 
                         
    def build(self,*args):
        gtk.Table.__init__(self,8,5,True)
        if os.path.exists(th.pathasmaa+'data/last-books.pkl') : th.list_book = cPickle.load(file(th.pathasmaa+'data/last-books.pkl'))
        else: th.list_book = []
        self.set_row_spacings(5)        
        self.tree_k = gtk.TreeView()
        self.tree_k.props.has_tooltip = True
        self.tree_k.connect("query-tooltip", th.tooltip_toc,0)
        cells = []
        cols = []
        r = gtk.CellRendererPixbuf()
        cells.append(gtk.CellRendererText()) 
        cols.append(gtk.TreeViewColumn('المكتبة'))
        cols[-1].pack_start(r,False)
        cols[-1].pack_start(cells[-1],True)
        cols[-1].add_attribute(cells[-1], 'text', 0)
        cols[-1].set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        cols[-1].set_expand(True)
        for i in cols: 
            self.tree_k.insert_column(i, -1)
        r.set_property("pixbuf-expander-closed",gtk.gdk.pixbuf_new_from_file('icons/Books-24.png'))
        r.set_property("pixbuf-expander-open",gtk.gdk.pixbuf_new_from_file('icons/Books-24.png'))
        r.set_property("pixbuf", gtk.gdk.pixbuf_new_from_file('icons/Book-24.png')) 
        self.tree_k.set_model(th.store_k)
        self.tree_k.set_headers_visible(False)
        self.tree_k.modify_font(pango.FontDescription(th.fontc))
        self.tree_k.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcf))
        self.tree_k.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcb))
        self.tree_k.set_show_expanders(True)
        self.ent_search = gtk.Entry()
        cher = gtk.ToolButton(gtk.STOCK_FIND) 
        cher.connect('clicked',self.cherch0)
        self.ent_search.connect("key-release-event", self.cherch) 
        self.tree_k.connect("row-activated", self.ok_k)
        self.tree_k.connect("cursor-changed", self.ok_k1)
        scok3 = gtk.ScrolledWindow()
        scok3.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scok3.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC) 
        scok3.add(self.tree_k)
        self.attach(scok3,0,5,0,5)
        hb1 = gtk.HBox(False,10)
        vb1 = gtk.VBox(False,5)
        hb2 = gtk.HBox(False,10)
        hb3 = gtk.HBox(False,10)
        col = gtk.Button('ضمّ')
        def col0(widget,*a):
            self.tree_k.collapse_all()
            self.tree_k.scroll_to_cell((0,0))
            th.list_p = []
        col.connect('clicked',col0)
        vb1.pack_start(hb1,0,0)
        hb1.pack_start(col,0,0)
        hb1.pack_start(cher,0,0)
        hb1.pack_start(self.ent_search,0,0)
        self.text_inf = gtk.TextView()
        self.text_inf.modify_font(pango.FontDescription("KacstOne 13"))
        self.text_inf.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornf))
        self.text_inf.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colornb))
        self.text_inf.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.text_inf.set_right_margin(20)
        self.text_inf_b = gtk.TextBuffer()
        self.text_inf.set_buffer(self.text_inf_b)
        self.scok4 = gtk.ScrolledWindow()
        self.scok4.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.scok4.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scok5 = gtk.ScrolledWindow()
        self.scok5.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.scok5.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        kl1 = gtk.TreeView()
        kl1.set_rules_hint(True)
        saf1 = gtk.TreeViewColumn('آخر الكتب',gtk.CellRendererText(),text = 0)
        kl1.append_column(saf1)
        kl1.set_headers_visible(False)
        self.store_last = gtk.ListStore(str)
        for a in th.list_book: self.store_last.prepend([a])
        kl1.set_model(self.store_last)
        kl1.modify_font(pango.FontDescription("KacstOne 12"))
        kl1.modify_text(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcf))
        kl1.modify_base(gtk.STATE_NORMAL,color = gtk.gdk.Color(th.colorcb))
        def ok_last(wedget,*a):
            if not os.path.exists(th.pathasmaa+'books/'): return
            t_selec = kl1.get_selection()
            (model, i) = t_selec.get_selected()
            if i:
                r = model.get(i,0)[0]
                th.hr = str(r)
                fd = th.pathasmaa+'books/'+r+'.asm'
                fd0 = th.pathasmaa+'data/book.asmaa'
                self.c = sqlite3.connect(fd0,isolation_level = None)
                cr = self.c.cursor()
                cr.execute('select fav from books where bk = "'+th.hr+'"')
                rd = cr.fetchall()
                try: ri = int(rd[0][0])
                except: ri = 1
                if th.conf['ka'] == '1': self.destroy()
                else: th.ka1.destroy()
                th.open_bk(fd, ri,th.hr)
        kl1.connect("row-activated", ok_last)
        def ok_t(widget,*args):
            t_sel = kl1.get_selection()
            (model, i) = t_sel.get_selected()
            if i:
                r = model.get(i,0)[0]
                self.btk(r)
        kl1.connect("cursor-changed", ok_t)
        def ifo0(wedget,*a):
            self.scok4.hide_all()
            self.scok5.show_all()
            th.conf['lb'] = '0'
            th.conf.save()
        def last0(wedget,*a):
            self.scok5.hide_all()
            self.scok4.show_all()
            th.conf['lb'] = '1'
            th.conf.save()
        self.scok4.add(kl1)
        self.scok5.add(self.text_inf)
        hb3.pack_start(self.scok4,1,1)
        hb3.pack_start(self.scok5,1,1)
        vb1.pack_start(hb3,1,1)
        vb1.pack_start(hb2,0,0)
        clr = gtk.Button('مسح')
        def clr0(wedget,*a):
            global res_dlg
            dlg_res("هل تريد مسح قائمة الكتب الأخيرة ؟")
            if res_dlg == False: return
            else:
                os.remove(th.pathasmaa+'data/last-books.pkl')
                self.store_last.clear()
                th.list_book = []
                res_dlg = False
        clr.connect('clicked',clr0)
        clr.set_tooltip_text("مسح قائمة الكتب الأخيرة")
        hb2.pack_start(clr,0,0)
        self.clo = gtk.Button("إغلاق")
        def close_win(widget,*a):
            if th.conf['ka'] == '0': 
                self.ka1.destroy()
                self.destroy()
            elif th.conf['ka'] == '1': TabLabel(self,"قائمة الكتب").close_tab(self)
        self.clo.connect('clicked',close_win)
        hb2.pack_end(self.clo,0,0)
        self.ifo = gtk.RadioButton(None,'بطاقة كتاب')
        self.ifo.connect('toggled',ifo0,'بطاقة كتاب')
        self.last = gtk.RadioButton(self.ifo,'الكتب الأخيرة')
        self.last.connect('toggled',last0,'الكتب الأخيرة')
        hb2.pack_start(self.last,0,0)
        hb2.pack_start(self.ifo,0,0)
        self.attach(vb1,0,5,5,8)
        if th.list_p != []:
            self.tree_k.expand_to_path(th.list_p[0])
            if th.list_p[0][1] == 0: self.tree_k.scroll_to_cell((th.list_p[0][0],))
            else: self.tree_k.scroll_to_cell((th.list_p[0][0],th.list_p[0][1]-1))
            i122 = th.store_k.get_iter(th.list_p[0])
            self.tree_k.get_selection().select_iter(i122)
            self.ent_search.set_text(th.list_p[1])
            self.text_inf_b.set_text(th.list_p[2])
        else: pass
        self.show_all()
        self.show1()

# class مركز التحكم----------------------------------------------------------------------------        
        
class Modification(gtk.VBox):
    
    def __init__(self, *a):
        self.ico = 'icons/center-16.png'
        self.cnm = gtk.Label()
        self.build()  
        
    def build(self):
        gtk.VBox.__init__(self, False,10)
        self.hb1 = gtk.HBox(False,20)
        tab_1 = gtk.Table(1,3,True)
        self.kai = gtk.RadioButton(None,'قائمة الكتب')
        tab_1.attach(self.kai,0,1,0,1)
        self.bah = gtk.RadioButton(self.kai,'نافذة البحث')
        tab_1.attach(self.bah,1,2,0,1)
        self.non = gtk.RadioButton(self.bah,'لا شيء')
        tab_1.attach(self.non,2,3,0,1)
        def nss0(widget,*args):
            th.conf['ev'] = "0"
            th.conf.save()
        self.kai.connect('toggled',nss0)
        def ans0(widget,*args):
            th.conf['ev'] = "1"
            th.conf.save()
        self.bah.connect('toggled',ans0)
        def qrn0(widget,*args):
            th.conf['ev'] = "2"
            th.conf.save()
        self.non.connect('toggled',qrn0) 
        ees = gtk.Frame(' عند النقر على الخلفية يظهر : ')
        self.hb1.pack_start(ees,0,0)
        ees.add(tab_1) 
        if th.conf['ev'] == "0":
            self.kai.set_active(True)
        elif th.conf['ev'] == "1":
            self.bah.set_active(True)
        else:
            self.non.set_active(True)
        tab_2 = gtk.Table(1,2,True)
        self.lis = gtk.RadioButton(None,'لسان جديد')
        tab_2.attach(self.lis,0,1,0,1)
        self.naf = gtk.RadioButton(self.lis,'نافذة مستقلة')
        tab_2.attach(self.naf,1,2,0,1)
        def lis0(widget,*args):
            th.conf['ka'] = "1"
            th.conf.save()
        self.lis.connect('toggled',lis0)
        def naf0(widget,*args):
            th.conf['ka'] = "0"
            th.conf.save()
        self.naf.connect('toggled',naf0) 
        efs = gtk.Frame(' فتح قائمة الكتب في : ')
        self.hb1.pack_start(efs,0,0)
        efs.add(tab_2) 
        if th.conf['ka'] == "0":
            self.naf.set_active(True)
        elif th.conf['ka'] == "1":
            self.lis.set_active(True)
        else:
            self.non.set_active(True)
        self.hb2 = gtk.HBox(False,20)
        tab_3 = gtk.Table(1,2,True)
        self.nw = gtk.RadioButton(None,'النافذة السابقة')
        tab_3.attach(self.nw,0,1,0,1)
        self.lg = gtk.RadioButton(self.nw,'نافذة جديدة')
        tab_3.attach(self.lg,1,2,0,1)
        def nw0(widget,*args):
            th.conf['fi'] = "1"
            th.conf.save()
        self.nw.connect('toggled',nw0)
        def lg0(widget,*args):
            th.conf['fi'] = "0"
            th.conf.save()
        self.lg.connect('toggled',lg0) 
        efs = gtk.Frame(' أظهر نافذة البحث في نفس الجلسة في : ')
        self.hb2.pack_start(efs,0,0)
        efs.add(tab_3) 
        if th.conf['fi'] == "0":
            self.lg.set_active(True)
        elif th.conf['fi'] == "1":
            self.nw.set_active(True)
        else:
            self.non.set_active(True)
        self.hb3 = gtk.HBox(False,0)
        tab_4 = gtk.Table(1,5,True)
        self.ist = gtk.RadioButton(None,'استبدله')
        tab_4.attach(self.ist,0,1,0,1)
        self.isa = gtk.RadioButton(self.ist,'غير الاسم')
        tab_4.attach(self.isa,1,2,0,1)
        self.isf = gtk.RadioButton(self.isa,'الاسم فقط')
        tab_4.attach(self.isf,2,3,0,1)
        self.tak = gtk.RadioButton(self.isf,'تخطي')
        tab_4.attach(self.tak,3,4,0,1)
        self.isl = gtk.RadioButton(self.tak,'اسألني')
        tab_4.attach(self.isl,4,5,0,1)
        def ist0(widget,*args):
            th.conf['ad'] = "0"
            th.conf.save()
        self.ist.connect('toggled',ist0)
        def isa0(widget,*args):
            th.conf['ad'] = "1"
            th.conf.save()
        self.isa.connect('toggled',isa0)
        def isf0(widget,*args):
            th.conf['ad'] = "2"
            th.conf.save()
        self.isf.connect('toggled',isf0)
        def tak0(widget,*args):
            th.conf['ad'] = "3"
            th.conf.save()
        self.tak.connect('toggled',tak0)
        def isl0(widget,*args):
            th.conf['ad'] = "4"
            th.conf.save()
        self.isl.connect('toggled',isl0)
        sfs = gtk.Frame(' عند استيراد كتاب موجود فعلا : ')
        self.hb3.pack_start(sfs,0,0)
        sfs.add(tab_4) 
        if th.conf['ad'] == "0":
            self.ist.set_active(True)
        if th.conf['ad'] == "1":
            self.isa.set_active(True)
        if th.conf['ad'] == "2":
            self.isf.set_active(True)
        if th.conf['ad'] == "3":
            self.tak.set_active(True)
        if th.conf['ad'] == "4":
            self.isl.set_active(True)
        self.pack_start(self.hb1,0,0)
        self.pack_start(self.hb2,0,0)
        self.pack_start(self.hb3,0,0)
        self.set_border_width(10)
        tab_1.set_border_width(10)
        tab_2.set_border_width(10)
        tab_1.set_col_spacings(10)
        tab_2.set_col_spacings(10)
        tab_3.set_border_width(10)
        tab_3.set_col_spacings(10)
        tab_4.set_border_width(10)
        tab_4.set_col_spacings(10)
        self.show_all()   
         
# class إضافة كتاب--------------------------------------------------------------

class AddBooks(gtk.Window):
    
    def add_cb(self, *args):
        self.progress.set_fraction(0.0)
        self.progress.set_text('')
        add_dlg = gtk.FileChooserDialog("اختر ملفات الشاملة",
                                      buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        cl_button = add_dlg.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        def cll(widget,*a):
            for i in add_dlg.get_filenames():
                self.ls.append([i,os.path.basename(i)])
        cl_button.connect('clicked',cll)
        ff = gtk.FileFilter()
        ff.set_name('جميع الملفات المدعومة')
        ff.add_pattern('*.[Tt][Hh]')
        ff.add_pattern('*.[Bb][Oo][Kk]')
        ff.add_pattern('*.[Aa][Ss][Mm]')
        add_dlg.add_filter(ff)
        ff = gtk.FileFilter()
        ff.set_name('ملفات الشاملة (bok)')
        ff.add_pattern('*.[Bb][Oo][Kk]')
        add_dlg.add_filter(ff)
        ff = gtk.FileFilter()
        ff.set_name('ملفات ثواب2 (th)')
        ff.add_pattern('*.[Tt][Hh]')
        add_dlg.add_filter(ff)
        ff = gtk.FileFilter()
        ff.set_name('ملفات أسماء (asm)')
        ff.add_pattern('*.[Aa][Ss][Mm]')
        add_dlg.add_filter(ff)
        add_dlg.set_select_multiple(True)
        add_dlg.run()
        add_dlg.destroy()
    
    def istbdal0(self,*a):
        try: self.dialog.destroy()
        except: pass
        self.export(self.fd2)
        self.s += 1
        
    def ism_akher0(self,*a):
        try: 
            ggg = u""+self.entry.get_text()
            if ggg == self.fd1 :
                ggg = self.fd1 + '1'
        except: ggg = self.fd1 + '1' 
        fd2 = th.pathasmaa+'books/'+ggg+'.asm'
        try: self.dialog.destroy()
        except: pass
        self.export(fd2)
        th.cur1.execute('INSERT INTO books VALUES ("'+ggg+'","'+self.fw1+'",0)')
        th.con.commit()
        self.s += 1
            
    def ism_fakat0(self,*a):
        try: self.dialog.destroy()
        except: pass
        th.cur1.execute('SELECT bk FROM books where bk = "'+self.fd1+'" and val = "'+self.fw1+'"')
        fe8 = th.cur1.fetchall()
        if len(fe8) == 0:
            th.cur1.execute('INSERT INTO books VALUES ("'+self.fd1+'","'+self.fw1+'",0)')
            th.con.commit()
        self.s += 1
            
    def takhati0(self,*a):
        try: self.dialog.destroy()
        except: pass
        self.s += 1 
        
    def export(self,fd2):
        if os.path.basename(self.ext)[-4:]==".asm":
            os.system('cp "'+self.ext+'" "'+th.pathasmaa+'"books')
        else: self.db.export(fd2)
        
    def start(self, *args):
        l, ls_p = self.lsv.get_selection().get_selected_rows()
        if len(l) == 0: return
        gf = self.chajara.get_active_text()
        if gf == None:
            dlg("اختر القسم المراد ضم الكتب إليه")
        else:
            self.progress.set_fraction(0.0)
            self.b_cancel.set_sensitive(True)
            self.b_clear.set_sensitive(False)
            self.b_convert.set_sensitive(False)
            self.b_remove.set_sensitive(False)
            self.b_add.set_sensitive(False)
            th.cur1.execute('SELECT val FROM groups where grp = "'+gf+'"')
            fe2 = th.cur1.fetchall()
            self.fw1 = str(fe2[0][0])
            fd = u""
            r = len(l)
            self.s = 0
            f = 0
            while (self.s < r):
                self.progress.pulse()
                while (gtk.events_pending()): gtk.main_iteration()
                self.progress.set_text(str(self.s)+"""/"""+str(r))
                fd = u""
                fd += l[f][0]
                self.ext = fd
                try:   
                    fd0 = os.path.basename(fd)
                    self.db = self.data(fd,-1)
                    self.fd1 = self.db.bk
                    self.fd2 = th.pathasmaa+'books/'+self.fd1+'.asm'
                    if os.path.exists(self.fd2):
                        if th.conf['ad'] == '4':
                            self.dialog = gtk.Dialog("ماذا تريد ؟", None,
                                                gtk.DIALOG_DESTROY_WITH_PARENT)
                            self.dialog.vbox.pack_start(gtk.Label('''
                            الكتاب المسمى "'''+self.fd1+'''" موجود بالفعل
                            هل تريد استبداله ؟ أم تريد استيراده باسم آخر ؟
                            أم تريد استيراد الاسم فقط ؟ أم تريد تخطي هذا الكتاب ؟
                            '''), True, True, 0)
                            self.entry = gtk.Entry()
                            self.entry.set_text(self.fd1)
                            self.dialog.vbox.pack_start(self.entry, True, True, 0)
                            istbdal = self.dialog.add_button('استبدال',0)
                            istbdal.connect('clicked',self.istbdal0)
                            ism_akher = self.dialog.add_button('باسم آخر',1)
                            ism_akher.connect('clicked',self.ism_akher0)
                            ism_fakat = self.dialog.add_button('الاسم فقط',2)
                            ism_fakat.connect('clicked',self.ism_fakat0)
                            takhati = self.dialog.add_button('تخطي',3)
                            takhati.connect('clicked',self.takhati0)
                            self.dialog.show_all()
                            self.dialog.run()
                            self.dialog.destroy()
                        elif th.conf['ad'] == '0':
                            self.istbdal0()
                        elif th.conf['ad'] == '1':
                            self.ism_akher0()
                        elif th.conf['ad'] == '2':
                            self.ism_fakat0()
                        elif th.conf['ad'] == '3':
                            self.takhati0()
                            i1 = self.ls.get_iter((f,))
                            self.ls.remove(i1)
                    else:
                        self.db = self.data(fd,-1)
                        self.export(self.fd2)
                        th.cur1.execute('INSERT INTO books VALUES ("'+self.fd1+'","'+self.fw1+'",0)')
                        th.con.commit()
                        self.s += 1
                        i1 = self.ls.get_iter((f,))
                        self.ls.remove(i1)
                except : 
                    self.s += 1
                    f +=1
            self.progress.set_text('انتهى !!')
            self.progress.set_fraction(1.0)
            th.store_k.clear()
            th.store_s.clear()
            th.tree0()
            
    def __init__(self,*a):
        gtk.Window.__init__(self)
        from Asmaa.ThwabDB import ThwabBook
        self.data = ThwabBook
        self.set_border_width(10)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file("icons/Chamila-24.png")
        self.set_modal(True)
        self.set_title('استيراد ملفات الشاملة وثواب2') 
        vb = gtk.VBox(False,2); self.add(vb)
        hb0 = gtk.HBox(False,2)
        hb = gtk.HBox(False,2)
        vb.pack_start(hb0,False, False, 2)
        hb0.pack_start(hb,False, False, 2)
        self.b_add = gtk.Button("جديد")
        self.b_add.connect('clicked', self.add_cb)
        hb.pack_start(self.b_add, False, False, 2)
        self.b_remove = gtk.Button("حذف")
        def rm(widget, *args):
            l, ls_p = self.lsv.get_selection().get_selected_rows()
            r = map(lambda p: gtk.TreeRowReference(self.ls, p), ls_p)
            for i in r:
                self.ls.remove(self.ls.get_iter(i.get_path()))
        self.b_remove.connect('clicked', rm)
        hb.pack_start(self.b_remove, False, False, 2)
        self.b_clear = gtk.Button("مسح")
        self.b_clear.connect('clicked', lambda *a: self.ls.clear())
        hb.pack_start(self.b_clear, False, False, 2)
        self.b_convert = gtk.Button("تحويل")
        self.b_convert.connect('clicked',self.start)
        hb.pack_start(self.b_convert, False, False, 2)
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        self.progress = gtk.ProgressBar()
        align.add(self.progress)
        hb0.pack_start(align, True, True, 2)
        self.b_cancel = gtk.Button("إلغاء")
        def stop(widget, *args):
            l, ls_p = self.lsv.get_selection().get_selected_rows()
            self.s = len(l)
            self.b_cancel.set_sensitive(False)
            self.b_clear.set_sensitive(True)
            self.b_convert.set_sensitive(True)
            self.b_remove.set_sensitive(True)
            self.b_add.set_sensitive(True)
        self.b_cancel.connect('clicked', stop)
        self.b_cancel.set_sensitive(False)
        hb0.pack_start(self.b_cancel, False, False, 2)
        self.ls = gtk.ListStore(str,str)
        self.lsv = gtk.TreeView(self.ls)
        cells = []
        cols = []
        cells.append(gtk.CellRendererText())
        cols.append(gtk.TreeViewColumn('الكتب', cells[-1], text = 1))
        cols[-1].set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        cols[-1].set_resizable(True)
        cols[-1].set_expand(True)
        self.lsv.set_headers_visible(True)
        self.lsv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        for i in cols: self.lsv.insert_column(i, -1)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
        scroll.add(self.lsv)
        vb.pack_start(scroll,True, True, 2)
        self.chajara = gtk.ComboBox()
        cell = gtk.CellRendererText()
        self.chajara.pack_start(cell)
        self.chajara.add_attribute(cell, 'text', 0)
        self.chajara.set_wrap_width(1)
        self.chajara.set_model(th.store_kaima1)
        vb.pack_start(gtk.Label('ضع هذه الكتب في قسم :'),False, False, 2)
        vb.pack_start(self.chajara,False, False, 2)
        self.resize(400,300) 
        self.show_all() 
                      
#----------------------------------------------------

th = ThwabApplication()   
def main(): 
    gtk.main()

if __name__ == "__main__":
    main()
