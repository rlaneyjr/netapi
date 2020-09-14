from dataclasses import dataclass, field
from typing import Optional
from netapi.metadata import Metadata, EntityCollections


@dataclass(unsafe_hash=True)
class DeviceBase:
    # TODO: Make the device objects more than connectors -> lets make them have data of
    # the device itself, like developing a get_facts method
    "Handler of device connections and command execution"

    host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = field(repr=False, default=None)

    def __post_init__(self, **_ignore):
        self.metadata = Metadata(name="device", type="entity")


class DevicesBase(EntityCollections):
    ENTITY = "device"

    def __init__(self, *args, **kwargs):
        super().__init__(entity=self.ENTITY, *args, **kwargs)
        self.metadata = Metadata(name="devices", type="collection")

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, entity=self.ENTITY, **kwargs)
