"""
Show currently-open restaurants that are within one mile of the given address.

FourSquare credentials are grabbed from environment variables. You can be create
and lookup your own credentials on this page:
https://foursquare.com/developers/apps

"""

from __future__ import print_function
import os
import functools
import foursquare
import clint.arguments
from quip import WebRunner, send


def main():
    args = clint.arguments.Args()
    address = args.get(0)
    if args.flags.contains('--web'):
        func = functools.partial(nearby_restaurants, address)
        runner = WebRunner(func)
        runner.run()
    else:
        nearby_restaurants(address)


def nearby_restaurants(address):
    client_id, client_secret = os.environ['FOURSQUARE_PARAMS'].split(',')
    client = foursquare.Foursquare(
        client_id=client_id, client_secret=client_secret)
    params = dict(
        near=address,
        radius=1600,
        section='food',
        venuePhotos=1,
        openNow=1,
        sortByDistance=1,
    )
    # resp = client.venues.explore(params=params)
    import json
    resp = json.load(open('sample_response.json'))
    proj_id, access_token = os.environ['MAPBOX_PARAMS'].split(',')
    send(dict(
        type='map_params',
        center=resp['geocode']['center'],
        query_address=resp['geocode']['displayString'],
        id=proj_id,
        access_token=access_token,
    ))

    for group in resp['groups']:
        for item in group['items']:
            venue = item['venue']
            send(venue)
            print(venue['name'])
            print(venue['location']['formattedAddress'][0])
            print('Rating:', venue['rating'])
            categories = (c['shortName'] for c in venue['categories'])
            print('Categories:', ', '.join(categories))
            print('-' * 80)


if __name__ == '__main__':
    main()
