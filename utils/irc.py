import sys
import socket
import string

class Server(object):
    """object to handle an irc server
    Idea is to have a Server manage a single connection to an irc server,
    and let a user join rooms, send messages to rooms, send messages to users on
    this network, and do all of the operations you can think of on an irc
    server connection.
    
    Notes:
        1:  thing to note about the implementation, rooms are a simple k,v dict
            and it's assumed you can only have 1 room with 1 name
        2:  you can only send messages to rooms you've joined
        3:  you can only leave rooms you've joined
    """
    host = "irc.enterthegame.com"
    port = 6667
    cache = []
    readbuffer=""
    def __init__(self, user, host=host, port=port):
        self.user = user
        self.host = host
        self.port = port
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.rooms = {}
        
    def connect(self):
        self.sock.connect( (self.host, self.port) )
        self.sock.send("NICK %s\r\n" % self.user.nick )
        self.sock.send("USER %s %s bla :%s\r\n" % ( self.user.ident, self.host, self.user.realname))
        
    def join_room(self, room_name):
        room = Room(room_name)
        self.sock.send("JOIN #%s \r\n" % room.name )
        self.rooms[ room.name ] = room
        
    def message_room(self, room_name, message):
        if room_name in self.rooms:
            self.sock.send("PRIVMSG #%s :%s\r\n" % (room_name, message.content) )
            
    def leave_room(self, room_name):
        if room_name in self.rooms:
            self.sock.send("PART #%s \r\n" % room_name )
            self.rooms[ room_name ] = None
    
    def idle(self, clear_cache=True):
        
        if clear_cache:
            self.cache = []
        readbuffer = self.sock.recv(1024)
        temp=string.split(readbuffer, "\n")
        readbuffer=temp.pop( )

        for line in temp:
            line=string.rstrip(line)
            line=string.split(line)
            self.cache.append(line)
            if(line[0]=="PING"):
                self.sock.send("PONG %s\r\n" % line[1])
            if(line[0] == "PRIVMSG"):
                print "\n\n woo priv msg"
                print line
            

    def disconnect(self):
        
        for room in self.rooms:
            self.leave_room(room)
        self.sock.close()
        
class User(object):
    
    nick = "default"
    ident = "default"
    realname = "default"
    
    def __init__(self, nick=nick, ident=ident, realname=realname):
        self.nick = nick
        self.ident = ident
        self.realname = realname
    
    
class Room(object):
    
    def __init__(self, name):
        self.name = name

class Message(object):
    
    def __init__(self, content):
        self.content = content

if __name__ == '__main__':
    
    usr = User(ident="test")
    print usr.nick
    print usr.ident
    print usr.realname
