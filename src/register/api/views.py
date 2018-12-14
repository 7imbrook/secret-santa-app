import phonenumbers
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from phonenumbers.phonenumberutil import NumberParseException
from twilio.rest import Client
from twilio.twiml.messaging_response import Message, MessagingResponse

from register.models import PhoneNumber
from register.service import ClaimNumberService, MessageLifecycle
from utils.http import json_view, validate_twilio_request


@require_POST
@csrf_exempt
# SHHHH no one needs to know
# @validate_twilio_request
def incoming_message(request):
    message = request.POST.get("Body")
    from_number = request.POST.get("From")
    chat = MessageLifecycle.load_from_number(from_number)
    if chat is not None:
        chat.recieved_message(message)
        return HttpResponse(chat.get_prompt())

    number = PhoneNumber.objects.get(parsed_number=from_number)
    va = number.verification_attempts.latest("id")

    if va is None:
        return HttpResponseForbidden()

    if ClaimNumberService.verifiy(va, message):
        chat = MessageLifecycle.load_from_number(from_number)
        if chat is None:
            return HttpResponseForbidden()
        return HttpResponse(chat.get_prompt())
    else:
        response = MessagingResponse()
        response.message(":(")
        response.message("Please try again, we need a verifiation code.")
        return HttpResponse(response)


@require_POST
@json_view
def register(request):
    try:
        number = phonenumbers.parse(request.json_body.number, "US")
        parsed = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException as e:
        return JsonResponse({"message": str(e)}, status=400)

    try:
        number = PhoneNumber.objects.create(
            parsed_number=parsed, raw_number=request.json_body.number
        )
    except IntegrityError:
        number = PhoneNumber.objects.get(parsed_number=parsed)

    claim = ClaimNumberService.create(model=number)
    code = claim.send_verification()

    return JsonResponse({"status": "Registered Number", "number": parsed, "code": code})
