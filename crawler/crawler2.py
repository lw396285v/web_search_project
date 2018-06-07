from selenium import webdriver
from pyquery import PyQuery
import sqlite3
import urllib3
import re
import os


class BookKm(object):
    def __init__(self):
        super().__init__()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        self.webkit = None
        self.url_base = 'http://book.km.com'
        self.classes_num = 37
        self.http = urllib3.PoolManager()
        self.db_conn = None
        self.log_handle = None
        self.book_id = 0

    def init_log(self):
        self.log_handle = open('log.txt', 'w')

    def init_database(self):
        self.db_conn = sqlite3.connect('bk.db')
        cursor = self.db_conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS BkBooks''')
        cursor.execute('''CREATE TABLE BkBooks
                        (
                        BID INTEGER PRIMARY KEY NOT NULL,
                        TITLE TEXT NOT NULL,
                        AUTHOR TEXT NOT NULL,
                        FEATURE TEXT NOT NULL
                        )''')
        self.db_conn.commit()
        self.db_conn.close()

    def insert_database(self, bid, title, author, feature):
        try:
            cursor = self.db_conn.cursor()
        except:
            print('connect to database...')
            self.db_conn = sqlite3.connect('bk.db')
            cursor = self.db_conn.cursor()
        try:
            cursor.execute("INSERT INTO BkBooks VALUES (?, ?, ?, ?)", (bid, title, author, feature))
            self.db_conn.commit()
        except sqlite3.IntegrityError as e:
            print(e)
            info = 'bid=%s, title=%s, author=%s, feature=%s' % (bid, title, author, feature)
            print('trace_back: ' + info)
            if self.log_handle.closed or self.log_handle is None:
                self.init_log()
            self.log_handle.write(info+'\n')

    def get_books_on_page(self, url, feature):
        reply = self.http.request('GET', url, self.headers)
        data = reply.data.decode('GBK')
        jq = PyQuery(data)
        books = jq('.info')
        for i in range(len(books)):
            book = books.eq(i)
            if book('a').eq(2).attr('href') is None:
                break
            self.book_id += 1
            title = book('a').eq(0).text()
            author = book('dd').eq(0)('span').text()
            match_res = re.match(r'.*/(.*)\.', book('a').eq(0).attr('href'))
            bid = match_res.group(1)
            print('%d: {title: %s, author: %s, bid: %s, feature: %s}' % (self.book_id, title, author, bid, feature))
            self.insert_database(bid, title, author, feature)

    def make_page_url(self, class_id, page_id):
        return self.url_base + '/shuku_0_' + str(class_id) + '_0_0_0_0_' + str(page_id) + '.html'

    def make_book_url(self, bid):
        return self.url_base + '/chapterlist/' + str(bid) + '.html'

    def get_page_num_and_class_name(self, url):
        reply = self.http.request('GET', url, self.headers)
        data = reply.data.decode('GBK')
        jq = PyQuery(data)
        page_num = 1
        if jq('.page')('a').length != 0:
            if jq('.page')('.a_btn').eq(-1).text() == '尾页':
                page_num = int(re.match(r'.*_(.*)\.', jq('.page')('a').eq(-1).attr('href')).group(1))
            elif jq('.page')('.a_btn').eq(-2).text() == '下一页':
                page_num = int(re.match(r'.*_(.*)\.', jq('.page')('a').eq(-3).attr('href')).group(1))
        class_name = jq('meta').eq(3).attr('content').split('，')[0].rstrip('图书').rstrip('小说')
        return [page_num, class_name]

    def get_all_books(self):
        for class_id in range(27, 1 + self.classes_num):
            page_num, class_name = self.get_page_num_and_class_name(self.make_page_url(class_id, 1))
            for page_id in range(1, 1 + page_num):
                self.get_books_on_page(self.make_page_url(class_id, page_id), class_name)

    def finish(self):
        self.log_handle.close()
        self.db_conn.close()

    def run(self):
        self.init_database()
        self.init_log()
        self.get_all_books()
        self.finish()

    def download_contents(self):
        try:
            self.webkit = webdriver.Chrome()
            self.webkit.implicitly_wait(3)
        except:
            print('Chrome-driver not found, exit')
            exit()
        try:
            cursor = self.db_conn.cursor()
        except:
            print('connect to database...')
            self.db_conn = sqlite3.connect('bk.db')
            cursor = self.db_conn.cursor()
        cursor.execute('SELECT * FROM BkBooks')
        book_list = cursor.fetchall()
        for book in book_list:
            bid = book[0]
            print('[Downloading book: %s]' % book[1])
            self.download_book(bid)
        self.webkit.close()

    def default_content(self, bid):
        if not os.path.exists('./books/' + str(bid)):
            os.mkdir('./books/' + str(bid))
        with open('./books/' + str(bid) + '/1.txt', 'w') as f:
            f.write("小说不支持预览")

    def content(self, bid, cid, url):
        if not os.path.exists('./books/' + str(bid)):
            os.mkdir('./books/' + str(bid))
        with open('./books/' + str(bid) + '/' + str(cid) + '.txt', 'w') as f:
            self.webkit.get(url)
            text = self.webkit.find_element_by_class_name('article-body').text
            f.write(text)

    def download_book(self, bid):
        try:
            reply = self.http.request('GET', self.make_book_url(bid), self.headers)
            data = reply.data.decode('GBK')
            jq = PyQuery(data)
            chapter_list = jq('.mod_catalog')('li')
            for cid in range(1, chapter_list.length + 1):
                if chapter_list.eq(cid - 1).attr('class') is not None:
                    break
                chapter = chapter_list.eq(cid - 1)('a').eq(0).attr('href')
                self.content(bid, cid, self.url_base + chapter)
            print('Successful')
        except:
            self.default_content(bid)
            print('Failed')


if __name__ == '__main__':
    crawler = BookKm()
    #crawler.run()
    crawler.download_contents()
