import re
import pytest
import netapi.net as net
from netapi.net.facts import FactsBase
from pendulum import Duration, DateTime
from pendulum.datetime import Timezone
from bitmath import Byte
from netaddr import EUI
from pydantic import ValidationError


MODULE_MAPPING = {"EOS-PYEAPI": net.eos.pyeapier}


FACTS_BASE_ARGS = {
    "default": dict(),
    "precalculated_values": dict(
        hostname="lab-device",
        os_version="4.21.5F",
        model="vEOS",
        serial_number="SOMESERIAL",
        uptime=Duration(hours=19, minutes=5, seconds=21, microseconds=630000),
        up_since=DateTime(2019, 6, 1, 10, 35, 55, 682022, tzinfo=Timezone("UTC")),
        system_mac=EUI("0C-62-02-A6-87-A3"),
        available_memory=Byte(1031120000.0),
        total_memory=Byte(1265832000.0),
        os_arch="i386",
        interfaces=["Ethernet1", "Ethernet2"],
    ),
    "raw_data_values": dict(
        hostname="lab-device2",
        os_version="4.21.5F",
        model="vEOS",
        serial_number="SOMESERIAL",
        uptime=123,
        up_since=(2019, 7, 3),
        system_mac="0c62:02a6:87a3",
        available_memory=123456,
        total_memory=24343434,
        interfaces=["Ethernet1", "Ethernet2"],
    ),
    "invalid_uptime": dict(uptime="dummy"),  # Invalid duration format
    "invalid_up_since": dict(up_since="2017-06-01-01-2 12:22"),  # Invalid datetime fmt
    "invalid_system_mac": dict(system_mac="0C-62-02-A6-87-A3-XYZ"),  # Extra 3 (XYZ)
    "invalid_available_memory": dict(available_memory="123456"),  #  Cannot be str
}
FACTS_BASE_REPR = {
    "default": (
        "FactsBase(hostname=None, os_version=None, model=None, serial_number=None, "
        "uptime=None, up_since=None, system_mac=None, available_memory=None, "
        "total_memory=None, os_arch=None, hw_revision=None, "
        "interfaces=None)"
    ),
    "raw_data_values": (
        "FactsBase(hostname='lab-device2', os_version='4.21.5F', model='vEOS', "
        "serial_number='SOMESERIAL', uptime=Duration(weeks=17, days=4), "
        "up_since=DateTime(2019, 7, 3, 0, 0, 0), system_mac=EUI('0C-62-02-A6-87-A3'), "
        "available_memory=Byte(123456.0), total_memory=Byte(24343434.0), "
        "os_arch=None, hw_revision=None, "
        "interfaces=['Ethernet1', 'Ethernet2'])"
    ),
    "precalculated_values": (
        "FactsBase(hostname='lab-device', os_version='4.21.5F', model='vEOS',"
        " serial_number='SOMESERIAL', uptime=Duration(hours=19, minutes=5, "
        "seconds=21, microseconds=630000), up_since=DateTime(2019, 6, 1, 10, 35, "
        "55, 682022, tzinfo=Timezone('UTC')), system_mac="
        "EUI('0C-62-02-A6-87-A3'), available_memory=Byte(1031120000.0), "
        "total_memory=Byte(1265832000.0), os_arch='i386', "
        "hw_revision=None, interfaces=['Ethernet1', 'Ethernet2'])"
    ),
}
FACTS_BASE_METADATA_REPR = (
    "Metadata(name='facts', type='entity', implementation=None, "
    "created_at=<CREATED_AT>, id=<UUID>, "
    "updated_at=<UPDATED_AT>, collection_count=<COUNT>, parent=None)"
)
FACTS_BASE_ASDICT = {
    "default": {
        "hostname": None,
        "os_version": None,
        "model": None,
        "serial_number": None,
        "uptime": None,
        "up_since": None,
        "system_mac": None,
        "available_memory": None,
        "total_memory": None,
        "os_arch": None,
        "hw_revision": None,
        "interfaces": None,
        "metadata": None,
    },
    "precalculated_values": {
        "hostname": "lab-device",
        "os_version": "4.21.5F",
        "model": "vEOS",
        "serial_number": "SOMESERIAL",
        "uptime": "19 hours 5 minutes 21 seconds",
        "up_since": "2019-06-01T10:35:55.682022+00:00",
        "system_mac": "0C-62-02-A6-87-A3",
        "available_memory": 1031120000.0,
        "total_memory": 1265832000.0,
        "os_arch": "i386",
        "hw_revision": None,
        "interfaces": ["Ethernet1", "Ethernet2"],
        "metadata": None,
    },
    "raw_data_values": {
        "hostname": "lab-device2",
        "os_version": "4.21.5F",
        "model": "vEOS",
        "serial_number": "SOMESERIAL",
        "uptime": "17 weeks 4 days",
        "up_since": "2019-07-03T00:00:00",
        "system_mac": "0C-62-02-A6-87-A3",
        "available_memory": 123456,
        "total_memory": 24343434,
        "os_arch": None,
        "hw_revision": None,
        "interfaces": ["Ethernet1", "Ethernet2"],
        "metadata": None,
    },
}
FACTS_GET_COMMANDS = {
    "default": {"eos": ["show hostname", "show version", "show interfaces"]}
}
FACTS_DATA = {
    "eos": {
        "precalculated_values": [
            {
                "show hostname": {
                    "fqdn": "lab-device.example.com",
                    "hostname": "lab-device",
                },
                "show version": {
                    "memTotal": 1265832,
                    "uptime": 68721.630000,
                    "modelName": "vEOS",
                    "internalVersion": "4.21.5F-11604264.4215F",
                    "mfgName": "",
                    "serialNumber": "SOMESERIAL",
                    "systemMacAddress": "0c:62:02:a6:87:a3",
                    "bootupTimestamp": 1559385355.682022,
                    "memFree": 1031120,
                    "version": "4.21.5F",
                    "architecture": "i386",
                    "isIntlVersion": False,
                    "internalBuildId": "1a44ce37-92c4-48b6-b922-38b7eed939b6",
                    "hardwareRevision": "",
                },
                "show interfaces": {
                    # NOTE: Some interfaces attrs were deleted since they are not used
                    "interfaces": {
                        "Ethernet1": {
                            "lastStatusChangeTimestamp": 1559388891.5290008,
                            "lanes": 0,
                            "name": "Ethernet8",
                            "interfaceStatus": "disabled",
                            "autoNegotiate": "off",
                            "burnedInAddress": "0c:62:02:d6:54:08",
                            "loopbackMode": "loopbackNone",
                            "mtu": 9214,
                            "hardware": "ethernet",
                            "duplex": "duplexFull",
                            "bandwidth": 0,
                            "forwardingModel": "bridged",
                            "lineProtocolStatus": "down",
                            "interfaceAddress": [],
                            "physicalAddress": "0c:62:02:d6:54:08",
                            "description": "",
                        },
                        "Ethernet2": {
                            "lastStatusChangeTimestamp": 1559388890.928964,
                            "lanes": 0,
                            "name": "Ethernet2",
                            "interfaceStatus": "connected",
                            "autoNegotiate": "unknown",
                            "burnedInAddress": "0c:62:02:d6:54:02",
                            "loopbackMode": "loopbackNone",
                            "mtu": 9214,
                            "hardware": "ethernet",
                            "duplex": "duplexFull",
                            "bandwidth": 0,
                            "forwardingModel": "bridged",
                            "lineProtocolStatus": "up",
                            "interfaceAddress": [],
                            "physicalAddress": "0c:62:02:d6:54:02",
                            "description": "dc1fwi1a - G3/3",
                        },
                    }
                },
            }
        ]
    }
}
FACTS_DATA_PARSED = {
    "eos": {
        "precalculated_values": {
            "hostname": "lab-device",
            "os_version": "4.21.5F",
            "model": "vEOS",
            "serial_number": "SOMESERIAL",
            "uptime": "19 hours 5 minutes 21 seconds",
            "up_since": "2019-06-01T10:35:55.682022+00:00",
            "system_mac": "0C-62-02-A6-87-A3",
            "available_memory": 1031120000.0,
            "total_memory": 1265832000.0,
            "os_arch": "i386",
            "hw_revision": None,
            "interfaces": ["Ethernet1", "Ethernet2"],
        }
    }
}


