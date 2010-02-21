from django.test.client import *

class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Copied from http://www.djangosnippets.org/snippets/963/, modified to
    add the _bare_request method rather than override the 'request' method.
    That makes it necessary to add methods that mimic get() and post(), but
    call the _bare_request method instead of the request method.

    Usage:

    rf = RequestFactory()
    get_request = rf.get_request('/hello/')
    post_request = rf.post_request('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function, 
    just as if that view had been hooked up using a URLconf.
    """
    def _bare_request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

    def get_request(self, path, data={}, **extra):
        """
        Requests a response from the server using GET.
        """
        r = {
            'CONTENT_LENGTH':  None,
            'CONTENT_TYPE':    'text/html; charset=utf-8',
            'PATH_INFO':       urllib.unquote(path),
            'QUERY_STRING':    urlencode(data, doseq=True),
            'REQUEST_METHOD': 'GET',
        }
        r.update(extra)

        return self._bare_request(**r)

    def post_request(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        """
        Requests a response from the server using POST.
        """
        if content_type is MULTIPART_CONTENT:
            post_data = encode_multipart(BOUNDARY, data)
        else:
            post_data = data

        r = {
            'CONTENT_LENGTH': len(post_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      urllib.unquote(path),
            'REQUEST_METHOD': 'POST',
            'wsgi.input':     FakePayload(post_data),
        }
        r.update(extra)

        return self._bare_request(**r)