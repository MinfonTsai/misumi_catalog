__author__ = 'minfon'
# -*- coding: utf-8 -*-

import urllib
import urllib2
from sgmllib import SGMLParser
import MySQLdb
import sys
import threading
import pycurl


websrc = "http://cn.misumi-ec.com"
#  解析  列表
#  第 1 級
class Misumi_home_HTMLParser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)

        self.div_1_tag_unclosed = 0
        self.a_tag_unclosed = 0
        self.pagelink = ''
        self.pagename = ''

    def start_div(self,attrs):
        for name,value in attrs:
            if( name=='class' and  value=='topCategoryBtn' ):
                self.div_1_tag_unclosed = 1
            if( name=='class' and  value=='topMaker' ):
                self.div_1_tag_unclosed = 0

    def end_div(self):
        pass

    def start_a(self,attrs):
        for name,value in attrs:
            if( name=='href' and self.div_1_tag_unclosed == 1):
                self.a_tag_unclosed = 1
                self.pagelink = value
                print self.pagelink

    def end_a(self):
        self.a_tag_unclosed = 0

    def handle_data(self, data):
        if( self.a_tag_unclosed == 1):
            self.pagename = data
            print self.pagename
            content2 = myurl().urlopen( websrc+self.pagelink )
            #desp = Misumi_HTMLParser(self.pagename , websrc+self.pagelink)
            #desp.feed(content2)

            desp = Misumi_CATALOGParser(self.pagename , websrc+self.pagelink)
            s1 = content2.find('categoryList')
            s2 = content2.find('div class=\"maker\"')
            d = content2[s1-12 : s2-2]
            desp.feed(d)

#  解析  列表
#  第 1.5 級 :
class Misumi_CATALOGParser(SGMLParser):
    def __init__(self, pagename, linkaddr ):
        SGMLParser.__init__(self)

        self.catalog1 = pagename
        self.a_tag_unclosed = 0
        self.div_tag_unclosed = 0

    def start_div(self,attrs):
                self.div_tag_unclosed = 1

    def end_div(self):
                self.div_tag_unclosed = 0

    def start_a(self,attrs):
        for name,value in attrs:
            self.a_tag_unclosed = 1
            if ( name=='href' ):
                self.catalog2_link =  websrc + value;

    def end_a(self):
        self.a_tag_unclosed = 0

    def handle_data(self, data):
        if(self.a_tag_unclosed == 1 and self.div_tag_unclosed == 1 ):
           self.catalog2 = data #.decode('gbk').encode('utf8').strip()
           print self.catalog2
           content2 = myurl().urlopen( self.catalog2_link )
           desp2 = Misumi_HTMLParser(  self.catalog1 ,self.catalog2_link )
           desp2.feed(content2)


#  解析  列表
#  第 2 級 :
class Misumi_HTMLParser(SGMLParser):
    def __init__(self, pagename, linkaddr ):
        SGMLParser.__init__(self)

        self.catalog1 = pagename
        self.linkaddr = linkaddr
        self.div_1_tag_unclosed = 0
        self.div_2_tag_unclosed = 0
        self.div_3_tag_unclosed = 0
        self.div_4_tag_unclosed = 0
        self.a_tag_unclosed = 0
        self.li_tag_unclosed = 0
        self.img_tag_unclosed = 0
        self.span_tag_unclosed = 0
        self.h2_tag_unclosed = 0
        self.compinfo_canget = 0
        self.deliverfrom_canget = 0
        self.price_canget = 0
        #self.catalog1="工厂自动化零件"
        self.catalog2=""
        self.catalog3=""
        self.name=""
        self.imagelink=""
        self.Provider=""
        self.catalog3_link=""


    def start_li(self,attrs):
        for name,value in attrs:
            pass

    def end_li(self):
        pass

    def start_a(self,attrs):
        for name,value in attrs:
            if (self.div_2_tag_unclosed == 1 and name=='href' ):
                self.catalog3_link =  websrc + value;

    def end_a(self):
        pass

    def start_span(self,attrs):
        for name,value in attrs:
            pass

    def end_span(self):
        pass

    def start_div(self,attrs):
        for name,value in attrs:
            if( name=='class' and  value=='itemBody' ):
                self.div_1_tag_unclosed = 1
            if( name=='class' and value=='itemTitle'):
                self.div_2_tag_unclosed = 1
            if( name=='class' and  value=='side' ):
                self.div_1_tag_unclosed = 0
            if( name=='class' and  value=='item' ):
                self.div_3_tag_unclosed = 1
            if( name=='class' and  value=='itemImage' ):
                self.div_4_tag_unclosed = 1
                #    self.imagelink = websrc+value
                # if( name=='id'  and self.div_1_tag_unclosed == 1 ):
                #     id_1 = value #[3:]
                #     self.imagelink = websrc+"/material/mech/category/"+id_1+".jpg"
                #    print self.imagelink

    def end_div(self):
        self.div_2_tag_unclosed = 0
        self.div_3_tag_unclosed = 0
        self.div_4_tag_unclosed = 0

    def start_h2(self,attrs):
        for name,value in attrs:
            if( self.div_1_tag_unclosed == 1):
                self.h2_tag_unclosed = 1

    def end_h2(self):
        self.h2_tag_unclosed = 0

    def start_img(self,attrs):
        for name,value in attrs:
            if( self.div_3_tag_unclosed == 1 and  self.div_4_tag_unclosed == 1 and name=='src' ):
                self.imagelink = websrc+value
                print self.imagelink

    def end_img(self):
        pass

    def handle_data(self, data):
        if( self.h2_tag_unclosed == 1 ):
            self.catalog2 = data #.decode('gbk').encode('utf8').strip()
        if( self.div_2_tag_unclosed == 1 ):
            self.catalog3 = data #.decode('gbk').encode('utf8').strip()
            print self.catalog3
            #  -----  save eCatalog into DB  ------
            cursor = db.cursor()
            para = (self.catalog1 ,self.catalog2,self.catalog3,self.name,self.imagelink,self.Provider)
            cursor.execute(query_1,para)    #write to MySQL database
            #print self.catalog3.decode('gbk').encode('utf8')
            #  -------------------------------------
            #content3 = myurl().urlopen( self.catalog3_link )
            #desp3 = Component_HTMLParser( self.catalog3_link , self.catalog3 )
            #desp3.feed(content3)


