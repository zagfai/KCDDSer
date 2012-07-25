# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import time
import json
import re

# Kingsoft
class Signer():
    user = ''
    pwd  = ''
    result = {}
    login_url = 'https://www.kuaipan.cn/index.php?ac=account&op=login'
    logined_url = 'http://www.kuaipan.cn/home.htm'
    sign_url = 'http://www.kuaipan.cn/index.php?ac=common&op=usersign'
    logout_url = 'http://www.kuaipan.cn/index.php?ac=account&op=logout'
    header = [('Host', 'www.kuaipan.cn'),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0'),
        ('Referer', 'http://www.kuaipan.cn/account_login.htm' ),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ('Accept-Language', 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'),
        ('Connection', 'keep-alive')]

    def __init__( self, user, pwd ):
        self.user = user
        self.pwd  = pwd
        self.result['user'] = user

    def sign( self ):
        self.result['status'] = self.steps()
        return self.result

    def steps( self ):
        # ready some data
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )
        urllib2.install_opener( opener )
        opener.addheaders = self.header

        #login
        req = urllib2.Request( self.login_url,
                urllib.urlencode({ 'username':self.user, 'userpwd':self.pwd }) )
        try:
            fd = opener.open( req )
        except:
            return u"網絡錯誤，請重試。"
        if fd.url != self.logined_url:
            return u"用戶名或密碼錯誤，請重試。"

        #sign
        req = urllib2.Request( self.sign_url )
        try:
            fd = opener.open( req )
            sign_js = json.loads(fd.read())
            fd.close()
        except:
            return u"獲取金山JSON錯誤，請稍後重試。"

        if sign_js['state'] == -102:
            return u'今天簽到了，不能再簽！'
        elif sign_js['state'] == 1:
            return u'增加 %d 到 %d 積分，還附送 %dM！' % (sign_js['increase'], sign_js['status']['points'], sign_js['rewardsize'])
        else:
            return u'金山JSON可能已經更新，請自便。'

# 115.com
class OOFSign():
    user = ''
    pwd = ''
    result = {}
    login_url = "https://passport.115.com/?ac=login"
    logined_url = 'http://www.kuaipan.cn/home.htm'
    sign_url = 'http://www.kuaipan.cn/index.php?ac=common&op=usersign'
    header = [('Host', 'passport.115.com'),
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0'),
            ('Referer', 'www.115.com' ),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'),
            ('Connection', 'keep-alive')]

    def __init__( self, user, pwd ):
        self.user = user
        self.pwd  = pwd
        self.result['user'] = user

    def sign( self ):
        self.result['status'] = self.steps()
        return self.result

    def steps( self ):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )
        urllib2.install_opener( opener )
        opener.addheaders = self.header

        # login
        req = urllib2.Request( self.login_url,
                urllib.urlencode({ 'login[account]':self.user, 'login[passwd]':self.pwd }) )
        try:
            fd = opener.open( req )
        except:
            return u'網絡錯誤'

        if len( fd.read() ) > 100:
            return u'錯誤用戶名或密碼'
        else:
            req = urllib2.Request( "http://115.com/?ct=file&ac=userfile&aid=1&cid=0&tpl=list_pg&limit=36" )
            try:
                fd = opener.open( req )
                reg = re.search("[a-z0-9]{32}", fd.read())
            except:
                return u'網絡錯誤'

            if reg != None:
                req = urllib2.Request("http://115.com/?ct=ajax_user&ac=pick_space&token=" + reg.group(0) + "&_=" + str(int(time.time())))
                try:
                    fd = opener.open( req )
                    js = json.loads(fd.read())
                    fd.close()
                except:
                    return u"獲取JSON失敗"
                return u"搖曳成功，獲得%s，達到%s！"%( js['picked'], js['total_size'] )
            else:
                print u'已經搖了，不能再搖！'



