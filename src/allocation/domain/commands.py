# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from datetime import date
from typing import Optional


class Command:
    pass


@dataclass
class ReserveSlot(Command):
    requestid: str
    service_type: str
    availability: int


@dataclass
class InsertSlot(Command):
    slot_ref: str
    service_type: str
    slot_qty: int
    start_time: Optional[date] = None


@dataclass
class ChangeSlotAvailability(Command):
    slot_ref: str
    availability: int
