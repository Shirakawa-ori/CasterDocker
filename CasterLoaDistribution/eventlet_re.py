import eventlet
import redis
import time

class colourOutput():
    def __init__(self):
        pass
    def red(self,s):
        print "\033[1;31;40m"+s+"\033[0m"
    def green(self,s):
        print "\033[1;32;40m"+s+"\033[0m"
    def blue(self,s):
        print "\033[1;34;40m"+s+"\033[0m"

def get_upstream(rs):
    upstream = rs.srandmember('upstream','1')[0].split(':')
    upstreamHost = upstream[0]
    upstreamPort = upstream[1]
    return upstreamHost,int(upstreamPort)

def conn_redis(redis_host = 'localhost',redis_port = '6379',redis_db = '15'):
    return redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db)

def closed_callback():
    server.close()
    co.blue('    ## Close CallBack ##\n      Time : %s , IP : %s' % (str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) ,str(addr)))

def forward(source, dest, cb=lambda: None):
    """Forwards bytes unidirectionally from source to dest"""
    while True:
        d = source.recv(32384)
        if d == '':
            cb()
            break
        dest.sendall(d)

if __name__ == "__main__":
    co = colourOutput()
    co.green('INIT CHECK SET')
    listenHost = '0.0.0.0'
    listenPort = 1926
    co.blue('    start '+listenHost+':'+str(listenPort))
    co.blue('    Check Redis')
    rs = conn_redis(redis_host = '127.0.0.1',redis_db = '3')
    co.blue('    %s' % str(rs.keys('*')))
    co.blue('    %s' % str(get_upstream(rs)))
    co.blue('    Start listen')
    listener = eventlet.listen((listenHost, listenPort))
    co.green('ALL CHECK OK')
    print ''
    try :
        while True:
            try:
                #co.green('## Start New listener ##')
                client, addr = listener.accept()
                upstreamHost, upstreamPort = get_upstream(rs)
                co.blue('    ## listener get client ##\n      Time : %s , IP : %s , upstream : %s:%s' % (str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))),addr,upstreamHost,str(upstreamPort)))
                server = eventlet.connect((upstreamHost ,upstreamPort))
                # two unidirectional forwarders make a bidirectional one
                eventlet.spawn_n(forward, client, server, closed_callback)
                eventlet.spawn_n(forward, server, client)
            except Exception,e:
                co.red('listener ERROR %s' % str(e))
    except Exception,e:
        listener.close()
        co.red('STOP %s' % str(e))
