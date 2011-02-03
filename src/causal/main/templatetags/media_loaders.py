from django import template
from django.conf import settings

register = template.Library()

GOOGLE_FILES = {
    'js': {
        'jquery-1.5.min.js': '//ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js',
        'jquery-ui.min.js': '//ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js',
    },
    'css': {
        'cupertino/jquery-ui.css': '//ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/cupertino/jquery-ui.css',
    },
    'image': {
    }
}

USE_GOOGLE_CDN = getattr(settings, 'USE_GOOGLE_CDN', False)
if getattr(settings, 'SERVE_STATIC', False):
    STATIC_PATH = '/static/'
else:
    STATIC_PATH = getattr(settings, 'MEDIA_URL', '')

def _load(metiatype, path):
    ret_path = None
    if '//' not in path:
        if USE_GOOGLE_CDN:
            ret_path = GOOGLE_FILES[metiatype].get(path, None)
        if not ret_path:
            ret_path = "%s%s/%s" % (STATIC_PATH, metiatype, path)
    else:
        ret_path = path
    return ret_path

@register.simple_tag
def load_js_path(path):
    return _load('js', path)
@register.simple_tag
def load_js(path):
    return '<script type="text/javascript" src="%s"></script>' % (_load('js', path),)

@register.simple_tag
def load_css_path(path):
    return _load('css', path)
@register.simple_tag
def load_css(path):
    return '<link rel="stylesheet" type="text/css" media="screen" href="%s" />' % (_load('css', path),)

@register.simple_tag
def load_image_path(path):
    return _load('image', path)
# Don't really need a load_image as you'd barely ever use it like this
