import json
from browser.html import *
from browser import document, window
from browser.ajax import ajax
from browser.websocket import WebSocket


restaurant_ul = document['rlist']
L = window.L
map = None
selected = None


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
    elif obj.get('type') == 'map_params':
        init_map(obj)
    else:
        add_venue(obj)


def init_map(params):
    global map
    map = L.map('map')
    map.setView(params['center'], 15)
    url = 'https://a.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}'
    tile_params = dict(
      attribution='Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
      maxZoom=18,
      id=params['id'],
      accessToken=params['access_token'],
    )
    L.tileLayer(url, tile_params).addTo(map)

    # One mile circle.
    L.circle(params['center'], 1600, dict(
        color='blue',
        fillColor='grey',
        fillOpacity=0.2,
    )).addTo(map)

    # Center point.
    dot = L.circleMarker(params['center'], dict(
        color='blue',
        fillColor='blue',
        fillOpacity=1,
    )).addTo(map)
    dot.setRadius(5)
    dot.bindPopup(params['query_address'])


def add_venue(venue):
    location = venue['location']
    coords = [location['lat'], location['lng']]

    dot = L.circleMarker(coords, dict(
        color='red',
        fillColor='red',
        fillOpacity=1,
    )).addTo(map)
    dot.setRadius(5)
    dot.bindPopup(venue['name'])

    li = LI(
        get_img(venue) +
        DIV(
            get_name_el(venue) +
            DIV(location['address']) +
            get_category_div(venue) +
            DIV('Rating: %s' % venue['rating']),
            Class='info'
        )
    )

    def on_click(evt):
        global selected
        if selected:
            selected['li'].class_name = ''
            selected['dot'].setStyle(dict(fillColor='red'))
        map.panTo(coords)
        dot.openPopup()
        dot.setStyle(dict(fillColor='pink'))
        dot.bringToFront()
        li.class_name = 'yellow'
        selected = dict(li=li, dot=dot)
    li.bind('click', on_click)

    restaurant_ul <= li


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
        return A(venue['name'], href=url, target='_blank')
    else:
        return B(venue['name'])


def get_category_div(venue):
    categories = (c['shortName'] for c in venue['categories'])
    return DIV('Category: ' + ', '.join(categories))


main()
