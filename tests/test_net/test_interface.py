import re
import pytest
import pendulum
import netapi.net as net
from netapi.net.interface import (
    InterfaceBase,
    InterfacesBase,
    InterfaceCounters,
    InterfaceIP,
    InterfaceOptical,
    InterfacePhysical,
)
from pydantic import ValidationError


MODULE_MAPPING = {"EOS-PYEAPI": net.eos.pyeapier}

INTERFACE_PHYSICAL_ARGS = {
    "standard1": {
        "mtu": 1500,
        "bandwidth": 1000000000,
        "duplex": "full",
        "mac": "2899:3AF8:5DE8",
    },
    "standard2": {
        "mtu": 9000,
        "bandwidth": 1000000000000,
        "duplex": None,
        "mac": "2899.3af8.5de8",
    },
    "invalid_mac_format": dict(mac="28.99.3a.f8.5d.e8"),
}

INTERFACE_PHYSICAL_REPR = {
    "standard1": (
        "InterfacePhysical(mtu=Byte(1500.0), bandwidth=Bit(1000000000.0), "
        "duplex='full', mac=EUI('28-99-3A-F8-5D-E8'))"
    ),
    "standard2": (
        "InterfacePhysical(mtu=Byte(9000.0), bandwidth=Bit(1000000000000.0), "
        "duplex=None, mac=EUI('28-99-3A-F8-5D-E8'))"
    ),
}

INTERFACE_IP_ARGS = {
    "ipv4_only": {
        "ipv4": "7.7.7.1/24",
        "ipv6": None,
        "secondary_ipv4": [],
        "dhcp": False,
    },
    "ipv6_only": {
        "ipv4": None,
        "ipv6": "fe80::42:32ff:feb1:9fd3/64",
        "secondary_ipv4": [],
        "dhcp": False,
    },
    "dhcp": {"ipv4": "77.77.77.9/24", "ipv6": None, "secondary_ipv4": [], "dhcp": True},
    "all_ips": {
        "ipv4": "7.7.7.1/24",
        "ipv6": "fe80::42:32ff:feb1:9fd3/64",
        "secondary_ipv4": ["7.7.7.2", "7.7.7.3"],
        "dhcp": False,
    },
    "invalid_ipv4": dict(ipv4="7.7.7.7 255.255.255.0"),
    "invalid_ipv6": dict(ipv6="fe80::42:32ff:feb1:9fd3/255"),
}

INTERFACE_IP_REPR = {
    "ipv4_only": (
        "InterfaceIP(ipv4=IPNetwork('7.7.7.1/24'), ipv6=None, secondary_ipv4=[], "
        "dhcp=False)"
    ),
    "ipv6_only": (
        "InterfaceIP(ipv4=None, ipv6=IPNetwork('fe80::42:32ff:feb1:9fd3/64'), "
        "secondary_ipv4=[], dhcp=False)"
    ),
    "dhcp": (
        "InterfaceIP(ipv4=IPNetwork('77.77.77.9/24'), ipv6=None, secondary_ipv4=[], "
        "dhcp=True)"
    ),
    "all_ips": (
        "InterfaceIP(ipv4=IPNetwork('7.7.7.1/24'), "
        "ipv6=IPNetwork('fe80::42:32ff:feb1:9fd3/64'), "
        "secondary_ipv4=['7.7.7.2', '7.7.7.3'], dhcp=False)"
    ),
}

INTERFACE_OPTICAL_ARGS = {
    "green": {
        "tx": -2.32,
        "rx": -4.5,
        "status": "green",
        "serial_number": "XXXYYYZZZ",
        "media_type": "10GBASE-SR",
    },
    "yellow": {"tx": -2.32, "rx": -15, "status": "yellow"},
    "red": {"tx": -1, "rx": -40, "status": "red"},
}

INTERFACE_OPTICAL_REPR = {
    "green": (
        "InterfaceOptical(tx=-2.32, rx=-4.5, status='green', "
        "serial_number='XXXYYYZZZ', media_type='10GBASE-SR')"
    ),
    "yellow": (
        "InterfaceOptical(tx=-2.32, rx=-15.0, status='yellow', "
        "serial_number=None, media_type=None)"
    ),
    "red": (
        "InterfaceOptical(tx=-1.0, rx=-40.0, status='red', "
        "serial_number=None, media_type=None)"
    ),
}

INTERFACE_COUNTERS_ARGS = {
    "normal": {
        "rx_bits_rate": 17440.6122262025538,
        "tx_bits_rate": 38000.04350234883145,
        "rx_pkts_rate": 1.8763970219715047,
        "tx_pkts_rate": 0.6081652214056465,
        "rx_unicast_pkts": 14558700.0,
        "tx_unicast_pkts": 14240960.0,
        "rx_multicast_pkts": 1996273.0,
        "tx_multicast_pkts": 123582.0,
        "rx_broadcast_pkts": 1781616.0,
        "tx_broadcast_pkts": 6.0,
        "rx_bytes": 1929656819.0,
        "tx_bytes": 1455044979.0,
        "rx_discards": 0.0,
        "tx_discards": 0.0,
        "rx_errors_general": 0.0,
        "tx_errors_general": 0.0,
        "rx_errors_fcs": 0.0,
        "rx_errors_crc": 0.0,
        "rx_errors_runt": 0.0,
        "rx_errors_rx_pause": 0.0,
        "rx_errors_giant": 0.0,
        "rx_errors_symbol": 0.0,
        "tx_errors_collisions": 0.0,
        "tx_errors_late_collisions": 0.0,
        "tx_errors_deferred_transmissions": 0.0,
        "tx_errors_tx_pause": 0.0,
    }
}

