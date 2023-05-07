# skipping this due to dependency on email

# # pylint: disable=redefined-outer-name
# import pytest
# import requests
# from sqlalchemy.orm import clear_mappers
# from allocation import bootstrap, config
# from allocation.domain import commands
# from allocation.adapters import notifications
# from allocation.service_layer import unit_of_work
# from ..random_refs import random_sku


# @pytest.fixture
# def bus(sqlite_session_factory):
#     bus = bootstrap.bootstrap(
#         start_orm=True,
#         uow=unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory),
#         notifications=notifications.EmailNotifications(),
#         publish=lambda *args: None,
#     )
#     yield bus
#     clear_mappers()


# def get_email_from_mailhog(service_type):
#     host, port = map(config.get_email_host_and_port().get, ["host", "http_port"])
#     all_emails = requests.get(f"http://{host}:{port}/api/v2/messages").json()
#     return next(m for m in all_emails["items"] if service_type in str(m))


# def test_no_available_slots_email(bus):
#     service_type = random_service_type()
#     bus.handle(commands.CreateBatch("slot1", service_type, 9, None))
#     bus.handle(commands.ReserveSlot("request1", service_type, 10))
#     email = get_email_from_mailhog(service_type)
#     assert email["Raw"]["From"] == "reservations@example.com"
#     assert email["Raw"]["To"] == ["no_available_slots@made.com"]
#     assert f"No available slots for {service_type}" in email["Raw"]["Data"]
