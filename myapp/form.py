#coding=utf-8
import web
import model
import warnings

warnings.warn("由于自带的form生成的是表格形式的html,现在统一改为div样式,不再使用web.form了",
              DeprecationWarning, 2)
notnull = web.form.Validator(u"不能为空", bool)
vpass = web.form.regexp(r".{3,20}$", u'密码必须大于3位小于20位')
vmail = web.form.regexp(r'.*@.*', u'请输入有效的email地址')

myform = web.form.Form(
    web.form.Textbox('title',
                     web.form.notnull,
                     # web.form.regexp('\w+', 'Must be a character'),
                     web.form.Validator('Must be more than 5', lambda x: len(x) > 5),
                     maxlength='10',
                     description='my title is..',
    ),
    web.form.Button('Add to mydb'),
    validators=[
        web.form.Validator(u'存在相同的数据',
                           lambda x:
                           len(model.db.query('select title from mydb where title=$title',
                                              vars={'title': x.title})) == 0)]
)

register_form = web.form.Form(
    web.form.Textbox('user', notnull,
                     web.form.Validator(u'存在相同的用户', lambda x: len(
                         model.db.select('user', where='name=$name', vars={'name': x})) == 0),
                     description=u'用户名', style="width:120px;"),
    web.form.Textbox('email', vmail,
                     description=u'邮箱', style="width:120px;"),
    web.form.Password('password1', vpass,
                      description=u'密码',
                      maxlength='20', style="width:120px;"),
    web.form.Password('password2', description=u'确认密码', maxlength='20', style="width:120px;"),
    # web.form.Button("submit", value="submit", html=u"<b>确定</b>"),
    validators=[web.form.Validator(u'两次输入密码不一致', lambda x: x.password1 == x.password2)

    ]
)

login_form = web.form.Form(
    web.form.Textbox('name', notnull,
                     web.form.Validator(u'无效的用户', lambda x: len(
                         model.db.select('user', where='name=$name', vars={'name': x})) != 0),
                     description=u'用户名', style="width:120;"),
    web.form.Password('password', notnull, description=u'密码', style="width:120;"),
    validators=[web.form.Validator(u'密码错误', lambda x:
    x.password == model.db.select('user', what='password', where='name=$name', vars={'name': x.name})[0].password
    )]
    # web.form.Checkbox('remember',value='bar'),
    # web.form.Button("submit", value="submit", html=u"<b>登录</b>")

)
