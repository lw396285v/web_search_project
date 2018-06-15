import urllib3
from pyquery import PyQuery as pyq
from lxml import etree
from bs4 import BeautifulSoup
import sqlite3

db_conn = sqlite3.connect('bk.db')
cursor = db_conn.cursor()

