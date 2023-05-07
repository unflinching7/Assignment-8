import pytest

from ..random_refs import random_slot_ref, random_requestid, random_service_type
from . import api_client


# in_memory_sqlite_db
# @pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("in_memory_sqlite_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_202_and_slot_is_reserved():
    requestid = random_requestid()
    service_type, otherservice_type = random_service_type(), random_service_type("other")
    earlyslot = random_slot_ref(1)
    laterslot = random_slot_ref(2)
    otherslot = random_slot_ref(3)
    api_client.post_to_add_slot(laterslot, service_type, 100, "2011-01-02")
    api_client.post_to_add_slot(earlyslot, service_type, 100, "2011-01-01")
    api_client.post_to_add_slot(otherslot, otherservice_type, 100, None)

    r = api_client.post_to_reserve(requestid, service_type, availability=3)
    assert r.status_code == 202

    r = api_client.get_reservation(requestid)
    assert r.ok
    assert r.json() == [
        {"service_type": service_type, "slot_ref": earlyslot},
    ]


# in_memory_sqlite_db
# @pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("in_memory_sqlite_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_service_type, requestid = random_service_type(), random_requestid()
    r = api_client.post_to_reserve(
        requestid, unknown_service_type, availability=20, expect_success=False)
    assert r.status_code == 400
    assert r.json()[
        "message"] == f"Invalid service_type {unknown_service_type}"

    r = api_client.get_reservation(requestid)
    assert r.status_code == 404
