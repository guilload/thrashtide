from datetime import datetime

from pytz import timezone
from schema import And, Optional, Schema, SchemaError, Use

from .constants import DATE_FORMAT, FEET, METERS, UTC


def between(low, high):
    return lambda value: low <= value and value <= high


def to_datetime(string):
    return datetime.strptime(string, DATE_FORMAT)


def to_utc(dt, tz):
    return tz.localize(dt).astimezone(UTC)


def within(*args):
    return lambda value: value in args


QUERY = Schema({"start": And(unicode, Use(to_datetime)),
                "stop": And(unicode, Use(to_datetime)),
                "latitude": And(unicode, Use(float), between(-90, 90)),
                "longitude": And(unicode, Use(float), between(-180, 180)),
                Optional("timezone"): And(unicode, Use(timezone)),
                Optional("unit"): And(unicode, within(FEET, METERS)),
                })


def validate_request(request):
    args = QUERY.validate(request)

    if args["start"] >= args["stop"]:
        raise SchemaError("'start' is higher or equal to 'stop'", None)

    for key, default in (("timezone", UTC), ("unit", METERS)):
        if key not in args:
            args[key] = default

    for key in ("start", "stop"):
        args[key] = to_utc(args[key], args["timezone"])

    return args
