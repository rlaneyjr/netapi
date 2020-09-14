import re
import pytest
import netapi.net as net
from netapi.net.vrrp import VrrpBase, VrrpsBase
from pydantic import ValidationError


MODULE_MAPPING = {"EOS-PYEAPI": net.eos.pyeapier}


VRRP_ARGS = {
    "default": dict(group_id=7, interface="Vlan7"),
    # "not_exist": dict(group_id=247, interface="Loopback777"),
    "master": dict(
        group_id=7,
        interface="Vlan7",
        description="TEST VRRP INSTANCE",
        status_up=True,
        status="master",
        instance="default",
        priority=200,
        master_priority=200,
        master_interval=1.0,
        master_down_interval=3.21,
        mac_advertisement_interval=30.0,
        preempt=True,
        preempt_delay=0.0,
        skew_time=0.21,
        virtual_ip="7.7.7.7",
        virtual_mac="0000.5e00.7777",
        master_ip="7.7.7.1",
        tracked_objects=[
            {
                "trackedObject": "LO77",
                "priority": 0,
                "shutdown": True,
                "interface": "Loopback77",
            }
        ],
        virtual_ip_secondary=["7.7.7.8", "7.7.7.9", "7.7.7.10"],
        version=2,
        extra_attributes=dict(
            bfd_peer_ip="7.7.7.2",
            vr_id_disabled=False,
            vr_id_disabled_reason=None,
            advertisement_interval=1.0,
        ),
    ),
    "backup": dict(
        group_id=7,
        interface="Vlan7",
        description="TEST VRRP INSTANCE",
        status="backup",
        status_up=True,
        instance="default",
        priority=100,
        master_priority=200,
        master_interval=1.0,
        master_down_interval=3.21,
        mac_advertisement_interval=30.0,
        preempt=True,
        preempt_delay=0.0,
        skew_time=0.21,
        virtual_ip="7.7.7.7",
        virtual_mac="0000.5e00.7777",
        master_ip="7.7.7.1",
        tracked_objects=[
            {
                "trackedObject": "LO77",
                "priority": 0,
                "shutdown": True,
                "interface": "Loopback77",
            }
        ],
        virtual_ip_secondary=["7.7.7.8", "7.7.7.9", "7.7.7.10"],
        version=2,
        extra_attributes=dict(
            bfd_peer_ip="7.7.7.1",
            vr_id_disabled=False,
            vr_id_disabled_reason=None,
            advertisement_interval=1.0,
        ),
    ),
    "stopped": dict(
        group_id=70,
        interface=None,
        description=None,
        status="stopped",
        status_up=False,
        instance="TEST-VRF",
        priority=200,
        master_priority=200,
        master_interval=1.0,
        master_down_interval=3.21,
        preempt=False,
        preempt_delay=0.0,
        virtual_ip="7.7.7.7",
        virtual_mac="0000.5e00.0147",
        master_ip="0.0.0.0",
    ),
    "invalid_status": dict(group_id=7, status="dummy"),
    "invalid_virtual_ip": dict(group_id=7, virtual_ip="10.71.1.1.1.1"),
    "invalid_virtual_mac": dict(group_id=7, virtual_mac="0000.5e00.7777.XXXX.YYYY"),
}
VRRP_BASE_REPR = {
    "default": (
        "VrrpBase(group_id=7, interface='Vlan7', description=None, version=None, "
        "status_up=None, status=None, instance=None, virtual_ip=None, "
        "virtual_ip_secondary=None, virtual_mac=None, priority=None, master_ip=None, "
        "master_priority=None, master_interval=None, mac_advertisement_interval=None, "
        "preempt=None, preempt_delay=None, master_down_interval=None, skew_time=None, "
        "tracked_objects=None, extra_attributes={})"
    ),
    "master": (
        "VrrpBase(group_id=7, interface='Vlan7', description='TEST VRRP INSTANCE', "
        "version=2, status_up=True, status='master', instance='default', virtual_ip="
        "IPAddress('7.7.7.7'), virtual_ip_secondary=['7.7.7.8', '7.7.7.9', '7.7.7.10'],"
        " virtual_mac=EUI('00-00-5E-00-77-77'), priority=200, master_ip=IPAddress"
        "('7.7.7.1'), master_priority=200, master_interval=1.0, "
        "mac_advertisement_interval=30.0, preempt=True, preempt_delay=0.0, "
        "master_down_interval=3.21, skew_time=0.21, tracked_objects=["
        "{'trackedObject': 'LO77', 'priority': 0, 'shutdown': "
        "True, 'interface': 'Loopback77'}], extra_attributes="
        "{'bfd_peer_ip': '7.7.7.2', 'vr_id_disabled': False, 'vr_id_disabled_reason': "
        "None, 'advertisement_interval': 1.0})"
    ),
    "backup": (
        "VrrpBase(group_id=7, interface='Vlan7', description='TEST VRRP INSTANCE', "
        "version=2, status_up=True, status='backup', instance='default', virtual_ip="
        "IPAddress('7.7.7.7'), virtual_ip_secondary=['7.7.7.8', '7.7.7.9', '7.7.7.10'],"
        " virtual_mac=EUI('00-00-5E-00-77-77'), priority=100, master_ip=IPAddress"
        "('7.7.7.1'), master_priority=200, master_interval=1.0, "
        "mac_advertisement_interval=30.0, preempt=True, preempt_delay=0.0, "
        "master_down_interval=3.21, skew_time=0.21, tracked_objects=["
        "{'trackedObject': 'LO77', 'priority': 0, 'shutdown': "
        "True, 'interface': 'Loopback77'}], extra_attributes="
        "{'bfd_peer_ip': '7.7.7.1', 'vr_id_disabled': False, 'vr_id_disabled_reason': "
        "None, 'advertisement_interval': 1.0})"
    ),
    "stopped": (
        "VrrpBase(group_id=70, interface=None, description=None, version=None, "
        "status_up=False, status='stopped', instance='TEST-VRF', virtual_ip=IPAddress"
        "('7.7.7.7'), virtual_ip_secondary=None, virtual_mac=EUI('00-00-5E-00-01-47'), "
        "priority=200, master_ip=IPAddress('0.0.0.0'), master_priority=200, "
        "master_interval=1.0, mac_advertisement_interval=None, preempt=False, "
        "preempt_delay=0.0, master_down_interval=3.21, skew_time=None, tracked_objects="
        "None, extra_attributes={})"
    ),
}
VRRP_BASE_METADATA_REPR = (
    "Metadata(name='vrrp', type='entity', implementation=None, "
    "created_at=<CREATED_AT>, id=<UUID>, "
    "updated_at=<UPDATED_AT>, collection_count=<COUNT>, parent=None)"
)
VRRP_BASE_ASDICT = {
    "master": {
        "group_id": 7,
        "interface": "Vlan7",
        "description": "TEST VRRP INSTANCE",
        "version": 2,
        "status_up": True,
        "status": "master",
        "instance": "default",
        "virtual_ip": "7.7.7.7",
        "virtual_ip_secondary": ["7.7.7.8", "7.7.7.9", "7.7.7.10"],
        "virtual_mac": "00-00-5E-00-77-77",
        "priority": 200,
        "master_ip": "7.7.7.1",
        "master_priority": 200,
        "master_interval": 1.0,
        "mac_advertisement_interval": 30.0,
        "preempt": True,
        "preempt_delay": 0.0,
        "master_down_interval": 3.21,
        "skew_time": 0.21,
        "tracked_objects": [
            {
                "trackedObject": "LO77",
                "priority": 0,
                "shutdown": True,
                "interface": "Loopback77",
            }
        ],
        "extra_attributes": {
            "bfd_peer_ip": "7.7.7.2",
            "vr_id_disabled": False,
            "vr_id_disabled_reason": None,
            "advertisement_interval": 1.0,
        },
        "metadata": None,
        "vrrp_api": None,
    },
    "backup": {
        "group_id": 7,
        "interface": "Vlan7",
        "description": "TEST VRRP INSTANCE",
        "version": 2,
        "status_up": True,
        "status": "backup",
        "instance": "default",
        "virtual_ip": "7.7.7.7",
        "virtual_ip_secondary": ["7.7.7.8", "7.7.7.9", "7.7.7.10"],
        "virtual_mac": "00-00-5E-00-77-77",
        "priority": 100,
        "master_ip": "7.7.7.1",
        "master_priority": 200,
        "master_interval": 1.0,
        "mac_advertisement_interval": 30.0,
        "preempt": True,
        "preempt_delay": 0.0,
        "master_down_interval": 3.21,
        "skew_time": 0.21,
        "tracked_objects": [
            {
                "trackedObject": "LO77",
                "priority": 0,
                "shutdown": True,
                "interface": "Loopback77",
            }
        ],
        "extra_attributes": {
            "bfd_peer_ip": "7.7.7.1",
            "vr_id_disabled": False,
            "vr_id_disabled_reason": None,
            "advertisement_interval": 1.0,
        },
        "metadata": None,
        "vrrp_api": None,
    },
    "stopped": {
        "group_id": 70,
        "interface": None,
        "description": None,
        "version": None,
        "status_up": False,
        "status": "stopped",
        "instance": "TEST-VRF",
        "virtual_ip": "7.7.7.7",
        "virtual_ip_secondary": None,
        "virtual_mac": "00-00-5E-00-01-47",
        "priority": 200,
        "master_ip": "0.0.0.0",
        "master_priority": 200,
        "master_interval": 1.0,
        "mac_advertisement_interval": None,
        "preempt": False,
        "preempt_delay": 0.0,
        "master_down_interval": 3.21,
        "skew_time": None,
        "tracked_objects": None,
        "extra_attributes": {},
        "metadata": None,
        "vrrp_api": None,
    },
}
VRRP_GET_COMMANDS = {
    "master": {"eos": ["show vrrp group 7 interface Vlan7 all"]},
    # "custom_backup": {"eos": ["show vrrp group 7 interface Vlan7 all"]},
    "stopped": {"eos": ["show vrrp group 70 vrf TEST-VRF all"]},
}
VRRP_DATA = {
    "eos": {
        "master": [
            {
                "show vrrp group 7 interface Vlan7 all": {
                    "virtualRouters": [
                        {
                            "masterPriority": 200,
                            "vrfName": "default",
                            "description": "TEST VRRP INSTANCE",
                            "macAddressInterval": 30,
                            "trackedObjects": [
                                {
                                    "priority": 0,
                                    "shutdown": True,
                                    "interface": "Loopback77",
                                    "trackedObject": "LO77",
                                }
                            ],
                            "preempt": True,
                            "interface": "Vlan7",
                            "bfdPeerAddr": "7.7.7.2",
                            "groupId": 7,
                            "masterInterval": 1,
                            "virtualMac": "00:00:5e:00:77:77",
                            "vrIdDisabled": False,
                            "preemptDelay": 0,
                            "virtualIpSecondary": ["7.7.7.8", "7.7.7.9", "7.7.7.10"],
                            "masterAddr": "7.7.7.1",
                            "virtualIp": "7.7.7.7",
                            "priority": 200,
                            "skewTime": 0.21,
                            "state": "master",
                            "version": 2,
                            "vrIdDisabledReason": "",
                            "masterDownInterval": 3210,
                            "vrrpAdvertInterval": 1,
                            "preemptReload": 0,
                        }
                    ]
                }
            }
        ],
        "backup": [
            {
                "show vrrp group 7 interface Vlan7 all": {
                    "virtualRouters": [
                        {
                            "masterPriority": 200,
                            "vrfName": "default",
                            "description": "TEST VRRP INSTANCE",
                            "macAddressInterval": 30,
                            "trackedObjects": [
                                {
                                    "priority": 0,
                                    "shutdown": True,
                                    "interface": "Loopback77",
                                    "trackedObject": "LO77",
                                }
                            ],
                            "preempt": True,
                            "interface": "Vlan7",
                            "bfdPeerAddr": "7.7.7.1",
                            "groupId": 7,
                            "masterInterval": 1,
                            "virtualMac": "00:00:5e:00:77:77",
                            "vrIdDisabled": False,
                            "preemptDelay": 0,
                            "virtualIpSecondary": ["7.7.7.8", "7.7.7.9", "7.7.7.10"],
                            "masterAddr": "7.7.7.1",
                            "virtualIp": "7.7.7.7",
                            "priority": 100,
                            "skewTime": 0.21,
                            "state": "backup",
                            "version": 2,
                            "vrIdDisabledReason": "",
                            "masterDownInterval": 3210,
                            "vrrpAdvertInterval": 1,
                            "preemptReload": 0,
                        }
                    ]
                }
            }
        ],
        "stopped": [
            {
                "show vrrp group 70 vrf TEST-VRF all": {
                    "virtualRouters": [
                        {
                            "masterPriority": 200,
                            "vrfName": "TEST-VRF",
                            "description": "",
                            "macAddressInterval": 30,
                            "trackedObjects": [],
                            "preempt": True,
                            "interface": None,  # there is an interface in real world
                            "bfdPeerAddr": "0.0.0.0",
                            "groupId": 70,
                            "masterInterval": 1,
                            "virtualMac": "00:00:5e:00:01:47",
                            "vrIdDisabled": False,
                            "preemptDelay": 0,
                            "virtualIpSecondary": [],
                            "masterAddr": "0.0.0.0",
                            "virtualIp": "7.7.7.7",
                            "priority": 200,
                            "skewTime": 0.21,
                            "state": "stopped",
                            "version": 2,
                            "vrIdDisabledReason": "",
                            "masterDownInterval": 3210,
                            "vrrpAdvertInterval": 1,
                            "preemptReload": 0,
                        }
                    ]
                }
            }
        ],
    }
}
VRRP_DATA_PARSED = {
    "eos": {
        "master": {
            "group_id": 7,
            "interface": "Vlan7",
            "description": "TEST VRRP INSTANCE",
            "version": 2,
            "status_up": True,
            "status": "master",
            "instance": "default",
            "virtual_ip": "7.7.7.7",
            "virtual_ip_secondary": ["7.7.7.8", "7.7.7.9", "7.7.7.10"],
            "virtual_mac": "00-00-5E-00-77-77",
            "priority": 200,
            "master_ip": "7.7.7.1",
            "master_priority": None,
            "master_interval": 1.0,
            "mac_advertisement_interval": 30.0,
            "preempt": True,
            "preempt_delay": 0.0,
            "master_down_interval": 3.21,
            "skew_time": 0.21,
            "tracked_objects": [
                {
                    "trackedObject": "LO77",
                    "priority": 0,
                    "shutdown": True,
                    "interface": "Loopback77",
                }
            ],
            "extra_attributes": {
                "bfd_peer_ip": "7.7.7.2",
                "preempt_reload": 0,
                "vrrp_id_disabled": False,
                "vrrp_id_disabled_reason": "",
                "vrrp_advertisement_interval": 1,
            },
            "metadata": None,
            "vrrp_api": None,
        },
        "backup": {
            "group_id": 7,
            "interface": "Vlan7",
            "description": "TEST VRRP INSTANCE",
            "version": 2,
            "status_up": True,
            "status": "backup",
            "instance": "default",
            "virtual_ip": "7.7.7.7",
            "virtual_ip_secondary": ["7.7.7.8", "7.7.7.9", "7.7.7.10"],
            "virtual_mac": "00-00-5E-00-77-77",
            "priority": 100,
            "master_ip": "7.7.7.1",
            "master_priority": None,
            "master_interval": 1.0,
            "mac_advertisement_interval": 30.0,
            "preempt": True,
            "preempt_delay": 0.0,
            "master_down_interval": 3.21,
            "skew_time": 0.21,
            "tracked_objects": [
                {
                    "trackedObject": "LO77",
                    "priority": 0,
                    "shutdown": True,
                    "interface": "Loopback77",
                }
            ],
            "extra_attributes": {
                "bfd_peer_ip": "7.7.7.1",
                "preempt_reload": 0,
                "vrrp_id_disabled": False,
                "vrrp_id_disabled_reason": "",
                "vrrp_advertisement_interval": 1,
            },
            "metadata": None,
            "vrrp_api": None,
        },
        "stopped": {
            "group_id": 70,
            "interface": None,
            "description": "",
            "version": 2,
            "status_up": False,
            "status": "stopped",
            "instance": "TEST-VRF",
            "virtual_ip": "7.7.7.7",
            "virtual_ip_secondary": [],
            "virtual_mac": "00-00-5E-00-01-47",
            "priority": 200,
            "master_ip": "0.0.0.0",
            "master_priority": None,
            "master_interval": 1.0,
            "mac_advertisement_interval": 30.0,
            "preempt": True,
            "preempt_delay": 0.0,
            "master_down_interval": 3.21,
            "skew_time": 0.21,
            "tracked_objects": [],
            "extra_attributes": {
                "bfd_peer_ip": "0.0.0.0",
                "preempt_reload": 0,
                "vrrp_advertisement_interval": 1,
                "vrrp_id_disabled": False,
                "vrrp_id_disabled_reason": "",
            },
            "metadata": None,
            "vrrp_api": None,
        },
    }
}


