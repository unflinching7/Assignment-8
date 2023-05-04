# pylint: disable=broad-except
import threading
import time
import traceback
from typing import List
import pytest
from allocation.domain import model
from allocation.service_layer import unit_of_work
from ..random_refs import random_service_type, random_appointment_reference


def insert_appointment(session, appointment_ref, service_type, appointment_version=1):
    session.execute(
        "INSERT INTO service_offerings (service_type, version_number) VALUES (:service_type, :version)",
        dict(service_type=service_type, version=appointment_version),
    )
    session.execute(
        "INSERT INTO walkin_appointments (appointment_reference, service_type)"
        " VALUES (:appointment_ref, :service_type)",
        dict(appointment_ref=appointment_ref, service_type=service_type),
    )


def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
    service_type, appointment = random_service_type(), random_appointment_reference()
    session = postgres_session_factory()
    insert_appointment(session, appointment, service_type,
                       appointment_version=1)
    session.commit()

    appointments = [random_appointment_reference() for _ in range(10)]
    exceptions = []  # type: List[Exception]

    def try_to_schedule_appointment(appointment_ref):
        try:
            with unit_of_work.SqlAlchemyUnitOfWork() as uow:
                appointment = uow.walkin_appointments.get(appointment_ref)
                appointment.schedule()
                time.sleep(0.2)
                uow.commit()
        except Exception as e:
            print(traceback.format_exc())
            exceptions.append(e)

    threads = []
    for appointment_ref in appointments:
        thread = threading.Thread(
            target=try_to_schedule_appointment, args=(appointment_ref,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    assert len(exceptions) == 0
