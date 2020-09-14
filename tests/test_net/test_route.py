import re
import copy
import pytest
import netapi.net as net
from netapi.net.route import RouteBase, Via
from pydantic import ValidationError


MODULE_MAPPING = {"EOS-PYEAPI": net.eos.pyeapier}


VIA_ARGS = {
    "default": dict(interface="Ethernet77", next_hop=None),
    "with_next_hop": dict(interface="Ethernet44", next_hop="10.44.44.44"),
    "multiple_vias": [
        dict(interface="Vlan120", next_hop="10.120.0.1"),
        dict(interface="Vlan140", next_hop="10.140.0.1"),
    ],
    "invalid_next_hop": dict(interface="Ethernet99", next_hop="1.1.1.2323.12"),
}


ROUTE_BASE_ARGS = {
    "route_default_attrs": dict(
        dest="10.167.0.0/30",
        instance=None,
        network="10.167.0.0/30",
        protocol="connected",
        active=True,
        inactive_reason=None,
        age=None,  # NOTE: By default EOS does not give age
        tag=None,
        metric=None,
        preference=None,
        vias=[VIA_ARGS["default"]],
        extra_attributes={},
    ),
    "route_multiple_vias": dict(
        dest="10.77.7.7",
        instance="default",
        network="10.77.0.0/16",
        protocol="ospf",
        active=True,
        inactive_reason=None,
        age=1234567,
        tag=77,
        metric=20,
        preference=110,
        vias=VIA_ARGS["multiple_vias"],
        extra_attributes={},
    ),
    "route_vrf_with_attrs": dict(
        dest="10.40.7.7",
        instance="TEST-INSTANCE",
        network="10.40.7.0/24",
        protocol="bgp",
        active=True,
        inactive_reason=None,
        age=1234567,
        tag=77,
        metric=0,
        preference=200,
        vias=[VIA_ARGS["with_next_hop"]],
        extra_attributes={"route_leaked": False, "route_action": "forward"},
    ),
    "route_intf": dict(dest="3.3.3.3"),
    "route_intf_and_ip": dict(dest="2.2.2.2"),
    "route_vrf": dict(dest="5.5.5.5", instance="MANAGEMENT"),
    "invalid_destination": dict(dest="10.40.7.7777", instance="TEST-INSTANCE"),
    "invalid_vias_obj": dict(dest="10.40.7.7", vias=[{"dummy": "value"}]),
    "invalid_network": dict(
        dest="10.40.127.77", network="10.40.1237.0/24", protocol="bgp"
    ),
    "invalid_protocol": dict(
        dest="10.40.127.77", network="10.40.127.0/24", protocol="bgp123"
    ),
    "invalid_age": dict(
        dest="10.40.127.77", network="10.40.127.0/24", protocol="bgp", age="123"
    ),
}


def via_builder(via_dict):
    """Returns a Via object from a dict passed"""
    return Via(**via_dict)


def route_base_builder(route_base_dict):
    _vias = []
    new_route_base_dict = copy.deepcopy(route_base_dict)
    for via in new_route_base_dict.get("vias", []):
        _vias.append(via_builder(via))
    # By doing it this way it gets validated
    new_route_base_dict["vias"] = _vias
    return RouteBase(**new_route_base_dict)


VIA_REPR = {
    "default": "Via(interface='Ethernet77', next_hop=None)",
    "with_next_hop": "Via(interface='Ethernet44', next_hop=IPAddress('10.44.44.44'))",
}

