import pytest
from allocation.adapters import repository
from allocation.domain import model

pytestmark = pytest.mark.usefixtures("mappers")


def test_get_by_slot_ref(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    s1 = model.AppointmentSlot(
        slot_ref="s1", service_type="svc1", availability=100, start_time=None)
    s2 = model.AppointmentSlot(
        slot_ref="s2", service_type="svc1", availability=100, start_time=None)
    s3 = model.AppointmentSlot(
        slot_ref="s3", service_type="svc2", availability=100, start_time=None)
    so1 = model.ServiceOffering(service_type="svc1", slots=[s1, s2])
    so2 = model.ServiceOffering(service_type="svc2", slots=[s3])
    repo.add(so1)
    repo.add(so2)
    assert repo.get_by_slot_ref("s2") == so1
    assert repo.get_by_slot_ref("s3") == so2
