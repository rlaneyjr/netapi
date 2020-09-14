"""
Route main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).
"""
from dataclasses import field
from typing import Optional, List, Any, Dict
from pydantic import validator
from pydantic.dataclasses import dataclass
from netapi.net.interface import interface_converter
from netapi.units import unit_validator
from netapi.probe.utils import is_it_valid_ip
from netapi.metadata import Metadata, DataConfig, EntityCollections, custom_asdict


__all__ = ["RouteBase"]


def protocol_verification(raw_protocol):
    """
    Method that reads protocol data and returns it on standard name format
    Example:
    raw_protocol = directlyConnected
    protocol = connected
    """
    name_map = {
        "bgp": "bgp",
        "b": "bgp",
        "ibgp": "ibgp",
        "ebgp": "ebgp",
        "ospf": "ospf",
        "o": "ospf",
        "ospfv3": "ospfv3",
        "o3": "ospfv3",
        "is-is": "is-is",
        "i": "is-is",
        "static": "static",
        "s": "static",
        "rip": "rip",
        "r": "rip",
        "eigrp": "eigrp",
        "d": "eigrp",
        "connected": "connected",
        "c": "connected",
        "directlyConnected": "connected",
    }
    try:
        return name_map[raw_protocol.lower()]
    except KeyError:
        raise ValueError(f"Unknown protocol {raw_protocol.lower()}")


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class Via:
    """
    Via definition object.

    Attributes:

    - `interface`: (str) Interface for the next hop of the route
    - `next_hop`: (IPAddress) IP address of the next hop
    """

    interface: Optional[str] = None
    next_hop: Optional[Any] = None

    @validator("interface")
    def valid_interface(cls, value):
        return interface_converter(value)

    @validator("next_hop")
    def valid_address(cls, value):
        return unit_validator("netaddr.ip.IPAddress", "IPAddress", value)


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class RouteBase:
    """
    Route object definition.

    Attributes:

    - `dest`: (str) IP Address/network to collect route information from the device
    - `instance`: (str) Is the VRF or routing instance of the route object
    - `network`: (IPNetwork) IP `dest`, destination, present on the device's route
    - `protocol`: (str) Routing protocol
    - `vias`: (List) Available `Via`s objects for the respective route
    - `metric`: (int) Route metric (dependant on the routing protocol)
    - `preference`: (int) Route preference (respect other routes and routing protocols)
    - `active`: (bool) Flag which specifies if the route is currently active
    - `inactive_reason`: (str) Description of the reason of an inactive route
    - `age`: (Duration) object which tells the current age of the route. This is
    available on some routes, not all implementations you can retrieve the `age`
    attribute. You can look at the `metadata` object for creation and update time
    of the object
    - `tag`: (int) tag value assigned to the route
    - `extra_attributes`: (Dict) Custom key and values depending on the implementation.
    - `route_api`: API object which is dependant on the implementation used.
    - `connector`: Device object used to perform the necessary connection.
    - `metadata`: Metadata object which contains information about the current object.
    - `get_cmd`: Command to retrieve route information out of the device
    """

    dest: str
    instance: Optional[str] = None
    network: Optional[Any] = None
    protocol: Optional[str] = None
    vias: List[Via] = field(default_factory=list)
    metric: Optional[int] = None
    preference: Optional[int] = None
    active: Optional[bool] = None
    inactive_reason: Optional[str] = None
    age: Optional[Any] = None
    tag: Optional[int] = None
    extra_attributes: Dict[str, Any] = field(default_factory=dict)
    connector: Optional[Any] = field(default=None, repr=False)
    metadata: Optional[Any] = field(default=None, repr=False)
    route_api: Optional[Any] = field(default=None, repr=False)
    get_cmd: Optional[Any] = field(default=None, repr=False)

    @validator("dest")
    def valid_dest(cls, value):
        # NOTE: It only verifies that is a valid IP address/network - does not transform
        if not is_it_valid_ip(value):
            raise ValueError(f"Not a valid IP address: {value}")
        return value

    @validator("network")
    def valid_network(cls, value):
        return unit_validator("netaddr.ip.IPNetwork", "IPNetwork", value)

    @validator("protocol")
    def valid_protocol(cls, value):
        return protocol_verification(value)

    @validator("age")
    def valid_age(cls, value):
        """It validate the age value as seconds"""
        return unit_validator(
            "pendulum.duration.Duration", "Duration", dict(seconds=value)
        )

    def __post_init__(self, **_ignore):
        self.metadata = Metadata(name="route", type="entity")
        if self.connector:
            if not hasattr(self.connector, "metadata"):
                raise ValueError(
                    f"It does not contain metadata attribute: {self.connector}"
                )
            if self.connector.metadata.name != "device":
                raise ValueError(
                    f"It is not a valid connector object: {self.connector}"
                )

    def to_dict(self):
        # NOTE: Workaround to TypeError: can't pickle SSLContext objects
        return custom_asdict(self, "route_api")


class RoutesBase(EntityCollections):
    ENTITY = "route"

    def __init__(self, *args, **kwargs):
        super().__init__(entity=self.ENTITY, *args, **kwargs)
        self.metadata = Metadata(name="routes", type="collection")

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, entity=self.ENTITY, **kwargs)
