import sys
import socket
import string
import irc
import tweepy
import tweepy.cursor as cursor
import random
import time

HOST="irc.enterthegame.com"
PORT=6667
NICK="pokerbot"
IDENT="pokerbot"
REALNAME="pureevil"
INI="gsbot.ini"
NAME_TO_BOT="GSElevator"
USER_TIMELINE_MAX=3200
class Bot(object):
    
    commands = [ "!tweet", "!rtweet" ]
    followed_users = {}
    def __init__(self,
                 host=HOST,
                 port=PORT,
                 nick=NICK,
                 ident=IDENT,
                 realname=REALNAME,
                 followed_users={}):
        self.user = irc.User(nick=nick, ident=ident, realname=realname)
        import copy
        self.followed_users = copy.deepcopy(followed_users)
        self.server = irc.Server(self.user, host=host, port=port)
        self.server.connect()
        
    def display_followed_users(self):
        return ' '.join(self.cache.keys())
        
    def join_room(self, room_name):
        self.server.join_room(room_name)
        
    def message_room(self, room_name, message):
        msg = irc.Message(message)
        self.server.message_room(room_name, msg)
        
    def set_cache(self, cache):
        self.cache = cache
        
    def random_message(self, room_name):
        if len(self.cache) > 0:
            self.message_room( room_name, self.cache[ random.randrange(0, len(self.cache)) ] )
    
            
    def random(self, user_name):
        if len(self.cache) > 0:
            return self.cache[ user_name ][ random.randrange(0, len(self.cache[ user_name ])) ]
        else:
            return "no messages.  cache not set"

    def last_tweet(self, user_name):
        if len(self.cache) > 0:
            try:
                return self.cache[ user_name ][ 0 ]
            except:
                return "poker bot isn't following that person.  try:" + self.display_followed_users()
        
    def get_word_after_command(self, command):
        concat_cache = ' '.join( self.server.cache[0] )
        index = concat_cache.find(command)
        first_char = index+len(command)+1
        first_char = concat_cache[first_char:].find(' ') + first_char + 1
        last_char = concat_cache[first_char:].find(' ') - 1
        if last_char <= 0:
            last_char = len(concat_cache)
        print concat_cache[first_char:last_char]
        word = concat_cache[first_char:last_char]
        print self.cache
        print command
        print concat_cache
        print index
        print first_char
        print last_char
        print word
        return word
        

    
    def handle_command(self, command, room_name="poker"):
        user_name = self.get_word_after_command(command)
        
        if command == "!tweet":
            self.message_room(room_name,
                              "@"+user_name + ": " + self.last_tweet(user_name))
            
        if command == "!rtweet":
            self.message_room(room_name,
                              "@"+user_name + ": " + self.random(user_name))
    
        
    def idle(self):
        
        while True:
            time.sleep(1)
            if len(self.server.cache) > 0:
                concat_cache = ''.join( self.server.cache[0] )
                for command in self.commands:
                    if concat_cache.find( command ) > 0:
                        self.handle_command(command)
                        
            self.server.idle()
                        
                        
                
    
def grab_tweets(params):
    auth = tweepy.auth.OAuthHandler(params['oauth']['consumer_key'],
                                        params['oauth']['consumer_secret'])
    auth.set_access_token(params['oauth']['access_token'],
                          params['oauth']['access_token_secret'])
    
    api = tweepy.API(auth_handler=auth, secure=True, retry_count=3)
    friends = api.friends_ids()
    user_id = 0
    followed_users = {}
    
    for friend in friends[0]:
        u = api.get_user(friend)
        """
        if str(u.screen_name).lower() != 'ctide':
            continue
        """ 
        followed_users[ str(u.screen_name).lower() ] = friend
    
    #page_limit = 5000
    tweet_blocks = []
    total = 0
    
    tweets_by_user = {}
    for followed in followed_users:
        user_id = followed_users[ followed ] 
        tweets = api.user_timeline(id=user_id, count=USER_TIMELINE_MAX)
        total = total + len( tweets )
        print "tweets for", followed, len(tweets)
        tweets_by_user[followed] = []
        for tweet in tweets:
            tweets_by_user[followed].append( tweet.text )
        
    return tweets_by_user
        
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
    room_name = "poker"
    params = parse_ini(sys.argv[1])
    print "proecssing tweets"
    tweets = grab_tweets(params)
    print "got: ", len(tweets), " tweets"
    
    gs = Bot()
    gs.set_cache( tweets )
    gs.join_room(room_name)
    gs.message_room(room_name, "sup, bros")
    gs.idle()    
    gs.server.disconnect()
    