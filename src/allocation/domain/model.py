from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class NoAvailableSlots(Exception):
    pass


class ServiceOffering:
    def __init__(self, service_type: str, appointment_slots: List[AppointmentSlot], version_number: int = 0):
        self.service_type = service_type
        self.appointment_slots = appointment_slots
        self.version_number = version_number

    def allocate(self, request: CheckInRequest) -> str:
        try:
            slot = next(s for s in sorted(self.appointment_slots)
                        if s.can_allocate(request))
            slot.allocate(request)
            self.version_number += 1
            return slot.appointment_reference
        except StopIteration:
            raise NoAvailableSlots(
                f"No available slots for service type {request.service_type}")


@dataclass(unsafe_hash=True)
class CheckInRequest:
    orderid: str
    service_type: str
    availability: int


class AppointmentSlot:
    def __init__(self, appointment_reference: str, service_type: str, availability: int, start_time: Optional[date]):
        self.appointment_reference = appointment_reference
        self.service_type = service_type
        self.start_time = start_time
        self._purchased_quantity = availability
        self._allocations = set()  # type: Set[CheckInRequest]

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

    def allocate(self, request: CheckInRequest):
        if self.can_allocate(request):
            self._allocations.add(request)

    def deallocate(self, request: CheckInRequest):
        if request in self._allocations:
            self._allocations.remove(request)

    @property
    def allocated_quantity(self) -> int:
        return sum(request.availability for request in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, request: CheckInRequest) -> bool:
        return self.service_type == request.service_type and self.available_quantity >= request.availability
