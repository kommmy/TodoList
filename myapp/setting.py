#coding=utf-8
'全局配置'
import web
from web.session import Session
from myapp import app
import markdown
from Crypto.Cipher import AES
from Crypto import Random

#AES相关配置，iv为一个16字节随机数
key = 'Sixteen byte key'
iv = Random.new().read(AES.block_size)
mode = AES.MODE_CFB

#DEBUG
web.config.debug = True

#DATABASE
database = web.database(dbn='mysql', db='todo', user='root', pw='')

#SessionExpiryHandler
class ExpiryHandler(Session):
    '重载Session，当session过期后，回调expired，跳回login'

    def __init__(self, app, store, init):
        Session.__init__(self, app, store, init)

    def expired(self):
        self._killed = True
        self._save()
        raise web.seeother('/login')


#Session
web.config.session_parameters['ignore_expiry'] = False
web.config.session_parameters['timeout'] = 3600 #24 * 60 * 60, # 24 hours   in seconds
if web.config.get('_session') is None:
    # session = web.session.Session(app, web.session.DiskStore('myapp/sessions'), {'auth': 0})
    session = ExpiryHandler(app, web.session.DiskStore('myapp/sessions'), {'auth': 0})
    web.config._session = session
else:
    session = web.config._session

#Template
t_globals = {
    'session': session,
    'cookie': web.cookies,
    'markdown': markdown.markdown,
}
render = web.template.render('templates/', base='layout', globals=t_globals)
render_without_layout = web.template.render('templates/', globals=t_globals)

#一个全局请求的处理器，如果不登录，则无法进入首页
def my_processor(handler):
    if ('token' not in web.cookies()) \
        and ('auth' not in session or session.get('auth') == 0):
        if web.ctx.fullpath != '/login' and web.ctx.fullpath != '/register' and web.ctx.fullpath != '/forget':
            print web.ctx.fullpath
            raise web.seeother('/login')
        elif web.ctx.fullpath == '/register':
            return handler()
        elif web.ctx.fullpath == '/forget':
            return handler()
    elif 'token' in web.cookies():
        userinfo = AES.new(key, mode, iv).decrypt(web.cookies().get('token')).split(';')
        try:
            username = userinfo[0].strip()
            password = userinfo[1].strip()
        except IndexError:
            print 'IndexError'
            web.setcookie('token', 0, -1)
            raise web.seeother('/login')
        import model
        if not model.check_user_info(username, password):
            raise web.seeother('/login')
        return handler()
    return handler()

#邮件server
web.config.smtp_server = 'mail.corp.qihoo.net'

#加载处理器 现在改用装饰器的方式限制登录状态，这个方法不再使用了
# app.add_processor(my_processor)