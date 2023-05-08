# pylint: disable=redefined-outer-name
from datetime import date
from unittest import mock

import pytest
from allocation import bootstrap, views
from allocation.domain import commands
from allocation.service_layer import unit_of_work
from sqlalchemy.orm import clear_mappers

today = date.today()


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory),
        notifications=mock.Mock(),
        publish=lambda *args: None,
    )
    yield bus
    clear_mappers()


def test_reservations_view(sqlite_bus):
    sqlite_bus.handle(commands.InsertSlot(
        "service_type1slot", "service_type1", 50, None))
    sqlite_bus.handle(commands.InsertSlot(
        "service_type2slot", "service_type2", 50, today))
    sqlite_bus.handle(commands.ReserveSlot("request1", "service_type1", 20))
    sqlite_bus.handle(commands.ReserveSlot("request1", "service_type2", 20))
    # add a spurious slot and request to make sure we're getting the right ones
    sqlite_bus.handle(commands.InsertSlot(
        "service_type1slot-later", "service_type1", 50, today))
    sqlite_bus.handle(commands.ReserveSlot(
        "otherrequest", "service_type1", 30))
    sqlite_bus.handle(commands.ReserveSlot(
        "otherrequest", "service_type2", 10))

    assert views.reservations("request1", sqlite_bus.uow) == [
        {"service_type": "service_type1", "slot_ref": "service_type1slot"},
        {"service_type": "service_type2", "slot_ref": "service_type2slot"},
    ]


def test_cancel_reservation(sqlite_bus):
    sqlite_bus.handle(commands.InsertSlot("slot1", "service_type1", 50, None))
    sqlite_bus.handle(commands.InsertSlot("slot2", "service_type1", 50, today))
    sqlite_bus.handle(commands.ReserveSlot("request1", "service_type1", 40))
    sqlite_bus.handle(commands.ChangeSlotAvailability("slot1", 10))

    assert views.reservations("request1", sqlite_bus.uow) == [
        {"service_type": "service_type1", "slot_ref": "slot2"},
    ]
