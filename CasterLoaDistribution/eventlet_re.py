# -*- coding: utf-8 -*-
import eventlet
import redis
import time
import uuid

def timer(func):
    def decor(*args):
        start_time = time.time();
        func(*args);
        end_time = time.time();
        d_time = end_time - start_time
        print("run the func use : ", d_time)
    return decor;

def set_fun(func):
    def call_fun(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print '程序用时：%s秒' % int(end_time - start_time)
    return call_fun

def create_adder():
    init = [0]
    def add(x):
        init[0] += x
        return init[0]
    return add

class colourOutput():
    def __init__(self):
        pass
    def red(self,s):
        print "\033[1;31;40m%s\033[0m" % s
    def green(self,s):
        print "\033[1;32;40m%s\033[0m" % s
    def blue(self,s):
        print "\033[1;34;40m%s\033[0m" % s

class poll():
    def __init__(self):
        self.add = create_adder()
        self.ip2num = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    def conn_redis(self,redis_host = 'localhost',redis_port = '6379',redis_db = '15'):
        self.rs = redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db)
        return self.rs
    def refresh_poll(self):
        self.poll = list(self.rs.smembers('upstream'))
        return self.poll
    def get_upstream(self): 
        upstream = self.rs.srandmember('upstream','1')[0].split(':')
        return upstream[0],int(upstream[1])
    def roll(self):
        num = self.add(1)-1
        if num < len(self.poll):
            pass
        else :
            num = 0
            self.add = create_adder()
            self.refresh_poll()
        #co.red('    Poll_roll index:%d' % num)
        upstream = self.poll[num].split(':')
        return upstream[0],int(upstream[1])
    def ip_hash(self,addr):
         upstream = self.poll[self.ip2num(addr)%len(self.poll)].split(':')
         return upstream[0],int(upstream[1])
    def no_redis(self,upstream):
         upstream = upstream.split(':')
         return upstream[0],int(upstream[1])

def closed_callback():
    co.blue('%s    ## Close CallBack ##\n      Time : %s , IP : %s' % (coid,str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) ,str(addr)))

def forward(source, dest, cb=lambda: None):
    """Forwards bytes unidirectionally from source to dest"""
    while True:
        #d = source.recv(32384)
        d = source.recv(4096)
        print d
        if d == '':
            cb()
            try :
                dest.shutdown(2)
                dest.close()
            except :
                pass
            break
        dest.sendall(d)

if __name__ == "__main__":
    co = colourOutput()
    co.green('INIT CHECK SET')
    poll = poll()
    listenHost = '0.0.0.0'
    listenPort = 1926
    co.blue('    start '+listenHost+':'+str(listenPort))
    co.blue('    Check Redis')
    poll.conn_redis(redis_db = '3')
    co.blue('    %s' % str(poll.rs.keys('*')))
    if 'upstream' in poll.rs.keys('*'):
        pass
    else :
        co.red('Redis upstream Not Found')
        exit(1)
    co.blue('    %s , %d' % (str(poll.rs.smembers('upstream')),len(poll.refresh_poll())))
    if len(poll.rs.smembers('upstream')) >= 0:
        pass
    else :
        co.red('upstream len <=0 Prudent withdrawal')
        exit(1)
    co.blue('    Start listen')
    listener = eventlet.listen((listenHost, listenPort))
    pool = eventlet.GreenPool(200)
    co.green('ALL CHECK OK')
    print ''
    try :
        while True:
            try:
                #co.green('## Start New listener ##')
                coid = uuid.uuid1()
                client, addr = listener.accept()
                #
                #upstreamHost, upstreamPort = poll.get_upstream()
                #upstreamHost, upstreamPort = poll.roll()
                #upstreamHost, upstreamPort = poll.ip_hash(addr[0])
                upstreamHost, upstreamPort = poll.no_redis('127.0.0.1:80')
                #
                co.blue('%s    ## listener get client ##\n      Time : %s , IP : %s , upstream : %s:%s' % (coid,str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))),addr,upstreamHost,str(upstreamPort)))
                server = eventlet.connect((upstreamHost ,upstreamPort))
                # two unidirectional forwarders make a bidirectional one
                eventlet.spawn_n(forward, client, server, closed_callback)
                eventlet.spawn_n(forward, server, client)
            except Exception,e:
                co.red('listener ERROR %s' % str(e))
    except Exception,e:
        listener.close()
        co.red('STOP %s' % str(e))
