"""
NXOS Nxapier module.

Contains the method to create Network Objects for the NXOS-NXAPI implementation.
"""
import pendulum
from bitmath import kB
from netapi.net import vlan, vrrp, interface, facts, route
from netapi.exceptions import NetApiParseError


def update_attrs(obj, data_dict):
    "Updates object attributes based on data from dictionary"
    for key, value in data_dict.items():
        setattr(obj, key, value)


def update_container_attrs(obj, list_of_dict, entity):
    "Updates collections based on data from dictionary contained in list"
    for data_dict in list_of_dict:
        for key, value in data_dict.items():
            obj[key] = entity(**value)


class Vlans(vlan.VlansBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlan_range = None
        self.get_cmd = None
        self.metadata.implementation = "NXOS-NXAPI"

    @staticmethod
    def generate_get_cmd(vlan_range=None):
        "Returns commands necessary to build a collection of entities"
        if isinstance(vlan_range, list):
            vlan_range = sorted(vlan_range)
            vlan_range = f"{vlan_range[0]} - {vlan_range[-1]}"

        if vlan_range:
            return [f"show vlan id {vlan_range}"]
        else:
            return ["show vlan"]

    def get(self, **_ignore):
        "Automatic trigger a data collection. A connector object has to be passed"
        if self.connector.metadata.implementation != "NXOS-NXAPI":
            raise ValueError(
                "Connector is not of the correct implementation: NXOS-NXAPI"
            )

        # Verify show command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(self.vlan_range)

        parsed_data = ParseVlan.collector_parse(
            self.connector.run(self.get_cmd), **_ignore
        )

        update_container_attrs(self, parsed_data, Vlan)
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True


class Vlan(vlan.VlanBase):
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "NXOS-NXAPI"
        self._vlan_api_generator()

    def _vlan_api_generator(self):
        if self.connector is not None:
            if self.connector.metadata.implementation != "NXOS-NXAPI":
                raise ValueError(
                    "Connector is not of the correct implementation: NXOS-NXAPI"
                )
            self.vlan_api = self.connector.connector.api("vlans")
            return True
        else:
            return False

    @staticmethod
    def generate_get_cmd(id):
        "Returns commands necessary to build the entity"
        return [f"show vlan id {id}"]

    def get(self, **_ignore):
        "Automatic trigger a data collection by running get_cmd"
        if self.connector is None:
            raise NotImplementedError("Need to have the connector defined")

        # Generate get command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(self.id)

        parsed_data = ParseVlan.parse(self.connector.run(self.get_cmd), **_ignore)

        # Update the attributes
        update_attrs(self, parsed_data)

        # Do extra work for the status
        self.status, self.status_up = vlan.status_conversion(parsed_data["status"])

        # Update obj cache
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True

    def enable(self):
        "Enable VLAN"
        if not hasattr(self, "vlan_api"):
            if not self._vlan_api_generator():
                raise NotImplementedError("Need to have the connector API defined")
        return self.vlan_api.set_state(self.id, value="active")

    def disable(self):
        "Disable VLAN"
        if not hasattr(self, "vlan_api"):
            if not self._vlan_api_generator():
                raise NotImplementedError("Need to have the connector API defined")
        return self.vlan_api.set_state(self.id, value="suspend")


class ParseVlan:
    @staticmethod
    def data_constructor(vlan_id, data, **kwargs):
        # If no data is passed a known error
        if not data:
            raise NetApiParseError("No data to be parsed")

        interfaces = data.get("interfaces")

        parsed_data = dict(
            id=vlan_id,
            name=data.get("name"),
            dynamic=data.get("dynamic"),
            interfaces=list(interfaces.keys()) if interfaces else None,
            status=data.get("status"),
        )

        return parsed_data

    @staticmethod
    def data_validation(raw_data, entity=True, **kwargs):
        "Returns useful data and performs some initial validations"
        try:
            rdata = list(raw_data.values())[0].get("vlans")
        except Exception as err:
            raise NetApiParseError(
                f"{str(err)}\nCould not retrieve data from: {raw_data}"
            )

        # If no data is passed a known error
        if not rdata:
            raise NetApiParseError("No data to be parsed")

        if entity:
            if len(rdata) > 1:
                print("[WARNING]: Multiple entities present")

        return rdata

    @staticmethod
    def parse(raw_data, **kwargs):
        """
        Returns a dictionary with the entity data parsed
        """
        rdata = ParseVlan.data_validation(raw_data, **kwargs)

        for _vlan_id, _vlan_data in rdata.items():
            vlan_data = ParseVlan.data_constructor(_vlan_id, _vlan_data, **kwargs)

        return vlan_data

    @staticmethod
    def collector_parse(raw_data, **kwargs):
        """
        Returns list of dictionaries of each entity parsed
        """
        rdata = ParseVlan.data_validation(raw_data, entity=False, **kwargs)

        vlans_container = []
        for _vlan_id, _vlan_data in rdata.items():
            _parsed_data = ParseVlan.data_constructor(_vlan_id, _vlan_data, **kwargs)
            vlans_container.append({int(_vlan_id): _parsed_data})

        return vlans_container


class Vrrps(vrrp.VrrpsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = None
        self.instance = None
        self.get_cmd = None
        self.metadata.implementation = "NXOS-NXAPI"

    @staticmethod
    def generate_get_cmd(instance=None, interface=None):
        "Returns commands necessary to build a collection of entities"
        if interface:
            return [f"show vrrp interface {interface} all"]
        elif instance:
            return [f"show vrrp vrf {instance} all"]
        else:
            return [f"show vrrp all"]

    def get(self, **_ignore):
        "Automatic trigger a data collection. A connector object has to be passed"
        if self.connector.metadata.implementation != "NXOS-NXAPI":
            raise ValueError(
                "Connector is not of the correct implementation: NXOS-NXAPI"
            )

        # Verify show command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(self.instance, self.interface)

        parsed_data = ParseVrrp.collector_parse(
            self.connector.run(self.get_cmd), **_ignore
        )

        update_container_attrs(self, parsed_data, Vrrp)

        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True


class Vrrp(vrrp.VrrpBase):
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "NXOS-NXAPI"
        self._vrrp_api_generator()

    def _vrrp_api_generator(self):
        if self.connector is not None:
            if self.connector.metadata.implementation != "NXOS-NXAPI":
                raise ValueError(
                    "Connector is not of the correct implementation: NXOS-NXAPI"
                )
            self.vrrp_api = self.connector.connector.api("vrrp")
            return True
        else:
            return False

    @staticmethod
    def generate_get_cmd(group_id, interface=None, instance=None):
        "Returns commands necessary to build the entity"
        if interface:
            return [f"show vrrp group {group_id} interface {interface} all"]
        elif instance:
            return [f"show vrrp group {group_id} vrf {instance} all"]
        else:
            return [f"show vrrp group {group_id} vrf all"]

    def get(self, **_ignore):
        "Automatic trigger a data update on the object"
        if self.connector is None:
            raise NotImplementedError("Need to have the connector defined")

        # Verify show command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(
                self.group_id, self.interface, self.instance
            )

        parsed_data = ParseVrrp.parse(self.connector.run(self.get_cmd), **_ignore)

        # Update the attributes
        update_attrs(self, parsed_data)

        # Do extra work for the status
        self.status, self.status_up = vrrp.status_conversion(parsed_data["status"])

        # Update obj cache
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True

    def enable(self):
        "Enable VRRP group"
        if not hasattr(self, "vrrp_api"):
            if not self._vrrp_api_generator():
                raise NotImplementedError("Need to have the connector API defined")
        return self.vrrp_api.set_enable(self.interface, self.group_id, value=True)

    def disable(self):
        "Disable VRRP group"
        if not hasattr(self, "vrrp_api"):
            if not self._vrrp_api_generator():
                raise NotImplementedError("Need to have the connector API defined")
        return self.vrrp_api.set_enable(self.interface, self.group_id, value=False)


class ParseVrrp:
    @staticmethod
    def data_constructor(data, **kwargs):
        # If no data is passed a known error
        if not data:
            raise NetApiParseError("No data to be parsed")

        parsed_data = dict(
            group_id=data.get("groupId"),
            interface=data.get("interface"),
            instance=data.get("vrfName"),
            description=data.get("description"),
            virtual_mac=data.get("virtualMac"),
            virtual_ip_secondary=data.get("virtualIpSecondary"),
            master_ip=data.get("masterAddr"),
            virtual_ip=data.get("virtualIp"),
            priority=data.get("priority"),
            skew_time=data.get("skewTime"),
            version=data.get("version"),
            preempt=data.get("preempt"),
            preempt_delay=data.get("preemptDelay"),
            mac_advertisement_interval=data.get("macAddressInterval"),
            master_interval=data.get("masterInterval"),
            master_down_interval=float(data.get("masterDownInterval")) / 1000.0,
            tracked_objects=data.get("trackedObjects"),
            status=data.get("state"),
            extra_attributes=dict(
                vrrp_advertisement_interval=data.get("vrrpAdvertInterval"),
                vrrp_id_disabled=data.get("vrIdDisabled"),
                vrrp_id_disabled_reason=data.get("vrIdDisabledReason"),
                bfd_peer_ip=data.get("bfdPeerAddr"),
                preempt_reload=data.get("preemptReload"),
            ),
        )

        return parsed_data

    @staticmethod
    def data_validation(raw_data, entity=True, **kwargs):
        "Returns useful data and performs some initial validations"
        try:
            rdata = list(raw_data.values())[0].get("virtualRouters")
        except Exception as err:
            raise NetApiParseError(
                f"{str(err)}\nCould not retrieve data from: {raw_data}"
            )

        # If no data is passed a known error
        if not rdata:
            raise NetApiParseError("No data to be parsed")

        if entity:
            if len(rdata) > 1:
                print("[WARNING]: Multiple entities present")

        return rdata

    @staticmethod
    def parse(raw_data, **kwargs):
        """
        Returns a dictionary with the entity data parsed
        """
        rdata = ParseVrrp.data_validation(raw_data, **kwargs)[0]

        vrrp_data = ParseVrrp.data_constructor(rdata, **kwargs)

        return vrrp_data

    @staticmethod
    def collector_parse(raw_data, **kwargs):
        """
        Returns list of dictionaries of each entity parsed
        """
        rdata = ParseVrrp.data_validation(raw_data, entity=False, **kwargs)

        vrrps_container = []
        for vrrp_data in rdata:
            # Placeholder
            _parsed_data = ParseVrrp.data_constructor(vrrp_data, **kwargs)
            vrrps_container.append(
                {(_parsed_data["group_id"], _parsed_data["interface"]): _parsed_data}
            )

        return vrrps_container


class Interfaces(interface.InterfacesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface_range = None
        self.get_cmd = None
        self.metadata.implementation = "NXOS-NXAPI"

    @staticmethod
    def generate_get_cmd(interface_range=None):
        "Returns commands necessary to build the collection of entities"
        if isinstance(interface_range, list):
            raise ValueError("Must pass a str (i.e. Eth1 - 10) or None to collect all")
        if interface_range is not None:
            return [
                f"show interfaces {interface_range}",
                f"show ip interface {interface_range}",
                f"show interfaces {interface_range} transceiver",
            ]
        else:
            return [
                "show interfaces",
                "show ip interface",
                "show interfaces transceiver",
            ]

    def get(self, **_ignore):
        "Automatic trigger a data collection. A connector object has to be passed"
        if self.connector.metadata.implementation != "NXOS-NXAPI":
            raise ValueError(
                "Connector is not of the correct implementation: NXOS-NXAPI"
            )
        # Verify show command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(self.interface_range)

        parsed_data = ParseInterface.collector_parse(
            self.connector.run(self.get_cmd), **_ignore
        )

        update_container_attrs(self, parsed_data, Interface)
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True


class Interface(interface.InterfaceBase):
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "NXOS-NXAPI"
        self._interface_api_generator()

    def _interface_api_generator(self):
        if self.connector is not None:
            if self.connector.metadata.implementation != "NXOS-NXAPI":
                raise ValueError(
                    "Connector is not of the correct implementation: NXOS-NXAPI"
                )
            self.interface_api = self.connector.connector.api("interfaces")
            return True
        else:
            return False

    @staticmethod
    def generate_get_cmd(name):
        "Returns commands necessary to build the entity"
        return [
            f"show interfaces {name}",
            f"show ip interface {name}",
            f"show interfaces {name} transceiver",
        ]

    def get(self, **_ignore):
        "Automatic trigger a data collection by running get_cmd"
        if self.connector is None:
            raise NotImplementedError("Need to have the connector defined")

        # Generate get command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(self.name)

        parsed_data = ParseInterface.parse(
            self.connector.run(self.get_cmd, silent=True), **_ignore
        )

        # Update the attributes
        update_attrs(self, parsed_data)

        # Do extra work for the status
        self.status, self.status_up, self.enabled = interface.status_conversion(
            parsed_data["status"]
        )

        # Update obj cache
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True

    def enable(self):
        "Enable Interface"
        if not hasattr(self, "interface_api"):
            if not self._interface_api_generator():
                raise NotImplementedError("Need to have the connector API defined")
        return self.interface_api.set_shutdown(self.name, disable=True)

    def disable(self):
        "Disable Interface"
        if not hasattr(self, "interface_api"):
            if not self._interface_api_generator():
                raise NotImplementedError("Need to have the connector API defined")
        return self.interface_api.set_shutdown(self.name, disable=False)


class ParseInterface:
    @staticmethod
    def data_constructor(intf_name, data, **kwargs):
        # If no data is passed a known error
        if not data:
            raise NetApiParseError("No data to be parsed")

        statistics = data.get("interfaceStatistics", {})

        # Physical bit
        physical = dict(
            mac=data.get("physicalAddress"),
            mtu=data.get("mtu", 0),
            duplex=data.get("duplex"),
            bandwidth=data.get("bandwidth", 0),
        )

        # Addresses bit
        addr_info = data.get("interfaceAddress")
        if not addr_info:
            addresses = None
        else:
            addresses = dict(dhcp=addr_info.get("dhcp"), secondary_ipv4=[])
            for _ip in addr_info.get("secondaryIpsOrderedList", []):
                addresses["secondary_ipv4"].append(f"{_ip['address']}/{_ip['maskLen']}")
            if addr_info.get("primaryIp"):
                _ip = addr_info["primaryIp"]
                addresses.update(ipv4=f"{_ip['address']}/{_ip['maskLen']}")
            if addr_info.get("linkLocalIp6"):
                _ip = addr_info["linkLocalIp6"]
                addresses.update(ipv6=f"{_ip['address']}/{_ip['maskLen']}")

        # Counters bit
        counter_info = data.get("interfaceCounters", {})
        if not counter_info:
            counters = None
        else:
            counters = dict(
                tx_broadcast_pkts=counter_info.get("outBroadcastPkts", 0.0),
                rx_broadcast_pkts=counter_info.get("inBroadcastPkts", 0.0),
                tx_unicast_pkts=counter_info.get("outUcastPkts", 0.0),
                rx_unicast_pkts=counter_info.get("inUcastPkts", 0.0),
                tx_multicast_pkts=counter_info.get("outMulticastPkts", 0.0),
                rx_multicast_pkts=counter_info.get("inMulticastPkts", 0.0),
                tx_bytes=counter_info.get("outOctets", 0.0),
                rx_bytes=counter_info.get("inOctets", 0.0),
                tx_errors_general=counter_info.get("totalOutErrors", 0.0),
                rx_errors_general=counter_info.get("totalInErrors", 0.0),
                tx_discards=counter_info.get("outDiscards", 0.0),
                rx_discards=counter_info.get("inDiscards", 0.0),
            )
            # Tx Errors
            tx_errors = counter_info.get("outputErrorsDetail")
            if tx_errors:
                counters.update(
                    tx_errors_collisions=tx_errors.get("collisions", 0.0),
                    tx_errors_deferred_transmissions=tx_errors.get(
                        "deferredTransmissions", 0.0
                    ),
                    tx_errors_tx_pause=tx_errors.get("txPause", 0.0),
                    tx_errors_late_collisions=tx_errors.get("lateCollisions"),
                )
            # Rx Errors
            rx_errors = counter_info.get("inputErrorsDetail")
            if rx_errors:
                counters.update(
                    rx_errors_runt=rx_errors.get("runtFrames", 0.0),
                    rx_errors_rx_pause=rx_errors.get("rxPause", 0.0),
                    rx_errors_fcs=rx_errors.get("fcsErrors", 0.0),
                    rx_errors_crc=rx_errors.get("alignmentErrors", 0.0),
                    rx_errors_giant=rx_errors.get("giantFrames", 0.0),
                    rx_errors_symbol=rx_errors.get("symbolErrors", 0.0),
                )

            # Statistics
            if statistics:
                counters.update(
                    rx_bits_rate=statistics.get("inBitsRate", 0.0),
                    rx_pkts_rate=statistics.get("inPktsRate", 0.0),
                    tx_bits_rate=statistics.get("outBitsRate", 0.0),
                    tx_pkts_rate=statistics.get("outPktsRate", 0.0),
                )

        # Optical bit
        optical = dict(
            tx=data.get("txPower"),
            rx=data.get("rxPower"),
            serial_number=data.get("vendorSn"),
            media_type=data.get("mediaType"),
        )

        if optical.get("tx") is not None and optical.get("rx") is not None:
            optical["status"] = interface.light_levels_alert(
                tx_power=optical["tx"], rx_power=optical["rx"], net_os="eos"
            )

        if not any(optical.values()):
            optical = None

        parsed_data = dict(
            name=intf_name,
            forwarding_model=data.get("forwardingModel"),
            description=data.get("description"),
            instance=data.get("vrf"),
            status=data.get("interfaceStatus"),
            last_status_change=data.get("lastStatusChangeTimestamp"),
            last_clear=counter_info.get("lastClear"),
            number_status_changes=counter_info.get("linkStatusChanges"),
            update_interval=statistics.get("updateInterval"),
            members=list(data.get("memberInterfaces", {}).keys()),
            physical=physical,
            addresses=addresses,
            optical=optical,
            counters=counters,
        )

        return parsed_data

    @staticmethod
    def data_validation(raw_data, entity=True, **kwargs):
        "Returns useful data and performs some initial validations"
        rdata = {}
        try:
            # Merge the results off al the commands into each interface found
            for value in raw_data.values():
                if not value:
                    continue
                for intf, intf_data in value.get("interfaces", {}).items():
                    if rdata.get(intf):
                        rdata[intf] = {**rdata[intf], **intf_data}
                    else:
                        rdata[intf] = intf_data
        except Exception as err:
            raise NetApiParseError(
                f"{str(err)}\nCould not retrieve data from: {raw_data}"
            )

        # If no data is passed a known error
        if not rdata:
            raise NetApiParseError("No data to be parsed")

        if entity:
            if len(rdata) > 1:
                print("[WARNING]: Multiple interfaces present")

        return rdata

    @staticmethod
    def parse(raw_data, **kwargs):
        """
        Returns a dictionary with the entity data parsed
        """
        rdata = ParseInterface.data_validation(raw_data, **kwargs)

        for _name, data in rdata.items():
            interface_data = ParseInterface.data_constructor(_name, data, **kwargs)

        return interface_data

    @staticmethod
    def collector_parse(raw_data, **kwargs):
        """
        Returns list of dictionaries of each entity parsed
        """
        rdata = ParseInterface.data_validation(raw_data, entity=False, **kwargs)

        intf_container = []
        for _intf, _intf_data in rdata.items():
            _parsed_data = ParseInterface.data_constructor(_intf, _intf_data, **kwargs)
            intf_container.append({_intf: _parsed_data})

        return intf_container


class Facts(facts.FactsBase):
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "NXOS-NXAPI"
        # NOTE: No self.facts_api since this is a custom net object

    @staticmethod
    def generate_get_cmd():
        "Returns commands necessary to build the entity"
        return ["show hostname", "show version", "show interfaces"]

    def get(self, **_ignore):
        "Automatic trigger a data collection"
        if self.connector is None:
            raise NotImplementedError("Need to have the connector defined")

        # Generate get command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd()

        parsed_data = ParseFacts.parse(self.connector.run(self.get_cmd), **_ignore)

        # Update the attributes
        update_attrs(self, parsed_data)

        # Update obj cache
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True


class ParseFacts:
    @staticmethod
    def data_constructor(hostname, version, interfaces, **kwargs):
        # If no data is passed a known error
        if not hostname and not version and not interfaces:
            raise NetApiParseError("No data to be parsed")

        raw_interfaces = list(interfaces.get("interfaces", {}).keys())

        parsed_data = dict(
            hostname=hostname.get("hostname"),
            os_version=version.get("version"),
            model=version.get("modelName"),
            serial_number=version.get("serialNumber"),
            uptime=pendulum.duration(seconds=version["uptime"]),
            up_since=pendulum.from_timestamp(version["bootupTimestamp"]),
            system_mac=version.get("systemMacAddress"),
            available_memory=kB(version.get("memFree")).Byte,
            total_memory=kB(version.get("memTotal")).Byte,
            os_arch=version.get("architecture"),
            hw_revision=version.get("hardwareRevision"),
            interfaces=sorted(
                [interface.interface_converter(x) for x in raw_interfaces],
                key=interface.sort_interface,
            ),
        )

        return parsed_data

    @staticmethod
    def parse(raw_data, **kwargs):
        hostname = raw_data.get("show hostname", {})
        version = raw_data.get("show version", {})
        interfaces = raw_data.get("show interfaces", {})

        facts_data = ParseFacts.data_constructor(
            hostname, version, interfaces, **kwargs
        )

        return facts_data


class Routes(route.RoutesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = None
        self.instance = None
        self.vrf_all = False
        self.get_cmd = None
        self.metadata.implementation = "NXOS-NXAPI"

    @staticmethod
    def generate_get_cmd(protocol=None, instance=None, vrf_all=False):
        "Returns commands necessary to build a collection of entities"
        if protocol and instance:
            return [f"show ip route vrf {instance} {protocol}"]
        elif instance:
            return [f"show ip route vrf {instance}"]
        elif protocol:
            return [f"show ip route {protocol}"]
        else:
            return ["show ip route"] if not vrf_all else ["show ip route vrf all"]

    def get(self, **_ignore):
        "Automatic trigger a data collection. A connector object has to be passed"
        if self.connector.metadata.implementation != "NXOS-NXAPI":
            raise ValueError(
                "Connector is not of the correct implementation: NXOS-NXAPI"
            )

        # Verify show command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(
                self.protocol, instance=self.instance, vrf_all=self.vrf_all
            )

        parsed_data = ParseRoute.collector_parse(
            self.connector.run(self.get_cmd), **_ignore
        )

        update_container_attrs(self, parsed_data, Route)
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True


class Route(route.RouteBase):
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "NXOS-NXAPI"
        self._route_api_generator()

    def _route_api_generator(self):
        if self.connector is not None:
            if self.connector.metadata.implementation != "NXOS-NXAPI":
                raise ValueError(
                    "Connector is not of the correct implementation: NXOS-NXAPI"
                )
            self.route_api = self.connector.connector.api("staticroute")
            return True
        else:
            return False

    @staticmethod
    def generate_get_cmd(dest, instance=None):
        """
        Returns commands necessary to build the entity.

        NOTE: This is preferred over the original `get(name)` method of pyeapi because
        it provides with much more info
        """
        if instance:
            return [f"show ip route vrf {instance} {dest} detail"]
        else:
            return [f"show ip route {dest} detail"]

    def get(self, **_ignore):
        "Automatic trigger a data collection by running the get_cmd"
        if self.connector is None:
            raise NotImplementedError("Need to have the connector defined")

        # Generate get command
        if not self.get_cmd:
            self.get_cmd = self.generate_get_cmd(self.dest, self.instance)

        parsed_data = ParseRoute.parse(self.connector.run(self.get_cmd), dest=self.dest)

        # Update the attributes
        update_attrs(self, parsed_data)

        # Update obj cache
        self.metadata.updated_at = pendulum.now()
        self.metadata.collection_count += 1
        return True


class ParseRoute:
    @staticmethod
    def data_constructor(_instance, _route, data, **kwargs):
        active = (
            True
            if data.get("hardwareProgrammed") or data.get("kernelProgrammed")
            else False
        )

        # Vias
        vias = [
            dict(interface=x.get("interface"), next_hop=x.get("nexthopAddr"))
            for x in data.get("vias", [])
        ]

        # Extra attributes
        extra_attributes = dict(
            route_action=data.get("routeAction"), route_leaked=data.get("routeLeaked")
        )

        parsed_data = dict(
            dest=kwargs["dest"] if "dest" in kwargs else _route,
            instance=_instance,
            network=_route,
            active=active,
            inactive_reason=None,
            protocol=data.get("routeType"),
            metric=data.get("metric"),
            preference=data.get("preference"),
            vias=vias,
            extra_attributes=extra_attributes,
        )

        return parsed_data

    @staticmethod
    def data_validation(raw_data, entity=True, **kwargs):
        "Returns useful data and performs some initial validations"
        try:
            rdata = list(raw_data.values())[0].get("vrfs")
        except Exception as err:
            raise NetApiParseError(
                f"{str(err)}\nCould not retrieve data from: {raw_data}"
            )

        # If no data is passed a known error
        if not rdata:
            raise NetApiParseError("No data to be parsed")

        if entity:
            if len(rdata) > 1:
                print("[WARNING]: Multiple entities present")

        return rdata

    @staticmethod
    def parse(raw_data, **kwargs):
        """
        Returns a dictionary with the entity data parsed
        """
        rdata = ParseRoute.data_validation(raw_data, **kwargs)

        for _instance, _vrfdata in rdata.items():
            _routes_data = _vrfdata.get("routes")
            if not _routes_data:
                print("No route information collected")
                return dict(
                    dest=kwargs["dest"], active=False, inactive_reason="Route not found"
                )
            for _route, _route_data in _routes_data.items():
                route_data = ParseRoute.data_constructor(
                    _instance, _route, _route_data, **kwargs
                )

        return route_data

    @staticmethod
    def collector_parse(raw_data, **kwargs):
        """
        Returns list of dictionaries of each entity parsed
        """
        rdata = ParseRoute.data_validation(raw_data, entity=False, **kwargs)

        routes_container = []
        for _instance, _vrfdata in rdata.items():
            _routes_data = _vrfdata.get("routes", {})
            for _route, _route_data in _routes_data.items():
                _parsed_data = ParseRoute.data_constructor(
                    _instance, _route, _route_data, **kwargs
                )
                routes_container.append({(_instance, _route): _parsed_data})

        return routes_container
