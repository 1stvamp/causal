import flickrapi
from datetime import datetime
from django.utils import simplejson
from causal.main.models import ServiceItem, AccessToken
from causal.main.service_utils import get_model_instance
from causal.main.exceptions import LoggedServiceError

DISPLAY_NAME = 'Flickr'
CUSTOM_FORM = False
OAUTH_FORM = False

def get_items(user, since, model_instance):
    serv = model_instance or get_model_instance(user, __name__)
    items = []

    at = AccessToken.objects.get(service=serv)
    flickr = flickrapi.FlickrAPI(at.api_token)

    try:
        photos_json = flickr.photos_search(
            user_id=at.userid,
            per_page='10',
            format='json'
        )
    except Exception, e:
        raise LoggedServiceError(original_exception=e)

    photos_json = photos_json.replace('jsonFlickrApi(', '')
    photos_json = photos_json.rstrip(')')
    photos = simplejson.loads(photos_json)

    for photo in photos['photos']['photo']:
        # flickr.photos.getInfo
        pic = flickr.photos_getInfo(photo_id=photo['id'], format='json')
        pic = pic.replace('jsonFlickrApi(', '')
        pic = pic.rstrip(')')
        p = simplejson.loads(pic)
        epoch = p['photo']['dateuploaded']

        item = ServiceItem()
        item.location = {}
        item.title = p['photo']['title']['_content']
        item.body = p['photo']['urls']['url'][0]['_content']
        item.created = datetime.fromtimestamp(float(epoch))
        item.service = serv
        item.link_back = p['photo']['urls']['url'][0]['_content']
        item.tags = p['photo']['tags']['tag']
        item.favorite = p['photo']['isfavorite']
        item.number_of_comments = p['photo']['comments']['_content']
        item.url = "http://farm%s.static.flickr.com/%s/%s_%s_m_d.jpg" %(p['photo']['farm'], p['photo']['server'], p['photo']['id'], p['photo']['secret'])
        # add location
        if p['photo'].has_key('location'):
            item.location['lat'] = p['photo']['location']['latitude']
            item.location['long'] = p['photo']['location']['longitude']
        item.user = user
        items.append(item)
    return items