@pytest.fixture
def vrrp_params(request):
    return VRRP_ARGS[request.getfixturevalue("vrrp_type")]


# RouteBase fixture
@pytest.fixture
def vrrp_base_obj(request, vrrp_params):
    return VrrpBase(**vrrp_params)


@pytest.fixture
def module(get_implementation):
    return MODULE_MAPPING[get_implementation]


@pytest.fixture
def vrrp_imp_obj(module, vrrp_params):
    return module.Vrrp(**vrrp_params)


@pytest.fixture
def vrrp_imp_parser(module, vrrp_params):
    return module.ParseVrrp


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


class TestVrrpBase:
    @pytest.mark.parametrize("vrrp_type", ["default", "master", "backup", "stopped"])
    def test_instatiation(self, vrrp_type, vrrp_base_obj):
        expected_metadata = metadata_processor(
            vrrp_base_obj.metadata,
            implementation="None",
            representation=VRRP_BASE_METADATA_REPR,
        )
        assert repr(vrrp_base_obj) == VRRP_BASE_REPR[vrrp_type]
        assert repr(vrrp_base_obj.metadata) == expected_metadata

    @pytest.mark.parametrize(
        "vrrp_type,expected",
        [
            ("invalid_status", "Vrrp status not known: dummy"),
            (
                "invalid_virtual_ip",
                "failed to detect a valid IP address from '10.71.1.1.1.1'",
            ),
            (
                "invalid_virtual_mac",
                "failed to detect EUI version: '0000.5e00.7777.XXXX.YYYY'",
            ),
        ],
    )
    def test_invalid(self, vrrp_type, expected):
        with pytest.raises(ValidationError, match=expected):
            VrrpBase(**VRRP_ARGS[vrrp_type])

    @pytest.mark.parametrize("vrrp_type", ["master", "backup", "stopped"])
    def test_asdict(self, vrrp_type, vrrp_base_obj):
        del vrrp_base_obj.metadata
        assert vrrp_base_obj.to_dict() == VRRP_BASE_ASDICT[vrrp_type]


