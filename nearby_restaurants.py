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
from genrunner import GeneratorRunner


def main():
    args = clint.arguments.Args()
    address = args.get(0)
    if args.flags.contains('--web'):
        func = functools.partial(nearby_restaurants, address)
        runner = GeneratorRunner(func)
        runner.run()
    else:
        noop = lambda *args, **kwargs: None
        for _ in nearby_restaurants(address, noop):
            pass


def nearby_restaurants(address, send):
    client_id, client_secret = os.environ['FOURSQUARE_CREDENTIALS'].split(',')
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
            yield


if __name__ == '__main__':
    main()
