import uuid


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_service_type(name=""):
    return f"service_type-{name}-{random_suffix()}"


def random_slot_reference(name=""):
    return f"slot-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"check-in-{name}-{random_suffix()}"
