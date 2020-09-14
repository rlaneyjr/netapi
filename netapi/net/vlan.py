"""
Vlan main dataclass object.

Contains all attributes and hints about the datatype (some attributes have the
attribute forced when is assigned).
"""
from dataclasses import field
from typing import Optional, List, Any
from pydantic import validator
from pydantic.dataclasses import dataclass
from netapi.metadata import Metadata, EntityCollections, DataConfig, custom_asdict


def status_conversion(raw_status):
    """
    Based on a raw (known) status of the vlan, it returns a standard status (UP,
    DOWN) string and its boolean representation.
    """
    status = raw_status.lower()
    if status == "active":
        status_up = True
    elif status == "suspended":
        status_up = False
    else:
        raise ValueError(f"Vlan status not known: {status}")

    return status, status_up


@dataclass(unsafe_hash=True, config=DataConfig)  # type: ignore
class VlanBase:
    """
    Vlan object definition.

    Attributes:

    - `id`: (int) ID of the vlan
    - `name`: (str) Name of the vlan
    - `status`: (str) Status of the vlan. The `status_conversion` is applied and also
    sets the value of `status_up`.
    - `status_up`: (bool) Flag indicating the current status of the vlan.
    - `interfaces`: (List) contains interfaces configured under the vlan.
    - `vlan_api`: API object which is dependant on the implementation used.
    - `connector`: Device object used to perform the necessary connection.
    - `metadata`: Metadata object which contains information about the current object.
    - `get_cmd`: Command to retrieve route information out of the device
    - `config_cmd`: Command to enable/disable object. Depending on the implementation it
    can be automatically generated when issuing enable/disable methods. It can also be
    generated using `generate_config_cmd()`.
    """

    id: int
    name: Optional[str] = None
    dynamic: Optional[bool] = None
    status_up: Optional[bool] = None
    status: Optional[str] = None
    # TODO: Could create builder methods for populating interfaces of that VLAN
    interfaces: Optional[List[str]] = None
    connector: Optional[Any] = field(default=None, repr=False)
    metadata: Optional[Any] = field(default=None, repr=False)
    vlan_api: Optional[Any] = field(default=None, repr=False)
    get_cmd: Optional[Any] = field(default=None, repr=False)

    @validator("status")
    def valid_status(cls, v, values):
        # NOTE: It does not work when the parameters are assigned! only new instances!
        status, values["status_up"] = status_conversion(v)
        return status

    def __post_init__(self, **_ignore):
        self.metadata = Metadata(name="vlan", type="entity")
        self.id = int(self.id)
        if self.connector:
            if not hasattr(self.connector, "metadata"):
                raise ValueError(
                    f"It does not contain metadata attribute: {self.connector}"
                )
            if self.connector.metadata.name != "device":
                raise ValueError(
                    f"It is not a valid connector object: {self.connector}"
                )

    def to_dict(self):
        # NOTE: Workaround to TypeError: can't pickle SSLContext objects
        return custom_asdict(self, "vlan_api")


class VlansBase(EntityCollections):
    ENTITY = "vlan"

    def __init__(self, *args, **kwargs):
        super().__init__(entity=self.ENTITY, *args, **kwargs)
        self.metadata = Metadata(name="vlans", type="collection")

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, entity=self.ENTITY, **kwargs)
