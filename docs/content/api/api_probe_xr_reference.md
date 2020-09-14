# `xr`


# `xr.netmikoer`


## `PATTERNS`

```python
PATTERNS = {
    "ping": re.compile(
        r"Success rate is (?P<rate>\d+) percent \((?P<tx>\d+)/(?P<rx>\d+)\ ...
```


## `TIMEOUT_PATTERNS`

```python
TIMEOUT_PATTERNS = {
    "ping": re.compile(
        r"Success rate is (?P<rate>\d+) percent \((?P<tx>\d+)/(?P<rx>\d+)\ ...
```


## `Ping` Objects

Minimalistic ping

### `Ping.__post_init__()`

```python
def __post_init__(self, _ignore)
```


### `Ping.generate_ping_cmd()`

```python
def generate_ping_cmd(self, _ignore)
```


### `Ping.execute()`

```python
def execute(self, warning_thld=None, critical_thld=None, _ignore)
```

Automatic execution of entity to retrieve results. Also applies warning/critical
thresholds for the analysis if given.

- `warning_thld`: Packet loss above this value is flagged as `warning`
- `critical_thld`: Packet loss above this value is flagged as `critical`

NOTE: If `warning_thld` was set and paket loss is below the percentage value,
it is then flagged as `ok`

By default it uses the built-in analysis:
`packet_loss` >= 100 -> `critical`
`packet_loss` == 0   -> `ok`
`packet_loss` != 0   -> `warning`

## `ParsePing` Objects


### `UNREACHABLE_MESSAGES`

```python
UNREACHABLE_MESSAGES = ["Name or service not known"]
```


### `ParsePing.matched_obj()`

```python
@staticmethod
def matched_obj(data)
```


### `ParsePing.matched_timeout_obj()`

```python
@staticmethod
def matched_timeout_obj(data)
```


### `ParsePing.matched_data()`

```python
@staticmethod
def matched_data(regex_obj)
```


### `ParsePing.matched_timeout_data()`

```python
@staticmethod
def matched_timeout_data(regex_obj)
```


### `ParsePing.extraction_operation()`

```python
@staticmethod
def extraction_operation(data)
```


