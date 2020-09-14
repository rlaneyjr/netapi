Network API library that perform the core of the work -> requests execution and data parsing.

It relies on the main vendor libraries to perform its work and its main objective to grant network objects that can be used with your applications.

# Installation

You can directly install it using pip

```
pip install netapi
```

## Development Version

You will need [poetry](https://github.com/sdispater/poetry) for clonning and installing the repo

# How it works

Is a library that abstracts the connection and parsing method of the data collected on the target device. It then presents a developer-friendly object that you can use to interact with.

All the objects are created with some cool features for manipulating their attributes and creating your applications on top of it. An example is the `IPNetwork` object returned of the ipv4 address of an interface. You will see that later.

The library is divided in 3 main types of objects:

- **Device**: These are connector objects used fot the `net` and `probes` objects. Needed for the execution and data collection.
- **Net**: These are network _entities_, which basically means technologies or parts of the network protocols like interface, vlan, vrrp, bgp, etc...
- **Probes**: These are tester objects to run in your `device` objects. For example `ping` or `trace`.

There is also a `Metadata` object that collects information about the implementation, how many times the object has been executed and timestamp. Useful for reports and other tests.

## Network Entities example

Here is an example of how to use the library when using a network entity. In this case `Interface`:

```python
# Use Arista pyeapi client for connection
from netapi.connector.eos.pyeapier import Device
from netapi.net.eos.pyeapier import Interface

from pprint import pprint

# Create a device connection object using its api https interface
router01 = Device(
    host="192.168.0.77",
    username="someuser",
    password="somepassword",
    transport="https"
)
```

Show device connection attributes, notice that secrets are hidden
```python
print(router01)

Device(host='192.168.0.77', username='someuser', port=None, net_os='eos', transport='https')
```

You can see the metadata for this instance and get information like timestamp, type of implementation, id of the instance, among other things:
```python
print(router01.metadata)

Metadata(name='device', type='entity', implementation='EOS-PYEAPI', created_at=DateTime(2019, 5, 14, 16, 47, 35, 319134), id=UUID('51d317ab-584d-4f32-a789-402770c361f2'), updated_at=None, collection_count=0, parent=None)
```

You can run a command/action and retrieve its output. The format would depend mostly of the device, net_os, implementation (like EOS-PYEAPI or raw SSH for example) and the type of command.
```python
>>> pprint(router01.run('show version'))

{'show version': {'architecture': 'i386',
                  'bootupTimestamp': 1557851831.0,
                  'hardwareRevision': '',
                  'internalBuildId': '1a44ce37-92c4-48b6-b922-38b7eed939b6',
                  'internalVersion': '4.21.5F-11604264.4215F',
                  'isIntlVersion': False,
                  'memFree': 1372616,
                  'memTotal': 2015608,
                  'mfgName': '',
                  'modelName': 'vEOS',
                  'serialNumber': '',
                  'systemMacAddress': '0c:59:30:85:d7:1d',
                  'uptime': 1158.4,
                  'version': '4.21.5F'}}
```
This library provides common handlers,  for well known network technologies. Here is an example for the Management 1 interface. Notice that I pass the device connector object:
```python
>>> mgmt1 = Interface(name="Management1", connector=router01)

# You can collect its attributes by running the get() method
>>> mgmt1.get()
```

You can see its attributes. Since it is an interface I will only show some key ones
```python
print(mgmt1)

Interface(name='Management1',
          description='Some description',
          enabled=True,
          instance='MANAGEMENT',
          members=None,
          status_up=True,
          status='connected',
          last_status_change=DateTime(2019, 5, 9, 11, 40, 38, 144796, tzinfo=Timezone('Europe/Dublin')),
          number_status_changes=4,
          last_clear=DateTime(2019, 5, 9, 11, 34, 32, 150340, tzinfo=Timezone('Europe/Dublin')),
          update_interval=5.0,
          forwarding_model='routed',
          physical=InterfacePhysical(mtu=Byte(1500.0),
                                     bandwidth=Bit(1000000000.0),
                                     duplex='duplexFull',
                                     mac=EUI('28-99-3A-F8-5D-E7')),
          optical=InterfaceOptical(tx=-2.5,
                                   rx=-5.4,
                                   status="green",
                                   serial_number="XXXYYYZZZ",
                                   media_type="10GBASE-SR"),
          addresses=InterfaceIP(ipv4=IPNetwork('10.193.0.177/24'),
                                ipv6=None,
                                secondary_ipv4=[],
                                dhcp=None))
```

NOTE: The `counters` attribute is not refelcted by default. You can access it directly with `<interface_obj>.counters`

There are multiple parameters here but and I ommitted othere but you can see that IP addresses are netaddr IPNetwork object and similarly the MAC addresses are EUI objects. Also the counter_refresh interval are datetime objects.

These instances also have metadata
```python
>>> print(mgmt1.metadata)

Metadata(name='interface', type='entity', implementation='EOS-PYEAPI', created_at=DateTime(2019, 5, 14, 16, 43, 44, 819105), id=UUID('73297adf-a0d6-4f8d-b247-0d793e577efb'), updated_at=DateTime(2019, 5, 14, 16, 43, 54, 483277), collection_count=1, parent=None)
```

You can see that in the metadata the updated_at field is populated? This happened because we invoked the get() method to collect the data. Now let's change the interface description and refresh the interface data (this is done outside of the script)

Assuming a change to the description was done, now retrieve again the data
```python
>>> print(mgmt01.description)

DUMMY DESCRIPTION
```

You can see that the description changes but also the metadata has been updated!
```python
>>> print(mgmt01.metadata)

Metadata(name='interface', type='entity', implementation='EOS-PYEAPI', created_at=DateTime(2019, 5, 14, 16, 43, 44, 819105), id=UUID('73297adf-a0d6-4f8d-b247-0d793e577efb'), updated_at=DateTime(2019, 5, 14, 17, 20, 27, 557810), collection_count=2, parent=None)
```
You can see updated_at has been updated :) and the collection_count has increased to 2

