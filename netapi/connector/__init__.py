from netapi.connector.eos import pyeapier
from netapi.connector.linux import subprocesser, paramikoer


class DeviceBuilder:
    """
    Helper class used to create device objects by passing a device the `net_os` and
    `provider` implementations.
    """

    def create_device(self, net_os, provider, **kwargs):
        # Instantiate builder
        return device_factory.get_connector(
            f"{net_os.upper()}-{provider.upper()}", **kwargs
        )


class ObjectFactory:
    "General Factory Method"

    def __init__(self):
        self._connectors = {}

    def register_connector(self, key, connector):
        self._connectors[key] = connector

    def create(self, key, **kwargs):
        connector = self._connectors.get(key)
        if not connector:
            raise NotImplementedError(key)
        return connector(**kwargs)


class DeviceFactory(ObjectFactory):
    "Registers new implementations for connecting to devices"

    def get_connector(self, connector, **kwargs):
        return self.create(connector, **kwargs)


device_factory = DeviceFactory()
device_factory.register_connector("EOS-PYEAPI", {"entity": pyeapier.Device})
device_factory.register_connector("LINUX-SUBPROCESS", {"entity": subprocesser.Device})
device_factory.register_connector("LINUX-PARAMIKO", {"entity": paramikoer.Device})
