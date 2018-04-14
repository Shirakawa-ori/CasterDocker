#!/usr/bin/env python
# -*- coding:utf-8 -*-
import redis
import requests
import tornado.ioloop
import tornado.web
from tornado import gen

def conn_redis(redis_host = 'localhost',redis_port = '6379',redis_db = '15'):
    return redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db) 

class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine 
    def get(self):
        upstream = rs.srandmember('upstream','1')[0]+self.request.uri
        rf = requests.get(upstream,headers=self.request.headers,stream=True)
        for chunk in rf.iter_content(chunk_size=1024):
            if not chunk: break
            self.write(chunk)
            self.flush()

application = tornado.web.Application([
    (r'.*', MainHandler),
])

if __name__ == "__main__":
    print 'Redis'
    rs = conn_redis(redis_host = 'redis',redis_db = '3')
    print rs.keys('*')
    application.listen(5050)
    tornado.ioloop.IOLoop.instance().start()
