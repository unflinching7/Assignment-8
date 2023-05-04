from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

from allocation.domain import model

mapper_registry = registry()

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("service_type", String(255)),
    Column("availability", Integer, nullable=False),
    Column("orderid", String(255)),
)

appointment_slots = Table(
    "appointment_slots",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("slot_reference", String(255)),
    Column("service_type", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("start_time", Date, nullable=True),
)

checked_into_location = Table(
    "checked_into_location",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("slot_id", ForeignKey("appointment_slots.id")),
)


def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(
        model.CheckInRequest, order_lines)
    mapper_registry.map_imperatively(
        model.ServiceOffering,
        appointment_slots,
        properties={
            "_checked_into_location": relationship(
                lines_mapper,
                secondary=checked_into_location,
                collection_class=set,
            )
        },
    )
