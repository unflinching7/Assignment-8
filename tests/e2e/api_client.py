import requests
from reservation import config


def post_to_add_slot(slot_ref, service_type, slot_qty, start_time):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_slot", json={"slot_ref": slot_ref, "service_type": service_type, "slot_qty": slot_qty, "start_time": start_time}
    )
    assert r.status_code == 201


def post_to_reserve(requestid, service_type, reserved_quantity, expect_success=True):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/reserve_slot",
        json={
            "requestid": requestid,
            "service_type": service_type,
            "reserved_quantity": reserved_quantity,
        },
    )
    if expect_success:
        assert r.status_code == 202
    return r


def get_reservation(requestid):
    url = config.get_api_url()
    return requests.get(f"{url}/reservations/{requestid}")
