# encoding: utf-8
import logging as log
import requests as req
from msg import Msg
import threading
from foaas import fuck
import random
from socketIO_client_nexus import BaseNamespace, SocketIO
from urllib.parse import urlparse
import gspread


log.getLogger(__name__).addHandler(
    log.NullHandler())
log.basicConfig(level=log.INFO)


def check_init(func):
    """If the init var is not set we need to wait to call the function
    until the client has fully initialized | Decorator"""

    def wrapper(self, *args, **kwargs):
        if not self.init:
            pass
        else:
            return func(self, *args, **kwargs)
    return wrapper


class Client(BaseNamespace):

    def initialize(self):
        """Secondary __init__ created for the SocketIO_client instantiation method
        """
        self.voteskips = []
        self.response = {}
        self.route = {}
        self.userlist = []
        self.media = []
        self.init = False

    def config(self, config):
        if 'response' in config:
            self.response = config['response']
        if 'route' in config:
            self.route = config['route']
        if all(k in config for k in ('channel', 'username', 'password')):
            self.login(config['channel'], config['username'],
                       config['password'])

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
        """An example of executing arbitrary messages through chat.
        Stores all media in `media`. Flags the skips.
        """
        sent = False
        if(self.media and self.media['id'] not in self.voteskips):
            self.emit('voteskip', {})
            self.voteskips.append(self.media['id'])
            sent = True
        return sent

    def pm_kill(self, msg, *args):
        if(msg.username == 'zim'):
            exit()

    def chat_love(self, msg, *args):
        data = {'msg': 'No love.'}
        if(msg.username in self.response):
            data['msg'] = self.response[
                msg.username].format(args[0], msg.username)
        else:
            data['msg'] = random.choice(
                self.response['generic']).format(args[0], msg.username)

        self.sendmsg(Msg(data))

    def chat_fuck(self, msg, *args):
        fmsg = fuck.random(from_=msg.username)
        if len(args) > 0:
            fmsg = fuck.random(from_=msg.username, name=args[0])
        data = Msg({'msg': fmsg.text})
        self.sendmsg(data)
        return True

    def chat_rate(self, msg, *args):
        """TODO: If the socket app does not support media, allow this to wait
        for a callback; this will let users rate functionality?
        (SCOPE CREEP)"""
        if(args[0]):
            print('rated %s, %s, %s %s' %
                  (self.media['id'], self.media['title'],
                   self.media['type'], args[0]))

    def chat_jumble(self, msg, *args):
        """Attempts to solve an anagram based on letters parsed from handle_msg
        Requests calls based on the arguments and the whole Msg.

        Args:
            match (str): The anagram which has been parsed from the Msg
            to be solved to an english word
        """
        x = req.get('http://www.anagramica.com/best/' + args[0])
        word = x.json()['best'][0]
        log.info('Anagram Guessing:' + word)
        if len(args[0]) == len(word):
            data = {'body': '$j ' + word}
            self.sendmsg(Msg(data))

    def chat_catboy(self, msg, *args):
        data = {'body': 'Meow'}
        self.sendmsg(Msg(data))

    def sendmsg(self, msg):
        if(msg.to):
            self.emit('pm', {'msg': msg.body, 'meta': {}, 'to': msg.to})
        else:
            self.emit('chatMsg', {'msg': msg.body, 'meta': msg.meta})
        log.debug(msg)

    def handout(self):
        t = threading.Timer(60 * 61, self.handout)
        t.daemon = True
        t.start()
        self.sendmsg(Msg({'body': '$handout'}))

    @check_init
    def handle_msg(self, msg):
        ret = False
        cmd = ''
        cnt = False
        if(msg.text.startswith('!')):
            cmd = msg.text.split()
            dir_cmd = cmd[0][1:]
            args = cmd[1:]
            cnt = True
        if(self.route):
            for user in self.route:
                if(msg.username == user):
                    for func in self.route[user]:
                        match = msg.search_body(self.route[user][func])
                        if(match):
                            dir_cmd = func
                            args = match
                            cnt = True
        if(cnt):
            call = 'chat_' + dir_cmd
            if(msg.to):  # It's a PM
                call = 'pm_' + dir_cmd
            try:
                func = getattr(self, call.lower())
                if callable(func):
                    ret = func(msg, *args)
            except Exception as e:
                log.error('Exception[%s]: %s' % (e, msg))
#               data = {'body': '(%s) failed to run.' % (cmd),
#                       'to': msg.username}
        return ret
#           self.sendmsg(Msg(data))

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
        log.info('[Connected]')
        self.handout()

    def on_login(self, *args):
        if(not args[0]['success']):
            log.error(args[0]['error'])
            raise SystemExit

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


def cytube(config):
    url = 'http://%s/socketconfig/%s.json' % ('cytu.be', config['channel'])
    server_list = req.get(url).json()['servers']
    server = [i['url'] for i in server_list if i['secure'] is False][0]
    url = urlparse(server)
    sio = SocketIO(url.hostname, url.port, Client)
    instance = sio.get_namespace()
    instance.config(config)
    sio.wait()
