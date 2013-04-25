#coding=utf-8
import re
import web
import model
from setting import render, render_without_layout, session
from setting import key, iv, mode
from Crypto.Cipher import AES


def requierLoginStatus(func):
    '用于判断是否为登录状态的装饰器，如果非登录状态则跳回login'

    def todo(instance, arg=None):
        if ('token' not in web.cookies()) \
            and ('auth' not in session or session.get('auth') == 0):
            raise web.seeother('/login')
        if arg:
            return func(instance, arg)
        return func(instance)

    return todo


class Index():
    @requierLoginStatus
    def GET(self):
        todolist = model.get_todolist()
        data = web.input()
        if data.get('err') == 'none':
            errormsg = '没有这条记录'
        elif data.get('err') == 'badrequest':
            errormsg = '无效的请求'
        else:
            errormsg = None
            return render.index(todolist, errormsg=errormsg)
        return render.index(todolist, errormsg=errormsg)

    def POST(self):
        data = web.input()
        title = data.get('title', None)
        if title:
            model.insert_todolist(title)
            raise web.seeother('/')
        else:
            todolist = model.get_todolist()
            return render.index(todolist, errormsg='必须输入内容')


class Finish():
    @requierLoginStatus
    def GET(self, id):
        data = web.input()
        if data.get('status') == '1':
            finished = 1
        elif data.get('status') == '0':
            finished = 0
        else:
            raise web.seeother('/?err=badrequest')
        model.update_finish_stauts(id, finished)
        raise web.seeother('/')


class Del():
    @requierLoginStatus
    def GET(self, id):
        title = model.get_by_id(id)
        if title:
            model.del_by_id(id)
            raise web.seeother('/')
        raise web.seeother('/?err=none')


class Edit:
    @requierLoginStatus
    def GET(self, id):
        todo = model.get_by_id(id)
        if not todo:
            raise web.seeother('/?err=none')
        return render.edit(todo)

    def POST(self, id):
        todo = model.get_by_id(id)
        if not todo:
            raise web.seeother('/?err=none')
        data = web.input()
        if not data.get('title'):
            return render_without_layout.warning('需要输入内容', '/edit/%s' % id)
        model.update_title(id, data.title)
        return render_without_layout.warning('修改成功', '/')


class Login():
    def GET(self):
        print web.ctx
        cur_user = session.get('register')
        if cur_user:
            session.pop('register')
            return render.login(cur_user=cur_user)
        else:
            return render.login(cur_user=None)

    def POST(self):
        data = web.input()
        if not (data.get('username') and data.get('password')):
            msg = u'用户名或密码不能为空'
            return render.login(cur_user=None, error=msg)
        else:
            if not model.check_user_is_duplicate(data.get('username')): #检查用户是否存在
                if model.check_user_info(data.get('username'), data.get('password')): #检查用户名密码是否匹配
                    session.auth = 1 #置登录状态，视为通过登录
                    if data.get('autoLogin'): #检查是否为自动登录
                        token = data.get('username') + ';' + data.get('password')
                        token = token.encode('utf-8')
                        web.setcookie('token', AES.new(key, mode, iv).encrypt(token), 3600) #对用户名密码AES加密，存入cookie
                    return web.seeother('/')
                return render.login(cur_user=None, error=u'用户名或密码错误')
            return render.login(cur_user=None, error=u'无效的用户名')


class Register():
    def GET(self):
        return render.register(faildict={}, msg='')

    def POST(self):
        register_data = web.input()
        isvalid = self.Valid(register_data)
        if isvalid != True: #验证注册数据是否合法
            faildict = isvalid
            return render.register(faildict=faildict, msg='')
        else:
            username = register_data.get('username')
            password = register_data.get('password')
            email = register_data.get('e-mail')
            model.insert_userinfo(username, password, email)
            session.register = username
            raise web.seeother('/login')


    def Valid(self, data):
        '验证注册数据的逻辑'
        faildict = self.isValidForm(data)
        if faildict:
            return faildict
        elif not self.isPswEqual(data.get('password'), data.get('confirm')):
            faildict['password'] = '两次输入密码不一致'
            return faildict
        elif not self.isValidEmail(data.get('e-mail')):
            faildict['e-mail'] = '邮箱格式不正确'
            return faildict
        elif not self.isDuplicateUser(data.get('username')):
            faildict['username'] = '用户已存在'
            return faildict
        else:
            return True

    def isValidForm(self, dataobj):
        '验证提交的表单是否合法'
        validdict = {}
        postdatalist = {'username': '用户名', 'e-mail': '邮件', 'password': '密码', 'confirm': '确认密码'}
        for name in postdatalist.keys():
            if not dataobj.get(name):
                validdict[name] = '%s不能为空' % postdatalist[name]
        return validdict

    def isPswEqual(self, password, confirm):
        '验证2次输入密码是否一致'
        if password != confirm:
            return False
        return True

    def isValidEmail(self, email):
        '验证邮箱是否符合规范'
        regexp = "\\w+([-+.]\\w+)*@\\w+([-.]\\w+)*\\.\\w+([-.]\\w+)*"
        if re.match(regexp, email):
            return True
        return False

    def isDuplicateUser(self, username):
        '验证用户名是否重复'
        if model.check_user_is_duplicate(username):
            return True
        return False


class Forget():
    def GET(self):
        return render.forget(None)

    def POST(self):
        data = web.input()
        email = data.get('email')
        username = data.get('username')
        if email and username:
            if model.check_email(email, username): #验证邮箱和用户名是否匹配
                newpassword = model.update_password(username) #更新密码
                try:
                    web.sendmail('no-reply@automail.com', email, u'找回密码', u'您的新密码为%s' % newpassword)
                except Exception, e:
                    print e
                return render_without_layout.warning('发送成功', '/login')
            return render.forget('用户名邮箱不匹配')
        return render.forget('邮箱或用户名不能为空')


class Logout():
    @requierLoginStatus
    def GET(self):
        if 'token' in web.cookies():
            web.setcookie('token', 0, -1)
        session.auth = 0
        raise web.seeother('/login')


class Expiry():
    def GET(self):
        return render_without_layout.warning('会话过期', '/login')


class Pages():
    @requierLoginStatus
    def GET(self, cur_page=1):
        titlescount = model.get_count_from_titles()
        eachnum = 10
        pages = titlescount // eachnum
        if titlescount % eachnum != 0:
            pages = pages + 1
        if int(cur_page) > pages or int(cur_page) <= 0:
            return render_without_layout.warning('没有数据', '/')
        titles = model.get_todolist_with_limit(eachnum, (int(cur_page) - 1) * 10)
        return render.pages(titles, cur_page, pages)





