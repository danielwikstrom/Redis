import redis

class redisConnection():
    client=None
    @staticmethod
    def conected():
        redisConnection.client=redis.StrictRedis(host='localhost', port=6379,db=0)
        return redisConnection.client

r=redisConnection.conected()
#r.set('foo','bar')
#print r.get('foo')