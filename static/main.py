import json
from browser.html import *
from browser import document, window
from browser.ajax import ajax
from browser.websocket import WebSocket


restaurant_list = document['restaurant-list']


def main():
    ws = WebSocket('ws://' + window.location.host + '/status/')
    ws.bind('open', on_open)
    ws.bind('message', on_message)

def on_open(evt):
    print('Starting...')
    request = ajax()
    request.open('GET', '/start/', True)
    request.send()

def on_message(evt):
    obj = json.loads(evt.data)
    if obj.get('type') == 'console':
        print(obj['value'])
    else:
        print(obj['name'])
        categories = (c['shortName'] for c in obj['categories'])
        restaurant_list <= LI(
            P(A(obj['name'], href=obj['url'])) +
            P(obj['location']['formattedAddress'][0]) +
            P('Category: ' + ', '.join(categories)) +
            P('Rating: %s' % obj['rating'])
        )


main()