INTERFACE_COUNTERS_REPR = {
    "normal": (
        "InterfaceCounters(rx_bits_rate=Bit(17440.612226202553), "
        "tx_bits_rate=Bit(38000.04350234883), rx_pkts_rate=1.8763970219715047,"
        " tx_pkts_rate=0.6081652214056465, rx_unicast_pkts=14558700.0, "
        "tx_unicast_pkts=14240960.0, rx_multicast_pkts=1996273.0, tx_multicast_pkts="
        "123582.0, rx_broadcast_pkts=1781616.0, tx_broadcast_pkts=6.0, rx_bytes="
        "Byte(1929656819.0), tx_bytes=Byte(1455044979.0), rx_discards=0.0, "
        "tx_discards=0.0, rx_errors_general=0.0, tx_errors_general=0.0, rx_errors_fcs="
        "0.0, rx_errors_crc=0.0, rx_errors_runt=0.0, rx_errors_rx_pause=0.0, "
        "rx_errors_giant=0.0, rx_errors_symbol=0.0, tx_errors_collisions=0.0,"
        " tx_errors_late_collisions=0.0, tx_errors_deferred_transmissions=0.0,"
        " tx_errors_tx_pause=0.0)"
    )
}


INTERFACE_BASE_ARGS = {
    "eth_down": dict(
        name="Eth1",
        enabled=True,
        status_up=False,
        status="notconnect",
        physical=INTERFACE_PHYSICAL_ARGS["standard1"],
        addresses=INTERFACE_IP_ARGS["ipv4_only"],
        counters=INTERFACE_COUNTERS_ARGS["normal"],
    ),
    "eth_up": dict(
        name="Ethernet4",
        enabled=True,
        status_up=True,
        status="up",
        # NOTE: Shows different ways to set the date type objects
        last_status_change="2019-06-01 12:22",
        last_clear=1496498400,
        physical=INTERFACE_PHYSICAL_ARGS["standard2"],
        addresses=INTERFACE_IP_ARGS["ipv6_only"],
        counters=INTERFACE_COUNTERS_ARGS["normal"],
    ),
    "portchannel_disabled": dict(
        name="Po200",
        description="L3 PEERLINK",
        enabled=False,
        status_up=False,
        status="disabled",
        last_status_change=pendulum.DateTime(2019, 2, 25, 17, 54, 42, 464872),
        number_status_changes=2,
        forwarding_model="routed",
        physical=INTERFACE_PHYSICAL_ARGS["standard2"],
        optical=INTERFACE_OPTICAL_ARGS["green"],
        addresses=INTERFACE_IP_ARGS["all_ips"],
        instance="default",
        counters=INTERFACE_COUNTERS_ARGS["normal"],
        members=["Ethernet52", "Ethernet51"],
        last_clear=None,
        update_interval=300.0,
    ),
    "l3_vlan": dict(name="Vl177"),
    "l2_eth_optical": dict(name="Ethernet52"),
    "l3_portchannel": dict(name="Port-Channel200"),
    "invalid_status": dict(name="Lo1", status="dummy_up"),
    "invalid_forwarding_model": dict(name="Lo1", forwarding_model="dummy"),
    "invalid_datetime_attr": dict(name="Lo1", last_status_change="dummy"),
    "invalid_dataclass_attr": dict(name="Lo1", optical=123),
}
INTERFACE_BASE_REPR = {
    "eth_down": (
        "InterfaceBase(name='Ethernet1', description=None, instance=None, members=[], "
        "enabled=True, status_up=False, status='notconnect', last_status_change=None, "
        "number_status_changes=None, last_clear=None, update_interval=None, "
        "forwarding_model=None, physical=InterfacePhysical(mtu=Byte(1500.0), "
        "bandwidth=Bit(1000000000.0), duplex='full', mac=EUI('28-99-3A-F8-5D-E8')), "
        "optical=None, addresses=InterfaceIP(ipv4=IPNetwork('7.7.7.1/24'), ipv6=None, "
        "secondary_ipv4=[], dhcp=False))"
    ),
    "eth_up": (
        "InterfaceBase(name='Ethernet4', description=None, instance=None, members=[], "
        "enabled=True, status_up=True, status='up', last_status_change=DateTime"
        "(2019, 6, 1, 12, 22, 0, tzinfo=Timezone('UTC')), number_status_changes=None, "
        "last_clear=DateTime(2017, 6, 3, 14, 0, 0, tzinfo=Timezone('+00:00')), "
        "update_interval=None, forwarding_model=None, physical=InterfacePhysical(mtu="
        "Byte(9000.0), bandwidth=Bit(1000000000000.0), duplex=None, mac=EUI"
        "('28-99-3A-F8-5D-E8')), optical=None, addresses=InterfaceIP(ipv4=None, ipv6="
        "IPNetwork('fe80::42:32ff:feb1:9fd3/64'), secondary_ipv4=[], dhcp=False))"
    ),
    "portchannel_disabled": (
        "InterfaceBase(name='Port-Channel200', description='L3 PEERLINK', instance"
        "='default', members=['Ethernet52', 'Ethernet51'], enabled=False, status_up="
        "False, status='disabled', last_status_change=DateTime"
        "(2019, 2, 25, 17, 54, 42, 464872), number_status_changes=2, last_clear=None, "
        "update_interval=300.0, forwarding_model='routed', physical=InterfacePhysical"
        "(mtu=Byte(9000.0), bandwidth=Bit(1000000000000.0), duplex=None, mac=EUI"
        "('28-99-3A-F8-5D-E8')), optical=InterfaceOptical(tx=-2.32, rx=-4.5, "
        "status='green', serial_number='XXXYYYZZZ', media_type='10GBASE-SR'), "
        "addresses=InterfaceIP(ipv4=IPNetwork('7.7.7.1/24'), ipv6=IPNetwork"
        "('fe80::42:32ff:feb1:9fd3/64'), secondary_ipv4=['7.7.7.2', '7.7.7.3'], "
        "dhcp=False))"
    ),
}
INTERFACE_BASE_METADATA_REPR = (
    "Metadata(name='interface', type='entity', implementation=None, "
    "created_at=<CREATED_AT>, id=<UUID>, "
    "updated_at=<UPDATED_AT>, collection_count=<COUNT>, parent=None)"
)

