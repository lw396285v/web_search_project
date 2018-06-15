from .sphinxapi import *


class Query(object):
    def __init__(self):
        self.mode = SPH_MATCH_ALL
        self.host = 'localhost'
        self.port = 9312
        self.limit = 20

    def query_sphinx(self, index, q, limit=1000):
        self.limit = limit
        cl = SphinxClient()
        cl.SetServer(self.host, self.port)
        cl.SetMatchMode(self.mode)
        cl.SetLimits(0, self.limit, max(self.limit, 1000))
        return cl.Query(q, index)

