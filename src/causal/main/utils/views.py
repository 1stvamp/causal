"""Utilities for helping with views
"""

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

def render(request, data, template_path):
    data['real_path_to_template'] = template_path
    if request.is_ajax():
        new_template_path = 'causal/services/blank.html'
    else:
        new_template_path = 'causal/services/from_base.html'
    return render_to_response(
        new_template_path,
        data,
        context_instance=RequestContext(request)
    )

