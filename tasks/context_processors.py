from django import http
from django.utils import timezone


def user_tz(_: http.HttpRequest):
    return {"user_tz": timezone.localtime().tzinfo}
