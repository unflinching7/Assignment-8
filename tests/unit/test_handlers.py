# pylint: disable=no-self-use
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, List

import pytest
from allocation import bootstrap
from allocation.adapters import notifications, repository
from allocation.domain import commands
from allocation.service_layer import handlers, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, services):
        super().__init__()
        self._services = set(services)

    def _add(self, service_offering):
        self._services.add(service_offering)

    def _get(self, service_type):
        return next((p for p in self._services if p.service_type == service_type), None)

    def _get_by_slot_ref(self, slot_ref):
        return next(
            (p for p in self._services for s in p.appointment_slots if s.slot_reference == slot_ref),
            None,
        )


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.services = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeNotifications(notifications.AbstractNotifications):
    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, destination, message):
        self.sent[destination].append(message)


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications=FakeNotifications(),
        publish=lambda *args: None,
    )


class TestAddSlot:
    def test_for_new_service_offering(self):
        bus = bootstrap_test_app()
        bus.handle(commands.InsertSlot(
            "b1", "chiropractic service", 100, None))
        assert bus.uow.services.get("chiropractic service") is not None
        assert bus.uow.committed

    def test_for_existing_service_offering(self):
        bus = bootstrap_test_app()
        bus.handle(commands.InsertSlot(
            "b1", "chiropractic service", 100, None))
        bus.handle(commands.InsertSlot("b2", "chiropractic service", 99, None))
        assert "b2" in [s.slot_reference for s in bus.uow.services.get(
            "chiropractic service").appointment_slots]


class TestReserveSlot:
    def test_reserves_slot(self):
        bus = bootstrap_test_app()
        bus.handle(commands.InsertSlot(
            "batch1", "chiropractic service", 100, None))
        bus.handle(commands.ReserveSlot("o1", "chiropractic service", 10))
        [slot] = bus.uow.services.get("chiropractic service").appointment_slots
        assert slot.availability == 90

    def test_errors_for_invalid_service_type(self):
        bus = bootstrap_test_app()
        bus.handle(commands.InsertSlot(
            "b1", "chiropractic service", 100, None))

        with pytest.raises(handlers.InvalidServiceType, match="Invalid service type NONEXISTENTSERVICE"):
            bus.handle(commands.ReserveSlot("o1", "NONEXISTENTSERVICE", 10))

    def test_commits(self):
        bus = bootstrap_test_app()
        bus.handle(commands.InsertSlot(
            "b1", "chiropractic service", 100, None))
        bus.handle(commands.ReserveSlot("o1", "chiropractic service", 10))
        assert bus.uow.committed

    def test_sends_email_on_no_available_slots_error(self):
    fake_notifs = FakeNotifications()
    bus = bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications=fake_notifs,
        publish=lambda *args: None,
    )
    bus.handle(commands.InsertSlot("b1", "chiropractic service", 9, None))
    bus.handle(commands.ReserveSlot("o1", "chiropractic service", 10))
    assert fake_notifs.sent["slots@made.com"] == [
        f"No available slots for chiropractic service",
    ]


class TestChangeSlotAvailability:
    def test_changes_available_quantity(self):
        bus = bootstrap_test_app()
        bus.handle(commands.InsertSlot(
            "slot1", "chiropractic service", 100, None))
        [slot] = bus.uow.services.get(
            service_type="chiropractic service").slots
        assert slot.availability == 100

        bus.handle(commands.ChangeSlotAvailability("slot1", 50))
        assert slot.availability == 50

    def test_reallocates_if_necessary(self):
        bus = bootstrap_test_app()
        history = [
            commands.InsertSlot("slot1", "chiropractic service", 50, None),
            commands.InsertSlot(
                "slot2", "chiropractic service", 50, date.today()),
            commands.ReserveSlot("request1", "chiropractic service", 20),
            commands.ReserveSlot("request2", "chiropractic service", 20),
        ]
        for msg in history:
            bus.handle(msg)
        [slot1, slot2] = bus.uow.services.get(
            service_type="chiropractic service").slots
        assert slot1.availability == 10
        assert slot2.availability == 50

        bus.handle(commands.ChangeSlotAvailability("slot1", 25))

        # request1 or request2 will be cancelled, so we'll have 25 - 20
        assert slot1.availability == 5
        # and 20 will be reallocated to the next slot
        assert slot2.availability == 30
