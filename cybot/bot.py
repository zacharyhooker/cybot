# encoding: utf-8
import logging as log
import requests as req
from .msg import Msg
from .wallet import Wallet
from .timer import Timer
import threading
from functools import wraps
from foaas import fuck
import random
from socketIO_client_nexus import BaseNamespace
import re
import sys
import os
import giphypop
import html#just fo' the trivia. Ew.
from bs4 import BeautifulSoup as Soup
from imgurpython import ImgurClient
import tmdbsimple as tmdb


log.getLogger(__name__).addHandler(
    log.NullHandler())
log.basicConfig(level=log.INFO)

chatlog = log.getLogger('chat')
chatlog.addHandler(log.FileHandler('log/chat.log'))
chatlog.setLevel(log.INFO)


def check_init(func):
    """If the init var is not set we need to wait to call the function
    until the client has fully initialized | Decorator"""

    def wrapper(self, *args, **kwargs):
        if not self.init:
            pass
        else:
            return func(self, *args, **kwargs)
    return wrapper

def run_async(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = threading.Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl
    return async_func

class Client(BaseNamespace):

    def initialize(self):
        """Secondary __init__ created for the SocketIO_client instantiation method
        """
        self.voteskips = []
        self.response = {}
        self.route = {}
        self.userlist = []
        self.poll = []
        self.media = []
        self.init = False
        self.question = None
        self.jumble = None
        self.imgur = None

    def config(self, config):
        if 'response' in config:
            self.response = config['response']
        if 'route' in config:
            self.route = config['route']
        if all(k in config for k in ('channel', 'username', 'password')):
            self.login(config['channel'], config['username'],
                       config['password'])
        if 'tmdbapi' in config:
            tmdb.API_KEY = config['tmdbapi']
        if 'giphyapi' in config:
            self.giphy = giphypop.Giphy(api_key=config['giphyapi'])
        if 'timeout' in config:
            self.timeout = config['timeout']
        if 'cost' in config:
            self.cost = config['cost']
        if 'imgur' in config:
            self.imgur = ImgurClient(config['imgur']['client_id'],
            config['imgur']['client_secret'])

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
        msg.to = msg.username
        self.emit('voteskip', {})

    def pm_kill(self, msg, *args):
        if(msg.username == 'zim'):
            exit()

    def chat_give(self, msg, *args):
        omsg = msg
        omsg.body = 'test'
        if(len(args) > 0):
            wFrom = Wallet(msg.username)
            to = args[0][0]
            amt = int(args[0][1])
            if amt <= 0 or (to == msg.username):
                omsg.to = msg.username
                omsg.body = 'Bruh, really?'
            elif(wFrom.balance < amt):
                omsg.to = msg.username
                omsg.body = 'Give: Insufficient funds.'
            else:
                wTo = Wallet(to)
                wFrom.transaction(-amt)
                wTo.transaction(amt)
                omsg.body = '{} gave {} {} squids!'.format(
                    msg.username, to, amt)
        else:
            omsg.body = 'The syntax is !give <username> <amount>'
            omsg.to = msg.username
        self.sendmsg(omsg)

    def chat_help(self, msg, *args):
        msg.to = msg.username
        meth = dir(self)
        lst = []
        for cmd in meth:
            if 'chat_' in cmd:
                lst.append(cmd[5:])
        msg.body = "This is an experimental feature, some of these may not work.\n"
        msg.body += ', '.join(lst)
        self.sendmsg(msg)

    def getUser(self, name):
        for usr in self.userlist:
            if 'name' in usr and name in usr['name']:
                return usr

    def x_imgur(self, msg, *args):
        if(args[0]):
            search = self.imgur.gallery_search(' '.join(args[0]), window='all',
                    sort='time', page=0)
        else:
            search = self.imgur.gallery_random()
        if len(search)>0:
            item = random.choice(search)
            if item.is_album:
                choice = random.choice(self.imgur.get_album_images(item.id))
                choice = choice.link
            else:
                choice = item.link
        else:
            out = 'There were no results for that request.'
        self.emit('pm', {'msg': out, 'meta': {}, 'to': msg.to})

    def chat_giphy(self, msg, *args):
        if(args[0]):
            x = self.giphy.search(' '.join(args[0]), rating='pg-13')
            for y in x:
                out = y.media_url + '.pic'
                self.sendmsg(out)
                return
            out = 'There were no PG-13 results for that request.'
            self.sendmsg(out)

    def chat_slots(self, msg, *args):
        if(args[0]):
            wallet = Wallet(msg.username)
            timer = Timer(msg.username, 'slots')
            cost = 0
            if args[0][0].isdigit():
                cost = -abs(int(args[0][0]))
            else:
                self.sendmsg('Please place a numeric bet.')
                return

            chk = timer.check(self.timeout['slots'])
            if(not chk['ready']):
                timetil = chk['timetil'] / 60
                self.sendmsg('Try again in {} minute(s).'.format(timetil))
                return
            else:
                cost = abs(int(args[0][0]))
                if wallet.balance >= cost:
                    wallet.transaction(-cost)
                    serverWallet = Wallet('{{server}}')
                    lst = [0]*5 + [1]*5 + [2]*5+[3]*5+[4]*2+[5]
                    x, y, z = random.choices(lst, k=3)
                    prizemsg = ":botchat3:"
                    translate = ['♥', '♣', '♠', '♪','♀', '♦']
                    prizemsg = "| {} | {} | {} |\n".format(
                        translate[x], translate[y], translate[z])

                    if 5 in (x, y, z) and (x == y == z):
                        cost = serverWallet.balance
                        wallet.transaction(cost)
                        serverWallet.transaction(-abs(serverWallet.balance))
                        prizemsg += '{} hit the jackpot! They have earned {} squids!'.format(
                            msg.username, cost)
                    elif (x == y == z) and max(x, y, z) < 4:
                        wallet.transaction(cost * 3)
                        prizemsg += '{} matches 3 (three) fruits! [3x] Multiplyer (Bal: {})'.format(
                            msg.username, wallet.balance)
                    elif 5 in (x,y,z) and len({x,y,z})==2:
                        wallet.transaction(cost*2)
                        prizemsg += '{} got a diamond and two matches. [2x] (Bal: {})'.format(msg.username, wallet.balance)
                    elif 5 in (x, y, z) and len({x, y, z}) == 3:
                        wallet.transaction(cost)
                        prizemsg += '{} breaks even with 1 (one) diamond. [1x] (Bal: {})'.format( msg.username, wallet.balance)
                    elif len({x, y, z}) == 2:
                        wallet.transaction(2 * cost)
                        prizemsg += '{} matches 2! [2x] Multiplyer (Bal: {})'.format(
                            msg.username, wallet.balance)
                    else:
                        serverWallet.transaction(cost)
                        prizemsg += '{}, better luck next time. (Bal: {})'.format(
                            msg.username, wallet.balance)
                    self.sendmsg(prizemsg)
                    timer.setTimer()
                else:
                    msg.to = msg.username
                    msg.body = 'Slots: Insufficient funds.'
                    self.sendmsg(msg)

    def chat_trivia(self, msg, *args):
        if not self.question:
            r = req.get('https://opentdb.com/api.php?amount=1')
            self.question = r.json()['results'][0]
            sub = 'True/False' if any(s in self.question['correct_answer'] for s in ('True', 'False')) else None
            body = '{}(Category: {}) {}'.format('['+sub+']' if sub else '', self.question['category'], html.unescape(self.question['question']))
            self.sendmsg(body)
        else:
            sub = 'True/False' if any(s in self.question['correct_answer'] for s in ('True', 'False')) else None
            body = '{}(Category: {}) {}'.format('['+sub+']' if sub else '', self.question['category'], html.unescape(self.question['question']))
            self.sendmsg(body)
        if(self.question['type']=='multiple'):
            choices = self.question['incorrect_answers']
            choices.append(self.question['correct_answer'])
            random.shuffle(choices)
        #    self.sendmsg("Choices: {}".format(html.unescape(','.join(choices))))

    def chat_nq(self, msg, *args):
        w = Wallet(msg.username)
        if(w.balance >= 100):
            w.transaction(-100)
            self.question = None
            self.sendmsg('{} spent 100 squids to skip the question.\
                    ({})'.format(msg.username, w.balance))

    def chat_a(self, msg, *args):
        if(len(args[0])>0):
            ans = html.unescape(' '.join(args[0]).lower())
            if(html.unescape(self.question['correct_answer'].lower().rstrip().lstrip()) == ans):
                w = Wallet(msg.username)
                w.transaction(100)
                self.sendmsg('{} got it right! (100 Squids)'.format(msg.username))
                self.question=None
        else: 
            return

    def chat_hint(self, msg, *args):
        if self.question:
            body = ' '.join([''.join(random.sample(word, len(word))) for word
                    in html.unescape(self.question['correct_answer']).split()])
            self.sendmsg(body)

    def chat_love(self, msg, *args):
        data = {'msg': 'No love.'}
        if args[0]:
            args = args[0]
        to = args[0] if len(args) > 0 else self.username
        frm = args[1] if len(args) > 1 else msg.username
        if(msg.username in self.response):
            data['msg'] = self.response[
                msg.username].format(to, frm)
        else:
            data['msg'] = random.choice(
                self.response['generic']).format(to, frm)

        self.sendmsg(Msg(data))

    def chat_squids(self, msg, *args):
        wallet = Wallet(msg.username)
        self.sendmsg(Msg({'body': '{0} has {1} squids.'.format(
            msg.username, wallet.balance)}))

    def chat_skin(self, msg, *args):
        search = tmdb.Search()
        body = 'No sexual parental guide found'
        if len(args) > 0:
            response = search.movie(query=' '.join(args[0]))
            if search.results:
                mid = search.results[0]['id']
                movie = tmdb.Movies(mid)
                info = movie.info()
                if 'imdb_id' in info:
                    t = req.get('https://www.imdb.com/title/'+info['imdb_id']+'/parentalguide')
                    advise = Soup(t.content).find('section', id='advisory-nudity')
                    if advise:
                        body = ''
                        items = advise.find_all('li', 'ipl-zebra-list__item')
                        for item in items:
                            body += item.contents[0].strip().replace('\n', '.').replace('-', ' ')
        msg.body = '/sp '+body
        self.sendmsg(msg)

    def chat_trailers(self, msg, *args):
        search = tmdb.Search()
        vids = {}
        msg.to = msg.username
        regex = re.compile('[^a-zA-Z ]')
        for movie in self.poll:
            movie = movie.replace('.', ' ')
            movie = regex.sub('', movie)
            response = search.movie(query=movie)
            if search.results:
                mid = search.results[0]['id']
            else:
                break
            movie = tmdb.Movies(mid)
            videos = movie.videos()
            for video in videos:
                if 'results' in videos:
                    for t in videos['results']:
                        if t['type'] == 'Trailer':
                            vids[
                                search.results[0]['title']] = t['key']
        for title, vid in vids.items():
            msg.body = title + ': http://youtube.com/watch?v=' + vid
            self.sendmsg(msg)
            for user in self.userlist:
                if(user['name'].lower() == msg.username.lower() and user['rank'] > 1):
                    if any(t['key'] in s for s in self.media):
                        msg.body = title + ' already exists in queue.'
                        self.sendmsg(msg)
                    else:
                        self.queue(vid, True)

    def pm_debug(self, msg, *args):
        if msg.username == 'zim':
            msg.to = 'zim'
            for x in self.media:
                msg.body = ''.join(x)
                self.sendmsg(msg)

    def chat_choose(self, msg, *args):
        if args[0]:
            msg.body = random.choice(args[0])
            self.sendmsg(msg)

    def chat_fuck(self, msg, *args):
        args = args[0]
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
        if(len(args) > 0):
            msg.to = msg.username
            msg.body = 'Thank you for rating, wzrd will be pleased!'
            self.sendmsg(msg)

    def chat_j(self, msg, *args):
        if(len(args[0]) > 0 and self.jumble):
            if ' '.join(args[0]).lower() == self.jumble:
                msg.body = "{} solved the jumble: {}. (50 squids)".format(msg.username,
                        self.jumble)
                wallet = Wallet(msg.username)
                wallet.transaction(50)
                self.jumble = None
                self.sendmsg(msg)
            else:
                pass

    def chat_jumble(self, msg, *args):
        """Attempts to solve an anagram based on letters parsed from handle_msg
        Requests calls based on the arguments and the whole Msg.

        Args:
            match (str): The anagram which has been parsed from the Msg
            to be solved to an english word
        """
        if self.jumble:
            msg.body = ''.join(random.sample(self.jumble, len(self.jumble)))
        else:
            word_site = "https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
            r = req.get(word_site)
            self.jumble = random.choice(r.text.splitlines()).lower()
            msg.body = ''.join(random.sample(self.jumble, len(self.jumble)))
        self.sendmsg(msg)

    def chat_handout(self, msg, *args):
        amt = random.randint(1, 100)
        wallet = Wallet(msg.username)
        timer = Timer(msg.username, 'handout')
        chk = timer.check(self.timeout['handout'])
        if(chk['ready']):
            wallet.transaction(amt)
            timer.setTimer()
        else:
            timetil = chk['timetil'] / 60
            self.sendmsg(
                'Try again in {} minute(s).'.format(timetil))
            return
        balance = wallet.balance
        if(balance):
            self.sendmsg('Here''s {} squids. {} has {} squids!'.format(
                amt, msg.username, balance))
        return

    def qryCur(self, qry):
        self.currencyCur.execute(qry)
        res = self.currencyCur.fetchone()
        self.currencyConn.commit()
        return res

    def chat_catboy(self, msg, *args):
        self.sendmsg(':catfap:')

    def chat_auto(self, msg, *args):
        if(msg.username == 'catboy'):
            if random.random() < 0.02:
                self.sendmsg('Meow')

    def sendmsg(self, msg):
        if(isinstance(msg, str)):
            self.emit('chatMsg', {'msg': msg})
        elif(msg.to):
            self.emit('pm', {'msg': msg.body, 'meta': {}, 'to': msg.to})
        else:
            self.emit('chatMsg', {'msg': msg.body, 'meta': msg.meta})
        log.debug(msg)

    def queue(self, url, after=False):
        data = {"id": url, "type": "yt", "pos": "next", "temp": True}
        self.emit('queue', data)
        self.media.append(url)

    def sendadminmsg(self, msg):
        msg = {'username': None, 'rank': 0}
        for y in self.userlist:
            if(not y['meta']['afk']):
                if(msg['rank'] < y['rank']):
                    msg['username'] = y['name']
                    msg['rank'] = y['rank']

    @check_init
    def jackpot_announce(self):
        timeout = 15 * 60
        if('jackpot' in self.timeout):
            timeout = self.timeout['jackpot']
        t = threading.Timer(timeout, self.jackpot_announce)
        t.daemon = True
        t.start()
        serverWallet = Wallet('{{server}}')
        self.sendmsg('Current jackpot is: {} squids!'.format(
            serverWallet.balance))
        p = random.random()
        if p < 0.0002:
            bal = serverWallet.balance
            amt = random.randint(int(bal / len(str(bal))), int(bal / 2))
            user = random.choice(self.userlist)['name']
            serverWallet.transaction(-amt)
            userWallet = Wallet(user)
            userWallet.transaction(amt)
            self.sendmsg(
                'The accountant made a mistake and {} got {} squids!'.format(user, amt))

    @run_async
    @check_init
    def handle_msg(self, msg):
        chatlog.info(msg)
        ret = False
        cmd = ''
        cnt = False
        if(self.route):
            for user in self.route:
                if(msg.username == user):
                    for func in self.route[user]:
                        match = msg.search_body(self.route[user][func])
                        if(match):
                            dir_cmd = func
                            args = match
                            cnt = True
        if(msg.text.startswith('!') and msg.username):
            cmd = msg.text.split()
            dir_cmd = cmd[0][1:]
            args = cmd[1:]
            cnt = True
        if(cnt):
            call = 'chat_' + dir_cmd
            if(msg.to):  # It's a PM
                call = 'pm_' + dir_cmd
            try:
                func = getattr(self, call.lower())
                if callable(func):
                    if(dir_cmd in self.cost):
                        wallet = Wallet(msg.username)
                        if(wallet.balance < self.cost[dir_cmd]):
                            self.sendmsg('{0} costs {1} squids. {2} has {3}'.format(
                                dir_cmd, self.cost[dir_cmd], msg.username, wallet.balance))
                            return
                        else:
                            wallet.transaction(-self.cost[dir_cmd])
                            self.sendmsg(
                                Msg({'to': msg.username, 'body': 'You spent {0} squids on {1}'.format(self.cost[dir_cmd], dir_cmd)}))

                    log.info('%s : %s' % (func.__name__, msg))
                    ret = func(msg, args)
            except Exception as e:
                log.error('Exception[%s]: %s' % (e, msg))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                log.error(exc_type, fname, exc_tb.tb_lineno)
        return ret

    @run_async
    def on_chatMsg(self, omsg):
        msg = Msg(omsg)
        self.handle_msg(msg)

    def on_changeMedia(self, *args):
        try:
            self.media.remove(args[0]['id'])
        except Exception as e:
            return

    def on_newPoll(self, *args):
        self.poll = []
        for poll in args:
            if 'options' in poll:
                for opt in poll['options']:
                    self.poll.append(opt)

    def on_userlist(self, *args):
        self.userlist = args[0]
        self.userlist.append({'name': self.username})
        self.init = True

    def on_queue(self, *args):
        for arg in args:
            for media in arg:
                if 'media' in media:
                    if media['media']['id'] not in self.media:
                        self.media.append(media['media']['id'])

    def on_pm(self, omsg):
        msg = Msg(omsg)
        self.handle_msg(msg)

    def on_userLeave(self, *args):
        self.userlist[:] = [d for d in self.userlist if d[
            'name'] != args[0]['name']]

    def on_addUser(self, *args):
        self.userlist.append(args[0])

    def on_connect(self):
        log.info('[Connected]')

    def on_disconnect(self):
        raise Exception('disconnected')

    def on_login(self, *args):
        self.jackpot_announce()
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

    def on_playlist(self, *args):
        for arg in args:
            for media in arg:
                if 'media' in media:
                    if media['media']['id'] not in self.media:
                        self.media.append(media['media']['id'])
        log.info('Playlist Loaded')

    def on_channelOpts(self, *args):
        pass

    def on_mediaUpdate(self, *args):
        pass
