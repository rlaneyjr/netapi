"""
Interface main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).
"""
import re
from dataclasses import field
from pydantic import validator
from pydantic.dataclasses import dataclass
from typing import Optional, Any, List
from netapi.metadata import Metadata, EntityCollections, DataConfig, custom_asdict
from netapi.units import unit_validator


def forwarding_model_verification(forwarding_model):
    """
    Verifies the forwarding model of the interface. Based on the EOS specifications.
    Details on the EAPI https://<device>/documentation.html#interfaces_
    """
    forwarding_model_data = {
        "dataLink": "data_link",
        "unauthorized": "unauthorized",
        "recirculation": "recirculation",
        "routed": "routed",
        "bridged": "bridged",
        "quiteDataLink": "quiet_data_link",
    }

    try:
        data = forwarding_model_data[forwarding_model]
    except KeyError:
        raise ValueError(f"Unknown forwarding model: {forwarding_model}")

    return data


def interface_converter(raw_interface):
    """
    Method that reads interface data and returns it on standard name format
    Example:
    raw_interface = Eth0/0
    new_interface = Ethernet0/0
    """
    pattern = re.compile(r"^(?P<value>\D+)(?P<remainder>\S+)")
    name_map = {
        "eth": "Ethernet",
        "ethernet": "Ethernet",
        "fa": "FastEthernet",
        "fastethernet": "FastEthernet",
        "gi": "GigabitEthernet",
        "ge": "GigabitEthernet",
        "gigabitethernet": "GigabitEthernet",
        "te": "TenGigabitEthernet",
        "tengigabitethernet": "TenGigabitEthernet",
        "po": "Port-Channel",
        "port-channel": "Port-Channel",
        "vl": "Vlan",
        "vlan": "Vlan",
        "lo": "Loopback",
        "loopback": "Loopback",
        "tu": "Tunnel",
        "tunnel": "Tunnel",
    }

    match = re.search(pattern, raw_interface)
    try:
        value = match.group("value").lower()
        remainder = match.group("remainder")

        if value in name_map.keys():
            new_interface = name_map[value] + remainder

        else:
            new_interface = raw_interface
    except AttributeError:
        # Leaving interface as is if no match
        new_interface = raw_interface

    return new_interface


def sort_interface(intf):
    """
    Based on the inteface name it collects the interface name ID and the numbers of the
    slots/port number (up to 3 digits value) and returns them.

    It is useful for when is called on the sorted method. Like:
    sorted(list_intf, key=sort_interface)
    """
    pattern = re.compile(
        r"(?P<id>[a-zA-Z]+(-[a-zA-Z]+)?)-?(?P<slot1>\d+)?(/|-)?(?P<slot2>\d+)?(/|-)?"
        r"(?P<slot3>\d+)?"
    )

    result = pattern.search(intf).groupdict()

    number = ""
    if result["slot1"]:
        number += result["slot1"]
    if result["slot2"]:
        number += result["slot2"]
    if result["slot3"]:
        number += result["slot3"]
    if not number:
        # Set a placeholder when only names have been passed (for those unique intf)
        number = "0"

    return result["id"], int(number)


def status_conversion(raw_status, interface_conn_status=None):
    """
    Based on a raw (known) status of the interface (line protocol in the case of
    Cisco and Arista), it returns a status (up, dormant, etc...) string and its boolean
    representation.
    """
    status = raw_status.lower()
    if status == "connected":
        enabled = True
        status_up = True
    elif status == "notconnect":
        enabled = True
        status_up = False
    elif status == "disabled":
        enabled = False
        status_up = False
    elif status == "dormant":
        enabled = interface_conn_verification(interface_conn_status)
        status_up = False
    elif status == "lowerlayerdown":
        enabled = interface_conn_verification(interface_conn_status)
        status_up = False
    elif status == "testing":
        enabled = interface_conn_verification(interface_conn_status)
        status_up = False
    elif status == "up":
        enabled = True
        status_up = True
    elif status == "down":
        enabled = interface_conn_verification(interface_conn_status)
        status_up = False
    elif status == "notpresent":
        enabled = interface_conn_verification(interface_conn_status)
        status_up = False
    else:
        raise ValueError(
            f"Interface status not known: {status} - {interface_conn_status}"
        )

    return status, status_up, enabled


def interface_conn_verification(interface_conn_status):
    """
    Some vendors have a separate variable for interface admin status. This is used in
    situations where the operational status does not reflect the admin status of the
    interface.
    """
    if interface_conn_status == "disabled":
        enabled = False
    else:
        enabled = True

    return enabled


def status_declaration(raw_status):
    status, _, _ = status_conversion(raw_status)
    return status