INTERFACE_BASE_ASDICT = {
    "eth_down": {
        "name": "Ethernet1",
        "description": None,
        "enabled": True,
        "instance": None,
        "members": [],
        "status_up": False,
        "status": "notconnect",
        "last_status_change": None,
        "number_status_changes": None,
        "last_clear": None,
        "update_interval": None,
        "forwarding_model": None,
        "physical": {
            "mtu": 1500,
            "bandwidth": 1000000000,
            "duplex": "full",
            "mac": "28-99-3A-F8-5D-E8",
        },
        "optical": None,
        "addresses": {
            "ipv4": "7.7.7.1/24",
            "ipv6": None,
            "secondary_ipv4": [],
            "dhcp": False,
        },
        "counters": {
            "rx_bits_rate": 17440.612226202553,
            "tx_bits_rate": 38000.04350234883,
            "rx_pkts_rate": 1.8763970219715047,
            "tx_pkts_rate": 0.6081652214056465,
            "rx_unicast_pkts": 14558700.0,
            "tx_unicast_pkts": 14240960.0,
            "rx_multicast_pkts": 1996273.0,
            "tx_multicast_pkts": 123582.0,
            "rx_broadcast_pkts": 1781616.0,
            "tx_broadcast_pkts": 6.0,
            "rx_bytes": 1929656819.0,
            "tx_bytes": 1455044979.0,
            "rx_discards": 0.0,
            "tx_discards": 0.0,
            "rx_errors_general": 0.0,
            "tx_errors_general": 0.0,
            "rx_errors_fcs": 0.0,
            "rx_errors_crc": 0.0,
            "rx_errors_runt": 0.0,
            "rx_errors_rx_pause": 0.0,
            "rx_errors_giant": 0.0,
            "rx_errors_symbol": 0.0,
            "tx_errors_collisions": 0.0,
            "tx_errors_late_collisions": 0.0,
            "tx_errors_deferred_transmissions": 0.0,
            "tx_errors_tx_pause": 0.0,
        },
        "metadata": None,
        "interface_api": None,
    },
    "eth_up": {
        "name": "Ethernet4",
        "description": None,
        "enabled": True,
        "instance": None,
        "members": [],
        "status_up": True,
        "status": "up",
        "last_status_change": "2019-06-01T12:22:00+00:00",
        "number_status_changes": None,
        "last_clear": "2017-06-03T14:00:00+00:00",
        "update_interval": None,
        "forwarding_model": None,
        "physical": {
            "mtu": 9000,
            "bandwidth": 1000000000000,
            "duplex": None,
            "mac": "28-99-3A-F8-5D-E8",
        },
        "optical": None,
        "addresses": {
            "ipv4": None,
            "ipv6": "fe80::42:32ff:feb1:9fd3/64",
            "secondary_ipv4": [],
            "dhcp": False,
        },
        "counters": {
            "rx_bits_rate": 17440.612226202553,
            "tx_bits_rate": 38000.04350234883,
            "rx_pkts_rate": 1.8763970219715047,
            "tx_pkts_rate": 0.6081652214056465,
            "rx_unicast_pkts": 14558700.0,
            "tx_unicast_pkts": 14240960.0,
            "rx_multicast_pkts": 1996273.0,
            "tx_multicast_pkts": 123582.0,
            "rx_broadcast_pkts": 1781616.0,
            "tx_broadcast_pkts": 6.0,
            "rx_bytes": 1929656819.0,
            "tx_bytes": 1455044979.0,
            "rx_discards": 0.0,
            "tx_discards": 0.0,
            "rx_errors_general": 0.0,
            "tx_errors_general": 0.0,
            "rx_errors_fcs": 0.0,
            "rx_errors_crc": 0.0,
            "rx_errors_runt": 0.0,
            "rx_errors_rx_pause": 0.0,
            "rx_errors_giant": 0.0,
            "rx_errors_symbol": 0.0,
            "tx_errors_collisions": 0.0,
            "tx_errors_late_collisions": 0.0,
            "tx_errors_deferred_transmissions": 0.0,
            "tx_errors_tx_pause": 0.0,
        },
        "metadata": None,
        "interface_api": None,
    },
    "portchannel_disabled": {
        "name": "Port-Channel200",
        "description": "L3 PEERLINK",
        "enabled": False,
        "instance": "default",
        "members": ["Ethernet52", "Ethernet51"],
        "status_up": False,
        "status": "disabled",
        "last_status_change": "2019-02-25T17:54:42.464872",
        "number_status_changes": 2,
        "last_clear": None,
        "update_interval": 300.0,
        "forwarding_model": "routed",
        "physical": {
            "mtu": 9000,
            "bandwidth": 1000000000000,
            "duplex": None,
            "mac": "28-99-3A-F8-5D-E8",
        },
        "optical": {
            "tx": -2.32,
            "rx": -4.5,
            "status": "green",
            "serial_number": "XXXYYYZZZ",
            "media_type": "10GBASE-SR",
        },
        "addresses": {
            "ipv4": "7.7.7.1/24",
            "ipv6": "fe80::42:32ff:feb1:9fd3/64",
            "secondary_ipv4": ["7.7.7.2", "7.7.7.3"],
            "dhcp": False,
        },
        "counters": {
            "rx_bits_rate": 17440.612226202553,
            "tx_bits_rate": 38000.04350234883,
            "rx_pkts_rate": 1.8763970219715047,
            "tx_pkts_rate": 0.6081652214056465,
            "rx_unicast_pkts": 14558700.0,
            "tx_unicast_pkts": 14240960.0,
            "rx_multicast_pkts": 1996273.0,
            "tx_multicast_pkts": 123582.0,
            "rx_broadcast_pkts": 1781616.0,
            "tx_broadcast_pkts": 6.0,
            "rx_bytes": 1929656819.0,
            "tx_bytes": 1455044979.0,
            "rx_discards": 0.0,
            "tx_discards": 0.0,
            "rx_errors_general": 0.0,
            "tx_errors_general": 0.0,
            "rx_errors_fcs": 0.0,
            "rx_errors_crc": 0.0,
            "rx_errors_runt": 0.0,
            "rx_errors_rx_pause": 0.0,
            "rx_errors_giant": 0.0,
            "rx_errors_symbol": 0.0,
            "tx_errors_collisions": 0.0,
            "tx_errors_late_collisions": 0.0,
            "tx_errors_deferred_transmissions": 0.0,
            "tx_errors_tx_pause": 0.0,
        },
        "metadata": None,
        "interface_api": None,
    },
}

