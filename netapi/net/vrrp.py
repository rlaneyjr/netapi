"""
Vrrp main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).
"""
from dataclasses import field
from pydantic.dataclasses import dataclass
from pydantic import validator
from typing import Optional, Any, List, Dict
from netapi.metadata import Metadata, EntityCollections, DataConfig, custom_asdict
from netapi.units import unit_validator


def status_conversion(raw_status):
    """
    Based on a raw (known) status of the vrrp, it returns a standard status (UP,
    DOWN) string and its boolean representation.
    """
    status = raw_status.lower()
    if status == "master" or status == "backup":
        status_up = True
    elif status == "stopped":
        status_up = False
    else:
        raise ValueError(f"Vrrp status not known: {status}")

    return status, status_up


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class VrrpBase:
    """
    Vrrp object definition

    Attributes:

    - `group_id`: (int) VRRP group ID
    - `interface`: (str) Interface where the VRRP group is defined
    - `description`: (str) VRRP description
    - `version`: (int) VRRP version
    - `status_up`: (bool) Flag of the vrrp status
    - `status`: (str) Status of vrrp
    - `instance`: (str) Instance/vrf of the vrrp object
    - `virtual_ip`: (IPAddress) VRRP IP address
    - `virtual_ip_secondary`: (List) Secondary virtual IP Addresses
    - `virtual_mac`: (EUI) VRRP virtual MAC address
    - `priority`: (int) VRRP priority value
    - `master_ip`: (IPAddress) Current address of the master virtual router
    - `master_priority`: (int) VRRP value of the master node priority
    - `master_interval`: (int) Master advertisement interval in seconds (TBR)
    - `mac_advertisement_interval`: (float) The time in seconds between sending neighbor
    discovery or arp of the virtual mac address
    - `preempt`: (bool) Flag is preemption is enabled
    - `preempt_delay`: (float) Preemption delay time in seconds (TBR)
    - `master_down_interval`: (float) The master down interval of the virtual router in
    seconds
    - `skew_time`: (float) The skew of the master down interval in seconds
    - `tracked_objects`: (List[Dict]) tracked objects attributes
    - `extra_attributes`: (Dict) Custom key and values depending on the implementation.
    - `vrrp_api`: API object which is dependant on the implementation used.
    - `connector`: Device object used to perform the necessary connection.
    - `metadata`: Metadata object which contains information about the current object.
    - `get_cmd`: Command to retrieve route information out of the device
    """

    group_id: int
    interface: Optional[str] = None
    description: Optional[str] = None
    version: Optional[int] = None
    status_up: Optional[bool] = None
    status: Optional[str] = None
    instance: Optional[str] = None
    virtual_ip: Optional[Any] = None
    virtual_ip_secondary: Optional[List[str]] = None
    virtual_mac: Optional[Any] = None
    priority: Optional[int] = None
    master_ip: Optional[Any] = None
    master_priority: Optional[int] = None
    master_interval: Optional[float] = None  # seconds
    mac_advertisement_interval: Optional[float] = None  # seconds
    preempt: Optional[bool] = None
    preempt_delay: Optional[float] = None  # seconds
    master_down_interval: Optional[float] = None  # seconds
    skew_time: Optional[float] = None  # seconds
    tracked_objects: Optional[List[Dict[str, Any]]] = None
    extra_attributes: Dict[str, Any] = field(default_factory=dict)
    connector: Optional[Any] = field(default=None, repr=False)
    metadata: Optional[Any] = field(default=None, repr=False)
    vrrp_api: Optional[Any] = field(default=None, repr=False)
    get_cmd: Optional[Any] = field(default=None, repr=False)

    @validator("status")
    def valid_status(cls, v, values):
        # NOTE: It does not work when the parameters are assigned! only new instances!
        status, values["status_up"] = status_conversion(v)
        return status

    @validator("virtual_ip", "master_ip")
    def valid_ip(cls, value):
        return unit_validator("netaddr.ip.IPAddress", "IPAddress", value)

    @validator("virtual_mac")
    def valid_mac(cls, value):
        return unit_validator("netaddr.eui.EUI", "EUI", value)

    def __post_init__(self, **_ignore):
        self.metadata = Metadata(name="vrrp", type="entity")
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
        return custom_asdict(self, "vrrp_api")


class VrrpsBase(EntityCollections):
    ENTITY = "vrrp"

    def __init__(self, *args, **kwargs):
        super().__init__(entity=self.ENTITY, *args, **kwargs)
        self.metadata = Metadata(name="vrrps", type="collection")

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, entity=self.ENTITY, **kwargs)
