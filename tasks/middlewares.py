from django.middleware import common
from django.utils import timezone
import pytz


class TimezoneMiddleware(common.CommonMiddleware):
    def process_request(self, request):
        tz = request.COOKIES.get("client_timezone")
        if tz:
            timezone.activate(pytz.timezone(tz))
        else:
            timezone.deactivate()
