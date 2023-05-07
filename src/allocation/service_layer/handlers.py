# pylint: disable=unused-argument
from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Callable, Dict, List, Type

from allocation.domain import commands, events, model
from allocation.domain.model import CheckInRequest, ServiceOffering, AppointmentSlot

if TYPE_CHECKING:
    from allocation.adapters import notifications
    from . import unit_of_work


class InvalidServiceType(Exception):
    pass


def add_slot(
    cmd: commands.InsertSlot,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        service_offering = uow.service_offerings.get(
            service_type=cmd.service_type)
        if service_offering is None:
            service_offering = ServiceOffering(
                cmd.service_type, appointment_slots=[])
            uow.service_offerings.add(service_offering)
        service_offering.appointment_slots.append(AppointmentSlot(
            cmd.slot_ref, cmd.service_type, cmd.slot_qty, cmd.start_time))
        uow.commit()


def reserve_slot(
    cmd: commands.ReserveSlot,
    uow: unit_of_work.AbstractUnitOfWork,
):
    reservation = CheckInRequest(cmd.requestid, cmd.service_type, cmd.slot_qty)
    with uow:
        service_offering = uow.service_offerings.get(
            service_type=reservation.service_type)
        if service_offering is None:
            raise InvalidServiceType(
                f"Invalid service type {reservation.service_type}")
        if not service_offering.can_reserve(reservation):
            raise model.UnableToReserveSlot(
                f"Not enough availability to reserve slot for {reservation.service_type}")
        service_offering.reserve_slot(reservation)
        uow.commit()


def reallocate(
    event: events.CancelledReservation,
    uow: unit_of_work.AbstractUnitOfWork,
):
    reserve_slot(commands.ReserveSlot(**asdict(event)), uow=uow)


def ChangeSlotAvailability(
    cmd: commands.ChangeSlotAvailability,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        service_offering = uow.service_offerings.get_by_slotref(
            slotref=cmd.slot_ref)
        service_offering.change_slot_availability(
            ref=cmd.slot_ref, availability=cmd.availability)
        uow.commit()


# pylint: disable=unused-argument
def send_no_available_slots_notification(
    event: events.NoAvailableSlots,
    notifications: notifications.AbstractNotifications,
):
    notifications.send(
        "checkin@yourbusiness.com",
        f"No available slots for {event.service_type}",
    )


def publish_reserved_slot_event(
    event: events.SlotReserved,
    publish: Callable,
):
    publish("slot_reserved", event)


def add_reservation_to_read_model(
    event: events.SlotReserved,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            INSERT INTO reservations_view (requestid, service_type, slot_ref)
            VALUES (:requestid, :service_type, :slot_ref)
            """,
            dict(requestid=event.requestid,
                 service_type=event.service_type, slot_ref=event.slot_ref),
        )
        uow.commit()


def remove_reservation_from_read_model(
    event: events.CancelledReservation,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            DELETE FROM reservations_view
            WHERE requestid = :requestid AND service_type = :service_type
            """,
            dict(requestid=event.requestid, service_type=event.service_type),
        )
        uow.commit()


EVENT_HANDLERS = {
    events.SlotReserved: [publish_reserved_slot_event, add_reservation_to_read_model],
