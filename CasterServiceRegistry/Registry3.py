import socket
import redis

def printRedChr(s):
    print "\033[1;31;40m"+s+"\033[0m"

def conn_redis(redis_host = 'localhost',redis_port = '6379',redis_db = '15'):
    return redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db) 
    
def get_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print hostname , ip
    return ip

if __name__ == "__main__":
    try :
        print 'Redis'
        rs = conn_redis(redis_host = 'redis',redis_db = '3')
        print rs.keys('*')
        print 'Done'
    except Exception, e:
        printRedChr('redis ERR!')
        print e
        exit(1)
    try :
        ip = get_ip()
    except Exception, e:
        printRedChr('getIp ERR!')
        print e
        exit(1)
    try :
        port = 10005
        upstream = ip+':'+str(port)
        rs.sadd('upstream',upstream)
        print str(rs.smembers('upstream'))
        print 'Registry success!'
    except Exception, e:
        printRedChr('Registry ERR!')
        exit(1)

    printRedChr('Registry Done.')
    exit(0)
