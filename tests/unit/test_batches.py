from datetime import date

from allocation.domain.model import AppointmentSlot, CheckInRequest


def test_reserving_to_a_slot_reduces_the_available_availability():
    slot = AppointmentSlot("slot-001", "chiropractic adjustment",
                           availability=20, start_time=date.today())
    request = CheckInRequest("request-ref", "chiropractic adjustment")

    slot.reserve(request)

    assert slot.availability == 19


def make_slot_and_request(service_type, slot_qty, request_qty):
    return (
        AppointmentSlot("slot-001", service_type,
                        slot_qty, start_time=date.today()),
        CheckInRequest("request-123", service_type),
    )


def test_can_reserve_if_available_greater_than_required():
    large_slot, small_request = make_slot_and_request(
        "chiropractic adjustment", 20, 2)
    assert large_slot.can_reserve(small_request)


def test_cannot_reserve_if_available_smaller_than_required():
    small_slot, large_request = make_slot_and_request(
        "chiropractic adjustment", 2, 20)
    assert small_slot.can_reserve(large_request) is False


def test_can_reserve_if_available_equal_to_required():
    slot, request = make_slot_and_request("chiropractic adjustment", 2, 2)
    assert slot.can_reserve(request)


def test_cannot_reserve_if_service_types_do_not_match():
    slot = AppointmentSlot(
        "slot-001", "chiropractic adjustment", 100, start_time=None)
    different_service_request = CheckInRequest(
        "request-123", "chiropractic adjustment")
    assert slot.can_reserve(different_service_request) is False


def test_reservation_is_idempotent():
    slot, request = make_slot_and_request("chiropractic adjustment", 20, 2)
    slot.reserve(request)
    slot.reserve(request)
    assert slot.availability == 18
