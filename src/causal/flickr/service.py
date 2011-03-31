"""This file provides the fetching and converting of the
feed from flickr.com.
"""

from causal.main.handlers import BaseServiceHandler
from causal.main.models import ServiceItem
from causal.main.exceptions import LoggedServiceError
from datetime import datetime, timedelta
from django.utils import simplejson
import flickrapi
import time

class ServiceHandler(BaseServiceHandler):
    display_name = 'Flickr'

    def get_items(self, since):
        """Fetch and normalise the updates from the service.
        """

        self.flickr = flickrapi.FlickrAPI(self.service.app.auth_settings['api_key'])
        photos = self._get_service_items() or {}
        items = []

        if photos:
            for photo in photos:
                # Info about the pic
                pic = self.flickr.photos_getInfo(photo_id=photo['id'], format='json', nojsoncallback='1')
                pic_json = simplejson.loads(pic)

                item = ServiceItem()

                item.title = pic_json['photo']['title']['_content']
                # Use date from when the photo was uploaded to flickr NOT when it was taken
                item.created = datetime.fromtimestamp(float(pic_json['photo']['dates']['posted'])) #u'posted': u'1300054696'

                item.link_back = pic_json['photo']['urls']['url'][0]['_content']
                item.tags = pic_json['photo']['tags']['tag']
                item.favorite = pic_json['photo']['isfavorite']

                item.url_thumb = "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.url_small = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.body = '<br/><img src="%s" />' % (item.url_thumb,)
                item.service = self.service

                items.append(item)
        return items

    def _get_service_items(self):
        """Helper method to fetch items for either history or stats page.
        """

        delta = timedelta(days=7)
        now = datetime.now()
        then = now - delta
        epoch_now = time.mktime(now.timetuple())
        epoch_then = time.mktime(then.timetuple())

        try:
            photos_json = self.flickr.photos_search(
                user_id = self.service.auth.secret,
                per_page = '10',
                format = 'json',
                nojsoncallback ='1',
                min_upload_date = int(epoch_then),
                max_upload_date = int(epoch_now)
            )

        except Exception, exception:
            raise LoggedServiceError(original_exception=exception)

        try:
            data = simplejson.loads(photos_json)
        except:
            return None

        return data.get('photos', {}).get('photo', None)

    def _fetch_favorites(self):
        """Fetch the list of photos that the current use has made their fav.
        """

        delta = timedelta(days=7)
        now = datetime.now()
        then = now - delta
        epoch_now = time.mktime(now.timetuple())
        epoch_then = time.mktime(then.timetuple())

        favs = self.flickr.favorites_getList(
            user_id=self.service.auth.secret,
            max_fave_date=int(epoch_now),
            min_fave_date=int(epoch_then),
            format='json',
            nojsoncallback ='1'
        )

        return simplejson.loads(favs)

    def get_stats_items(self, since):
        """Fetch and normalise the updates from the service and generate stats.
        """

        self.flickr = flickrapi.FlickrAPI(self.service.app.auth_settings['api_key'])
        photos = self._get_service_items()

        items = []

        if photos:
            for photo in photos:

                item = ServiceItem()

                # Info about the pic
                pic = se.fflickr.photos_getInfo(photo_id=photo['id'], format='json', nojsoncallback='1')
                pic_json = simplejson.loads(pic)

                # Info about how the pic was taken
                exif = self.flickr.photos_getExif(photo_id=photo['id'], format='json', nojsoncallback ='1')
                exif_json = simplejson.loads(exif)
                item.camera_make = self._extract_camera_type(exif_json)
                item.title = pic_json['photo']['title']['_content']

                # Use date from when the photo was uploaded to flickr NOT when it was taken
                item.created = datetime.fromtimestamp(float(pic_json['photo']['dates']['posted'])) #u'posted': u'1300054696'

                item.link_back = pic_json['photo']['urls']['url'][0]['_content']
                item.tags = pic_json['photo']['tags']['tag']
                item.favorite = pic_json['photo']['isfavorite']

                # Add views
                item.views = pic_json['photo']['views']

                # Add tags
                item.tags = pic_json['photo']['tags']['tag']

                item.number_of_comments = pic_json['photo']['comments']['_content']

                item.url_thumb = "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.url_small = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.body = '<br/><img src="%s" />' % (item.url_thumb,)

                # Add location
                item.location = {}
                if pic_json['photo'].has_key('location'):
                    item.location['lat'] = pic_json['photo']['location']['latitude']
                    item.location['long'] = pic_json['photo']['location']['longitude']

                item.service = self.service

                items.append(item)
        return items

    def _extract_camera_type(self, json):
        """Return the make and model of a photo.
        """

        try:
            if json['photo']['exif'][0]['tag'] == 'Make':
                make_model = json['photo']['exif'][1]['raw']['_content']
                return make_model
        except:
            pass
        try:
            if json['photo']['exif'][1]['tag'] == 'Model':
                make_model =  json['photo']['exif'][0]['raw']['_content']
                return make_model
        except:
            pass

        return "Unknown make"