class TestVrrpsBase:
    "Tests the collection object"

    def test_instatiation(self):
        # Creation on one instance
        vr7 = VrrpBase(**VRRP_ARGS["master"])
        vrrp_collection = VrrpsBase({7: vr7})

        # Creating second instance and attaching it
        vr70 = VrrpBase(**VRRP_ARGS["stopped"])
        vrrp_collection.update({70: vr70})

        assert repr(vrrp_collection) == "VrrpsBase(7, 70)"
        # Verifies as well the individual objects
        assert repr(vrrp_collection[7]) == VRRP_BASE_REPR["master"]
        assert repr(vrrp_collection[70]) == VRRP_BASE_REPR["stopped"]
        assert vrrp_collection.metadata.name == "vrrps"
        assert vrrp_collection.metadata.type == "collection"

    def test_invalid_attribute(self):
        with pytest.raises(
            ValueError, match="some_data_structure -> It is not a valid vrrp object"
        ):
            VrrpsBase({7: "some_data_structure"})


class VrrpTester:
    "Performs checks on the vrrp object of each implementation"

    @pytest.mark.parametrize("vrrp_type", ["master", "backup", "stopped"])
    def test_meta_attrs(self, vrrp_imp_obj, vrrp_type, get_implementation):
        assert "vrrp" == vrrp_imp_obj.metadata.name
        assert "entity" == vrrp_imp_obj.metadata.type
        assert get_implementation == vrrp_imp_obj.metadata.implementation

    @pytest.mark.parametrize("vrrp_type", ["master", "stopped"])
    def test_get_command(self, get_os, vrrp_imp_obj, vrrp_type):
        assert vrrp_imp_obj.get_cmd is None
        # Now verify the command when generated
        get_cmd = vrrp_imp_obj.generate_get_cmd(
            vrrp_imp_obj.group_id, vrrp_imp_obj.interface, vrrp_imp_obj.instance
        )
        assert get_cmd == VRRP_GET_COMMANDS[vrrp_type][get_os]

    # TODO: Implement `retrieve` method test - need mock
    # TODO: Implement `enable` method test - need mock
    # TODO: Implement `disable` method test - need mock

    @pytest.mark.parametrize("vrrp_type", ["master", "backup", "stopped"])
    def test_parse(self, get_os, vrrp_imp_parser, vrrp_type):
        raw_data = VRRP_DATA[get_os][vrrp_type]
        # Apply interface parsing of the object based on the raw output
        parsed_data = vrrp_imp_parser.parse(raw_data=raw_data[0])

        # Lets do the comparison based on the dict returned without metadata
        parsed_dict = VrrpBase(**parsed_data).to_dict()
        # parsed_dict.pop("metadata")
        parsed_dict["metadata"] = None
        assert parsed_dict == VRRP_DATA_PARSED[get_os][vrrp_type]


