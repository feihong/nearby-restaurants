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
        # print(obj['name'])
        restaurant_list <= LI(
            get_name_el(obj) +
            DIV(obj['location']['address']) +
            get_category_div(obj) +
            DIV('Rating: %s' % obj['rating'])
        )


def get_name_el(venue):
    url = venue.get('url')
    if not url:
        try:
            url = venue['menu']['url']
        except KeyError:
            pass
    if url:
        return A(venue['name'], href=url)
    else:
        return B(venue['name'])


def get_category_div(venue):
    categories = (c['shortName'] for c in venue['categories'])
    return DIV('Category: ' + ', '.join(categories))


main()
