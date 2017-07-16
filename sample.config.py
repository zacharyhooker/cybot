from cybot import Client
import requests as req
from urllib.parse import urlparse
from socketIO_client import SocketIO

"""
TODO: Bootstrap this whole connection scheme.
The SIO client is finicky with it's initalization
"""
config = {
    'route': {
        'imdbot':
        {
            'perds': '\[([^\s]+) [0-9]+ :perdgive: #!# ([0-9]*)',
            'jumble': 'word: (.*)\]'
        }
    },
    'response': {
        'catboy': 'Meow, meow. Meow. <3 %s',
        'bdizzle': 'Please no.',
        'generic':
        [
            'I love you %s! -%s',
            '%s is the best. -%s',
            '%s: Thanks for everything, %s.'
        ]
    }
}


def connect(channel, username, password):
    url = 'http://%s/socketconfig/%s.json' % ('cytu.be', channel)
    server_list = req.get(url).json()['servers']
    server = [i['url'] for i in server_list if i['secure'] is False][0]
    url = urlparse(server)
    sio = SocketIO(url.hostname, url.port, Client)
    instance = sio.get_namespace()
    instance.config(config)
    instance.login(channel, username, password)
    sio.wait()


if __name__ == '__main__':
    connect('channel', 'username', 'password')
