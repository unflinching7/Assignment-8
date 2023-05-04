import pytest
import requests

from allocation import config
from ..random_refs import random_service_type, random_batchref, random_orderid


def post_to_add_batch(ref, service_type, qty, eta):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_batch", json={"ref": ref, "service_type": service_type, "qty": qty, "eta": eta}
    )
    assert r.status_code == 201


def post_to_allocate(orderid, service_type, qty):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/allocate", json={"orderid": orderid, "service_type": service_type, "qty": qty}
    )
    return r


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch():
    service_type, otherservice_type = random_service_type(), random_service_type("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    post_to_add_batch(laterbatch, service_type, 100, "2011-01-02")
    post_to_add_batch(earlybatch, service_type, 100, "2011-01-01")
    post_to_add_batch(otherbatch, otherservice_type, 100, None)
    data = {"orderid": random_orderid(), "service_type": service_type, "qty": 3}

    r = post_to_allocate(data["orderid"], data["service_type"], data["qty"])

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_service_type, orderid = random_service_type(), random_orderid()
    data = {"orderid": orderid, "service_type": unknown_service_type, "qty": 20}
    url = config.get_api_url()
    r = post_to_allocate(data["orderid"], data["service_type"], data["qty"])
    assert r.status_code == 400
    assert r.json()[
        "message"] == f"Invalid service type {unknown_service_type}"
