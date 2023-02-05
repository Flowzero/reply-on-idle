
from datetime import datetime
import pytz

# provide timezones to convert time below:
timezones = set(pytz.all_timezones_set)


def time_convert(time_utc: datetime):
    local_time = {}

    localFormatEu = "%H:%M:%S %Y-%d-%m"
    localFormatUs = "%H:%M:%S %Y-%m-%d"

    # instead of providing timezones manually it can be adjusted to
    # find time convertation for all existing timezones by using:
    # pytz.all_timezones_set

    for tz in timezones:
        localDatetime = time_utc.astimezone(tz=pytz.timezone(tz))\
                                          .strftime(localFormatEu)
        local_time[tz] = localDatetime

    return local_time
