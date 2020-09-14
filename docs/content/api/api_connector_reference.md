# `__init__`


## `DeviceBuilder` Objects

Helper class used to create device objects by passing a device the `net_os` and
`provider` implementations.

### `DeviceBuilder.create_device()`

```python
def create_device(self, net_os, provider, kwargs)
```

Instantiate builder

## `DeviceFactory` Objects

Registers new implementations for connecting to devices

### `DeviceFactory.get_connector()`

```python
def get_connector(self, connector, kwargs)
```


# `device`


## `DeviceBase` Objects

Handler of device connections and command execution

## `DevicesBase` Objects


