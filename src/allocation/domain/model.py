from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class NoAvailableSlots(Exception):
    pass


class ServiceOffering:
    def __init__(self, service_type: str, appointment_slots: List[AppointmentSlot], location_number: int = 0):
        self.service_type = service_type
        self.appointment_slots = appointment_slots
        self.location_number = location_number

    def reserve_slot(self, request: CheckInRequest) -> str:
        try:
            slot = next(s for s in sorted(self.appointment_slots)
                        if s.can_reserve(request))
            slot.reserve(request)
            return slot.appointment_reference
        except StopIteration:
            raise NoAvailableSlots(
                f"No available slots for service type {request.service_type}")


@dataclass(unsafe_hash=True)
class CheckInRequest:
    orderid: str
    service_type: str
    reservation_qty: int


class AppointmentSlot:
    def __init__(self, appointment_reference: str, service_type: str, slot_qty: int, start_time: Optional[date]):
        self.appointment_reference = appointment_reference
        self.service_type = service_type
        self.start_time = start_time
        self.slot_qty = slot_qty
        self._reservations = set()  # type: Set[CheckInRequest]

    def __repr__(self):
        return f"<AppointmentSlot {self.appointment_reference}>"

    def __eq__(self, other):
        if not isinstance(other, AppointmentSlot):
            return False
        return other.appointment_reference == self.appointment_reference

    def __hash__(self):
        return hash(self.appointment_reference)

    def __gt__(self, other):
        if self.start_time is None:
            return False
        if other.start_time is None:
            return True
        return self.start_time > other.start_time

    def reserve(self, request: CheckInRequest):
        if self.can_reserve(request):
            self._reservations.add(request)

    def cancel_reservation(self, request: CheckInRequest):
        if request in self._reservations:
            self._reservations.remove(request)

    @property
    def reserved_quantity(self) -> int:
        return sum(request.reservation_qty for request in self._reservations)

    @property
    def available_quantity(self) -> int:
        return self.slot_qty - self.reserved_quantity

    def can_reserve(self, request: CheckInRequest) -> bool:
        return self.service_type == request.service_type and self.available_quantity >= request.reservation_qty
