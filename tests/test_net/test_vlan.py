import re
import pytest
import netapi.net as net
from netapi.net.vlan import VlanBase, VlansBase
from pydantic import ValidationError


MODULE_MAPPING = {"EOS-PYEAPI": net.eos.pyeapier}


VLAN_BASE_ARGS = {
    "default": dict(id=7),
    "custom_enabled": dict(
        id=7,
        name="TEST_VLAN",
        dynamic=False,
        status="active",
        status_up=True,
        interfaces=["Ethernet1", "Ethernet2"],
    ),
    "custom_disabled": dict(
        id=70,
        name="TEST_VLAN",
        dynamic=False,
        status="suspended",
        status_up=False,
        interfaces=["Ethernet1", "Ethernet2"],
    ),
    "ceos1_vlan_7_enabled": dict(
        id=7,
        name="TEST_VLAN",
        dynamic=False,
        status="active",
        status_up=True,
        interfaces=["Cpu", "Ethernet1"],
    ),
    "ceos1_vlan_7_disabled": dict(
        id=7,
        name="TEST_VLAN",
        dynamic=False,
        status="suspended",
        status_up=False,
        interfaces=["Cpu", "Ethernet1"],
    ),
    "invalid_status": dict(id=7, status="dummy"),
}
VLAN_BASE_REPR = {
    "default": (
        "VlanBase(id=7, name=None, dynamic=None, status_up=None, status=None, "
        "interfaces=None)"
    ),
    "custom_enabled": (
        "VlanBase(id=7, name='TEST_VLAN', dynamic=False, status_up=True, "
        "status='active', interfaces=['Ethernet1', 'Ethernet2'])"
    ),
    "custom_disabled": (
        "VlanBase(id=70, name='TEST_VLAN', dynamic=False, status_up="
        "False, status='suspended', interfaces=['Ethernet1', 'Ethernet2'])"
    ),
    "ceos1_vlan_7_enabled": (
        "VlanBase(id=7, name='TEST_VLAN', dynamic=False, status_up=True, "
        "status='active', interfaces=['Cpu', 'Ethernet1'])"
    ),
    "ceos1_vlan_7_disabled": (
        "VlanBase(id=7, name='TEST_VLAN', dynamic=False, status_up="
        "False, status='suspended', interfaces=['Cpu', 'Ethernet1'])"
    ),
}
VLAN_BASE_METADATA_REPR = (
    "Metadata(name='vlan', type='entity', implementation=None, "
    "created_at=<CREATED_AT>, id=<UUID>, "
    "updated_at=<UPDATED_AT>, collection_count=<COUNT>, parent=None)"
)
VLAN_BASE_ASDICT = {
    "default": {
        "id": 7,
        "name": None,
        "dynamic": None,
        "status_up": None,
        "status": None,
        "interfaces": None,
        "metadata": None,
        "vlan_api": None,
    },
    "custom_enabled": {
        "id": 7,
        "name": "TEST_VLAN",
        "dynamic": False,
        "status_up": True,
        "status": "active",
        "interfaces": ["Ethernet1", "Ethernet2"],
        "metadata": None,
        "vlan_api": None,
    },
    "custom_disabled": {
        "id": 70,
        "name": "TEST_VLAN",
        "dynamic": False,
        "status_up": False,
        "status": "suspended",
        "interfaces": ["Ethernet1", "Ethernet2"],
        "metadata": None,
        "vlan_api": None,
    },
}
VLAN_GET_COMMANDS = {"default": {"eos": ["show vlan id 7"]}}
VLAN_CONFIG_COMMANDS = {
    "custom_enabled": {"eos": (7, dict(value="active"))},
    "custom_disabled": {"eos": (70, dict(value="suspended"))},
}
VLAN_DATA = {
    "eos": {
        "default": [
            {
                "show vlan id 7": {
                    "sourceDetail": "",
                    "vlans": {
                        "7": {
                            "status": None,
                            "name": None,
                            "interfaces": None,
                            "dynamic": None,
                        }
                    },
                }
            }
        ],
        "custom_enabled": [
            {
                "show vlan id 7": {
                    "sourceDetail": "",
                    "vlans": {
                        "7": {
                            "status": "active",
                            "name": "TEST_VLAN",
                            "interfaces": {
                                "Ethernet1": {"privatePromoted": False},
                                "Ethernet2": {"privatePromoted": False},
                            },
                            "dynamic": False,
                        }
                    },
                }
            }
        ],
        "custom_disabled": [
            {
                "show vlan id 70": {
                    "sourceDetail": "",
                    "vlans": {
                        "70": {
                            "status": "suspended",
                            "name": "TEST_VLAN",
                            "interfaces": {
                                "Ethernet1": {"privatePromoted": False},
                                "Ethernet2": {"privatePromoted": False},
                            },
                            "dynamic": False,
                        }
                    },
                }
            }
        ],
    }
}
VLAN_DATA_PARSED = {
    "eos": {
        "default": {
            "id": 7,
            "name": None,
            "dynamic": None,
            "status": None,
            "status_up": None,
            "interfaces": None,
            "vlan_api": None,
        },
        "custom_enabled": {
            "id": 7,
            "name": "TEST_VLAN",
            "dynamic": False,
            "status": "active",
            "status_up": True,
            "interfaces": ["Ethernet1", "Ethernet2"],
            "vlan_api": None,
        },
        "custom_disabled": {
            "id": 70,
            "name": "TEST_VLAN",
            "dynamic": False,
            "status": "suspended",
            "status_up": False,
            "interfaces": ["Ethernet1", "Ethernet2"],
            "vlan_api": None,
        },
    }
}


