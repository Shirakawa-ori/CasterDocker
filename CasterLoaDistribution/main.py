import redis 
from twisted.internet.protocol import Protocol,ClientCreator
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory,ClientFactory

def conn_redis(redis_host = 'localhost',redis_port = '6379',redis_db = '15'):
    return redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db) 

class Transfer(Protocol):
    def __init__(self):
            pass
    def connectionMade(self):
            c = ClientCreator(reactor,Clienttransfer)
            host = rs.srandmember('upstream','1')[0]
            port = 80
            print host
            c.connectTCP(host,port).addCallback(self.set_protocol)
            self.transport.pauseProducing()
    def set_protocol(self,p):
            self.server = p
            p.set_protocol(self)
    def dataReceived(self,data):
            self.server.transport.write(data)
    def connectionLost(self,reason):
            self.transport.loseConnection()
            self.server.transport.loseConnection()

            
class Clienttransfer(Protocol):
    def __init__(self):
            pass
    def set_protocol(self,p):
            self.server = p
            self.server.transport.resumeProducing()
            pass
    def dataReceived(self,data):
            self.server.transport.write(data)
            pass
            
            
if __name__ == "__main__":
    print 'Redis'
    rs = conn_redis(redis_host = 'localhost',redis_db = '3')
    print rs.keys('*')
    factory = Factory()
    factory.protocol = Transfer
    reactor.listenTCP(5050,factory)
    reactor.run()
