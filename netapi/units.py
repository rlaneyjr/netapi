"""
Global and external units definitions for the metrics/parameters collected by netapi.
These are to be used on the classes definitions for certain parameters, like:

- memory
- disk space
- time
- IP addresses and MAC address

NOTE: These are built using external dependancies for convenience whe using the library.
It might change in the future depending usage/maintenance and other factors of the
external dependencies
"""
import pendulum
from pendulum import Duration, DateTime
from netaddr import EUI, IPNetwork, IPAddress
from bitmath import Byte, Bit
from pydantic.datetime_parse import parse_datetime, parse_duration


UNITS = {
    "EUI": EUI,
    "IPNetwork": IPNetwork,
    "IPAddress": IPAddress,
    "Byte": Byte,
    "Bit": Bit,
    "Duration": Duration,
    "DateTime": DateTime,
}


def pendulum_setter(f):
    def wrap(*args, **kwargs):
        x = f(*args, **kwargs)
        return pendulum.instance(x)

    return wrap


@pendulum_setter
def datetime_verifier(raw_data):
    return parse_datetime(raw_data)


@pendulum_setter
def duration_verifier(raw_data):
    return parse_duration(raw_data)


# TODO: Make use of pydantic custom types and validations
def unit_validator(type_string, obj_invoked, value):
    """
    Converts the value passed to the object invoked. For example: 1234 -> Byte(1234.0)

    It does not perform any change is the `type_string` is the same as the value passed.
    This means that if the `type_string` is `netaddr.eui.EUI` and value is already an
    object EUI(...), than it will return as is.
    """
    if type_string in str(type(value)):
        return value

    try:
        if isinstance(value, (tuple, list)):
            # Unpack values when passed as tuple or list. i.e. DateTime(2019, 7, 3)
            valor = UNITS[obj_invoked](*value)
        elif isinstance(value, dict):
            # Unpack values like dict(seconds=1234567)
            valor = UNITS[obj_invoked](**value)
        elif isinstance(value, int) and obj_invoked == "Duration":
            valor = UNITS[obj_invoked](value)
        else:
            if obj_invoked == "DateTime":
                valor = datetime_verifier(value)
            elif obj_invoked == "Duration":
                print("aqui aqui aqui")
                valor = duration_verifier(value)
            else:
                valor = UNITS[obj_invoked](value)
    except Exception as err:
        raise ValueError(str(err))

    return valor
