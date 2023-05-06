import pytest
import requests

from allocation import config
from ..random_refs import random_service_type, random_slot_ref, random_request_id


def post_to_add_slot(slot_ref, service_type, slot_qty, start_time):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_slot", json={"slot_ref": slot_ref, "service_type": service_type, "slot_qty": slot_qty, "start_time": start_time}
    )
    assert r.status_code == 201


def post_to_reserve_slot(request_id, service_type, availability):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/reserve_slot", json={"request_id": request_id, "service_type": service_type, "availability": availability}
    )
    return r


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_reserved_slot():
    service_type, otherservice_type = random_service_type(), random_service_type("other")
    early_slot = random_slot_ref(1)
    later_slot = random_slot_ref(2)
    other_slot = random_slot_ref(3)
    post_to_add_slot(later_slot, service_type, 100, "2011-01-02")
    post_to_add_slot(early_slot, service_type, 100, "2011-01-01")
    post_to_add_slot(other_slot, otherservice_type, 100, None)
    data = {"request_id": random_request_id(
    ), "service_type": service_type, "availability": 3}

    r = post_to_reserve_slot(
        data["request_id"], data["service_type"], data["availability"])

    assert r.status_code == 201
    assert r.json()["slot_ref"] == early_slot


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_service_type, request_id = random_service_type(), random_request_id()
    data = {"request_id": request_id,
            "service_type": unknown_service_type, "availability": 20}
    url = config.get_api_url()
    r = post_to_reserve_slot(
        data["request_id"], data["service_type"], data["availability"])
    assert r.status_code == 400
    assert r.json()[
        "message"] == f"Invalid service type {unknown_service_type}"