@pytest.mark.eos
class TestVrrpEos(VrrpTester):
    net_os = "eos"
    implementation = "pyeapi"


# class VrrpTester:
#     # TODO: Pending function to verify VrrpBuilder
#     @pytest.mark.init
#     @pytest.mark.parametrize(
#         "vrrp_type", ["default", "custom_master", "custom_backup", "custom_stopped"]
#     )
#     def test_vrrp_obj_instatiation(self, vrrp_type, vrrp_obj, get_implementation):
#         expected_metadata = metadata_processor(vrrp_obj.metadata, get_implementation)
#         assert repr(vrrp_obj) == VRRP_REPR[vrrp_type]
#         assert repr(vrrp_obj.metadata) == expected_metadata

#     @pytest.mark.init
#     @pytest.mark.parametrize("vrrp_type", ["invalid1"])
#     def test_vrrp_obj_instatiation_prohibition(self, vrrp_type, get_implementation):
#         with pytest.raises(TypeError):
#             MODULE_MAPPING[get_implementation].Vrrp(**VRRP_ARGS[vrrp_type])

#     @pytest.mark.command
#     @pytest.mark.parametrize("vrrp_type", ["default", "custom_master"])
#     def test_vrrp_obj_command(self, vrrp_type, vrrp_obj, vrrp_command):
#         assert vrrp_obj.command() == vrrp_command

