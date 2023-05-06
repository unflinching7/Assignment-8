from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

from allocation.domain import model

mapper_registry = registry()

check_in_requests = Table(
    "check_in_requests",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("service_type", String(255)),
    Column("availability", Integer, nullable=False),
    Column("requestid", String(255)),
)

appointment_slots = Table(
    "appointment_slots",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("slot_reference", String(255)),
    Column("service_type", String(255)),
    Column("slot_qty", Integer, nullable=False),
    Column("start_time", Date, nullable=True),
)

reservations = Table(
    "reservations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("checkinrequest_id", ForeignKey("check_in_requests.id")),
    Column("slot_id", ForeignKey("appointment_slots.id")),
)


def start_mappers():
    requests_mapper = mapper_registry.map_imperatively(
        model.CheckInRequest, check_in_requests)
    mapper_registry.map_imperatively(
        model.ServiceOffering,
        appointment_slots,
        properties={
            "_reservations": relationship(
                requests_mapper,
                secondary=reservations,
                collection_class=set,
            )
        },
    )
