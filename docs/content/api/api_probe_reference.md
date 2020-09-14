# `__init__`


## `PingBuilder` Objects

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

### `PingBuilder.get()`

```python
def get(self, connector, entity=True, parameters={}, ping_params)
```


# `ping`

PingBase main dataclass object where each implementation derive its attributes.

It is composed of `PingBase` and `PingResult` objects.

## `default_ping_analysis()`

```python
def default_ping_analysis(packet_loss)
```


## `PingResult` Objects

Ping results instance created from a Ping execution.

**Attributes:**

- `probes_sent`: (int) Number of probes sent
- `probes_received`: (int) Number of probes received
- `packet_loss`: (float) percentage of packet loss on the ping execution. /100
- `rtt_min`: (float) Minimum RTT encountered
- `rtt_avg`: (float) Average RTT encountered
- `rtt_max`: (float) Maximum RTT encountered
- `warning_thld` (int) Percentage when the ping execution packet loss is considered
warning. i.e. 80 (meaning 80%)
- `critical_thld` (int) Percentage when the ping execution packet loss is considered
critical. i.e. 80 (meaning 80%)
- `status`: (str) ok/warning/critical/no-route reflecting the status of the result
- `status_code`: (int) same as `status` but in numbers for visualization (0/1/2/3).
Result of analysis applied
- `status_up`: (bool) Flag if the ping was successful in overall. Result of analysis
applied

### `PingResult.applies_result_analysis()`

```python
@validator("apply_analysis")
def applies_result_analysis(cls, v, values)
```


## `PingBase` Objects

Ping instance creator. It creates a ping object based on parameters passed to it for
construction.

**Attributes:**

- `target` (str): IP or Host target
- `target_ip` (IPAddress): IP address of target (Optional)
- `target_name` (str): Hostname of target (Optional)
- `resolve_target` (bool): Resolve IP address and name assigned to attributes
for the likes of `target_ip` and `target_name`
- `source` (str): Interface/Name source of the request
- `source_ip` (IPAddress): IP Address of the source of the request
- `instance` (str): instance/vrf for the ping object
- `count` (int): Number of probes
- `timeout` (int): Timeout for when a probe is marked as unreachable
- `size` (int): Packet size of the ping probes
- `df_bit` (bool): Do not fragment bit to be set
- `interval` (float): Time interval between each probe
- `ttl` (int): Time-to-live value for the probes
- `result`: (PingResult) result object of the execution
- `connector`: Device object used to perform the necessary connection.
- `metadata`: Metadata object which contains information about the current object.
- `ping_cmd`: Ping command to be used for execution

### `PingBase.to_dict()`

```python
def to_dict(self)
```


