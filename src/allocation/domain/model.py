from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Set

from . import commands, events


class ServiceOffering:
    def __init__(self, service_type: str, appointment_slots: List[AppointmentSlot], location_number: int = 0):
        self.service_type = service_type
        self.appointment_slots = appointment_slots
        self.location_number = location_number
        self.events = []  # type: List[events.Event]

    def reserve_slot(self, checkin_request: CheckInRequest) -> str:
        try:
            slot = next(s for s in sorted(self.appointment_slots)
                        if s.can_reserve(checkin_request))
            slot.reserve(checkin_request)
            self.location_number += 1
            self.events.append(
                events.Reserved(
                    requestid=checkin_request.requestid,
                    service_type=checkin_request.service_type,
                    reserved_quantity=checkin_request.qty,
                    slot_ref=slot.slot_ref,
                )
            )
            return slot.slot_ref
        except StopIteration:
            self.events.append(events.NoAvailableSlots(
                checkin_request.service_type))
            return None

    def change_slot_quantity(self, slot_ref: str, qty: int):
        slot = next(s for s in self.appointment_slots if s.slot_ref == slot_ref)
        slot.slot_qty = qty
        while slot.available_quantity < 0:
            checkin_request = slot.cancel_reservation_one()
            self.events.append(events.CancelledReservation(
                checkin_request.requestid, checkin_request.service_type, checkin_request.qty))


@dataclass(unsafe_hash=True)
class CheckInRequest:
    requestid: str
    service_type: str
    qty: int


class AppointmentSlot:
    def __init__(self, slot_ref: str, service_type: str, availability: int, start_time: Optional[date]):
        self.slot_ref = slot_ref
        self.service_type = service_type
        self.start_time = start_time
        self._slot_qty = availability
        self._reservations = set()  # type: Set[CheckInRequest]

    def __repr__(self):
        return f"<AppointmentSlot {self.slot_ref}>"

    def __eq__(self, other):
        if not isinstance(other, AppointmentSlot):
            return False
        return other.slot_ref == self.slot_ref

    def __hash__(self):
        return hash(self.slot_ref)

    def __gt__(self, other):
        if self.start_time is None:
            return False
        if other.start_time is None:
            return True
        return self.start_time > other.start_time

    def reserve(self, checkin_request: CheckInRequest):
        if self.can_reserve(checkin_request):
            self._reservations.add(checkin_request)

    def cancel_reservation_one(self) -> CheckInRequest:
        return self._reservations.pop()

    @property
    def reserved_quantity(self) -> int:
        return sum(req.qty for req in self._reservations)

    @property
    def available_quantity(self) -> int:
        return self._slot_qty - self.reserved_quantity

    def can_reserve(self, checkin_request: CheckInRequest) -> bool:
        return self.service_type == checkin_request.service_type and self.available_quantity >= checkin_request.qty