@pytest.fixture
def module(get_implementation):
    return MODULE_MAPPING[get_implementation]


@pytest.fixture
def facts_parameters(request):
    return FACTS_BASE_ARGS[request.getfixturevalue("facts_type")]


@pytest.fixture
def facts_base_obj(facts_parameters):
    return FactsBase(**facts_parameters)


@pytest.fixture
def facts_imp_obj(module, facts_parameters):
    return module.Facts(**facts_parameters)


@pytest.fixture
def facts_imp_parser(module):
    return module.ParseFacts


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


class TestFactsBase:
    # TODO: Pending function to verify FactsBuilder
    @pytest.mark.parametrize(
        "facts_type", ["default", "precalculated_values", "raw_data_values"]
    )
    def test_instatiation(self, facts_type, facts_base_obj):
        expected_metadata = metadata_processor(
            facts_base_obj.metadata,
            implementation="None",
            representation=FACTS_BASE_METADATA_REPR,
        )
        assert repr(facts_base_obj) == FACTS_BASE_REPR[facts_type]
        assert repr(facts_base_obj.metadata) == expected_metadata

    @pytest.mark.parametrize(
        "facts_type,expected",
        [
            ("invalid_uptime", "invalid duration format"),
            ("invalid_up_since", "invalid datetime format"),
            (
                "invalid_system_mac",
                "failed to detect EUI version: '0C-62-02-A6-87-A3-XYZ'",
            ),
            (
                "invalid_available_memory",
                "Initialization value '123456' is of an invalid type: <class 'str'>",
            ),
        ],
    )
    def test_invalid(self, facts_type, expected):
        with pytest.raises(ValidationError, match=expected):
            FactsBase(**FACTS_BASE_ARGS[facts_type])

    @pytest.mark.parametrize(
        "facts_type", ["default", "precalculated_values", "raw_data_values"]
    )
    def test_asdict(self, facts_type, facts_base_obj):
        del facts_base_obj.metadata
        assert facts_base_obj.to_dict() == FACTS_BASE_ASDICT[facts_type]