INTERFACE_GET_COMMANDS = {
    "eth_down": {
        "eos": [
            f"show interfaces Ethernet1",
            f"show ip interface Ethernet1",
            f"show interfaces Ethernet1 transceiver",
        ]
    },
    "eth_up": {
        "eos": [
            f"show interfaces Ethernet4",
            f"show ip interface Ethernet4",
            f"show interfaces Ethernet4 transceiver",
        ]
    },
    "portchannel_disabled": {
        "eos": [
            f"show interfaces Port-Channel200",
            f"show ip interface Port-Channel200",
            f"show interfaces Port-Channel200 transceiver",
        ]
    },
}
INTERFACE_CONFIG_COMMANDS = {
    "eth_down": {"eos": {"name": "Ethernet1", "disable": None}},
    "eth_up": {"eos": {"name": "Ethernet4", "disable": None}},
    "portchannel_disabled": {"eos": {"name": "Port-Channel200", "disable": None}},
}
INTERFACE_DATA = {
    "eos": {
        "l3_vlan": [
            {
                "show interfaces Vlan177": {
                    "interfaces": {
                        "Vlan177": {
                            "lastStatusChangeTimestamp": 1557398489.1920662,
                            "name": "Vlan177",
                            "interfaceStatus": "connected",
                            "burnedInAddress": "28:99:3a:f8:5d:e8",
                            "mtu": 1500,
                            "hardware": "vlan",
                            "bandwidth": 0,
                            "forwardingModel": "routed",
                            "lineProtocolStatus": "up",
                            "interfaceAddress": [
                                {
                                    "secondaryIpsOrderedList": [],
                                    "broadcastAddress": "255.255.255.255",
                                    "virtualSecondaryIps": {},
                                    "dhcp": False,
                                    "secondaryIps": {},
                                    "primaryIp": {
                                        "maskLen": 28,
                                        "address": "10.177.0.68",
                                    },
                                    "virtualSecondaryIpsOrderedList": [],
                                    "virtualIp": {"maskLen": 0, "address": "0.0.0.0"},
                                }
                            ],
                            "physicalAddress": "28:99:3a:f8:5d:e8",
                            "description": "Vlan 177 description",
                        }
                    }
                },
                "show ip interface Ethernet4": {
                    "interfaces": {
                        "Vlan177": {
                            "directedBroadcastEnabled": False,
                            "interfaceAddress": {
                                "secondaryIpsOrderedList": [],
                                "broadcastAddress": "255.255.255.255",
                                "virtualSecondaryIps": {},
                                "dhcp": False,
                                "secondaryIps": {},
                                "primaryIp": {"maskLen": 28, "address": "10.177.0.68"},
                                "virtualSecondaryIpsOrderedList": [],
                                "virtualIp": {"maskLen": 0, "address": "0.0.0.0"},
                            },
                            "name": "Vlan177",
                            "urpf": "disable",
                            "interfaceStatus": "connected",
                            "maxMssEgress": 0,
                            "maxMssIngress": 0,
                            "enabled": True,
                            "mtu": 1500,
                            "addresslessForwarding": "isInvalid",
                            "vrf": "default",
                            "localProxyArp": False,
                            "injectHosts": False,
                            "proxyArp": False,
                            "gratuitousArp": False,
                            "lineProtocolStatus": "up",
                            "description": "Vlan 177 description",
                        }
                    }
                },
                "show interfaces Vlan177 transceiver": None,
            }
        ],
        "l2_eth_optical": [
            {
                "show interfaces Ethernet52": {
                    "interfaces": {
                        "Ethernet52": {
                            "lastStatusChangeTimestamp": 1559036026.8561628,
                            "lanes": 0,
                            "name": "Ethernet52",
                            "interfaceStatus": "connected",
                            "autoNegotiate": "off",
                            "burnedInAddress": "00:1c:73:f9:e4:3b",
                            "loopbackMode": "loopbackNone",
                            "interfaceStatistics": {
                                "inBitsRate": 218.61442406465778,
                                "inPktsRate": 0.2962212482850488,
                                "outBitsRate": 225.59171934649638,
                                "updateInterval": 5,
                                "outPktsRate": 0.344005348325921,
                            },
                            "mtu": 9214,
                            "hardware": "ethernet",
                            "duplex": "duplexFull",
                            "bandwidth": 10000000000,
                            "forwardingModel": "dataLink",
                            "lineProtocolStatus": "up",
                            "interfaceCounters": {
                                "outBroadcastPkts": 90463,
                                "outUcastPkts": 637813,
                                "lastClear": 1559035567.4582636,
                                "inMulticastPkts": 523404,
                                "counterRefreshTime": 1562149250.687581,
                                "inBroadcastPkts": 1,
                                "outputErrorsDetail": {
                                    "deferredTransmissions": 0,
                                    "txPause": 0,
                                    "collisions": 0,
                                    "lateCollisions": 0,
                                },
                                "inOctets": 89625885,
                                "outDiscards": 0,
                                "outOctets": 118481946,
                                "inUcastPkts": 314238,
                                "inTotalPkts": 837643,
                                "inputErrorsDetail": {
                                    "runtFrames": 0,
                                    "rxPause": 0,
                                    "fcsErrors": 0,
                                    "alignmentErrors": 0,
                                    "giantFrames": 0,
                                    "symbolErrors": 0,
                                },
                                "linkStatusChanges": 4,
                                "outMulticastPkts": 522769,
                                "totalInErrors": 0,
                                "inDiscards": 0,
                                "totalOutErrors": 0,
                            },
                            "interfaceMembership": "Member of Port-Channel200",
                            "interfaceAddress": [],
                            "physicalAddress": "00:1c:73:f9:e4:3b",
                            "description": "lab02 - Eth52",
                        }
                    }
                },
                "show ip interface Ethernet52": None,
                "show interfaces Ethernet52 transceiver": {
                    "interfaces": {
                        "Ethernet52": {
                            "txPower": -2.2482661457521322,
                            "updateTime": 1562101983.7156565,
                            "temperature": 52.1484375,
                            "vendorSn": "ACW1738001SP",
                            "txBias": 6.3020000000000005,
                            "voltage": 3.3571,
                            "narrowBand": False,
                            "rxPower": -1.6071054399385312,
                            "mediaType": "10GBASE-SR",
                        }
                    }
                },
            }
        ],
        "l3_portchannel": [
            {
                "show interfaces Port-Channel200": {
                    "interfaces": {
                        "Port-Channel200": {
                            "lastStatusChangeTimestamp": 1557398494.7540529,
                            "name": "Port-Channel200",
                            "interfaceStatus": "connected",
                            "memberInterfaces": {
                                "Ethernet52": {
                                    "duplex": "duplexFull",
                                    "bandwidth": 1000000000,
                                }
                            },
                            "interfaceStatistics": {
                                "inBitsRate": 464.59683825512343,
                                "inPktsRate": 0.44208471835691365,
                                "outBitsRate": 433.49434765957,
                                "updateInterval": 300,
                                "outPktsRate": 0.4850518108287211,
                            },
                            "mtu": 1500,
                            "hardware": "portChannel",
                            "bandwidth": 1000000000,
                            "forwardingModel": "routed",
                            "fallbackEnabled": False,
                            "lineProtocolStatus": "up",
                            "interfaceCounters": {
                                "outBroadcastPkts": 0,
                                "outUcastPkts": 813343,
                                "totalOutErrors": 0,
                                "inMulticastPkts": 797050,
                                "counterRefreshTime": 1562143933.084021,
                                "inBroadcastPkts": 1,
                                "inOctets": 150779670,
                                "outDiscards": 0,
                                "outOctets": 159640823,
                                "inUcastPkts": 687804,
                                "inTotalPkts": 1483198,
                                "linkStatusChanges": 2,
                                "outMulticastPkts": 797049,
                                "totalInErrors": 0,
                                "inDiscards": 0,
                            },
                            "fallbackEnabledType": "fallbackNone",
                            "interfaceAddress": [
                                {
                                    "secondaryIpsOrderedList": [],
                                    "broadcastAddress": "255.255.255.255",
                                    "virtualSecondaryIps": {},
                                    "dhcp": False,
                                    "secondaryIps": {},
                                    "primaryIp": {
                                        "maskLen": 30,
                                        "address": "10.177.0.9",
                                    },
                                    "virtualSecondaryIpsOrderedList": [],
                                    "virtualIp": {"maskLen": 0, "address": "0.0.0.0"},
                                }
                            ],
                            "physicalAddress": "28:99:3a:f8:5d:e8",
                            "description": "L3 PEERLINK",
                        }
                    }
                },
                "show ip interface Port-Channel200": {
                    "interfaces": {
                        "Port-Channel200": {
                            "directedBroadcastEnabled": False,
                            "interfaceAddress": {
                                "secondaryIpsOrderedList": [],
                                "broadcastAddress": "255.255.255.255",
                                "virtualSecondaryIps": {},
                                "dhcp": False,
                                "secondaryIps": {},
                                "primaryIp": {"maskLen": 30, "address": "10.177.0.9"},
                                "virtualSecondaryIpsOrderedList": [],
                                "virtualIp": {"maskLen": 0, "address": "0.0.0.0"},
                            },
                            "name": "Port-Channel200",
                            "urpf": "disable",
                            "interfaceStatus": "connected",
                            "maxMssEgress": 0,
                            "maxMssIngress": 0,
                            "enabled": True,
                            "mtu": 1500,
                            "addresslessForwarding": "isInvalid",
                            "vrf": "default",
                            "localProxyArp": False,
                            "injectHosts": False,
                            "proxyArp": False,
                            "gratuitousArp": False,
                            "lineProtocolStatus": "up",
                            "description": "L3 PEERLINK",
                        }
                    }
                },
                "show interfaces Port-Channel200 transceiver": None,
            }
        ],
    }
}
INTERFACE_DATA_PARSED = {
    "eos": {
        "l3_vlan": {
            "name": "Vlan177",
            "description": "Vlan 177 description",
            "enabled": True,
            "instance": "default",
            "members": [],
            "status_up": True,
            "status": "connected",
            "last_status_change": "2019-05-09T10:41:29.192066+00:00",
            "number_status_changes": None,
            "last_clear": None,
            "update_interval": None,
            "forwarding_model": "routed",
            "physical": {
                "mtu": 1500,
                "bandwidth": 0,
                "duplex": None,
                "mac": "28-99-3A-F8-5D-E8",
            },
            "optical": None,
            "addresses": {
                "ipv4": "10.177.0.68/28",
                "ipv6": None,
                "secondary_ipv4": [],
                "dhcp": False,
            },
            "counters": None,
            "interface_api": None,
        },
        "l2_eth_optical": {
            "name": "Ethernet52",
            "description": "lab02 - Eth52",
            "enabled": True,
            "instance": None,
            "members": [],
            "status_up": True,
            "status": "connected",
            "last_status_change": "2019-05-28T09:33:46.856163+00:00",
            "number_status_changes": 4,
            "last_clear": "2019-05-28T09:26:07.458264+00:00",
            "update_interval": 5.0,
            "forwarding_model": "data_link",
            "physical": {
                "mtu": 9214,
                "bandwidth": 10000000000,
                "duplex": "duplexFull",
                "mac": "00-1C-73-F9-E4-3B",
            },
            "optical": {
                "tx": -2.2482661457521322,
                "rx": -1.6071054399385312,
                "status": "green",
                "serial_number": "ACW1738001SP",
                "media_type": "10GBASE-SR",
            },
            "addresses": None,
            "counters": {
                "rx_bits_rate": 218.61442406465778,
                "tx_bits_rate": 225.59171934649638,
                "rx_pkts_rate": 0.2962212482850488,
                "tx_pkts_rate": 0.344005348325921,
                "rx_unicast_pkts": 314238.0,
                "tx_unicast_pkts": 637813.0,
                "rx_multicast_pkts": 523404.0,
                "tx_multicast_pkts": 522769.0,
                "rx_broadcast_pkts": 1.0,
                "tx_broadcast_pkts": 90463.0,
                "rx_bytes": 89625885.0,
                "tx_bytes": 118481946.0,
                "rx_discards": 0.0,
                "tx_discards": 0.0,
                "rx_errors_general": 0.0,
                "tx_errors_general": 0.0,
                "rx_errors_fcs": 0.0,
                "rx_errors_crc": 0.0,
                "rx_errors_runt": 0.0,
                "rx_errors_rx_pause": 0.0,
                "rx_errors_giant": 0.0,
                "rx_errors_symbol": 0.0,
                "tx_errors_collisions": 0.0,
                "tx_errors_late_collisions": 0.0,
                "tx_errors_deferred_transmissions": 0.0,
                "tx_errors_tx_pause": 0.0,
            },
            "interface_api": None,
        },
        "l3_portchannel": {
            "name": "Port-Channel200",
            "description": "L3 PEERLINK",
            "enabled": True,
            "instance": "default",
            "members": ["Ethernet52"],
            "status_up": True,
            "status": "connected",
            "last_status_change": "2019-05-09T10:41:34.754053+00:00",
            "number_status_changes": 2,
            "last_clear": None,
            "update_interval": 300.0,
            "forwarding_model": "routed",
            "physical": {
                "mtu": 1500,
                "bandwidth": 1000000000,
                "duplex": None,
                "mac": "28-99-3A-F8-5D-E8",
            },
            "optical": None,
            "addresses": {
                "ipv4": "10.177.0.9/30",
                "ipv6": None,
                "secondary_ipv4": [],
                "dhcp": False,
            },
            "counters": {
                "rx_bits_rate": 464.59683825512343,
                "tx_bits_rate": 433.49434765957,
                "rx_pkts_rate": 0.44208471835691365,
                "tx_pkts_rate": 0.4850518108287211,
                "rx_unicast_pkts": 687804.0,
                "tx_unicast_pkts": 813343.0,
                "rx_multicast_pkts": 797050.0,
                "tx_multicast_pkts": 797049.0,
                "rx_broadcast_pkts": 1.0,
                "tx_broadcast_pkts": 0.0,
                "rx_bytes": 150779670.0,
                "tx_bytes": 159640823.0,
                "rx_discards": 0.0,
                "tx_discards": 0.0,
                "rx_errors_general": 0.0,
                "tx_errors_general": 0.0,
                "rx_errors_fcs": 0.0,
                "rx_errors_crc": 0.0,
                "rx_errors_runt": 0.0,
                "rx_errors_rx_pause": 0.0,
                "rx_errors_giant": 0.0,
                "rx_errors_symbol": 0.0,
                "tx_errors_collisions": 0.0,
                "tx_errors_late_collisions": 0.0,
                "tx_errors_deferred_transmissions": 0.0,
                "tx_errors_tx_pause": 0.0,
            },
            "interface_api": None,
        },
    }
}


