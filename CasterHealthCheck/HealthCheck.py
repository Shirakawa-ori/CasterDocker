import requests
import redis
import time

def conn_redis(redis_host = 'localhost',redis_port = '6379',redis_db = '15'):
    return redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db) 

def get_code(url):
    return requests.get(url).status_code

def Checkaddlist(rs):
    urllist = rs.smembers ('upstream')
    print urllist
    cemetery = rs.smembers ('cemetery')
    print cemetery

    for u in urllist:
        status = str(000)
        url = 'http://'+u
        print url
        try:
            status = str(get_code(url))
        except Exception, e:
            print repr(e)
            print '--try again--'
            time.sleep(1)
            try:
                status = str(get_code(url))
            except Exception, e:
                print repr(e) + ',Dead'
                status = str('000')

        if str(status) == str('200'):
            print 'HTTP 200 OK! ' + url
        else :
            rs.srem ('upstream',u)
            rs.sadd('cemetery',u)
            print 'Error ' + url + ' is Dead ' + str(status)
            
    uploadTime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print uploadTime+ " " + str(rs.set('uploadTime',uploadTime))
    print '-----------------------------------------------------'
    
if __name__ == "__main__":
    try :
        print 'Redis'
        rs = conn_redis(redis_host = '172.17.0.15',redis_db = '3')
        print rs.keys('*')
        print 'Done'
        while(1):
            Checkaddlist(rs)
            time.sleep(60)
    except Exception, e:
        printRedChr('run ERR!')
        print e
        exit(1)
