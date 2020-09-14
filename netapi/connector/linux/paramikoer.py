"""
LINUX Paramiko (Remote) Implementation of Device object.

Note: The name of the module is created so it doesn't clash with the library
"""
from netapi.connector.device import DeviceBase
from dataclasses import dataclass, field


@dataclass
class Device(DeviceBase):
    net_os: str = field(init=False, default="linux")

    # Initialization of device connection
    def __post_init__(self, **_ignore):
        super().__post_init__(**_ignore)
        self.metadata.implementation = "LINUX-PARAMIKO"
