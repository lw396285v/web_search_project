from selenium import webdriver
from pyquery import PyQuery
import sqlite3
import urllib3
import re


class BookKm(object):
    def __init__(self):
        super().__init__()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        #self.webkit = webdriver.Chrome()
        self.url_base = 'http://book.km.com'
        self.classes = {1: '玄幻', 2: '奇幻', 3: '武侠', 4: '仙侠', 5: '都市', 6: 'None', 7: '军事', 8: '历史', 9: '游戏',
                        10: '科幻', 11: '现代言情', 12: '古代言情', 13: '穿越架空', 14: '总裁豪门', 15: '青春校园', 16: '同人',
                        17: '灵异', 18: '悬疑', 19: '文学', 20: '职场', 21: '其他', 22: '黑道', 23: '官场', 24: '女尊',
                        25: '种田', 26: '异界', 27: '流行小说'}
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
        for class_id in range(1, 1 + self.classes_num):
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


if __name__ == '__main__':
    crawler = BookKm()
    crawler.run()
