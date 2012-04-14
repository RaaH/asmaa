# -*- coding: utf-8 -*-
import gtk



def show_about1(widget,data = None):
    about = gtk.AboutDialog()
    about.set_program_name("مكتبة أسماء")
    about.set_version("1.5")
    about.set_copyright("asmaaarab@gmail.com")
    about.set_comments("""برنامج مكتبة أسماء بديل للشاملة على لينكس""")
    about.set_website("http://www.asmaaarab.wordpress.com")
    about.set_authors(['أحمد رغدي'])
    about.set_license("""
بسم الله الرحمن الرحيم 
الحمد لله رب العالمين ، والصلاة والسلام على محمد وآله وأزواجه وصحبه أجمعين
أما بعد : 
فمكتبة أسماء برمجية حرة ؛ وهي معدلة عن مكتبة ثواب 2 .
بإمكانك إعادة توزيعها وحتى تعديلها تحت شروط الرخصة "وقف"
يوزّع برنامج مكتبة أسماء على أمل أن يكون مفيدًا لمن يستخدمه دون أدنى ضمان؛
يمكنك أن تطلع على هذه الرخصة في دليل المستخدم الخاص بمكتبة أسماء
أو من صفحة الرخصة الموجودة على هذا الرابط"http://waqf.ojuba.org/" """)
    about.set_logo(gtk.gdk.pixbuf_new_from_file("icons/Ahmed_logo.png")) 
    about.set_artists(["فيصل شامخ"])
    about.run()
    about.destroy()
