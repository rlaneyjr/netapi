from netapi.probe.eos import pyeapier
from netapi.probe.ios import netmikoer as ios_netmikoer
from netapi.probe.junos import pyezer
from netapi.probe.linux import subprocesser, paramikoer
from netapi.probe.nxos import nxapier
from netapi.probe.xe import netmikoer as xe_netmikoer
from netapi.probe.xr import netmikoer as xr_netmikoer


class ObjectFactory:
    "General Factory Method"

    def __init__(self):
        self._builders = {}
        self._parsers = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def register_parser(self, key, parser):
        self._parsers[key] = parser

    def create(self, key, sub_key, **kwargs):
        builder_dict = self._builders.get(key)
        if not builder_dict:
            raise NotImplementedError(key)
        builder = builder_dict.get(sub_key)
        if not builder:
            raise NotImplementedError(f"{sub_key} not implemented for {key}")
        return builder


class ObjectBuilder:
    """
    Helper class used to create network objects by passing a device `connector` and the
    remaining parameters.

    It is a general builder method that calls the respective command and parser
    factories to get the registered implementations
    """

    def get_object(self, factory, connector, parameters, **obj_params):
        # Get Object class to instantiate it
        obj_key = f"{connector.metadata.implementation}"

        # Pass obj_params because the object might have some required arguments
        obj_entity = factory.get_builder(obj_key, sub_key="entity")

        # Create object
        obj = obj_entity(connector=connector, **obj_params)

        # Execute obj command
        obj.execute(**parameters)
        return obj


class PingBuilder(ObjectBuilder):
    """
    Builder used to create Ping object.

    **Ping object instatiation:**

    - `connector`: `Device` instance object
    - `target`: string (required)

    **Examples:**

    ```python
    from netapi.probe import PingBuilder
    from netapi.connector.linux.subprocesser import Device

    connector = Device()
    ping = PingBuilder()

    p1 = ping.get(connector, target="1.1.1.1")
    print(p1)
    # Ping(target='1.1.1.1', target_ip=None, ...)
    ```
    """

    def get(self, connector, entity=True, parameters={}, **ping_params):
        return self.get_object(ping_factory, connector, parameters, **ping_params)


class PingFactory(ObjectFactory):
    "Registers new implementation for commands to generate ping data"

    def get_builder(self, builder, **kwargs):
        return self.create(builder, **kwargs)


ping_factory = PingFactory()

ping_factory.register_builder("EOS-PYEAPI", {"entity": pyeapier.Ping})

ping_factory.register_builder("IOS-NETMIKO", ios_netmikoer.Ping)

ping_factory.register_builder("LINUX-SUBPROCESS", {"entity": subprocesser.Ping})
ping_factory.register_builder("LINUX-PARAMIKO", {"entity": paramikoer.Ping})

ping_factory.register_builder("XR-NETMIKO", xr_netmikoer.Ping)

ping_factory.register_builder("XE-NETMIKO", xe_netmikoer.Ping)

ping_factory.register_builder("NXOS-NXAPI", nxapier.Ping)

ping_factory.register_builder("JUNOS-PYEZ", pyezer.Ping)
