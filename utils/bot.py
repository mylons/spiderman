import sys
import socket
import string
import irc
import tweepy
import tweepy.cursor as cursor
import random

HOST="irc.enterthegame.com"
PORT=6667
NICK="goldman-sachs-elevator"
IDENT="goldman-sachs-elevator"
REALNAME="pureevil"
INI="gsbot.ini"
NAME_TO_BOT="GSElevator"
class Bot(object):
    
    def __init__(self,
                 host=HOST,
                 port=PORT,
                 nick=NICK,
                 ident=IDENT,
                 realname=REALNAME):
        self.user = irc.User(nick=nick, ident=ident, realname=realname)
        self.server = irc.Server(self.user, host=host, port=port)
        self.server.connect()
        
    
    def join_room(self, room_name):
        self.server.join_room(room_name)
        
    def message_room(self, room_name, message):
        msg = irc.Message(message)
        self.server.message_room(room_name, message)
        
    def set_cache(self, cache):
        self.cache = cache
        
    def random_message(self, room_name):
        if len(self.cache) > 0:
            self.message_room( room_name, self.cache[ random.randrange(0, len(self.cache)) ] )

def grab_tweets(params):
    auth = tweepy.auth.OAuthHandler(params['oauth']['consumer_key'],
                                        params['oauth']['consumer_secret'])
    auth.set_access_token(params['oauth']['access_token'],
                          params['oauth']['access_token_secret'])
    
    api = tweepy.API(auth_handler=auth, secure=True, retry_count=3)
    print api.me().name
    friends = api.friends_ids()
    user_id = 0
    for friend in friends[0]:
        u = api.get_user(friend)
        if str(u.screen_name).lower() == NAME_TO_BOT.lower():
            user_id = friend
            break
    
    page_limit = 5000
    tweet_blocks = []
    total = 0
    
    for i in xrange(page_limit):
        tweet_blocks.append( api.user_timeline(id=user_id, page=i) )
        tmp = total + len( tweet_blocks[-1] )
        if tmp == total:
            break
        total = tmp
        
    text_list = []
    for tweets in tweet_blocks:
        for tweet in tweets:
            text_list.append( tweet.text )
    
    return text_list
        
def parse_ini(ini):
    fp = open(ini, "r")
    params = {}
    for line in fp:
        line = line.rstrip()
        tokens = line.split('=')
        value = tokens[-1]
        param_super_name = tokens[0]
        param_tree = param_super_name.split('.')
        try:
            params[ param_tree[0] ][ param_tree[1] ] = value
        except KeyError:
            params[ param_tree[0] ] = {}
            params[ param_tree[0] ][ param_tree[1] ] = value

    return params

if __name__ == '__main__':
    params = parse_ini(sys.argv[1])
    print "proecssing tweets"
    tweets = grab_tweets(params)
    print "got: ", len(tweets), " tweets"
    
    gs = Bot()
    #gs.get_cache_tweets()
    gs.join_room("poker")
    gs.message_room("poker", tweets[0])
    gs.server.disconnect()
    