"""
LINUX Subprocess (Local) Implementation of Device object.

Note: The name of the module is created so it doesn't clash with the library
"""
from netapi.connector.device import DeviceBase
from subprocess import check_output, STDOUT
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Device(DeviceBase):
    net_os: str = field(init=False, default="linux")

    # Initialization of device connection
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "LINUX-SUBPROCESS"

    def run(self, commands: Optional[List[str]] = str, silent: bool = False, **kwargs):
        if isinstance(commands, str):
            commands = [commands]
        self._cache = {x: None for x in commands}
        # Perform run
        for _command in self._cache:
            # TODO: Need to test this on a linux machine
            self._cache[_command] = check_output(
                _command.split(), stderr=STDOUT
            ).decode("utf-8")

        return self._cache
