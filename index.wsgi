# -*- coding: utf-8 -*-
import sae
import web
import MySQLdb
import time
from sae.mail import send_mail
from datetime import date,timedelta
from utils import signer

class index():
    def GET( self ):
        web.header("CONTENT-TYPE","text/html")
        return ''.join( open('tmpl.html').readlines() )

class sign():
    def GET( self, user_host, pwd, checked ):
        web.header("CONTENT-TYPE","text/plain")
        if checked != 'checked':
            return u"請點擊閱讀免責聲明並確認"

        # make data
        user, pwd = str(user_host).split('!'), str(pwd)
        user, host = user[0], user[1]
        regip = str( web.ctx.get('ip', '') )
        expire = date.strftime( date.today() + timedelta( 60 ), "%Y-%m-%d" )

        # try and sign
        result = signer( host, user, pwd ).sign()['status']
#        result = u'！'
        if u'！' != result[-1]:
            return result

        # connect db
        conn = MySQLdb.connect(host=sae.const.MYSQL_HOST, port=int(sae.const.MYSQL_PORT),\
                                user=sae.const.MYSQL_USER, passwd=sae.const.MYSQL_PASS, \
                                db=sae.const.MYSQL_DB,     charset="utf8")
        cr = conn.cursor()
        try:
            cr.execute("INSERT INTO `userer` VALUES (%s,%s,%s,%s)", (user_host, pwd, expire, regip))
            result += u'<br>已加入自動簽到隊列，自動簽到至 ' + expire
        except Exception, e:
            if str(e)[1:5] == '1062':
                try:
                    cr.execute("UPDATE `userer` SET pwd=%s,expire=%s,regip=%s WHERE user=%s", (pwd, expire, regip, user_host))
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
    def GET( self ):
        time_start = time.time()
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

        for acount in users:
            user, host = str(acount[0]).split('!')
            # send mail to user
            if str(acount[2]) == date.strftime( date.today() + timedelta( 3 ), "%Y-%m-%d"):
                send_mail( str(acount[0]), "自動簽到到期通知",
                       "用戶你好，你的帳號" + str(acount[0]) +\
                       "自動簽到功能三日後到期，請登錄 http://kssign.sinaapp.com 重新確認自動簽到功能。",
                      ("smtp.sina.com", 25, "user", "passwd", False))
            # sign
            res = signer( host, user, str(acount[1]) ).sign()
            yield user + ' on ' + host + ' ' + res['status'].encode('utf-8') + '\n'
        yield 'Time uesd: ' + str( time.time() - time_start ) + 's'
# end signAll()

urls = (
    '/sign/(.+)/(.+)/(.+)/', 'sign',
    '/signall', 'signAll',
    '.*', 'index',
)
app = web.application( urls, globals() )
application = sae.create_wsgi_app( app.wsgifunc() )