ROUTE_BASE_REPR = {
    "no_values": ("RouteBase(destination=None, instance=None, paths=None)"),
    "route_default_attrs": (
        "RouteBase(dest='10.167.0.0/30', instance=None, "
        "network=IPNetwork('10.167.0.0/30'), protocol='connected', "
        "vias=[Via(interface='Ethernet77', next_hop=None)], metric=None, "
        "preference=None, active=True, inactive_reason=None, age=None, "
        "tag=None, extra_attributes={})"
    ),
    "route_multiple_vias": (
        "RouteBase(dest='10.77.7.7', instance='default', "
        "network=IPNetwork('10.77.0.0/16'), protocol='ospf', "
        "vias=[Via(interface='Vlan120', next_hop=IPAddress('10.120.0.1')), "
        "Via(interface='Vlan140', next_hop=IPAddress('10.140.0.1'))], metric=20, "
        "preference=110, active=True, inactive_reason=None, age=Duration(weeks=2, "
        "days=0, hours=6, minutes=56, seconds=7), tag=77, extra_attributes={})"
    ),
    "route_vrf_with_attrs": (
        "RouteBase(dest='10.40.7.7', instance='TEST-INSTANCE', "
        "network=IPNetwork('10.40.7.0/24'), protocol='bgp', "
        "vias=[Via(interface='Ethernet44', next_hop=IPAddress('10.44.44.44'))], "
        "metric=0, preference=200, active=True, inactive_reason=None, "
        "age=Duration(weeks=2, days=0, hours=6, minutes=56, seconds=7), tag=77, "
        "extra_attributes={'route_leaked': False, 'route_action': 'forward'})"
    ),
}
ROUTE_BASE_METADATA_REPR = (
    "Metadata(name='route', type='entity', implementation=None, "
    "created_at=<CREATED_AT>, id=<UUID>, "
    "updated_at=<UPDATED_AT>, collection_count=<COUNT>, parent=None)"
)
ROUTE_BASE_ASDICT = {
    "route_default_attrs": {
        "dest": "10.167.0.0/30",
        "instance": None,
        "network": "10.167.0.0/30",
        "protocol": "connected",
        "vias": [{"interface": "Ethernet77", "next_hop": None}],
        "metric": None,
        "preference": None,
        "active": True,
        "inactive_reason": None,
        "age": None,
        "tag": None,
        "extra_attributes": {},
        "route_api": None,
        "metadata": None,
    },
    "route_multiple_vias": {
        "dest": "10.77.7.7",
        "instance": "default",
        "network": "10.77.0.0/16",
        "protocol": "ospf",
        "vias": [
            {"interface": "Vlan120", "next_hop": "10.120.0.1"},
            {"interface": "Vlan140", "next_hop": "10.140.0.1"},
        ],
        "metric": 20,
        "preference": 110,
        "active": True,
        "inactive_reason": None,
        "age": "2 weeks 6 hours 56 minutes 7 seconds",
        "tag": 77,
        "extra_attributes": {},
        "route_api": None,
        "metadata": None,
    },
    "route_vrf_with_attrs": {
        "dest": "10.40.7.7",
        "instance": "TEST-INSTANCE",
        "network": "10.40.7.0/24",
        "protocol": "bgp",
        "vias": [{"interface": "Ethernet44", "next_hop": "10.44.44.44"}],
        "metric": 0,
        "preference": 200,
        "active": True,
        "inactive_reason": None,
        "age": "2 weeks 6 hours 56 minutes 7 seconds",
        "tag": 77,
        "extra_attributes": {"route_leaked": False, "route_action": "forward"},
        "route_api": None,
        "metadata": None,
    },
}
ROUTE_GET_COMMANDS = {
    "route_default_attrs": {"eos": ["show ip route 10.167.0.0/30 detail"]},
    "route_multiple_vias": {"eos": ["show ip route vrf default 10.77.7.7 detail"]},
    "route_vrf_with_attrs": {
        "eos": ["show ip route vrf TEST-INSTANCE 10.40.7.7 detail"]
    },
}
ROUTE_DATA = {
    "eos": {
        "route_intf": [
            {
                "show ip route 3.3.3.3 detail": {
                    "vrfs": {
                        "default": {
                            "routes": {
                                "3.3.3.3/32": {
                                    "kernelProgrammed": True,
                                    "directlyConnected": True,
                                    "routeAction": "forward",
                                    "routeLeaked": False,
                                    "vias": [{"interface": "Loopback77"}],
                                    "hardwareProgrammed": True,
                                    "routeType": "static",
                                }
                            },
                            "allRoutesProgrammedKernel": True,
                            "routingDisabled": False,
                            "allRoutesProgrammedHardware": True,
                            "defaultRouteState": "notReachable",
                        }
                    }
                }
            }
        ],
        "route_intf_and_ip": [
            {
                "show ip route 2.2.2.2 detail": {
                    "vrfs": {
                        "default": {
                            "routes": {
                                "2.2.2.2/32": {
                                    "kernelProgrammed": True,
                                    "directlyConnected": False,
                                    "routeAction": "forward",
                                    "routeLeaked": False,
                                    "vias": [
                                        {
                                            "interface": "Loopback77",
                                            "nexthopAddr": "77.77.77.2",
                                        }
                                    ],
                                    "metric": 0,
                                    "hardwareProgrammed": True,
                                    "routeType": "static",
                                    "preference": 1,
                                }
                            },
                            "allRoutesProgrammedKernel": True,
                            "routingDisabled": False,
                            "allRoutesProgrammedHardware": True,
                            "defaultRouteState": "notReachable",
                        }
                    }
                }
            }
        ],
        "route_vrf": [
            {
                "show ip route vrf MANAGEMENT 5.5.5.5 detail": {
                    "vrfs": {
                        "MANAGEMENT": {
                            "routes": {
                                "5.5.5.5/32": {
                                    "kernelProgrammed": True,
                                    "directlyConnected": False,
                                    "routeAction": "forward",
                                    "routeLeaked": False,
                                    "vias": [
                                        {
                                            "interface": "Management1",
                                            "nexthopAddr": "10.77.7.1",
                                        }
                                    ],
                                    "metric": 0,
                                    "hardwareProgrammed": True,
                                    "routeType": "static",
                                    "preference": 1,
                                }
                            },
                            "allRoutesProgrammedKernel": True,
                            "routingDisabled": False,
                            "allRoutesProgrammedHardware": True,
                            "defaultRouteState": "reachable",
                        }
                    }
                }
            }
        ],
    }
}

