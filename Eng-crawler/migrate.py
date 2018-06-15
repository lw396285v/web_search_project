import pymysql
import sqlite3

sqlite_db = sqlite3.connect('../Eng-crawler/eng.db')

cursor_lite = sqlite_db.cursor()

cursor_lite.execute('select * from Books')

books = cursor_lite.fetchall()

sqlite_db.close()

db = pymysql.connect("localhost", "root", "lw1001", "IR_db", charset='utf8', )

cursor = db.cursor()

i = 1

for book in books:
    sql = """INSERT INTO books_eng VALUES (%s, %s, %s, %s, %s, %s)"""
    print(book)
    path = '/home/liwen/Dataset/books-eng/'+str(str(book[0]))+'.txt'
    cursor.execute(sql, [str(i), book[0], book[1], book[2], book[3], path])
    i += 1

db.commit()