#     @pytest.mark.pytest_result
#     @pytest.mark.parametrize(
#         "vrrp_type", ["default", "custom_master", "custom_backup", "custom_stopped"]
#     )
#     def test_vrrp_obj_parse_result_asdict(
#         self, vrrp_type, vrrp_obj, vrrp_parser, raw_outputs, expected_result
#     ):
#         for raw_output in raw_outputs:
#             vrrp_parser.parse(raw_data=raw_output, vr=vrrp_obj)
#             assert asdict(vrrp_obj, dict_factory=HidePrivateAttrs) == expected_result

#     @pytest.mark.slow
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("vrrp_type", ["not_exist"])
#     def test_vrrp_obj_get_no_data(self, dev_connector, vrrp_type, vrrp_obj):
#         vrrp_obj.connector = dev_connector
#         with pytest.raises(ValueError, match=r"No data returned from device"):
#             # Network run
#             vrrp_obj.get()

#     @pytest.mark.slow
#     @pytest.mark.skip(reason="The devices need to be further developed (vrnetlab)")
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("vrrp_type", ["custom_master"])
#     def test_vrrp_obj_get(self, dev_connector, vrrp_type, vrrp_obj):
#         vrrp_obj.connector = dev_connector
#         # Network run
#         vrrp_obj.get()
#         # vrrp_obj.interfaces = sorted(vrrp_obj.interfaces, key=sort_interface)
#         assert repr(vrrp_obj) == VRRP_REPR[vrrp_type]