@pytest.fixture
def interface_params(request):
    return INTERFACE_BASE_ARGS[request.getfixturevalue("intf_type")]


@pytest.fixture
def interface_base_obj(interface_params):
    return InterfaceBase(**interface_params)


@pytest.fixture
def module(get_implementation):
    return MODULE_MAPPING[get_implementation]


@pytest.fixture
def intf_imp_obj(module, interface_params):
    return module.Interface(**interface_params)


@pytest.fixture
def intf_imp_parser(module):
    return module.ParseInterface


def metadata_processor(metadata_obj, implementation, representation):
    # Retrieving UUID from instantiated object
    uid = repr(metadata_obj.id)

    # Retrieving timestamp from instantiated object
    created = repr(metadata_obj.created_at)

    if metadata_obj.updated_at:
        updated_at = repr(metadata_obj.updated_at)
        count = "1"
    else:
        updated_at = "None"
        count = "0"

    # Make the respective replacement on the expected output
    expected_metadata = re.sub(r"<CREATED_AT>", created, representation)
    expected_metadata = re.sub(r"<UUID>", uid, expected_metadata)
    expected_metadata = re.sub(r"<UPDATED_AT>", updated_at, expected_metadata)
    expected_metadata = re.sub(r"<COUNT>", count, expected_metadata)
    expected_metadata = re.sub(r"<IMPLEMENTATION>", implementation, expected_metadata)

    return expected_metadata


