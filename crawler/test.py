import urllib3
from pyquery import PyQuery
import pymysql

db_conn = pymysql.connect("localhost", "root", "lw1001", "IR_db", charset='utf8', )
cursor = db_conn.cursor()

#cursor.execute('select * from books_cn')

url = 'http://book.km.com/shuku/165352.html'

jq = PyQuery(url)

for i in range(jq('.commentTxtList')('dl')('dd').length):
    print('---------------')
    print(jq('.commentTxtList')('dl')('dd').eq(i))

