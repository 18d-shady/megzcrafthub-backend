import uuid

class SessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('user_id'):
            request.session['user_id'] = uuid.uuid4().hex
        return self.get_response(request)