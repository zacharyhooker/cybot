import re

"""
TODO: Generic init for SocketIO emits
"""


class Msg:

    def __init__(self, data, **kwargs):
        """TODO: Data to become body/text of message, kwargs to
        expand into secondary/non-essential features of a message.
        Most Msgs sent over Socketio have a similar attributes.
        Generalize field names."""
        default = {'username': None, 'msg': None, 'text': None,
                   'meta': {}, 'to': None, 'time': None}
        default.update(data)
        self.username = default['username'].lower() if default[
            'username'] else default['username']
        if 'body' in default:
            self.body = default['body']
        elif 'msg' in default:
            self.body = default['msg']
        else:
            self.body = None
        self.meta = default['meta']
        self.time = default['time']
        if 'to' in default:
            self.to = default['to']
        else:
            self.to = None
        self.text = self._strip_text(self.body)

    def search_body(self, regstr: str):
        return re.findall(regstr, self.body)

    def _strip_text(self, text):
        regstr = re.sub('<.*?>', '', text).strip()
        return regstr.encode('ascii', 'ignore').decode('utf-8')

    def __str__(self):
        tmp = self.__dict__
        if 'text' in tmp:
            tmp.pop('body', None)
        return str(tmp)
