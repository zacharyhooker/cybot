from urllib.parse import urlparse
import requests as req
from socketIO_client_nexus import BaseNamespace, SocketIO
from .bot import Client


def cytube(config):
    url = 'http://%s/socketconfig/%s.json' % ('cytu.be', config['channel'])
    server_list = req.get(url).json()['servers']
    server = [i['url'] for i in server_list if i['secure'] is False][0]
    url = urlparse(server)
    sio = SocketIO(url.hostname, url.port, Client)
    instance = sio.get_namespace()
    instance.config(config)
    sio.wait()
