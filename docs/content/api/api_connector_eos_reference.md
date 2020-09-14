# `eos`


# `eos.pyeapier`

EOS PYEAPI Implementation of Device object.

Note: The name of the module is created so it doesn't clash with the python EAPI client

## `EOS_CONNECTION_METHODS`

```python
EOS_CONNECTION_METHODS = ["socket", "http", "https", "http_local"]
```


## `Devices` Objects


## `Device` Objects


### `Device.run()`

```python
def run(self, commands: Optional[List[str]] = str, silent: bool = False, kwargs)
```

Run method to executed list of commands passed to it

