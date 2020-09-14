# `__init__`

Module that houses all network technology related builder objects, and performs the
respective calls the respective command and parser factories to get the registered
implementations.

**Example:**

```python
from netapi.connector.pyeapier import Device
from netapi.net import FactsBuilder

connector = Device(
    host="<address>",
    username="<someuser>",
    password="<somepassword>"
)

facts = FactsBuilder()

facts_dev = facts.get(connector=connector)
print(facts_dev)
# Facts(hostname='lab01', os_version='4.21.5F', ...)
```

## `InterfaceBuilder` Objects

Builder used to create Interface object(s).

Interface single object instatiation:

- `entity`: True (default). Used to denote that only an Interface object is created
- `connector`: `Device` instance object
- `name`: string (required)

Interfaces collections object instatiation:

- `entity`: False. Used to denote a collection Interfaces object is created
- `connector`: `Device` instance object
- `interface_range`: (optional) Could be string '1-100' or by default is all
interfaces

**Example:**

```python
interfaces = InterfaceBuilder()
vl70 = interfaces.get(connector, name=70)
print(vl70)
# Interface(name='Vlan70', description='EXAMPLE-Interface', ...)

intf_range = interfaces.get(connector, entity=False, interface_range='Eth1-3')
print(intf_range)
# Interfaces('Ethernet1', 'Ethernet2', 'Ethernet3')

print(intf_range['Ethernet1'])
# Interface(name='Ethernet1', name='EXAMPLE-Interface', ...)
```

### `InterfaceBuilder.get()`

```python
def get(self, connector, entity=True, parameters={}, interface_params)
```


## `VlanBuilder` Objects

Builder used to create Vlan object(s).

Vlan single object instatiation:

- `entity`: True (default). Used to denote that only an Vlan object is created
- `connector`: `Device` instance object
- `id`: integer (required)

Vlans collections object instatiation:

- `entity`: False. Used to denote a collection Vlans object is created
- `connector`: `Device` instance object
- `vlan_range`: (optional) Could be string '1-100' or a list [1, 100]

**Example:**

```python
from netapi.net import VlanBuilder

vlan = VlanBuilder()
vl70 = vlan.get(connector, id=70)
print(vl70)
# Vlan(id=70, interface='EXAMPLE-VLAN', ...)

vlans = vlan.get(connector, entity=False, vlan_range='1-200')
print(vlans)
# Vlans(1, 70, 177)

print(vlans[70])
# Vlan(id=70, name='EXAMPLE-VLAN', ...)
```

### `VlanBuilder.get()`

```python
def get(self, connector, entity=True, parameters={}, vlan_params)
```


## `VrrpBuilder` Objects

Builder used to create Vrrp object(s).

Vrrp single object instatiation:

- `entity`: True (default). Used to denote that only an Vrrp object is created
- `connector`: `Device` instance object
- `group_id`: integer (required)
- `interface`: string (optional)
- `instance`: string (optional)

Vrrps collections object instatiation:

- `entity`: False. Used to denote a collection Vrrps object is created
- `connector`: `Device` instance object
- `interface`: string (optional)
- `instance`: string (optional)

**Example:**

```python
vrrp = VrrpBuilder()
vr70 = vrrp.get(connector, group_id=70)
print(vr70)
# Vrrp(group_id=70, interface='Vlan177', ...)

vrrp_vl177 = vrrp.get(connector, entity=False, interface='Vlan177')
print(vrrp_vl177)
# Vrrps((72, 'Vlan177'), (71, 'Vlan177'), (70, 'Vlan177'))

print(vrrp_vl177[(70, 'Vlan177')])
# Vrrp(group_id=70, interface='Vlan177', ...)
```

### `VrrpBuilder.get()`

```python
def get(self, connector, entity=True, parameters={}, vrrp_params)
```


## `FactsBuilder` Objects

Builder used to create Facts object.

Instatiation:

- `connector`: `Device` instance object

**Example:**

```python
facts = FactsBuilder()
facts_dev = facts.get(connector=connector)
print(facts_dev)
# Facts(hostname='lab01', os_version='4.21.5F', ...)
```

### `FactsBuilder.get()`

```python
def get(self, connector, parameters={}, facts_params)
```


## `RouteBuilder` Objects

Builder used to create Route object(s).

Route single object instatiation:

- `entity`: True (default). Used to denote that only an Route object is created
- `connector`: `Device` instance object
- `dest`: str (required)
- `instance`: string (optional)

Routes collections object instatiation:

- `entity`: False. Used to denote a collection Routes object is created
- `connector`: `Device` instance object
- `protocol`: string (optional)
- `instance`: string (optional)

**Example:**

```python
route = RouteBuilder()
r1 = route.get(connector, dest='10.1.1.1')
print(r1)
# Route(dest='10.1.1.1', instance='default', ...)

routes = route.get(connector, entity=False, por)
print(routes)
# Routes(('default', '10.1.1.0/24'),)

print(routes[('default', '10.1.1.0/24')])
# Route(dest='10.1.1.1', instance='default', ...)
```

### `RouteBuilder.get()`

```python
def get(self, connector, entity=True, parameters={}, route_params)
```


# `facts`

Facts main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).

## `FactsBase` Objects

Facts object definition.

Attributes:

- `hostname`: (str) Hostname of the device
- `os_version`: (str) Network OS version of the system
- `model`: (str) Model/platform of the network device appliance
- `serial_number`: (str) Serial number of the device. Chassis for the modular ones
- `uptime`: (Duration) object which specifies the device uptime
- `up_since`: (DateTime) object which has the date since the device was UP
- `system_mac`: (EUI) MAC address object of the system/chassis
- `available_memory`: (Byte) object which specifies the system available memory
- `total_memory`: (Byte) object which specifies the system memory
- `os_arch`: (str) System OS architecture
- `hw_revision`: (str) Hardware revision of the device
- `interfaces`: (List) Interfaces available on the device
- `connector`: Device object used to perform the necessary connection.
- `metadata`: Metadata object which contains information about the current object.
- `get_cmd`: Command to retrieve route information out of the device

# `interface`

Interface main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).

## `InterfaceCounters` Objects

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

## `InterfaceOptical` Objects

Houses interface optical levels and status.

Attributes:

- `tx`: (float) Tx dBm power of the optical interface
- `rx`: (float) Rx dBm power of the optical interface
- `status`: (str) Status flag of the optical interface based on the light levels
- `serial_number`: (str) Transceiver serial number
- `media_type`: (str) Transceiver media type

## `InterfaceIP` Objects

Houses interface IP attributes.

Attributes:

- `ipv4`: (IPNetwork) Primary IPv4 address of the interface.
- `ipv6`: (IPNetwork) Primary IPv6 address of the interface
- `secondary_ipv4`: (List[str]) List of ipv4 addresses on the interface
- `dhcp`: (bool) Flag to specify if address is DHCP learned

## `InterfacePhysical` Objects

Houses interface physical attributes.

Attributes:

- `mtu`: (Byte) Interface MTU value. NOTE: Is mainly interpreted as bytes
- `bandwidth`: (Bit) Interface descriptive bandwidth
- `duplex`: (str) Interface duplex mode. If applicable
- `mac`: (EUI) Interface EUI MAC address object

## `InterfaceBase` Objects

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

## `InterfacesBase` Objects


# `route`

Route main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).

## `Via` Objects

Via definition object.

Attributes:

- `interface`: (str) Interface for the next hop of the route
- `next_hop`: (IPAddress) IP address of the next hop

## `RouteBase` Objects

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

## `RoutesBase` Objects


# `vlan`

Vlan main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).

## `VlanBase` Objects

Vlan object definition.

Attributes:

- `id`: (int) ID of the vlan
- `name`: (str) Name of the vlan
- `status`: (str) Status of the vlan. The `status_conversion` is applied and also
sets the value of `status_up`.
- `status_up`: (bool) Flag indicating the current status of the vlan.
- `interfaces`: (List) contains interfaces configured under the vlan.
- `vlan_api`: API object which is dependant on the implementation used.
- `connector`: Device object used to perform the necessary connection.
- `metadata`: Metadata object which contains information about the current object.
- `get_cmd`: Command to retrieve route information out of the device
- `config_cmd`: Command to enable/disable object. Depending on the implementation it
can be automatically generated when issuing enable/disable methods. It can also be
generated using `generate_config_cmd()`.

## `VlansBase` Objects


# `vrrp`

Vrrp main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).

## `VrrpBase` Objects

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

## `VrrpsBase` Objects