ROUTE_DATA_PARSED = {
    "eos": {
        "route_intf": {
            "dest": "3.3.3.3/32",
            "instance": "default",
            "network": "3.3.3.3/32",
            "protocol": "static",
            "vias": [{"interface": "Loopback77", "next_hop": None}],
            "metric": None,
            "preference": None,
            "active": True,
            "inactive_reason": None,
            "age": None,
            "tag": None,
            "extra_attributes": {"route_action": "forward", "route_leaked": False},
            "route_api": None,
        },
        "route_intf_and_ip": {
            "dest": "2.2.2.2/32",
            "instance": "default",
            "network": "2.2.2.2/32",
            "protocol": "static",
            "vias": [{"interface": "Loopback77", "next_hop": "77.77.77.2"}],
            "metric": 0,
            "preference": 1,
            "active": True,
            "inactive_reason": None,
            "age": None,
            "tag": None,
            "extra_attributes": {"route_action": "forward", "route_leaked": False},
            "route_api": None,
        },
        "route_vrf": {
            "dest": "5.5.5.5/32",
            "instance": "MANAGEMENT",
            "network": "5.5.5.5/32",
            "protocol": "static",
            "vias": [{"interface": "Management1", "next_hop": "10.77.7.1"}],
            "metric": 0,
            "preference": 1,
            "active": True,
            "inactive_reason": None,
            "age": None,
            "tag": None,
            "extra_attributes": {"route_action": "forward", "route_leaked": False},
            "route_api": None,
        },
    }
}


@pytest.fixture
def route_params(request):
    return ROUTE_BASE_ARGS[request.getfixturevalue("route_type")]


# RouteBase fixture
@pytest.fixture
def route_base_obj(request, route_params):
    return route_base_builder(route_params)


@pytest.fixture
def module(get_implementation):
    return MODULE_MAPPING[get_implementation]


@pytest.fixture
def route_imp_obj(module, route_params):
    return module.Route(**route_params)


@pytest.fixture
def route_imp_parser(module, route_params):
    return module.ParseRoute


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