class TestInterfacePhysical:
    # TODO: Pending function to verify InterfacePhysicalBuilder
    @pytest.mark.parametrize("phy_type", ["standard1", "standard2"])
    def test_instation(self, phy_type):
        phy_dict = INTERFACE_PHYSICAL_ARGS[phy_type]
        assert repr(InterfacePhysical(**phy_dict)) == INTERFACE_PHYSICAL_REPR[phy_type]

    def test_invalid_mac_format(self):
        with pytest.raises(
            ValidationError, match="failed to detect EUI version: '28.99.3a.f8.5d.e8'"
        ):
            InterfacePhysical(**INTERFACE_PHYSICAL_ARGS["invalid_mac_format"])


class TestInterfaceIP:
    # TODO: Pending function to verify InterfaceIPBuilder
    @pytest.mark.parametrize("ip_type", ["ipv4_only", "ipv6_only", "dhcp", "all_ips"])
    def test_instation(self, ip_type):
        ip_dict = INTERFACE_IP_ARGS[ip_type]
        assert repr(InterfaceIP(**ip_dict)) == INTERFACE_IP_REPR[ip_type]

    @pytest.mark.parametrize(
        "ip_type,expected",
        [
            ("invalid_ipv4", "invalid IPNetwork 7.7.7.7 255.255.255.0"),
            ("invalid_ipv6", "invalid IPNetwork fe80::42:32ff:feb1:9fd3/255"),
        ],
    )
    def test_invalid(self, ip_type, expected):
        with pytest.raises(ValidationError, match=expected):
            InterfaceIP(**INTERFACE_IP_ARGS[ip_type])


