import sqlite3


db_conn = sqlite3.connect('eng.db')

cursor = db_conn.cursor()

cursor.execute('SELECT * FROM EngBooks')

a = cursor.fetchall()

for i in a:
    bid = i[0]
    title = i[1]
    author = i[2]
    cursor.execute("SELECT * FROM EngBooksFeatures WHERE BID="+str(bid))
    fs = cursor.fetchall()
    feature = ''
    for u in fs:
        feature += u[1] + ';'
    cursor.execute("INSERT INTO Books VALUES (?, ?, ?, ?)", (bid, title, author, feature))
    print('%d finish' % bid)
db_conn.commit()