#     @pytest.mark.slow
#     @pytest.mark.skip(reason="The devices need to be further developed (vrnetlab)")
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("vrrp_type", ["custom_master"])
#     def test_vrrp_obj_disable(
#         self, dev_connector, get_implementation, vrrp_type, vrrp_obj
#     ):
#         vrrp_obj.connector = dev_connector
#         # Network run
#         vrrp_obj.disable()
#         vrrp_obj.get()
#         # vrrp_obj.interfaces = sorted(vrrp_obj.interfaces, key=sort_interface)
#         expected_metadata = metadata_processor(vrrp_obj.metadata, get_implementation)
#         assert repr(vrrp_obj) == VRRP_REPR["custom_stopped"]
#         assert repr(vrrp_obj.metadata) == expected_metadata

#     @pytest.mark.slow
#     @pytest.mark.skip(reason="The devices need to be further developed (vrnetlab)")
#     @pytest.mark.network_run
#     @pytest.mark.parametrize("vrrp_type", ["custom_stopped"])
#     def test_vrrp_obj_enable(
#         self, dev_connector, get_implementation, vrrp_type, vrrp_obj
#     ):
#         vrrp_obj.connector = dev_connector
#         # Network run
#         vrrp_obj.enable()
#         vrrp_obj.get()
#         # vrrp_obj.interfaces = sorted(vrrp_obj.interfaces, key=sort_interface)
#         expected_metadata = metadata_processor(vrrp_obj.metadata, get_implementation)
#         assert repr(vrrp_obj) == VRRP_REPR["custom_master"]
#         assert repr(vrrp_obj.metadata) == expected_metadata


# @pytest.mark.eos
# class TestVrrpEos(VrrpTester):
#     net_os = "eos"
#     implementation = "pyeapi"

#     @pytest.mark.slow
#     @pytest.mark.network_run
#     def test_vrrp_obj_invalid_group_id(self, dev_connector, get_implementation):
#         # Biggest group number is 255
#         vrrp_obj = MODULE_MAPPING[get_implementation].Vrrp(
#             group_id=999, interface="Loopback999", connector=dev_connector
#         )
#         with pytest.raises(CommandError):
#             # Network run
#             vrrp_obj.get()
