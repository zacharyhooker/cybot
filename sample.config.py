from cybot import Client
import requests as req
from urllib.parse import urlparse
from socketIO_client import SocketIO


def connect(channel, username, password):
    url = 'http://%s/socketconfig/%s.json' % ('cytu.be', channel)
    server_list = req.get(url).json()['servers']
    server = [i['url'] for i in server_list if i['secure'] is False][0]
    url = urlparse(server)
    sio = SocketIO(url.hostname, url.port, Client)
    instance = sio.get_namespace()
    instance.login(channel, username, password)
    sio.wait()


if __name__ == '__main__':
    connect('channel', 'username', 'password')
