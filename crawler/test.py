import urllib3
from bs4 import BeautifulSoup


url = 'http://book.km.com/boy.html'

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'
}

fields = {'sz': 0, 'fc': '都市小说', 'wd': 0, 'tm': 0, 'st': 0, 'page': 1}

http = urllib3.PoolManager()

r = http.request('GET', url, headers)

data = r.data.decode('GBK')

soup = BeautifulSoup(data, 'lxml')

print(soup)

