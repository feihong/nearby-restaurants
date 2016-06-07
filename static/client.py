import json
from browser.html import *
from browser import document, window
from browser.ajax import ajax
from browser.websocket import WebSocket


restaurant_ul = document['rlist']
L = window.L
map = None
jq = window.jQuery


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
        VenueItem(obj)


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


class VenueItem:
    selected_item = None

    def __init__(self, venue):
        location = venue['location']
        coords = [location['lat'], location['lng']]

        dot = L.circleMarker(coords, dict(
            color='red',
            fillColor='red',
            fillOpacity=1,
        )).addTo(map)
        dot.setRadius(5)
        dot.on('click', self.select_and_scroll)
        self.dot = dot

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
        li.bind('click', self.select_and_pan)
        restaurant_ul <= li
        self.li = li

    def deselect(self):
        self.dot.setStyle(dict(fillColor='red'))
        self.li.class_name = ''

    def select(self):
        if VenueItem.selected_item:
            VenueItem.selected_item.deselect()

        self.dot.setStyle(dict(fillColor='yellow'))
        self.li.class_name = 'yellow'
        VenueItem.selected_item = self

    def select_and_pan(self, evt):
        self.select()
        self.dot.bringToFront()
        map.panTo(self.dot.getLatLng())

    def select_and_scroll(self, evt):
        self.select()
        ul = jq(restaurant_ul)
        li = jq(self.li)
        # print(li.find('.info').text())
        # print(ul.scrollTop())
        # print(li.offset().top)
        ul.scrollTop(li.offset().top - ul.offset().top + ul.scrollTop())


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
