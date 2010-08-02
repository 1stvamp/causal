import httplib2
from datetime import datetime, timedelta
from django.utils import simplejson
from django.utils.safestring import mark_safe
from helios.main.models import AccessToken, UserService, ServiceItem

display_name = 'Github'

def get_items(user, since, model_instance=None):
    serv = model_instance or get_model_instance(user)
    items = []
    try:
        at = AccessToken.objects.get(service=serv)

        url = 'http://github.com/api/v2/json/repos/show/%s' % at.username
        h = httplib2.Http()
        resp, content = h.request(url, "GET")

        git_hub = simplejson.loads(content)
        repos = []

        for repo in git_hub['repositories']:
            url = 'http://github.com/api/v2/json/commits/list/%s/%s/master' % (at.username, repo['name'],)
            resp, content = h.request(url, "GET")
            commits = simplejson.loads(content)

            for commit in commits['commits']:
                commited_datetime = commit['committed_date']
                utc_offset = commited_datetime.rsplit('-', 1)[1]
                utc_offset = utc_offset[:2]
                utc_offset_delta = timedelta(hours=int(utc_offset) + 1)

                commited_datetime = datetime.strptime(commited_datetime.rsplit('-', 1)[0], '%Y-%m-%dT%H:%M:%S')
                commited_datetime = commited_datetime + utc_offset_delta

                item = ServiceItem()
                item.title = 'Project: ' + repo['name']
                item.body = commit['message']
                item.created = commited_datetime
                item.service = serv
                items.append(item)
    except Exception, e:
        print e
        return False

    return items

def get_model_instance(user):
    return UserService.objects.get(user=user, app__module_name=__package__)