#  解析  列表
#  第 3 級 :
class Component_HTMLParser(SGMLParser):
    def __init__(self,  linkaddr, catalog3 ):
        SGMLParser.__init__(self)

        self.linkaddr = linkaddr
        self.catalog3 = catalog3
        self.div_1_tag_unclosed = 0
        self.li_tag_unclosed = 0
        self.a_tag_unclosed = 0
        self.Provider = ''
        self.name = ''
        self.component_link = ''

    def start_div(self,attrs):
        for name,value in attrs:
            if( name=='id' and  value=='series_table_contents' ):
                self.div_1_tag_unclosed = 1

    def end_div(self):
        self.div_1_tag_unclosed = 0

    def start_li(self,attrs):
        if(  self.div_1_tag_unclosed == 1):
            self.li_tag_unclosed = 1

    def end_li(self):
        self.li_tag_unclosed =0

    def start_a(self,attrs):
        for name,value in attrs:
            self.a_tag_unclosed = 1
            if (name=='href' and  self.div_1_tag_unclosed == 1 and self.li_tag_unclosed == 1):
                self.component_link = websrc + value;
            if(  self.li_tag_unclosed == 1):
                self.li_tag_unclosed = 0

    def end_a(self):
        self.a_tag_unclosed = 0

    def handle_data(self, data):
        if(  self.div_1_tag_unclosed == 1 and self.li_tag_unclosed == 1 ):
            self.Provider =  data.strip()  #.decode('gbk').en
            print self.Provider
        if(  self.div_1_tag_unclosed == 1 and self.a_tag_unclosed == 1 ):
            self.name =  data.strip()
            print self.name
            content4 = myurl().urlopen( self.component_link   )
            desp4 = Detail_HTMLParser( self.component_link ,  self.name, self.Provider , self.catalog3 )
            desp4.feed(content4)

#  解析  列表
#  第 4 級 :
class Detail_HTMLParser(SGMLParser):
    def __init__(self,  linkaddr, name, Provider , catalog3 ):
        SGMLParser.__init__(self)

        self.linkaddr = linkaddr
        self.name = name
        self.Provider = Provider
        self.catalog3 = catalog3
        self.div_1_tag_unclosed = 0
        self.div_2_tag_unclosed = 0
        self.p_tag_unclosed = 0
        self.ul_tag_unclosed = 0
        self.a_tag_unclosed = 0
        self.imgsrc = 0
        self.memo = ''

    def start_div(self,attrs):
        for name,value in attrs:
            if( name=='class' and  value=='itemDetailBody' ):
                self.div_1_tag_unclosed = 1
            if( self.div_1_tag_unclosed == 1 and name=='class' and  value=='itemImage' ):
                self.div_2_tag_unclosed = 1
            if( name=='class' and  value=='container' ):
                cursor2 = db.cursor()
                para2 = (self.name ,self.imgsrc, self.memo, self.Provider, self.catalog3, self.linkaddr)
                cursor2.execute(query_2,para2)    #write to MySQL database
                db.commit()

    def end_div(self):
        self.div_1_tag_unclosed = 0
        self.div_2_tag_unclosed = 0

    def start_img(self,attrs):
        for name,value in attrs:
            if( self.div_2_tag_unclosed == 1 and name =='src'  ):
                self.imgsrc = websrc + value


    def end_img(self):
        pass

    def start_p(self,attrs):
        for name,value in attrs:
            if( name =='class'  and value=='about'):
                self.p_tag_unclosed = 1

    def end_p(self):
        self.p_tag_unclosed = 0

    def start_ul(self,attrs):
        for name,value in attrs:
            if( name =='class'  and value=='tag'):
                self.ul_tag_unclosed = 1

    def end_ul(self):
        self.ul_tag_unclosed = 0

    def start_a(self,attrs):
        for name,value in attrs:
            if( self.ul_tag_unclosed == 1):
                self.a_tag_unclosed = 1

    def end_a(self):
        self.a_tag_unclosed = 0

    def handle_data(self, data):
        if( self.p_tag_unclosed == 1 ):
            self.memo =  data.strip()  #.decode('gbk').en
            print self.memo
        if( self.ul_tag_unclosed == 1 and self.a_tag_unclosed == 1 ):
            if( self.memo=='' ):
                self.memo =  data.strip()  #.decode('gbk').en
            print '-->'+ self.memo
            #self.memo =''



