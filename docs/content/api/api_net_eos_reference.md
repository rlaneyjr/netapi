# `eos`


# `eos.pyeapier`

EOS Pyeapi module.

Contains the method to create Network Objects for the EOS-PYEAPI implementation.

## `update_attrs()`

```python
def update_attrs(obj, data_dict)
```

Updates object attributes based on data from dictionary

## `update_container_attrs()`

```python
def update_container_attrs(obj, list_of_dict, entity)
```

Updates collections based on data from dictionary contained in list

## `Vlans` Objects


### `Vlans.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(vlan_range=None)
```

Returns commands necessary to build a collection of entities

### `Vlans.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection. A connector object has to be passed

## `Vlan` Objects


### `Vlan.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(id)
```

Returns commands necessary to build the entity

### `Vlan.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection by running get_cmd

### `Vlan.enable()`

```python
def enable(self)
```

Enable VLAN

### `Vlan.disable()`

```python
def disable(self)
```

Disable VLAN

## `ParseVlan` Objects


### `ParseVlan.data_constructor()`

```python
@staticmethod
def data_constructor(vlan_id, data, kwargs)
```

If no data is passed a known error

### `ParseVlan.data_validation()`

```python
@staticmethod
def data_validation(raw_data, entity=True, kwargs)
```

Returns useful data and performs some initial validations

### `ParseVlan.parse()`

```python
@staticmethod
def parse(raw_data, kwargs)
```

Returns a dictionary with the entity data parsed

### `ParseVlan.collector_parse()`

```python
@staticmethod
def collector_parse(raw_data, kwargs)
```

Returns list of dictionaries of each entity parsed

## `Vrrps` Objects


### `Vrrps.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(instance=None, interface=None)
```

Returns commands necessary to build a collection of entities

### `Vrrps.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection. A connector object has to be passed

## `Vrrp` Objects


### `Vrrp.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(group_id, interface=None, instance=None)
```

Returns commands necessary to build the entity

### `Vrrp.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data update on the object

### `Vrrp.enable()`

```python
def enable(self)
```

Enable VRRP group

### `Vrrp.disable()`

```python
def disable(self)
```

Disable VRRP group

## `ParseVrrp` Objects


### `ParseVrrp.data_constructor()`

```python
@staticmethod
def data_constructor(data, kwargs)
```

If no data is passed a known error

### `ParseVrrp.data_validation()`

```python
@staticmethod
def data_validation(raw_data, entity=True, kwargs)
```

Returns useful data and performs some initial validations

### `ParseVrrp.parse()`

```python
@staticmethod
def parse(raw_data, kwargs)
```

Returns a dictionary with the entity data parsed

### `ParseVrrp.collector_parse()`

```python
@staticmethod
def collector_parse(raw_data, kwargs)
```

Returns list of dictionaries of each entity parsed

## `Interfaces` Objects


### `Interfaces.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(interface_range=None)
```

Returns commands necessary to build the collection of entities

### `Interfaces.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection. A connector object has to be passed

## `Interface` Objects


### `Interface.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(name)
```

Returns commands necessary to build the entity

### `Interface.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection by running get_cmd

### `Interface.enable()`

```python
def enable(self)
```

Enable Interface

### `Interface.disable()`

```python
def disable(self)
```

Disable Interface

## `ParseInterface` Objects


### `ParseInterface.data_constructor()`

```python
@staticmethod
def data_constructor(intf_name, data, kwargs)
```

If no data is passed a known error

### `ParseInterface.data_validation()`

```python
@staticmethod
def data_validation(raw_data, entity=True, kwargs)
```

Returns useful data and performs some initial validations

### `ParseInterface.parse()`

```python
@staticmethod
def parse(raw_data, kwargs)
```

Returns a dictionary with the entity data parsed

### `ParseInterface.collector_parse()`

```python
@staticmethod
def collector_parse(raw_data, kwargs)
```

Returns list of dictionaries of each entity parsed

## `Facts` Objects


### `Facts.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd()
```

Returns commands necessary to build the entity

### `Facts.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection

## `ParseFacts` Objects


### `ParseFacts.data_constructor()`

```python
@staticmethod
def data_constructor(hostname, version, interfaces, kwargs)
```

If no data is passed a known error

### `ParseFacts.parse()`

```python
@staticmethod
def parse(raw_data, kwargs)
```


## `Routes` Objects


### `Routes.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(protocol=None, instance=None, vrf_all=False)
```

Returns commands necessary to build a collection of entities

### `Routes.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection. A connector object has to be passed

## `Route` Objects


### `Route.generate_get_cmd()`

```python
@staticmethod
def generate_get_cmd(dest, instance=None)
```

Returns commands necessary to build the entity.

NOTE: This is preferred over the original `get(name)` method of pyeapi because
it provides with much more info

### `Route.get()`

```python
def get(self, _ignore)
```

Automatic trigger a data collection by running the get_cmd

## `ParseRoute` Objects


### `ParseRoute.data_constructor()`

```python
@staticmethod
def data_constructor(_instance, _route, data, kwargs)
```


### `ParseRoute.data_validation()`

```python
@staticmethod
def data_validation(raw_data, entity=True, kwargs)
```

Returns useful data and performs some initial validations

### `ParseRoute.parse()`

```python
@staticmethod
def parse(raw_data, kwargs)
```

Returns a dictionary with the entity data parsed

### `ParseRoute.collector_parse()`

```python
@staticmethod
def collector_parse(raw_data, kwargs)
```

Returns list of dictionaries of each entity parsed

