from django.shortcuts import render_to_response

def multi_template(request):
    """
        Simple view that uses multiple templates via inheritance.
    """
    
    return render_to_response('testingapp/multi-template.html', {})