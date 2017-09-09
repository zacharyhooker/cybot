from cybot import cytube

config = {
    'username': 'username',
    'password': 'password',
    'channel': 'channel',
    'tmdbapi': 'KEY',
    'giphyapi': 'KEY',
    'route': {
        'imdbot':
        {
            'perds': '\[([^\s]+) [0-9]+ :perdgive: #!# ([0-9]*)',
            'jumble': 'word: (.*)\]'
        },
        'catboy': {
            'auto': '(.*)'
        }
    },
    'response': {
        'zim': 'Meow, meow. Meow. <3 {}',
        'bdizzle': 'Please no.',
        'generic':
        [
            'I love you {}! -{}',
            '{} is the best. -{}',
            '{}: Thanks for everything, {}.'
        ]
    }
}

if __name__ == '__main__':
    cytube(config)
