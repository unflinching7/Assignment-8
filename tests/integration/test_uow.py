# pylint: disable=broad-except
import threading
import time
import traceback
from typing import List
import pytest
from allocation.domain import model
from allocation.service_layer import unit_of_work
from ..random_refs import random_service_type, random_slot_reference


def insert_slot(session, slot_ref, service_type, location_number=1):
    session.execute(
        "INSERT INTO service_offerings (service_type, location_number) VALUES (:service_type, :location)",
        dict(service_type=service_type, location=location_number),
    )
    session.execute(
        "INSERT INTO appointment_slots (slot_reference, service_type)"
        " VALUES (:slot_ref, :service_type)",
        dict(slot_ref=slot_ref, service_type=service_type),
    )


def test_concurrent_updates_to_location_number_are_not_allowed(postgres_session_factory):
    service_type, slot_ref = random_service_type(), random_slot_reference()
    session = postgres_session_factory()
    insert_slot(session, slot_ref, service_type, location_number=1)
    session.commit()

    slot_refs = [random_slot_reference() for _ in range(10)]
    exceptions = []  # type: List[Exception]

    def try_to_reserve_slot(slot_ref):
        try:
            with unit_of_work.SqlAlchemyUnitOfWork() as uow:
                slot = uow.appointment_slots.get(slot_ref)
                slot.reserve_slot()
                time.sleep(0.2)
                uow.commit()
        except Exception as e:
            print(traceback.format_exc())
            exceptions.append(e)

    threads = []
    for slot_ref in slot_refs:
        thread = threading.Thread(
            target=try_to_reserve_slot, args=(slot_ref,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    assert len(exceptions) == 0


def test_can_add_new_slot(postgres_session_factory):
    # Set up: create a new service type and slot reference
    service_type = random_service_type()
    slot_ref = random_slot_reference()

    # Execute the test
    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        add_slot = model.InsertSlot(slot_ref, service_type, slot_qty=10)
        add_slot.execute(uow)

    # Verify that the slot was added correctly
    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        slot = uow.appointment_slots.get(slot_ref)
        assert slot.service_type == service_type
        assert slot.reserved_quantity == 0
        assert slot.available_quantity == 10


def test_cannot_add_duplicate_slot(postgres_session_factory):
    # Set up: create a new service type and slot reference
    service_type = random_service_type()
    slot_ref = random_slot_reference()

    # Execute the test
    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        add_slot = model.InsertSlot(slot_ref, service_type, slot_qty=10)
        add_slot.execute(uow)

    # Try to add the same slot again and verify that it fails
    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        add_slot = model.InsertSlot(slot_ref, service_type, slot_qty=10)
        with pytest.raises(ValueError, match="duplicate key value"):
            add_slot.execute(uow))