## Network Probes example

This is a simple example running a Ping against an specific IP address and applying a custom analysis to the result.

First initiate the device object and specify a target
```python
>>> from netapi.connector.linux.subprocesser import Device
>>> from netapi.probe.linux.subprocesser import Ping

>>> host = Device()
>>> ping = Ping(target="1.1.1.1", connector=host)
```

You can see the `Ping` object with the following attributes:
```python
>>> print(ping)

Ping(target='1.1.1.1',target_ip=None, target_name=None, resolve_target=False, source=None, source_ip=None, instance=None, count=5, timeout=2, size=692, df_bit=False, interval=1.0, ttl=None, result=None)
```
You can see that `result` attribute is empty, we need to tell to execute the `Ping` and we can apply our own logic to it.

The ping object is to be executed on my machine, you can see the command used on `ping_cmd`:
```python
>>> ping.generate_ping_cmd()
>>> print(ping.ping_cmd)

'ping 1.1.1.1 -s 692 -c 5 -W 2 -i 1.0'
```

If we execute it as es we can get a result like
```python
>>> ping.execute()
True

>>> print(ping)
Ping(target='1.1.1.1',
     target_ip=None,
     target_name=None,
     resolve_target=False,
     source=None,
     source_ip=None,
     instance=None,
     count=5,
     timeout=2,
     size=692,
     df_bit=False,
     interval=1.0,
     ttl=None,
     result=PingResult(
         probes_sent=5,
         probes_received=5,
         packet_loss=0.0,
         rtt_min=25.303,
         rtt_avg=30.289,
         rtt_max=43.923,
         warning_thld=None,
         critical_thld=None,
         status='ok',
         status_up=True,
         status_code=0,
         apply_analysis=True
    )
)
```

We can use our own threshold in execution to manipulate the `flag` and `status_up` parameters.

```python
>>> ping.execute(critical_thld=-1)
True

>>> ping.result

PingResult(probes_sent=5,
           probes_received=5,
           packet_loss=0.0,
           rtt_min=19.241,
           rtt_avg=23.471,
           rtt_max=26.184,
           warning_thld=None,
           critical_thld=-1,
           status='critical',
           status_up=False,
           status_code=2,
           apply_analysis=True)

# If you want to have a dict
>>> ping.to_dict()

{'count': 5,
 'df_bit': False,
 'instance': None,
 'interval': 1.0,
 'metadata': {'collection_count': 4,
              'created_at': '2019-07-05T18:19:30.075757+01:00',
              'id': '03d55fdf-2e0d-4a66-9f18-ef33a811bc2e',
              'implementation': 'LINUX-SUBPROCESS',
              'name': 'ping',
              'parent': None,
              'type': 'entity',
              'updated_at': '2019-07-05T18:32:32.840095+01:00'},
 'resolve_target': False,
 'result': {'apply_analysis': True,
            'critical_thld': -1,
            'packet_loss': 0.0,
            'probes_received': 5,
            'probes_sent': 5,
            'rtt_avg': 23.732,
            'rtt_max': 27.673,
            'rtt_min': 19.733,
            'status': 'critical',
            'status_code': 2,
            'status_up': False,
            'warning_thld': None},
 'size': 692,
 'source': None,
 'source_ip': None,
 'target': '1.1.1.1',
 'target_ip': None,
 'target_name': None,
 'timeout': 2,
 'ttl': None}
```
You can see that is `status_up = False` even though all the probes were received successfully. Usefull for custom testing.

# Supported Implementations

The following reflects the supported network operating systems with their respective libraries/method of connecting, collecting and parsing data out of the device.

## Connectors

| Connector Type | EOS      | IOS | IOS-XE  | IOS-XR  | NXOS  | JUNOS | LINUX                     |
| -------------- | -------- | --- | ------- | ------- | ----- | ----- | ------------------------- |
| Device         | `pyeapi` | ❌  | ❌      | ❌      | ❌   | ❌    | `subprocess`, `paramiko`  |

## Network Entities

| Network Entity | EOS      | IOS | IOS-XE  | IOS-XR  | NXOS  | JUNOS  |
| -------------- | -------- | --- | ------- | ------- | ----- | ------ |
| Facts          | `pyeapi` | ❌  | ❌      | ❌      | ❌    | ❌    |
| Interface      | `pyeapi` | ❌  | ❌      | ❌      | ❌    | ❌    |
| Vlan           | `pyeapi` | ❌  | ❌      | ❌      | ❌    | ❌    |
| Route          | `pyeapi` | ❌  | ❌      | ❌      | ❌    | ❌    |
| Vrrp           | `pyeapi` | ❌  | ❌      | ❌      | ❌    | ❌    |

## Network Probes

| Network Entity | EOS      | IOS | IOS-XE  | IOS-XR   | NXOS  | JUNOS | LINUX                     |
| -------------- | -------- | --- | ------- | -------- | ----- | ----- | ------------------------- |
| Ping           | `pyeapi` | ❌  | ❌      | ❌      | ❌    | ❌    | `subprocess`, `paramiko`  |
