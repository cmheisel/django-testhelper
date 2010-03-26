from django.shortcuts import render_to_response

def multi_template(request):
    """
        Simple view that uses multiple templates via inheritance.
    """
    
    return render_to_response('testingapp/multi-template.html', {})
    
def single_template(request):
    """
        Simple view that uses a signle template
    """

    return render_to_response('testingapp/single-template.html', {})

def json(request, template):
    """
        Renders a json template
    """
    return render_to_response('testingapp/%s' % template, {})