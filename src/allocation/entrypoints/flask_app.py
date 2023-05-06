from datetime import datetime
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation.domain import model as domain_model
from allocation.adapters import orm
from allocation.service_layer import services, unit_of_work

app = Flask(__name__)
orm.start_mappers()


@app.route("/add_appointment_slot", methods=["POST"])
def add_appointment_slot_endpoint():
    start_time = request.json["start_time"]
    if start_time is not None:
        start_time = datetime.fromisoformat(start_time).date()
    services.add_appointment_slot(
        request.json["slot_reference"],
        request.json["service_type"],
        request.json["availability"],
        start_time,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201


@app.route("/reserve_slot", methods=["POST"])
def reserve_slot_endpoint():
    try:
        slot_ref = services.reserve_slot(
            request.json["orderid"],
            request.json["service_type"],
            request.json["availability"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (domain_model.NoAvailableSlots, services.InvalidServiceType) as e:
        return {"message": str(e)}, 400

    return {"appointment_reference": slot_ref}, 201
