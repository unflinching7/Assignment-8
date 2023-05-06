import logging

from allocation.domain import model
from sqlalchemy import Column, Date, ForeignKey, Integer, MetaData, String, Table, event
from sqlalchemy.orm import registry, relationship

logger = logging.getLogger(__name__)

mapper_registry = registry()

check_in_requests = Table(
    "check_in_requests",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("service_type", String(255)),
    Column("availability", Integer, nullable=False),
    Column("requestid", String(255)),
)

service_offerings = Table(
    "service_offerings",
    mapper_registry.metadata,
    Column("service_type", String(255), primary_key=True),
    Column("location_number", Integer, nullable=False, server_default="0"),
)

appointment_slots = Table(
    "appointment_slots",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("slot_reference", String(255)),
    Column("service_type", ForeignKey("service_offerings.service_type")),
    Column("slot_qty", Integer, nullable=False),
    Column("start_time", Date, nullable=True),
)

reservations = Table(
    "reservations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("checkinrequest_id", ForeignKey("check_in_requests.id")),
    Column("appointment_slot_id", ForeignKey("appointment_slots.id")),
)

reservations_view = Table(
    "reservations_view",
    mapper_registry.metadata,
    Column("requestid", String(255)),
    Column("service_type", String(255)),
    Column("slot_reference", String(255)),
)


def start_mappers():
    logger.info("Starting mappers")
    requests_mapper = mapper_registry.map_imperatively(
        model.CheckInRequest, check_in_requests)
    slots_mapper = mapper_registry.map_imperatively(
        model.AppointmentSlot,
        appointment_slots,
        properties={
            "_reservations": relationship(
                requests_mapper,
                secondary=reservations,
                collection_class=set,
            )
        },
    )
    mapper_registry.map_imperatively(
        model.ServiceOffering,
        service_offerings,
        properties={"slots": relationship(slots_mapper)},
    )


@event.listens_for(model.ServiceOffering, "load")
def receive_load(service_offering, _):
    service_offering.events = []
