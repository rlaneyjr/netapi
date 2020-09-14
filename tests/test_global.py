import pytest
from netapi.metadata import Metadata


@pytest.mark.unico
def test_metadata():
    m1 = Metadata(name="m1", type="test")
    m2 = Metadata(name="m2", type="test")
    assert m1.id != m2.id
