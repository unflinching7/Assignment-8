from datetime import date, timedelta

from allocation.domain import events
from allocation.domain.model import AppointmentSlot, CheckInRequest, ServiceOffering

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_location1_slots_to_location2():
    location1_slot = AppointmentSlot(
        "location1-slot", "chiropractic service", 100, start_time=None)
    location2_slot = AppointmentSlot(
        "location2-slot", "chiropractic service", 100, start_time=tomorrow)
    service = ServiceOffering(service_type="chiropractic service", appointment_slots=[
                              location1_slot, location2_slot])
    check_in_request = CheckInRequest("oref", "chiropractic service", 10)

    service.reserve_slot(check_in_request)

    assert location1_slot.available_quantity == 90
    assert location2_slot.available_quantity == 100


def test_prefers_earlier_slots():
    earliest = AppointmentSlot(
        "speedy-slot", "chiropractic service", 100, start_time=today)
    medium = AppointmentSlot(
        "normal-slot", "chiropractic service", 100, start_time=tomorrow)
    latest = AppointmentSlot(
        "slow-slot", "chiropractic service", 100, start_time=later)
    service = ServiceOffering(service_type="chiropractic service", appointment_slots=[
                              medium, earliest, latest])
    check_in_request = CheckInRequest("request1", "chiropractic service", 10)

    service.reserve_slot(check_in_request)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_reserved_slot_ref():
    in_stock_slot = AppointmentSlot(
        "in-stock-slot-ref", "chiropractic service", 100, start_time=None)
    appointment_slot = AppointmentSlot(
        "appointment-slot-ref", "chiropractic service", 100, start_time=tomorrow)
    check_in_request = CheckInRequest("oref", "chiropractic service", 10)
    service = ServiceOffering(service_type="chiropractic service", appointment_slots=[
                              in_stock_slot, appointment_slot])
    reservation = service.reserve_slot(check_in_request)
    assert reservation == in_stock_slot.slot_reference


def test_outputs_reserved_event():
    slot = AppointmentSlot(
        "slotref", "chiropractic service", 100, start_time=None)
    check_in_request = CheckInRequest("oref", "chiropractic service", 10)
    service = ServiceOffering(
        service_type="chiropractic service", appointment_slots=[slot])
    service.reserve_slot(check_in_request)
    expected = events.Reserved(
        requestid="oref", service_type="chiropractic service", availability=10, slot_ref=slot.slot_reference
    )
    assert service.events[-1] == expected


def test_records_no_available_slots_event_if_cannot_reserve():
    slot = AppointmentSlot(
        "slot1", "chiropractic service", 10, start_time=today)
    service = ServiceOffering(
        service_type="chiropractic service", appointment_slots=[slot])
    service.reserve_slot(CheckInRequest(
        "request1", "chiropractic service", 10))

    reservation = service.reserve_slot(
        CheckInRequest("request2", "chiropractic service", 1))
    assert service.events[-1] == events.NoAvailableSlots(
        service_type="chiropractic service")
    assert reservation is None


def test_increment_location_number():
    check_in_request = CheckInRequest(
        requestid="oref",
        service_type="chiropractic service",
        availability=10,
        location_number=7,
        slot_reference="slot1",
    )
    service_offering = ServiceOffering(
        service_type="chiropractic service",
        appointment_slots=[AppointmentSlot(
            slot_ref="slot1", start_time=None, slot_availability=100)],
        location_number=7,
    )

    service_offering.increment_location_number()

    assert service_offering.location_number == 8
    assert service_offering.appointment_slots[0].slot_availability == 100
