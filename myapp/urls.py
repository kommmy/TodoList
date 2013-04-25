#coding=utf-8

pre_fix = 'myapp.views.'

urls = (
    '/login', pre_fix + 'Login',
    '/', pre_fix + 'Index',
    '/del/(\d+)', pre_fix + 'Del',
    '/finish/(\d+)', pre_fix + 'Finish',
    '/edit/(\d+)', pre_fix + 'Edit',
    '/register', pre_fix + 'Register',
    '/logout', pre_fix + 'Logout',
    '/forget', pre_fix + 'Forget',
    '/expiry', pre_fix + 'Expiry',
    '/pages/(\d+)', pre_fix + 'Pages',
    '/pages/', pre_fix + 'Pages'
)