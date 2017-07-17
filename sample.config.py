from cybot import cytube

config = {
    'username': 'username',
    'password': 'password',
    'channel': 'channel',
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


if __name__ == '__main__':
    cytube(config)
