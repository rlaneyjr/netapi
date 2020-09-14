"""
EOS PYEAPI Implementation of Device object.

Note: The name of the module is created so it doesn't clash with the python EAPI client
"""
import pyeapi
from netapi.connector.device import DeviceBase, DevicesBase
from dataclasses import dataclass, field
from typing import Optional, List


# NOTE: The socket method and http_local will not work because currently
# Arista runs with python 2.7 => it needs to change to 3.6 at least
EOS_CONNECTION_METHODS = ["socket", "http", "https", "http_local"]


class Devices(DevicesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata.implementation = "EOS-PYEAPI"


@dataclass
class Device(DeviceBase):
    port: Optional[int] = None
    net_os: str = field(init=False, default="eos")
    transport: Optional[str] = None
    _transport: Optional[str] = field(init=False, repr=False)

    # Initialization of device connection
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "EOS-PYEAPI"
        _conn = pyeapi.connect(
            host=self.host,
            transport=self.transport,
            username=self.username,
            password=self.password,
        )
        self.connector = pyeapi.client.Node(_conn)

    @property
    def transport(self) -> str:
        return self._transport

    @transport.setter
    def transport(self, v: str) -> None:
        if v not in EOS_CONNECTION_METHODS:
            raise NotImplementedError(f"Transport not implemented")
        self._transport = v

    # TODO: [1002]: CLI command 2 of 2 'show interfaces Loopback777' failed: invalid
    # command [Interface does not exist]
    def _silent_run(self, commands):
        # Is a controlled approach, where it runs each command and if a command error
        # occurs then it will remove that command from the list
        _responses = None
        while True:
            try:
                _responses = self.connector.enable(commands)
            except pyeapi.eapilib.CommandError as err:
                if err.error_code == 1002 or err.error_code == 1000:
                    err_command = err.commands[1]
                    # print(f"[SILENT_MODE] Issue with the command(s) -> {err_command}")
                    # print(f"[SILENT_MODE]: {err.message}")
                    self._cache[err_command] = None
                    commands.remove(err_command)
                else:
                    raise err
            else:
                if len(commands) == 0:
                    raise ValueError("None of the commands passed ...")
                break

        return _responses

    def _normal_run(self, commands):
        # It will raise an error if a command error happens
        _responses = self.connector.enable(commands)
        return _responses

    def run(self, commands: Optional[List[str]] = str, silent: bool = False, **kwargs):
        "Run method to executed list of commands passed to it"
        if isinstance(commands, str):
            commands = [commands]
        self._cache = {x: None for x in commands}
        # Perform run
        if silent:
            _responses = self._silent_run(commands)
        else:
            _responses = self._normal_run(commands)
        # Now map
        for _response in _responses:
            self._cache[_response["command"]] = _response["result"]

        return self._cache
