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
    sqlite_bus.handle(commands.InsertSlot("sku1slot", "sku1", 50, None))
    sqlite_bus.handle(commands.InsertSlot("sku2slot", "sku2", 50, today))
    sqlite_bus.handle(commands.ReserveSlot("order1", "sku1", 20))
    sqlite_bus.handle(commands.ReserveSlot("order1", "sku2", 20))
    # add a spurious slot and order to make sure we're getting the right ones
    sqlite_bus.handle(commands.InsertSlot("sku1slot-later", "sku1", 50, today))
    sqlite_bus.handle(commands.ReserveSlot("otherorder", "sku1", 30))
    sqlite_bus.handle(commands.ReserveSlot("otherorder", "sku2", 10))

    assert views.reservations("order1", sqlite_bus.uow) == [
        {"service_type": "sku1", "slot_ref": "sku1slot"},
        {"service_type": "sku2", "slot_ref": "sku2slot"},
    ]


def test_cancel_reservation(sqlite_bus):
    sqlite_bus.handle(commands.InsertSlot("slot1", "sku1", 50, None))
    sqlite_bus.handle(commands.InsertSlot("slot2", "sku1", 50, today))
    sqlite_bus.handle(commands.ReserveSlot("order1", "sku1", 40))
    sqlite_bus.handle(commands.ChangeSlotAvailability("slot1", 10))

    assert views.reservations("order1", sqlite_bus.uow) == [
        {"service_type": "sku1", "slot_ref": "slot2"},
    ]
