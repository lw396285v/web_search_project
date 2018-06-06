import sqlite3
import urllib3
from bs4 import BeautifulSoup
import json


class AliWx(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        self.url = 'http://www.aliwx.com.cn/store'
        self.fields = {'sz': 0, 'fc': '', 'wd': 0, 'tm': 0, 'st': 0, 'page': 1}
        self.classes = ['都市小说', '玄幻小说', '仙侠小说', '灵异小说', '历史小说',
                        '游戏小说', '科幻小说', '武侠小说', '奇幻小说', '竞技小说',
                        '其他小说', '现言小说', '古言小说', '幻言小说']
        self.http = urllib3.PoolManager()
        self.db_conn = None

    def init_database(self):
        self.db_conn = sqlite3.connect('aliwx.db')
        cursor = self.db_conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS AliBooks''')
        cursor.execute('''CREATE TABLE  AliBooks
                        (
                        BID INTEGER PRIMARY KEY NOT NULL,
                        NAME TEXT NOT NULL,
                        AUTHOR TEXT NOT NULL
                        )''')
        cursor.execute('''DROP TABLE IF EXISTS AliBooksDetail''')
        cursor.execute('''CREATE TABLE  AliBooksDetail
                                (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                CID INTEGER NOT NULL,
                                CIDO INTEGER NOT NULL,
                                BID INTEGER NOT NULL,
                                FOREIGN KEY (BID) REFERENCES AliBooks(BID)
                                )''')
        cursor.execute('''DROP TABLE IF EXISTS AliBooksFeatures''')
        cursor.execute('''CREATE TABLE AliBooksFeatures
                                (
                                FID INTEGER PRIMARY KEY AUTOINCREMENT,
                                FEATURE TEXT NOT NULL,
                                BID INTEGER NOT NULL,
                                FOREIGN KEY (BID) REFERENCES AliBooks(BID)
                                )''')
        self.db_conn.commit()
        self.db_conn.close()

    def get_info_on_page(self, soup):
        try:
            cursor = self.db_conn.cursor()
        except:
            self.db_conn = sqlite3.connect('aliwx.db')
            cursor = self.db_conn.cursor()
        all_books = soup.find_all('a', class_='clear')
        if len(all_books) == 0:
            self.db_conn.close()
            return False
        for book in all_books:
            title = book.attrs['title']
            bid = book.attrs['href'].split('=')[1]
            self.get_details(bid, title)
        self.db_conn.commit()
        return True

    def get_details(self, bid, title):
        try:
            cursor = self.db_conn.cursor()
        except:
            self.db_conn = sqlite3.connect('aliwx.db')
            cursor = self.db_conn.cursor()

        info_url = 'http://www.aliwx.com.cn/cover'
        content_url = 'http://www.aliwx.com.cn/reader'
        reply_detail = self.http.request('GET', info_url, {'bid': bid}, self.headers)
        reply_content = self.http.request('GET', content_url, {'bid': bid}, self.headers)
        data_detail = reply_detail.data.decode('UTF-8')
        data_content = reply_content.data.decode('UTF-8')
        soup_detail = BeautifulSoup(data_detail, 'lxml')
        soup_content = BeautifulSoup(data_content, 'lxml')

        try:
            author = soup_detail.find_all('span', class_='bauthor')[0].contents[0].contents[0]

        except:
            print('Author error')
            print('target url: %s, you can manually check it out\n' % (info_url + '?bid=' + bid))
            author = 'None'

        try:
            features = [s.contents[0].contents[0]
                        for s in soup_detail.find_all('ul', class_='tags clear')[0].find_all('li')]
        except:
            print('Feature error')
            print('target url: %s, you can manually check it out\n' % (info_url + '?bid=' + bid))
            features = ['None']

        try:
            j_dict = json.loads(str(soup_content.find('i',class_='page-data js-dataChapters').contents[0]))
            c_list = j_dict['chapterList'][0]['volumeList']
            cid_list = []
            for c in c_list:
                cid_list.append(int(c['chapterId']))

        except:
            print('ChapterId error')
            print('target url: %s, you can manually check it out\n' % (info_url + '?bid=' + bid))
            cid_list = []

        try:
            cursor.execute("INSERT INTO AliBooks VALUES (?, ?, ?)", (bid, title, author))
            for idx, cid in enumerate(cid_list):
                cursor.execute("INSERT INTO AliBooksDetail VALUES (NULL, ?, ?, ?)", (cid, idx, bid))
            for f in features:
                cursor.execute("INSERT INTO AliBooksFeatures VALUES (NULL, ?, ?)", (f, bid))
        except sqlite3.IntegrityError as e:
            print(e)
            print('trace_back: bid %s, title %s, author %s' % (bid, title, author))

    def get_books(self, c):
        self.fields['fc'] = c
        self.fields['page'] = 1
        reply = self.http.request('GET', self.url, self.fields, self.headers)
        data = reply.data.decode('UTF-8')
        soup = BeautifulSoup(data, 'lxml')
        while self.get_info_on_page(soup):
            print(self.fields)
            self.fields['page'] += 1
            reply = self.http.request('GET', self.url, self.fields, self.headers)
            data = reply.data.decode('UTF-8')
            soup = BeautifulSoup(data, 'lxml')

    def get_all_books(self):
        for c in self.classes[2:]:
            self.get_books(c)


c = AliWx()
#c.init_database()
c.get_all_books()

