from conexion import Connection
import time
conection = Connection.redisConnection()
client = conection.conected()
p=client.pubsub()

def createUser(name,password):
    if client.hget('users',name):
        print('username not available')
        return None
    id = client.incr('user:id:')
    client.hset('users', name,id)
    print client.hkeys('users')
    client.hmset(id,{
        'username':name,
        'password':password,
        'channel': str(id)+'ch'
    })
    return id

def login(id,password):
    if client.hget(str(id)+'cookie','cookie') == str(id):
        print("Welcome back!")
        return True
    if client.hget(id,'password') == password:
        client.hset(str(id)+'cookie','cookie',id )
        client.expire(str(id)+'cookie', 604800)
        print("succesfull login!")
        return True
    else:
        print ("login failed!")
        return False



def getUserName(id):
    name=client.hget(id,'username')
    return name

def getId(name):
    name= client.hget('users', name)
    return name

def getChannel(id):
    channel=client.hget(id,'channel')
    return channel

def addStream(id,streamName, hashtags):
    if not client.hget('users',getUserName(id)):
        print('there is no user with that id')
        return None
    name='vid'+str(id)+streamName
    client.hmset(name,{'Active':True,'date':time.strftime('%d%m%y%H%M%S'),'stream name':streamName,'Likes':0})
    for object in hashtags:
        client.sadd('#'+ name,object)
    client.publish(getChannel(id), 'stream '+ streamName + 'has started')

def closeStream(id, streamName):
    client.hset('vid'+str(id)+streamName, 'Active', False)

def follow(idFollower, idFollowed):
    if not client.hget('users',getUserName(idFollowed)):
        print('the user you want to follow doesnt exist')
        return None
    if(client.hget(str(idFollowed) + 'FWR',idFollower)):
        print('You already follow this user')
        return None
    client.hset(str(idFollowed) + 'FWR', idFollower,getUserName(idFollower))
    client.hset(str(idFollower)+'FWD',idFollowed,getUserName(idFollowed))
    p.subscribe(getChannel(idFollowed))
    print(getUserName(idFollower) + ' now follows ' + getUserName(idFollowed))

def searchVideoById(id,active):
    listActive=[]
    listClosed=[]
    for object in  client.scan_iter(match='vid'+str(id)+'*'):
            if(client.hget(object,'Active'))=='True':
                listActive.append(object)
            else:
                listClosed.append(object)
    if(active):
        return sortVideos(listActive)
    return sortVideos(listClosed)
    return sortVideos(listClosed)

def promote(retransmision, id):
    client.sadd('like'+retransmision, getUserName(id))
    client.sadd(id+'likedVideos', retransmision)
    client.hincrby(retransmision, 'Likes', 1)
    client.publish('promo' + retransmision + 'channel', getUserName(id) + ' liked this stream')
    p.subscribe('promo'+retransmision+'channel')

def searchByHashtag(hashtag,active):
    listActive = []
    listClosed = []
    for object in client.scan_iter(match='vid*'):
        if (hashtag in client.smembers('#' + object)):
            if (client.hget(object, 'Active')) == 'True':
                listActive.append(object)
            else:
                listClosed.append(object)
    if (active):
        return sortVideos(listActive)
    return sortVideos(listClosed)

def comment(retransmision, id,message):
    client.hset(str(id)+'comments',retransmision,message)
    client.publish('comment' + retransmision + 'channel', getUserName(str(id) + ': ' + message))
    p.subscribe('comment'+retransmision+'channel')
def sortVideos(list):
    lista=[]
    client.delete('sortedVideos')
    for object in list:
        client.zadd('sortedVideos', client.hget(object, 'date'), object);
    for object in client.zrevrange('sortedVideos', 0, -1):
        lista.append(object)
    return lista
def allStreams():
    lista=[]
    max=3;
    for object in client.scan_iter(match='vid*'):
        if (len(lista)<max):
            lista.append(object)
    return sortVideos(lista)
    return lista

if __name__ == "__main__":


    #cliente.hmset('user1',{'idUs':'1','password':'1234'})
    #cliente.hset('users','dawik',1)
    #print createUser('testing','123')

    #login(10,'321')
    #print cliente.hget(9,'password')
    #paco = 1
    #print str(paco)+'paco'
    #addStream(9, 'LOL')
    #print client.hgetall('9Vdo')
    #print getUserName(10)
    #follow(9,1)
    #print client.hvals(str(1)+'FWR')
    #print createUser('hiper','123')
    #login(11,'123')
    #hashtags=['#1','#2','#18']
    #closeStream(4,'bellesa')
    #addStream(12,'video5',hashtags)
    #print client.zrevrange('allvideos', 0, -1)
    #print searchByHashtag('#18',True)
    #print searchVideoById(12,True)
    #comment('vid11bellesa',1,'que guapo tio')
    #comment('vid11bellesa',2,'ya bes coleja')
    #print client.hvals('1comments')
    #print allStreams()