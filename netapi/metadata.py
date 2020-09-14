import uuid
import reprlib
import pendulum
from collections import ChainMap
from dataclasses import asdict
from pydantic import validator
from pydantic.dataclasses import dataclass
from typing import Optional, Any


class DataConfig:
    validate_assignment = True


@dataclass(config=DataConfig)  # type: ignore
class Metadata:
    name: str
    type: str
    implementation: Optional[str] = None
    created_at: Optional[Any] = None
    id: Optional[Any] = None
    updated_at: Optional[Any] = None
    collection_count: int = 0
    parent: Optional[str] = None

    @validator("id", pre=True, always=True)
    def valid_id(cls, v):
        return uuid.uuid4()

    @validator("created_at", pre=True, always=True)
    def valid_created_at(cls, v):
        return pendulum.now()


class EntityCollections(ChainMap):
    """
    Main entity collection object. Used for fast lookup and higher level wrapper.
    Should not be instantiated directly

    This allows Objects to be created and accessed like:
    >>> repr(vl177)
    Vlan(id=177, name='NATIVE', ... metadata=Metadata(name='vlan', ... parent=None))

    >>> vlan_collection = Vlans({177: vl177})
    >>> repr(vlan_collection)
    Vlans(177)

    >>> vlan_collection.update({178: vl178})
    >>> repr(vlan_collection)
    Vlans(177, 178)

    >>> vlan_collection[177]
    Vlan(id=177, name='NATIVE', ... metadata=Metadata(name='vlan', ... parent=None))

    >>> len(vlan_collection)
    2
    """

    def __init__(self, *args, entity=None, **kwargs):
        "Initializing ChainMap object and verifying values"
        for arg in args:
            for value in arg.values():
                self._attr_verify(value, entity)
        super().__init__(*args, **kwargs)

    def _attr_verify(self, attribute, expected_type):
        "Verify that each value inserted are of the expected type"
        try:
            if attribute.metadata.name != expected_type:
                raise ValueError(
                    f"{attribute} -> It is not a valid {expected_type} object"
                )
        except AttributeError:
            raise ValueError(f"{attribute} -> It is not a valid {expected_type} object")

    def __setitem__(self, *args, entity=None, **kwargs):
        "Verifying values when updating"
        value = args[-1]
        self._attr_verify(value, entity)
        super().__setitem__(*args, **kwargs)

        # Update the metadata timestamp if possible
        if hasattr(self, "metadata"):
            self.metadata.updated_at = pendulum.now()

    @reprlib.recursive_repr()
    def __repr__(self):
        "Show repr as calling class with the ID of each entity"
        return f"{self.__class__.__name__}(" + ", ".join(map(repr, self)) + ")"


def custom_asdict(obj, api_attribute):
    """
    Performs `asdict` functionality from dataclasses.

    Attributes:
    - `obj`: Dataclass object to transform to dict
    - `api_attribute`: Dataclass attributes that needs to be initialized before copy

    The `asdict` creates a copy of the obj using deepcopy for the dict creation.
    This can be an issue for object that cannot be copied like SSL Context ones.
    For example, the route.route_api attribute on pyeapi implementation cannot be copied
    because it throws the following error:

    TypeError: can't pickle SSLContext objects
    """
    _dump = getattr(obj, api_attribute)
    setattr(obj, api_attribute, None)
    result = asdict(obj, dict_factory=HidePrivateAttrs)
    setattr(obj, api_attribute, _dump)
    return result


class HidePrivateAttrs(dict):
    """
    Used as dict_factory for hiding private attributes and also returning string
    values of embeded objects
    """

    KNOWN_CLASSES = [
        "netaddr.ip.IPNetwork",
        "netaddr.ip.IPAddress",
        "netaddr.eui.EUI",
        "datetime.datetime",
        "pendulum.datetime.DateTime",
        "pendulum.duration.Duration",
        "uuid.UUID",
    ]

    def hide_attrs(self, raw_value):
        if any(x in str(type(raw_value)) for x in HidePrivateAttrs.KNOWN_CLASSES):
            return str(raw_value)
        elif "bitmath.Byte" in str(type(raw_value)):
            return raw_value.bytes
        elif "bitmath.Bit" in str(type(raw_value)):
            return raw_value.bits
        else:
            return raw_value

    def __init__(self, iterable):
        _iterable = []
        for key, value in iterable:
            # Hides the private attributes when creating dict
            if key.startswith("_"):
                continue
            #  Bypass the connector object
            if key == "connector":
                continue
            # Bypass the `get_cmd` or `config_cmd` type of attributes
            if key.endswith("_cmd"):
                continue
            _iterable.append((key, self.hide_attrs(value)))
        return super().__init__(_iterable)
