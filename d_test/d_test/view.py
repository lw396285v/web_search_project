from django.http import HttpResponse
from django.shortcuts import render
from .search_engine.query_cn import Query_cn
from .search_engine.query import Query
import json
import pymysql


def hello(request):
    return HttpResponse("Hello world ! ")


def main(request):
    return render(request, 'index.html')

def search(request):
    language = request.GET['language']
    type = request.GET['type']
    key = request.GET['key']
    if language == "Chinese":
        index = 'mysql'
        query = Query_cn()
    elif language == "English":
        index = 'booksENG'
        query = Query()
    else:
        return HttpResponse('internal error')

    q = '@'
    if type == "Title":
        q += 'TITLE'
    elif type == "Author":
        q += 'AUTHOR'
    elif type == "Feature":
        q += 'FEATURE'
    elif type == "Fulltext":
        q += 'PATH'
    else:
        return HttpResponse('internal error')

    q += ' ' + key


    print(q)
    result = query.query_sphinx(index, q)
    return HttpResponse(json.dumps(result))

def read(request):
    language = request.GET['lang']
    bid = request.GET['bid']
    db_conn = pymysql.connect("localhost", "root", "lw1001", "IR_db", charset='utf8', )
    cursor = db_conn.cursor()
    if language == "English":
        path = '/home/liwen/Dataset/books-eng/'
        cursor.execute("select title, author from books_eng where id=%s", [str(bid)])
    else:
        path = '/home/liwen/Dataset/books-cn/'
        cursor.execute("select title, author from books_cn where id=%s", [str(bid)])
    res = cursor.fetchall()
    title = res[0][0]
    author = res[0][1]
    with open(path + str(bid) + '.txt', 'r') as fh:
        content = fh.read()
    print(language, bid, title)
    db_conn.close()
    return render(request, 'read.html', {'content': content, 'title': title, 'author': author})
