# -*- coding: utf-8 -*-
import sae
import web
import MySQLdb
from datetime import date,timedelta
from utils import Signer

class index():
    def GET( self ):
        web.header("CONTENT-TYPE","text/html")
        return ''.join( open('tmpl.html').readlines() )

class sign():
    def GET( self, user, pwd, checked ):
       	web.header("CONTENT-TYPE","text/plain")
        if checked != 'checked':
            return u"請點擊閱讀免責聲明並確認"
        
        # make data
        user, pwd = str(user), str(pwd)
        regip = str( web.ctx.get('ip', '') )
        expire = date.strftime( date.today() + timedelta( 60 ), "%Y-%m-%d" )

        # try and sign
        result = Signer( user, pwd ).sign()['status']
#        result = u'！'
        if u'！' != result[-1]:
            return result

        # connect db
        conn = MySQLdb.connect(host=sae.const.MYSQL_HOST, port=int(sae.const.MYSQL_PORT),\
                                user=sae.const.MYSQL_USER, passwd=sae.const.MYSQL_PASS, \
                                db=sae.const.MYSQL_DB,     charset="utf8")
        cr = conn.cursor()
        try:
            cr.execute("INSERT INTO `userer` VALUES (%s,%s,%s,%s)", (user, pwd, expire, regip))
            result += u'<br>已加入自動簽到隊列，自動簽到至 ' + expire
        except Exception, e:
            if str(e)[1:5] == '1062':
                try:
                    cr.execute("UPDATE `userer` SET pwd=%s,expire=%s,regip=%s WHERE user=%s", (pwd, expire, regip, user)) 
                    result += u'<br>用戶已在自動簽到隊列，簽到延期至 ' + expire
                except:
                    result = False
            else:
                result = False
            
            if not result:
                result = u"未知錯誤，請檢查帳號密碼是否非法"

        cr.close()
        conn.commit()
        conn.close()

        return result
# end sign()  
        
class signAll():
    def POST( self ):
        # connect db
        conn = MySQLdb.connect(host=sae.const.MYSQL_HOST, port=int(sae.const.MYSQL_PORT),\
                                user=sae.const.MYSQL_USER, passwd=sae.const.MYSQL_PASS, \
                                db=sae.const.MYSQL_DB,     charset="utf8")
        conn.query('DELETE FROM `userer` WHERE expire < CURRENT_DATE()')
        conn.commit()

        cr = conn.cursor()
        cr.execute('SELECT * FROM `userer`')
        users = cr.fetchall()
        cr.close()
        conn.commit()
        conn.close()

        result = []
        for acount in users:
            print acount
            result.append( Signer( str(acount[0]), str(acount[1]) ).sign() )
            yield result[-1]['user'] + result[-1]['status'].encode('utf-8') + '\n'
# end POST()
    def GET( self ):
        web.header("CONTENT-TYPE","text/html")
        return ''.join( open('tmpl.html').readlines() )

urls = (
    '/sign/(.+)/(.+)/(.+)/', 'sign',
    '/signall', 'signAll',
    '.*', 'index',
)
app = web.application( urls, globals() )
application = sae.create_wsgi_app( app.wsgifunc() )
