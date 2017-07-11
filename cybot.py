# encoding: utf-8
import requests as req
from msg import Msg
import threading
from foaas import fuck
from socketIO_client import BaseNamespace


def check_init(func):
    """If the init var is not set we need to wait to call the function
    until the client has fully initialized"""

    def wrapper(self, *args, **kwargs):
        if not self.init:
            pass
        else:
            return func(self, *args, **kwargs)
    return wrapper


class Client(BaseNamespace):

    route = {
        'imdbot':
        {
            'perds': '\[([^\s]+) [0-9]+ :perdgive: #!# ([0-9]*)',
            'jumble': 'word: (.*)\]'
        }
    }

    def initialize(self):
        """Secondary __init__ created for the SocketIO_client instantiation method
        """
        self.voteskips = []
        self.userlist = []
        self.media = []
        self.init = False
        self.handout()

    def login(self, channel, username, password):
        """Simple login to the websocket. Emits the params to the
        websocket.

        Args:
            channel (str): Channel to join on login
            username (str): Username of account to login
            password (str): Password of account to control
        """
        self.username = username
        self.channel = channel
        self.emit('initChannelCallbacks')
        self.emit('joinChannel', {'name': channel})
        self.emit('login', {'name': username, 'pw': password})

    def chat_voteskip(self, msg, *args):
        sent = False
        if(self.media and self.media['id'] not in self.voteskips):
            self.emit('voteskip', {})
            self.voteskips.append(self.media['id'])
            sent = True
        return sent

    def chat_fuck(self, msg, *args):
        args = [item for sublist in args for item in sublist]
        fmsg = fuck.random(from_=msg.username)
        if len(args) > 0:
            fmsg = fuck.random(from_=msg.username, name=args[0])
        data = Msg({'msg': fmsg.text})
        self.sendmsg(data)
        return True

    def chat_jumble(self, msg):
        if msg['match']:
            x = req.get('http://www.anagramica.com/best/' + msg['match'])
            word = x.json()['best'][0]
            print('Anagram Guessing:' + word)
            if len(msg['match']) == len(word):
                self.sendmsg('$j ' + word)

    def sendmsg(self, msg):
        if(msg.to):
            self.emit('pm', {'msg': msg.body, 'meta': {}, 'to': msg.to})
        else:
            self.emit('chatMsg', {'msg': msg.body, 'meta': {}})

    def handout(self):
        t = threading.Timer(60 * 61, self.handout)
        t.daemon = True
        t.start()
        self.sendmsg(Msg({'body': '$handout'}))

    @check_init
    def handle_msg(self, msg):
        ret = False
        if(msg.text.startswith('!')):
            cmd = msg.text.split()
            call = cmd[0][1:]
            args = cmd[1:]
        if(self.route):
            for user, funcs in self.route:
                if(msg.username == user):
                    for func, sstr in funcs:
                        match = msg.search_body(sstr)
                        if(match):
                            cmd = func
                            args = match
        call = 'chat_' + cmd
        if(msg.to):  # It's a PM
            call = 'pm_' + cmd
        try:
            func = getattr(self, call)
            if callable(func):
                ret = func(msg, args)
        except Exception as e:
            print('Exception[%s]: %s' % (e, msg))
            if not ret:
                data = {'body': '(%s) failed to run.' % (cmd[0]),
                        'to': msg.username}
        self.sendmsg(Msg(data))

    def on_chatMsg(self, omsg):
        msg = Msg(omsg)
        self.handle_msg(msg)

    def on_changeMedia(self, *args):
        if(args[0]['id']):
            self.media = args[0]

    def on_userlist(self, *args):
        self.userlist = args[0]
        self.init = True

    def on_pm(self, omsg):
        msg = Msg(omsg)
        self.handle_msg(msg)

    def on_userLeave(self, *args):
        self.userlist[:] = [d for d in self.userlist if d[
            'name'] == args[0]['name']]

    def on_addUser(self, *args):
        self.userlist.append(args[0])

    def on_connect(self):
        print('[Connected]')

    def on_event(self, *args):
        pass

    def on_emoteList(self, *args):
        pass

    def on_channelCSSJS(self, *args):
        pass

    def on_setMotd(self, *args):
        pass

    def on_setPlaylistMeta(self, *args):
        pass

    def on_channelOpts(self, *args):
        pass

    def on_mediaUpdate(self, *args):
        pass