def light_levels_alert(tx_power, rx_power, net_os=None):
    """
    Returns flag and alert based on light level values and predefined thresholds
    """
    # Power alert thresholds (from Cisco)
    tx_low_warning = -7.61
    tx_high_warning = -1.00
    tx_low_alarm = -11.61
    tx_high_alarm = 1.99
    rx_low_warning = -9.50
    rx_high_warning = 2.39
    rx_low_alarm = -13.56
    rx_high_alarm = 3.39
    if net_os == "junos":
        rx_low_warning = -23.01
        rx_high_warning = -1.00
        rx_low_alarm = -23.98
        rx_high_alarm = 0.00

    if rx_power >= rx_high_alarm or rx_power <= rx_low_alarm:
        flag = "red"

    elif tx_power >= tx_high_alarm or tx_power <= tx_low_alarm:
        flag = "red"

    elif rx_power >= rx_high_warning or rx_power <= rx_low_warning:
        flag = "yellow"

    elif tx_power >= tx_high_warning or tx_power <= tx_low_warning:
        flag = "yellow"

    else:
        flag = "green"

    return flag


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class InterfaceCounters:
    """
    Houses interface counters. All attributes are optional, but their default value is
    a float -> 0.0

    Attributes:

    - `rx_bits_rate`: (Bit) Rx bps
    - `tx_bits_rate`: (Bit) Tx bps
    - `rx_pkts_rate`: (float) Rx pps
    - `tx_pkts_rate`: (float) Tx pps
    - `rx_unicast_pkts`: (float) Rx unicast pakets counter
    - `tx_unicast_pkts`: (float) Tx unicast pakets counter
    - `rx_multicast_pkts`: (float) Rx multicast pakets counter
    - `tx_multicast_pkts`: (float) Tx multicast pakets counter
    - `rx_broadcast_pkts`: (float) Rx broadcast pakets counter
    - `tx_broadcast_pkts`: (float) Tx broadcast pakets counter
    - `rx_bytes`: (Byte) Rx bytes counter
    - `tx_bytes`: (Byte) Tx bytes counter
    - `rx_discards`: (float) Rx discards counter
    - `tx_discards`: (float) Tx discards counter
    - `rx_errors_general`: (float) Rx main errors counter
    - `tx_errors_general`: (float) Tx main errors counter
    - `rx_errors_fcs`: (float) Rx FCS errors
    - `rx_errors_crc`: (float) Rx CRC errors
    - `rx_errors_runt`: (float) Rx runt frames errors
    - `rx_errors_rx_pause`: (float) Rx pause errors
    - `rx_errors_giant`: (float) Rx giant frames errors
    - `rx_errors_symbol`: (float) Rx symbol errors
    - `tx_errors_collisions`: (float) Tx collision errors
    - `tx_errors_late_collisions`: (float) Tx late collision errors
    - `tx_errors_deferred_transimissions`: (float) Tx deferred errors
    - `tx_errors_tx_pause`: (float) Tx pause errors

    NOTE: For more information regarding the Byte/Bit objects:
    https://bitmath.readthedocs.io/en/latest/instances.html
    """

    rx_bits_rate: Optional[float] = None
    tx_bits_rate: Optional[float] = None
    rx_pkts_rate: Optional[float] = None
    tx_pkts_rate: Optional[float] = None
    rx_unicast_pkts: Optional[float] = 0.0
    tx_unicast_pkts: Optional[float] = 0.0
    rx_multicast_pkts: Optional[float] = 0.0
    tx_multicast_pkts: Optional[float] = 0.0
    rx_broadcast_pkts: Optional[float] = 0.0
    tx_broadcast_pkts: Optional[float] = 0.0
    rx_bytes: Optional[float] = 0.0
    tx_bytes: Optional[float] = 0.0
    rx_discards: Optional[float] = 0.0
    tx_discards: Optional[float] = 0.0
    rx_errors_general: Optional[float] = 0.0
    tx_errors_general: Optional[float] = 0.0
    rx_errors_fcs: Optional[float] = 0.0
    rx_errors_crc: Optional[float] = 0.0
    rx_errors_runt: Optional[float] = 0.0
    rx_errors_rx_pause: Optional[float] = 0.0
    rx_errors_giant: Optional[float] = 0.0
    rx_errors_symbol: Optional[float] = 0.0
    tx_errors_collisions: Optional[float] = 0.0
    tx_errors_late_collisions: Optional[float] = 0.0
    tx_errors_deferred_transmissions: Optional[float] = 0.0
    tx_errors_tx_pause: Optional[float] = 0.0

    @validator("rx_bits_rate", "tx_bits_rate")
    def valid_bits(cls, value):
        return unit_validator("bitmath.Bit", "Bit", value)

    @validator("rx_bytes", "tx_bytes")
    def valid_bytes(cls, value):
        return unit_validator("bitmath.Byte", "Byte", value)


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class InterfaceOptical:
    """
    Houses interface optical levels and status.

    Attributes:

    - `tx`: (float) Tx dBm power of the optical interface
    - `rx`: (float) Rx dBm power of the optical interface
    - `status`: (str) Status flag of the optical interface based on the light levels
    - `serial_number`: (str) Transceiver serial number
    - `media_type`: (str) Transceiver media type
    """

    tx: Optional[float] = None
    rx: Optional[float] = None
    #  TODO: Make status be calculated on the Interface object of each implementation
    status: Optional[str] = None
    serial_number: Optional[str] = None
    media_type: Optional[str] = None


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class InterfaceIP:
    """
    Houses interface IP attributes.

    Attributes:

    - `ipv4`: (IPNetwork) Primary IPv4 address of the interface.
    - `ipv6`: (IPNetwork) Primary IPv6 address of the interface
    - `secondary_ipv4`: (List[str]) List of ipv4 addresses on the interface
    - `dhcp`: (bool) Flag to specify if address is DHCP learned
    """

    ipv4: Optional[Any] = None
    ipv6: Optional[Any] = None
    secondary_ipv4: List[str] = field(default_factory=list)
    dhcp: Optional[bool] = None

    @validator("ipv4")
    def valid_ipv4(cls, value):
        return unit_validator("netaddr.ip.IPNetwork", "IPNetwork", value)

    @validator("ipv6")
    def valid_ipv6(cls, value):
        return unit_validator("netaddr.ip.IPNetwork", "IPNetwork", value)


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class InterfacePhysical:
    """
    Houses interface physical attributes.

    Attributes:

    - `mtu`: (Byte) Interface MTU value. NOTE: Is mainly interpreted as bytes
    - `bandwidth`: (Bit) Interface descriptive bandwidth
    - `duplex`: (str) Interface duplex mode. If applicable
    - `mac`: (EUI) Interface EUI MAC address object
    """

    # TODO: Add more specialized attributes like interface type
    mtu: Optional[int] = None
    bandwidth: Optional[int] = None
    duplex: Optional[str] = None
    mac: Optional[Any] = None

    @validator("mac")
    def valid_mac(cls, value):
        return unit_validator("netaddr.eui.EUI", "EUI", value)

    @validator("mtu")
    def valid_mtu(cls, value):
        return unit_validator("bitmath.Byte", "Byte", value)

    @validator("bandwidth")
    def valid_bandwidth(cls, value):
        return unit_validator("bitmath.Bit", "Bit", value)


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class InterfaceBase:
    """
    Interface object definition.

    Attributes:

    - `name`: (str) Interface name
    - `description`: (str) Interface description
    - `enabled`: (bool) specifying if the interface is enabled
    - `status_up`: (bool) specifying if the interface is UP
    - `status`: (str) Current interface status
    - `last_status_change`: (DateTime) object specifying the last statys change
    - `number_status_changes`: (int) Counter of interfaces status changes
    - `forwarding_model`: (str) Specifies the forwarfing model of the device
    - `instance`: (str) Is the VRF or routing instance of the interface object
    - `members`: (List) Interfaces names that are memebers of a LAG
    - `last_clear`: (DateTime) of last time counters were cleared
    - `update_interval`: (float) Interface stats update interval
    - `counters`: (InterfaceCounters) counters object attributes
    - `physical`: (InterfacePhysical) physical object attributes
    - `optical`: (InterfaceOptical) optical object attributes
    - `addresses`: (InterfaceIP) addresses object attributes
    - `interface_api`: API object which is dependant on the implementation used.
    - `connector`: Device object used to perform the necessary connection.
    - `metadata`: Metadata object which contains information about the current object.
    - `get_cmd`: Command to retrieve interface information out of the device
    """

    name: str
    description: Optional[str] = None
    instance: Optional[str] = None
    members: List[str] = field(default_factory=list)
    enabled: Optional[bool] = None
    status_up: Optional[bool] = None
    status: Optional[str] = None
    last_status_change: Optional[Any] = None
    number_status_changes: Optional[int] = None
    last_clear: Optional[Any] = None
    # counter_refresh: Optional[Any] = None
    update_interval: Optional[float] = None
    forwarding_model: Optional[str] = None
    physical: Optional[InterfacePhysical] = None
    optical: Optional[InterfaceOptical] = None
    addresses: Optional[InterfaceIP] = None
    # NOTE: counters are not in repr
    counters: Optional[InterfaceCounters] = field(default=None, repr=False)
    connector: Optional[Any] = field(default=None, repr=False)
    metadata: Optional[Any] = field(default=None, repr=False)
    interface_api: Optional[Any] = field(default=None, repr=False)
    get_cmd: Optional[Any] = field(default=None, repr=False)

    @validator("name")
    def valid_name(cls, value):
        return interface_converter(value)

    @validator("status")
    def valid_status(cls, v, values):
        status, values["status_up"], values["enabled"] = status_conversion(v)
        return status

    @validator("last_status_change")
    def valid_last_status(cls, value):
        return unit_validator("pendulum.datetime.DateTime", "DateTime", value)

    @validator("last_clear")
    def valid_last_clear(cls, value):
        return unit_validator("pendulum.datetime.DateTime", "DateTime", value)

    @validator("forwarding_model")
    def valid_forwarding_model(cls, value):
        return forwarding_model_verification(value)

    def __post_init__(self, **_ignore):
        self.metadata = Metadata(name="interface", type="entity")
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
        return custom_asdict(self, "interface_api")


class InterfacesBase(EntityCollections):
    ENTITY = "interface"

    def __init__(self, *args, **kwargs):
        super().__init__(entity=self.ENTITY, *args, **kwargs)
        self.metadata = Metadata(name="interfaces", type="collection")

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, entity=self.ENTITY, **kwargs)