class FactsTester:
    "Performs checks on the facts object of each implementation"

    @pytest.mark.parametrize(
        "facts_type", ["default", "precalculated_values", "raw_data_values"]
    )
    def test_meta_attrs(self, facts_imp_obj, facts_type, get_implementation):
        assert "facts" == facts_imp_obj.metadata.name
        assert "entity" == facts_imp_obj.metadata.type
        assert get_implementation == facts_imp_obj.metadata.implementation

    @pytest.mark.parametrize("facts_type", ["default"])
    def test_get_command(self, get_os, facts_imp_obj, facts_type):
        assert facts_imp_obj.get_cmd is None
        # Now verify the command when generated
        get_cmd = facts_imp_obj.generate_get_cmd()
        assert get_cmd == FACTS_GET_COMMANDS[facts_type][get_os]

    @pytest.mark.parametrize("facts_type", ["precalculated_values"])
    def test_parse(self, get_os, facts_imp_obj, facts_imp_parser, facts_type):
        raw_data = FACTS_DATA[get_os][facts_type]
        # Apply route parsing of the object based on the raw output
        facts_imp_parser.parse(raw_data=raw_data[0], facts=facts_imp_obj)

        # Lets do the comparison based on the dict returned without metadata
        parsed_dict = facts_imp_obj.to_dict()
        parsed_dict.pop("metadata")
        assert parsed_dict == FACTS_DATA_PARSED[get_os][facts_type]


@pytest.mark.eos
class TestFactsEos(FactsTester):
    net_os = "eos"
    implementation = "pyeapi"
