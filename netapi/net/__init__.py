"""
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
"""
from netapi.net.eos import pyeapier
from .interface import InterfaceBase, InterfaceIP

__all__ = ["InterfaceBase", "InterfaceIP"]


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

    def parse(self, key, **kwargs):
        parser = self._parsers.get(key)
        if not parser:
            raise NotImplementedError(key)
        return parser


class ObjectBuilder:
    """
    Helper class used to create network objects by passing a device `connector` and the
    remaining parameters.

    It is a general builder method that calls the respective command and parser
    factories to get the registered implementations
    """

    def get_objects(self, factory, connector, parameters, **objs_params):
        # Get Object class and instantiate it
        obj_key = f"{connector.metadata.implementation}"
        obj_collector = factory.get_builder(obj_key, sub_key="collection")
        obj_entity = factory.get_builder(obj_key, sub_key="entity")

        # Execute obj command
        raw_data = connector.run(
            obj_collector.generate_get_cmd(**objs_params), **parameters
        )

        # Parse data and update object
        obj_parser = factory.get_parser(obj_key)

        parsed_data = obj_parser.collector_parse(raw_data, **objs_params)

        # Build the entities
        collected_data = []
        for data in parsed_data:
            for key, value in data.items():
                collected_data.append({key: obj_entity(**value)})

        # Create collection object and attach connector
        obj = obj_collector(*collected_data)
        obj.connector = connector
        obj.__dict__.update(objs_params)

        return obj

    def get_object(self, factory, connector, parameters, **obj_params):
        # Get Object class to instantiate it
        obj_key = f"{connector.metadata.implementation}"

        # Pass obj_params because the object might have some required arguments
        obj = factory.get_builder(obj_key, sub_key="entity")

        # Execute obj command
        raw_data = connector.run(obj.generate_get_cmd(**obj_params), **parameters)

        # Parse data and update object
        obj_parser = factory.get_parser(obj_key)
        parsed_data = obj_parser.parse(raw_data, **obj_params)
        parsed_data.update(connector=connector)
        return obj(**parsed_data)


class InterfaceBuilder(ObjectBuilder):
    """
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
    """

    def get(self, connector, entity=True, parameters={}, **interface_params):
        if "silent" not in parameters:
            parameters["silent"] = True
        if not entity:
            return self.get_objects(
                interface_factory, connector, parameters, **interface_params
            )
        else:
            return self.get_object(
                interface_factory, connector, parameters, **interface_params
            )


class InterfaceFactory(ObjectFactory):
    "Registers new implementation for commands to generate interface data"

    def get_builder(self, builder, **kwargs):
        return self.create(builder, **kwargs)

    def get_parser(self, builder, **kwargs):
        return self.parse(builder, **kwargs)


class VlanBuilder(ObjectBuilder):
    """
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
    """

    def get(self, connector, entity=True, parameters={}, **vlan_params):
        if not entity:
            return self.get_objects(vlan_factory, connector, parameters, **vlan_params)
        else:
            return self.get_object(vlan_factory, connector, parameters, **vlan_params)


class VlanFactory(ObjectFactory):
    "Registers new implementation for commands to generate vlan data"

    def get_builder(self, builder, **kwargs):
        return self.create(builder, **kwargs)

    def get_parser(self, builder, **kwargs):
        return self.parse(builder, **kwargs)


class VrrpBuilder(ObjectBuilder):
    """
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
    """

    def get(self, connector, entity=True, parameters={}, **vrrp_params):
        if not entity:
            return self.get_objects(vrrp_factory, connector, parameters, **vrrp_params)
        else:
            return self.get_object(vrrp_factory, connector, parameters, **vrrp_params)


class VrrpFactory(ObjectFactory):
    "Registers new implementation for commands to generate vrrp data"

    def get_builder(self, builder, **kwargs):
        return self.create(builder, **kwargs)

    def get_parser(self, builder, **kwargs):
        return self.parse(builder, **kwargs)


class FactsBuilder(ObjectBuilder):
    """
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
    """

    def get(self, connector, parameters={}, **facts_params):
        return self.get_object(facts_factory, connector, parameters, **facts_params)


class FactsFactory(ObjectFactory):
    "Registers new implementation for commands to generate vrrp data"

    def get_builder(self, builder, **kwargs):
        return self.create(builder, **kwargs)

    def get_parser(self, builder, **kwargs):
        return self.parse(builder, **kwargs)


class RouteBuilder(ObjectBuilder):
    """
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
    """

    def get(self, connector, entity=True, parameters={}, **route_params):
        if not entity:
            return self.get_objects(
                route_factory, connector, parameters, **route_params
            )
        else:
            return self.get_object(route_factory, connector, parameters, **route_params)


class RouteFactory(ObjectFactory):
    "Registers new implementation for commands to generate data"

    def get_builder(self, builder, **kwargs):
        return self.create(builder, **kwargs)

    def get_parser(self, builder, **kwargs):
        return self.parse(builder, **kwargs)


interface_factory = InterfaceFactory()
interface_factory.register_builder(
    "EOS-PYEAPI", {"entity": pyeapier.Interface, "collection": pyeapier.Interfaces}
)
interface_factory.register_parser("EOS-PYEAPI", pyeapier.ParseInterface)


vlan_factory = VlanFactory()
vlan_factory.register_builder(
    "EOS-PYEAPI", {"entity": pyeapier.Vlan, "collection": pyeapier.Vlans}
)
vlan_factory.register_parser("EOS-PYEAPI", pyeapier.ParseVlan)


vrrp_factory = VrrpFactory()
vrrp_factory.register_builder(
    "EOS-PYEAPI", {"entity": pyeapier.Vrrp, "collection": pyeapier.Vrrps}
)
vrrp_factory.register_parser("EOS-PYEAPI", pyeapier.ParseVrrp)


facts_factory = FactsFactory()
facts_factory.register_builder("EOS-PYEAPI", {"entity": pyeapier.Facts})
facts_factory.register_parser("EOS-PYEAPI", pyeapier.ParseFacts)


route_factory = FactsFactory()
route_factory.register_builder(
    "EOS-PYEAPI", {"entity": pyeapier.Route, "collection": pyeapier.Routes}
)
route_factory.register_parser("EOS-PYEAPI", pyeapier.ParseRoute)