class TestInterfaceOptical:
    # TODO: Pending function to verify InterfaceIPBuilder
    @pytest.mark.parametrize("optical_type", ["green", "yellow", "red"])
    def test_instation(self, optical_type):
        optical_dict = INTERFACE_OPTICAL_ARGS[optical_type]
        assert (
            repr(InterfaceOptical(**optical_dict))
            == INTERFACE_OPTICAL_REPR[optical_type]
        )


class TestInterfaceCounters:
    # TODO: Pending function to verify InterfaceCountersBuilder
    @pytest.mark.parametrize("counters_type", ["normal"])
    def test_instation(self, counters_type):
        counters_dict = INTERFACE_COUNTERS_ARGS[counters_type]
        assert (
            repr(InterfaceCounters(**counters_dict))
            == INTERFACE_COUNTERS_REPR[counters_type]
        )


class TestInterfaceBase:
    # TODO: Pending function to verify InterfaceBaseBuilder
    @pytest.mark.parametrize(
        "intf_type", ["eth_down", "eth_up", "portchannel_disabled"]
    )
    def test_instatiation(self, intf_type, interface_base_obj):
        expected_metadata = metadata_processor(
            interface_base_obj.metadata,
            implementation="None",
            representation=INTERFACE_BASE_METADATA_REPR,
        )
        assert repr(interface_base_obj) == INTERFACE_BASE_REPR[intf_type]
        assert repr(interface_base_obj.metadata) == expected_metadata

    @pytest.mark.parametrize(
        "intf_type,expected",
        [
            ("invalid_status", "Interface status not known: dummy_up - None"),
            ("invalid_forwarding_model", "Unknown forwarding model: dummy"),
            ("invalid_datetime_attr", "invalid datetime format"),
            (
                "invalid_dataclass_attr",
                "instance of InterfaceOptical, tuple or dict expected",
            ),
        ],
    )
    def test_invalid(self, intf_type, expected):
        with pytest.raises(ValidationError, match=expected):
            InterfaceBase(**INTERFACE_BASE_ARGS[intf_type])

    @pytest.mark.parametrize(
        "intf_type", ["eth_down", "eth_up", "portchannel_disabled"]
    )
    def test_asdict(self, intf_type, interface_base_obj):
        del interface_base_obj.metadata
        assert interface_base_obj.to_dict() == INTERFACE_BASE_ASDICT[intf_type]


