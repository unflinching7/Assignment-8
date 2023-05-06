from __future__ import annotations
from typing import Optional
from datetime import date

from allocation.domain import model as domain_model
from allocation.domain.model import CheckInRequest
from allocation.service_layer import unit_of_work


class InvalidServiceType(Exception):
    pass


def add_appointment_slot(
    slot_reference: str, service_type: str, availability: int, start_time: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        service_offering = uow.service_offerings.get(service_type=service_type)
        if service_offering is None:
            service_offering = domain_model.ServiceOffering(
                service_type, slots=[])
            uow.service_offerings.add(service_offering)
        service_offering.slots.append(domain_model.AppointmentSlot(
            slot_reference, service_type, availability, start_time))
        uow.commit()


def reserve_slot(
    requestid: str, service_type: str, availability: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    check_in_request = CheckInRequest(requestid, service_type, availability)
    with uow:
        service_offering = uow.service_offerings.get(
            service_type=check_in_request.service_type)
        if service_offering is None:
            raise InvalidServiceType(
                f"Invalid service type {check_in_request.service_type}")
        slot_ref = service_offering.reserve_slot(check_in_request)
        uow.commit()
    return slot_ref
