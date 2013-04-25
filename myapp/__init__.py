#coding=utf-8
'初始化Package，加载url，生成app对象'
import web
from myapp.urls import urls

app = web.application(urls, globals())


