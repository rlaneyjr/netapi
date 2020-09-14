"""
Global conftest that gathers the Pytests addoptions to the arguments
and reusable fictures among modules
"""
import pytest
import yaml
import netapi.connector as connector
from pathlib import Path


def pytest_addoption(parser):
    parser.addoption(
        "--network-setup",
        help="Network setup configuration YAML file. It should contain the data "
        "needed to connect to the device",
    )
    parser.addoption(
        "--network-run",
        action="store_true",
        default=False,
        help="Flag to specify if tests on network devices should run",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--network-setup") and config.getoption("--network-run"):
        return
    skip_network_run = pytest.mark.skip(
        reason="Needs to have network-setup and network-run flag to run"
    )
    for item in items:
        if "network_run" in item.keywords:
            item.add_marker(skip_network_run)


@pytest.fixture
def get_os(request):
    return request.cls.net_os


@pytest.fixture
def get_implementation(request, get_os):
    impl = request.cls.implementation
    return f"{get_os.upper()}-{impl.upper()}"


@pytest.fixture
def dev_connector(request, get_implementation):
    device_mapping, test_mapping = request.getfixturevalue(
        f"{get_implementation.lower().replace('-', '_')}_connector"
    )
    # Return the object if test is mapped
    if not test_mapping:
        pytest.skip("No test being mapped. Skipping...")
    connector_name = test_mapping.get(request.function.__name__)
    if not connector_name:
        pytest.skip(f"The test {request.node.name} is not mapped")
    return device_mapping[connector_name]


@pytest.fixture(scope="session")
def network_config(pytestconfig, request):
    config_path = pytestconfig.getoption("network_setup")
    if not config_path:
        return
    config = Path(config_path)
    if config.is_file():
        with open(str(config.resolve()), "r") as f:
            data = yaml.safe_load(f)
        return data
    else:
        pytest.skip("Network setup file path is not valid. (See network-setup)")


@pytest.fixture(scope="session")
def eos_pyeapi_connector(request, network_config):
    data = network_config.get("eos")
    if not data:
        pytest.skip("No network data found for eos. (See network-setup)")
    # Create network objects
    device_mapping = {}
    for device, parameters in data["devices"].items():
        eos_router = connector.eos.pyeapier.Device(
            host=parameters["host"],
            username=parameters["user"],
            password=parameters["password"],
            transport=parameters["transport"],
        )
        #  Test if there is basic connection
        try:
            eos_router.connector.enable("show version")
        except Exception as err:
            pytest.skip(f"Not able to connect to device -> {str(err)}")
        device_mapping.update({device: eos_router})
    # Return the object if test is mapped
    test_mapping = data.get("test_mapping")
    return device_mapping, test_mapping


@pytest.fixture(scope="session")
def ios_netmiko_connector(pytestconfig, network_config):
    pytest.skip("Method to connect to IOS device not implemented")


@pytest.fixture(scope="session")
def xe_netmiko_connector(pytestconfig, network_config):
    pytest.skip("Method to connect to XE device not implemented")


@pytest.fixture(scope="session")
def xr_netmiko_connector(pytestconfig, network_config):
    pytest.skip("Method to connect to XR device not implemented")


@pytest.fixture(scope="session")
def nxos_nxapi_connector(pytestconfig, network_config):
    pytest.skip("Method to connect to NXOS device not implemented")


@pytest.fixture(scope="session")
def junos_pyez_connector(pytestconfig, network_config):
    pytest.skip("Method to connect to JUNOS device not implemented")


@pytest.fixture(scope="session")
def linux_subprocess_connector(pytestconfig, network_config):
    data = network_config.get("linux-local")
    if not data:
        pytest.skip("No network data found for linux-local. (See network-setup)")
    linux_host = connector.linux.subprocesser.Device()
    #  Test if there is basic connection
    try:
        linux_host.run("ls -l")
    except Exception as err:
        pytest.skip(f"Not able to connect to device -> {str(err)}")
    return linux_host


@pytest.fixture(scope="session")
def linux_paramiko_connector(pytestconfig, network_config):
    pytest.skip("Method to connect to LINUX PARAMIKO device not implemented")
