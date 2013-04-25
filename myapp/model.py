#coding=utf-8
'数据库操作'
import random
from setting import database
from datetime import datetime

DATABASE = 'todo'
USERINFO = 'userinfo'


def get_by_id(id):
    value = database.select(DATABASE, what='id,title', where='id=$id', vars={'id': id})
    if not value:
        return False
    return value[0]


def insert_todolist(title):
    database.insert(DATABASE, title=title, post_date=datetime.now(), finished=0)
    return True


def insert_userinfo(username, password, email):
    database.insert(USERINFO, username=username, password=password, email=email)
    return True


def get_todolist():
    todolist = database.select(DATABASE, what='id,title,finished', order='finished,id DESC', limit=10, offset=0)
    return todolist


def get_todolist_with_limit(limit, offset):
    todolist = database.select(DATABASE, what='id,title,finished', order='finished,id DESC', limit=limit, offset=offset)
    return todolist


def update_finish_stauts(id, finished):
    database.update(DATABASE, finished=finished, where='id=$id', vars={'id': id})


def update_title(id, content):
    database.update(DATABASE, title=content, where='id=$id', vars={'id': id})


def del_by_id(id):
    database.delete('todo', where='id=$id', vars={'id': id})
    return True


def check_user_info(username, password):
    userpassword = database.select(USERINFO,
                                   what='password',
                                   where='username=$username',
                                   vars={'username': username})[0].password
    if userpassword == password:
        return True
    return False


def check_user_is_duplicate(username):
    usernames = database.select(USERINFO, what='username', where="username=$username", vars={'username': username})
    if len(usernames) != 0:
        return False
    return True


def update_password(username):
    database.update(USERINFO, where='username=$username', password='%d' % random.randint(1000, 10000),
                    vars={'username': username})
    return database.select(USERINFO, what='password', where="username=$username", vars={'username': username})[
        0].password


def check_email(email, username):
    emailsername = database.select(USERINFO, what='username', where="email=$email", vars={'email': email})
    if len(emailsername) == 0:
        return False
    elif username != emailsername[0].username:
        return False
    return True


def get_count_from_titles():
    for i in database.query('SELECT count(title) FROM todo'):
        return i.get('count(title)')


if __name__ == "__main__":
    print get_count_from_titles()
    # todo = get_todolist()
    # desc = database.query('desc todo')
    # for i in todo:
    #     print i
    print check_user_is_duplicate('11')