class TestInterfacesBase:
    "Tests the collection object"

    def test_instatiation(self):
        # Creation on one instance
        eth_down = InterfaceBase(**INTERFACE_BASE_ARGS["eth_down"])
        intf_collection = InterfacesBase({"eth1": eth_down})

        # Creating second instance and attaching it
        eth_up = InterfaceBase(**INTERFACE_BASE_ARGS["eth_up"])
        intf_collection.update({"eth4": eth_up})

        assert repr(intf_collection) == "InterfacesBase('eth1', 'eth4')"
        # Verifies as well the individual objects
        assert repr(intf_collection["eth1"]) == INTERFACE_BASE_REPR["eth_down"]
        assert repr(intf_collection["eth4"]) == INTERFACE_BASE_REPR["eth_up"]
        assert intf_collection.metadata.name == "interfaces"
        assert intf_collection.metadata.type == "collection"

    def test_invalid_attribute(self):
        with pytest.raises(
            ValueError,
            match="some_data_structure -> It is not a valid interface object",
        ):
            InterfacesBase({"eth1": "some_data_structure"})


class InterfaceTester:
    "Performs checks on the interface object of each implementation"

    @pytest.mark.parametrize(
        "intf_type", ["eth_down", "eth_up", "portchannel_disabled"]
    )
    def test_meta_attrs(self, intf_imp_obj, intf_type, get_implementation):
        assert "interface" == intf_imp_obj.metadata.name
        assert "entity" == intf_imp_obj.metadata.type
        assert get_implementation == intf_imp_obj.metadata.implementation

    @pytest.mark.parametrize(
        "intf_type", ["eth_down", "eth_up", "portchannel_disabled"]
    )
    def test_get_command(self, get_os, intf_imp_obj, intf_type):
        assert intf_imp_obj.get_cmd is None
        # Now verify the command when generated
        get_cmd = intf_imp_obj.generate_get_cmd(intf_imp_obj.name)
        assert get_cmd == INTERFACE_GET_COMMANDS[intf_type][get_os]

    # TODO: Implement `get` method test - need mock
    # TODO: Implement `enable` method test - need mock
    # TODO: Implement `disable` method test - need mock

    @pytest.mark.parametrize(
        "intf_type", ["l3_vlan", "l2_eth_optical", "l3_portchannel"]
    )
    def test_parse(self, get_os, intf_imp_parser, intf_type):
        raw_data = INTERFACE_DATA[get_os][intf_type]
        # Apply interface parsing of the object based on the raw output
        parsed_data = intf_imp_parser.parse(raw_data=raw_data[0])

        # Lets do the comparison based on the dict returned without metadata
        parsed_dict = InterfaceBase(**parsed_data).to_dict()
        parsed_dict.pop("metadata")
        assert parsed_dict == INTERFACE_DATA_PARSED[get_os][intf_type]


@pytest.mark.eos
class TestInterfaceEos(InterfaceTester):
    net_os = "eos"
    implementation = "pyeapi"
