import ujson
from box import Box
from functools import wraps
from django.http import HttpResponse, HttpResponseForbidden
from functools import wraps
from twilio import twiml
from twilio.request_validator import RequestValidator
from django.conf import settings


def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""

    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(settings.TWILIO_KEYS.token)

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.build_absolute_uri(),
            request.POST,
            request.META.get("HTTP_X_TWILIO_SIGNATURE", ""),
        )
        print(request.build_absolute_uri())

        # Continue processing the request if it's valid, return a 403 error if
        # it's not
        if request_valid:
            return f(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    return decorated_function


def json_view(f):
    """Wrapps the parsed json body in Box object"""

    @wraps(f)
    def middleware(request):
        if request.method == "POST" and request.content_type == "application/json":
            setattr(request, "json_body", Box(ujson.loads(request.body)))

        return f(request)

    return middleware
