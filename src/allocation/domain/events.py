# pylint: disable=too-few-public-methods
from dataclasses import dataclass


class Event:
    pass


@dataclass
class Reserved(Event):
    requestid: str
    service_type: str
    availability: int
    slot_ref: str


@dataclass
class CanceledReservation(Event):
    requestid: str
    service_type: str
    availability: int
    slot_ref: str


@dataclass
class NoAvailableSlots(Event):
    service_type: str
