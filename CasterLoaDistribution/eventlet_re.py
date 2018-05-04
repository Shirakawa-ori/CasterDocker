import eventlet
import redis
import time

def get_upstream(rs):
    upstream = rs.srandmember('upstream','1')[0].split(':')
    upstreamHost = upstream[0]
    upstreamPort = upstream[1]
    return upstreamHost,int(upstreamPort)

def conn_redis(redis_host = 'localhost',redis_port = '6379',redis_db = '15'):
    return redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db)

def closed_callback():
    print str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    print '##########'
    print ''

def forward(source, dest, cb=lambda: None):
    """Forwards bytes unidirectionally from source to dest"""
    while True:
        d = source.recv(32384)
        if d == '':
            cb()
            break
        dest.sendall(d)

if __name__ == "__main__":
    listenHost = '127.0.0.1'
    listenPort = 1926
    print 'start '+listenHost+':'+str(listenPort)
    print 'Redis'
    rs = conn_redis(redis_host = 'localhost',redis_db = '3')
    print rs.keys('*')
    print get_upstream(rs)
    listener = eventlet.listen((listenHost, listenPort))
    print 'OK' 
    while True:
        try:
            print '##########'
            upstreamHost, upstreamPort = get_upstream(rs)
            print upstreamHost+':'+str(upstreamPort)
            client, addr = listener.accept()
            print str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            print addr
            server = eventlet.connect((upstreamHost ,upstreamPort))
            # two unidirectional forwarders make a bidirectional one
            eventlet.spawn_n(forward, client, server, closed_callback)
            eventlet.spawn_n(forward, server, client)
        except Exception,e:
            print str(e)
