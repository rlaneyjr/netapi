"""
EOS PYEAPI Implementation of Device object.

Note: The name of the module is created so it doesn't clash with the python EAPI client
"""
from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
from netapi.connector.device import DeviceBase, DevicesBase
from dataclasses import dataclass, field
from typing import Union, Optional, List


# NOTE: The socket method and http_local will not work because currently
# Arista runs with python 2.7 => it needs to change to 3.6 at least
IOS_CONNECTION_METHODS = ["socket", "ssh", "telnet"]
NETMIKO_EXCEPTIONS = ['NetmikoAuthenticationException', 'NetmikoTimeoutException']


class Devices(DevicesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata.implementation = "IOS-NETMIKO"


@dataclass
class Device(DeviceBase):
    port: Optional[int] = 22
    net_os: str = field(init=False, default="cisco_ios")
    transport: Optional[str] = None
    _transport: Optional[str] = field(init=False, repr=False)

    # Initialization of device connection
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "IOS-NETMIKO"
        self.connector = ConnectHandler(
            host=self.host,
            device_type=self.net_os,
            username=self.username,
            password=self.password,
        )

    @property
    def transport(self) -> str:
        return self._transport

    @transport.setter
    def transport(self, v: str) -> None:
        if v not in IOS_CONNECTION_METHODS:
            raise NotImplementedError(f"Transport not implemented")
        self._transport = v

    def _silent_run(self, commands: list):
        # Is a controlled approach, where it runs each command and if a command error
        # occurs then it will remove that command from the list
        _responses = {}
        for command in commands:
            try:
                response = self.connector.send_command(command)
                _responses[command] = response
            except Exception as e:
                # Catch and re-raise exceptions that are fatal
                if e in NETMIKO_EXCEPTIONS:
                    raise e
                else:
                    _responses[command] = e
                    commands.remove(command)
        if not len(commands):
            raise ValueError("None of the commands passed ...")
        return _responses

    def _normal_run(self, commands: list):
        # It will raise an error if a command error happens
        _responses = {}
        for command in commands:
            response = self.connector.send_command(command)
            _responses[command] = response
        return _responses

    def run(self, commands: List[str], silent: bool=False, **kwargs):
        "Run method to executed list of commands passed to it"
        if isinstance(commands, str):
            commands = [commands]
        self._cache = {x: None for x in commands}
        if silent:
            _responses = self._silent_run(commands)
        else:
            _responses = self._normal_run(commands)
        for cmd, resp in _responses.items():
            self._cache[cmd] = resp
        return self._cache
