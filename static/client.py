import json
from browser.html import *
from browser import document, window
from browser.ajax import ajax
from browser.websocket import WebSocket


restaurant_ul = document['rlist']


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
    elif obj.get('type') == 'center':
        coord = obj['value']
        init_map(coord['lat'], coord['lng'])
    else:
        restaurant_ul <= LI(
            get_img(obj) +
            DIV(
                get_name_el(obj) +
                DIV(obj['location']['address']) +
                get_category_div(obj) +
                DIV('Rating: %s' % obj['rating']),
                Class='info'
            )
        )


def init_map(lat, lng):
    L = window.L
    map = L.map('map')
    map.setView([lat, lng], 16)
    url = 'https://a.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}'
    params = dict(
      attribution='Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
      maxZoom=18,
      id='feihong.0abbogke',
      accessToken='pk.eyJ1IjoiZmVpaG9uZyIsImEiOiJjaXAwbnI2dmQwMHloeHVtNXd4Y3V0M3FsIn0.cuYLb1WqhxoqlZWyS48u4g'
    )
    L.tileLayer(url, params).addTo(map)



def get_img(venue):
    """
    How to reassemble the image URL:
    https://developer.foursquare.com/docs/responses/photo

    """
    item = venue['featuredPhotos']['items'][0]
    return IMG(src='%swidth100%s' % (item['prefix'], item['suffix']))


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