@pytest.fixture
def module(get_implementation):
    return MODULE_MAPPING[get_implementation]


@pytest.fixture
def vlan_parameters(request):
    return VLAN_BASE_ARGS[request.getfixturevalue("vlan_type")]


@pytest.fixture
def vlan_base_obj(vlan_parameters):
    return VlanBase(**vlan_parameters)


@pytest.fixture
def vlan_imp_obj(module, vlan_parameters):
    return module.Vlan(**vlan_parameters)


@pytest.fixture
def vlan_imp_parser(module):
    return module.ParseVlan


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


class TestVlanBase:
    @pytest.mark.parametrize(
        "vlan_type", ["default", "custom_enabled", "custom_disabled"]
    )
    def test_instatiation(self, vlan_type, vlan_base_obj):
        expected_metadata = metadata_processor(
            vlan_base_obj.metadata,
            implementation="None",
            representation=VLAN_BASE_METADATA_REPR,
        )
        assert repr(vlan_base_obj) == VLAN_BASE_REPR[vlan_type]
        assert repr(vlan_base_obj.metadata) == expected_metadata

    def test_invalid_status(self):
        with pytest.raises(ValidationError, match="Vlan status not known: dummy"):
            VlanBase(**VLAN_BASE_ARGS["invalid_status"])

    @pytest.mark.parametrize(
        "vlan_type", ["default", "custom_enabled", "custom_disabled"]
    )
    def test_asdict(self, vlan_type, vlan_base_obj):
        del vlan_base_obj.metadata
        assert vlan_base_obj.to_dict() == VLAN_BASE_ASDICT[vlan_type]


class TestVlansBase:
    "Tests the collection object"

    def test_instatiation(self):
        # Creation on one instance
        vl7 = VlanBase(**VLAN_BASE_ARGS["custom_enabled"])
        vlan_collection = VlansBase({7: vl7})

        # Creating second instance and attaching it
        vl70 = VlanBase(**VLAN_BASE_ARGS["custom_disabled"])
        vlan_collection.update({70: vl70})

        assert repr(vlan_collection) == "VlansBase(7, 70)"
        # Verifies as well the individual objects
        assert repr(vlan_collection[7]) == VLAN_BASE_REPR["custom_enabled"]
        assert repr(vlan_collection[70]) == VLAN_BASE_REPR["custom_disabled"]
        assert vlan_collection.metadata.name == "vlans"
        assert vlan_collection.metadata.type == "collection"

    def test_invalid_attribute(self):
        with pytest.raises(
            ValueError, match="some_data_structure -> It is not a valid vlan object"
        ):
            VlansBase({7: "some_data_structure"})


class VlanTester:
    @pytest.mark.parametrize(
        "vlan_type", ["default", "custom_enabled", "custom_disabled"]
    )
    def test_meta_attr(self, get_implementation, vlan_type, vlan_imp_obj):
        assert "vlan" == vlan_imp_obj.metadata.name
        assert "entity" == vlan_imp_obj.metadata.type
        assert get_implementation == vlan_imp_obj.metadata.implementation

    @pytest.mark.parametrize("vlan_type", ["default"])
    def test_get_command(self, get_os, vlan_type, vlan_imp_obj):
        assert vlan_imp_obj.get_cmd is None
        # Now verify the command when generated
        get_cmd = vlan_imp_obj.generate_get_cmd(vlan_imp_obj.id)
        assert get_cmd == VLAN_GET_COMMANDS[vlan_type][get_os]

    # TODO: Implement `get` method test - need mock
    # TODO: Implement `enable` method test - need mock
    # TODO: Implement `disable` method test - need mock

    @pytest.mark.parametrize(
        "vlan_type", ["default", "custom_enabled", "custom_disabled"]
    )
    def test_parse(self, get_os, vlan_imp_parser, vlan_type):
        raw_data = VLAN_DATA[get_os][vlan_type]
        # Apply interface parsing of the object based on the raw output
        parsed_data = vlan_imp_parser.parse(raw_data=raw_data[0])

        # Lets do the comparison based on the dict returned without metadata
        parsed_dict = VlanBase(**parsed_data).to_dict()
        parsed_dict.pop("metadata")
        assert parsed_dict == VLAN_DATA_PARSED[get_os][vlan_type]