class TestVia:
    # TODO: Pending function to verify RouteBuilder
    @pytest.mark.parametrize("via_type", ["default", "with_next_hop"])
    def test_instatiation(self, via_type):
        via_dict = VIA_ARGS[via_type]
        assert repr(Via(**via_dict)) == VIA_REPR[via_type]

    def test_invalid_address(self):
        with pytest.raises(
            ValidationError,
            match="failed to detect a valid IP address from '1.1.1.2323.12'",
        ):
            Via(**VIA_ARGS["invalid_next_hop"])


class TestRouteBase:
    @pytest.mark.parametrize(
        "route_type",
        [
            # "no_values",
            "route_default_attrs",
            "route_multiple_vias",
            "route_vrf_with_attrs",
        ],
    )
    def test_instatiation(self, route_type, route_base_obj):
        expected_metadata = metadata_processor(
            route_base_obj.metadata,
            implementation="None",
            representation=ROUTE_BASE_METADATA_REPR,
        )
        assert repr(route_base_obj) == ROUTE_BASE_REPR[route_type]
        assert repr(route_base_obj.metadata) == expected_metadata

    @pytest.mark.parametrize(
        "route_type,expected",
        [
            ("invalid_destination", "Not a valid IP address: 10.40.7.7777"),
            ("invalid_vias_obj", "unexpected keyword argument 'dummy'"),
            ("invalid_network", "invalid IPNetwork 10.40.1237.0/24"),
            ("invalid_protocol", "Unknown protocol bgp123"),
            ("invalid_age", "unsupported type for timedelta seconds component: str"),
        ],
    )
    def test_invalid(self, route_type, expected):
        with pytest.raises(ValidationError, match=expected):
            RouteBase(**ROUTE_BASE_ARGS[route_type])

    @pytest.mark.parametrize(
        "route_type",
        ["route_default_attrs", "route_multiple_vias", "route_vrf_with_attrs"],
    )
    def test_asdict(self, route_type, route_base_obj):
        del route_base_obj.metadata
        assert route_base_obj.to_dict() == ROUTE_BASE_ASDICT[route_type]


class RouteTester:
    "Performs checks on the route object of each implementation"

    @pytest.mark.parametrize(
        "route_type",
        ["route_default_attrs", "route_multiple_vias", "route_vrf_with_attrs"],
    )
    def test_meta_attrs(self, route_imp_obj, route_type, get_implementation):
        assert "route" == route_imp_obj.metadata.name
        assert "entity" == route_imp_obj.metadata.type
        assert get_implementation == route_imp_obj.metadata.implementation

    @pytest.mark.parametrize(
        "route_type",
        ["route_default_attrs", "route_multiple_vias", "route_vrf_with_attrs"],
    )
    def test_get_command(self, get_os, route_imp_obj, route_type):
        assert route_imp_obj.get_cmd is None
        # Now verify the command when generated
        get_cmd = route_imp_obj.generate_get_cmd(
            route_imp_obj.dest, route_imp_obj.instance
        )
        assert get_cmd == ROUTE_GET_COMMANDS[route_type][get_os]

    # TODO: Implement `get` method test - need mock
    # TODO: Implement `create` method test - need mock
    # TODO: Implement `delete` method test - need mock

    @pytest.mark.parametrize(
        "route_type", ["route_intf", "route_intf_and_ip", "route_vrf"]
    )
    def test_parse(self, get_os, route_imp_parser, route_type):
        raw_data = ROUTE_DATA[get_os][route_type]
        # Apply route parsing of the object based on the raw output
        parsed_data = route_imp_parser.parse(raw_data=raw_data[0])

        # Lets do the comparison based on the dict returned without metadata
        parsed_dict = RouteBase(**parsed_data).to_dict()
        parsed_dict.pop("metadata")
        assert parsed_dict == ROUTE_DATA_PARSED[get_os][route_type]


@pytest.mark.eos
class TestRouteEos(RouteTester):
    net_os = "eos"
    implementation = "pyeapi"
