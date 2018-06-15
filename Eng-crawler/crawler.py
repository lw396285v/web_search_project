from pyquery import PyQuery
import sqlite3
import urllib3
import codecs


class EngCrawler(object):
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        #self.webkit = webdriver.Chrome()
        self.url_base = 'http://www.gutenberg.org'
        self.classes_num = 37
        self.http = urllib3.PoolManager()
        self.db_conn = None
        self.cate_list = []
        self.books = './books-eng/'

    def init_database(self):
        self.db_conn = sqlite3.connect('eng.db')
        cursor = self.db_conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS EngBooks''')
        cursor.execute('''CREATE TABLE EngBooks
                        (
                        BID INTEGER PRIMARY KEY NOT NULL,
                        TITLE TEXT NOT NULL,
                        AUTHOR TEXT NOT NULL
                        )''')
        cursor.execute('''DROP TABLE IF EXISTS EngBooksFeatures''')
        cursor.execute('''CREATE TABLE EngBooksFeatures
                                        (
                                        FID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        FEATURE TEXT NOT NULL,
                                        BID INTEGER NOT NULL,
                                        FOREIGN KEY (BID) REFERENCES EngBooks (BID)
                                        )''')
        self.db_conn.commit()
        self.db_conn.close()

    def get_all_category(self):
        url = self.url_base + '/wiki/Category:Bookshelf'
        url2 = self.url_base + '/w/index.php?title=Category:Bookshelf&pagefrom=The+Contemporary+Review+%28Bookshelf%29#mw-pages'
        jq = PyQuery(url)
        cates = jq('#mw-pages')("li")
        for i in range(cates.length):
            cate = cates.eq(i)
            self.cate_list.append([cate('a').attr('title').rstrip(' (Bookshelf)'), cate('a').attr('href')])
        jq = PyQuery(url2)
        cates = jq('#mw-pages')("li")
        for i in range(cates.length):
            cate = cates.eq(i)
            self.cate_list.append([cate('a').attr('title').rstrip(' (Bookshelf)'), cate('a').attr('href')])

    def download_books(self):
        for cate in self.cate_list:
            class_name = cate[0]
            url = self.url_base + cate[1]
            jq = PyQuery(url)

    def general_download(self, bid):
        while True:
            url = self.url_base + '/ebooks/' + str(bid)
            try:
                jq = PyQuery(url)
            except:
                if bid >= 57299:
                    print('exit')
                    break
                else:
                    bid += 1
                    continue
            a = jq('.files')('a')
            contents = 'No source available'
            title = 'None'
            author = 'None'
            features = []
            source = False
            tr = jq('tr')
            for i in range(tr.length):
                info = tr.eq(i)
                if info('th').text() == 'Title':
                    title = info('td').text()
                if info('th').text() == 'Author':
                    author = info('td').text()
                if info('th').text() == 'Subject':
                    features.append(info('td').text())

            # write database
            try:
                cursor = self.db_conn.cursor()
            except:
                self.db_conn = sqlite3.connect('eng.db')
                cursor = self.db_conn.cursor()

            cursor.execute("INSERT INTO EngBooks VALUES (?, ?, ?)", (bid, title, author))
            for f in features:
                cursor.execute("INSERT INTO EngBooksFeatures VALUES (NULL, ?, ?)", (f, bid))
            self.db_conn.commit()

            # download content
            for i in range(a.length):
                if a.eq(i).text() == 'Plain Text UTF-8':
                    url = a.eq(i).attr('href').lstrip('//')
                    contents = self.http.request('GET', url, self.headers).data.decode('UTF-8', 'ignore')
                    source = True
            with codecs.open(self.books + str(bid) + '.txt', 'w', 'utf-8') as f:
                f.write(contents)
            if source:
                print('BID: %d [%s], success' % (bid, title))
            else:
                print('BID: %d [%s], failed' % (bid, title))
            bid += 1


if __name__ == '__main__':
    c = EngCrawler()
    #c.init_database()
    c.general_download(182)