@pytest.mark.eos
class TestVlanEos(VlanTester):
    net_os = "eos"
    implementation = "pyeapi"


# class VlanTester:
#     # TODO: Pending function to verify VlanBuilder
#     @pytest.mark.init
#     @pytest.mark.parametrize(
#         "vlan_type", ["default", "custom_enabled", "custom_disabled"]
#     )
#     def test_vlan_obj_instatiation(self, vlan_type, vlan_obj, get_implementation):
#         expected_metadata = metadata_processor(vlan_obj.metadata, get_implementation)
#         assert repr(vlan_obj) == VLAN_REPR[vlan_type]
#         assert repr(vlan_obj.metadata) == expected_metadata

#     @pytest.mark.init
#     @pytest.mark.parametrize("vlan_type", ["invalid1"])
#     def test_vlan_obj_instatiation_prohibition(self, vlan_type, get_implementation):
#         with pytest.raises(TypeError):
#             MODULE_MAPPING[get_implementation].Vlan(**VLAN_BASE_ARGS[vlan_type])

#     @pytest.mark.command
#     @pytest.mark.parametrize("vlan_type", ["default"])
#     def test_vlan_obj_command(self, vlan_type, vlan_obj, vlan_command):
#         assert vlan_obj.command(id=7) == vlan_command

#     @pytest.mark.pytest_result
#     @pytest.mark.parametrize(
#         "vlan_type", ["default", "custom_enabled", "custom_disabled"]
#     )
#     def test_vlan_obj_parse_result_asdict(
#         self, vlan_type, vlan_obj, vlan_parser, raw_outputs, expected_result
#     ):
#         for raw_output in raw_outputs:
#             vlan_parser.parse(raw_data=raw_output, vl=vlan_obj)
#             assert asdict(vlan_obj, dict_factory=HidePrivateAttrs) == expected_result

#     @pytest.mark.slow
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("vlan_type", ["ceos1_vlan_7_enabled"])
#     def test_vlan_obj_get(self, dev_connector, vlan_type, vlan_obj):
#         # Verifies that VLAN is custom_enabled is the same as the one in the device
#         vlan_obj.connector = dev_connector
#         # Network run
#         vlan_obj.get()
#         vlan_obj.interfaces = sorted(vlan_obj.interfaces, key=sort_interface)
#         assert repr(vlan_obj) == VLAN_REPR[vlan_type]

#     # IT NEEDS TO RUN IN ORDER, FIRST DISABLED AND NEXT ENABLE
#     @pytest.mark.slow
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("vlan_type", ["ceos1_vlan_7_enabled"])
#     def test_vlan_obj_disable(
#         self, dev_connector, get_implementation, vlan_type, vlan_obj
#     ):
#         vlan_obj.connector = dev_connector
#         # Network run
#         vlan_obj.disable()
#         vlan_obj.get()
#         vlan_obj.interfaces = sorted(vlan_obj.interfaces, key=sort_interface)
#         expected_metadata = metadata_processor(vlan_obj.metadata, get_implementation)
#         assert repr(vlan_obj) == VLAN_REPR["ceos1_vlan_7_disabled"]
#         assert repr(vlan_obj.metadata) == expected_metadata

#     # IT NEEDS TO RUN IN ORDER, FIRST DISABLED AND NEXT ENABLE
#     @pytest.mark.slow
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("vlan_type", ["ceos1_vlan_7_disabled"])
#     def test_vlan_obj_enable(
#         self, dev_connector, get_implementation, vlan_type, vlan_obj
#     ):
#         vlan_obj.connector = dev_connector
#         # Network run
#         vlan_obj.enable()
#         vlan_obj.get()
#         vlan_obj.interfaces = sorted(vlan_obj.interfaces, key=sort_interface)
#         expected_metadata = metadata_processor(vlan_obj.metadata, get_implementation)
#         assert repr(vlan_obj) == VLAN_REPR["ceos1_vlan_7_enabled"]
#         assert repr(vlan_obj.metadata) == expected_metadata