import StringIO
class myurl:
    def __init__(self):
        self.c1 = ''
        self.c1 = pycurl.Curl()
        self.c1.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c1.setopt(pycurl.MAXREDIRS, 5)
        #self.c1.setopt(pycurl.PROXY, 'http://10.36.6.68:3128')
        #self.c1.setopt(pycurl.PROXYUSERPWD, '00011:mf2222')
        #self.c1.setopt(pycurl.PROXYAUTH, pycurl.HTTPAUTH_ANY)  # or HTTPAUTH_DIGES or HTTPAUTH_BASIC or HTTPAUTH_NTLM or HTTPAUTH_ANY

    def urlopen(self, url):
        self.c1.setopt(pycurl.URL, url )
        c1_data  = StringIO.StringIO()
        self.c1.setopt(pycurl.WRITEFUNCTION, c1_data.write)
        self.c1.perform()
        return c1_data.getvalue()

print u"開始解析 cn.misumi-ec.com"
#========= PROXY ===============
'''
proxy = urllib2.ProxyHandler({'http': r'http://00011:mf2222@10.191.131.3:3128'})
auth = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
urllib2.install_opener(opener)
'''

'''
passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
#passman.add_password(None, 'http://10.191.131.20:3128/', '00011', 'mf2222')
# use HTTPDigestAuthHandler instead here
authhandler = urllib2.HTTPDigestAuthHandler(passman)
authhandler = urllib2.ProxyDigestAuthHandler(passman)
authhandler = urllib2.AbstractDigestAuthHandler(passman)
#opener = urllib2.build_opener(authhandler)
opener = urllib2.install_opener(authhandler)
'''
db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="", db="misumi",charset='utf8')
query_1 = "insert ignore into eCatalog(class1,class2,class3,name,imagelink,Provider ) values(%s,%s,%s,%s,%s,%s)"
query_2 = "insert ignore into components(name,imagelink,memo,Provider,class3, srclink ) values(%s,%s,%s,%s,%s,%s)"
#query_2 = "insert  ignore into lesson( title,videolink,imagelink,courselink,lessonlink ) values(%s,%s,%s,%s,%s)"
#query_3 = "insert  ignore into teacher( name,imagelink ) values(%s,%s)"

# ------------- Get  163  Key Word Page --------------------- http://open.163.com/cuvocw/
#content = urllib2.urlopen("http://so.open.163.com/movie/search/searchprogram/ot0/%E8%83%BD%E6%BA%90/1.html?vs=%C4%DC%D4%B4&pltype=2&sub=").read()
#content = myurl().urlopen("http://so.open.163.com/movie/search/searchprogram/ot0/%E8%83%BD%E6%BA%90/1.html?vs=%C4%DC%D4%B4&pltype=2&sub=")



for num in range(1, 2):
    try:
        print '\nConnect page-%d ...\n' %num
        #"http://s.1688.com/selloffer/-B1C3.html?spm=a260b.152008.5634621.383&beginPage="
        # webaddr = "http://s.1688.com/selloffer/--10350.html?industryFlag=industrial&pageSize=60&from=industrySearch&offset=3&beginPage="
        webaddr = "http://cn.misumi-ec.com"
        content1 = myurl().urlopen( webaddr )  #+ str(num) )
        #s1 = content.find('<!--top end-->')
        #s2 = content.find('</html>')  #('</body>')
        #dd = content[s1+14 : s2]
        parse2 = Misumi_home_HTMLParser()
        #parse2.feed(dd)
        parse2.feed(content1)
        db.commit()
    except:
        print '\nPage %d Error!\n' %num

db.close()
