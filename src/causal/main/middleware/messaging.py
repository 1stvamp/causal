# From http://www.cupcakewithsprinkles.com/django-messaging-for-ajax-calls-using-jquery/

import simplejson as json
from django.contrib import messages

class AjaxMessaging(object):
    def process_response(self, request, response):
        if request.is_ajax():
            try:
                content = json.loads(response.content)
            except ValueError:
                return response

            django_messages = []

            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags,
                })

            content['django_messages'] = django_messages

            response.content = json.dumps(content)
        return response