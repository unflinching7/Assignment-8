from datetime import datetime

from allocation import bootstrap, views
from allocation.domain import commands
from allocation.service_layer.handlers import InvalidServiceType
from flask import Flask, jsonify, request

app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/add_slot", methods=["POST"])
def add_slot():
    start_time = request.json["start_time"]
    if start_time is not None:
        start_time = datetime.fromisoformat(start_time).date()
    cmd = commands.InsertSlot(
        request.json["slot_ref"], request.json["service_type"], request.json["availability"], start_time
    )
    bus.handle(cmd)
    return "OK", 201


@app.route("/reserve_slot", methods=["POST"])
def reserve_slot_endpoint():
    try:
        cmd = commands.ReserveSlot(
            request.json["requestid"], request.json["service_type"], request.json["slot_qty"]
        )
        bus.handle(cmd)
    except InvalidServiceType as e:
        return {"message": str(e)}, 400

    return "OK", 202


@app.route("/reservations/<requestid>", methods=["GET"])
def reservations_view_endpoint(requestid):
    result = views.reservations(requestid, bus.uow)
    if not result:
        return "not found", 404
    return jsonify(result), 200


@app.route("/change_slot_availability", methods=["POST"])
def change_slot_availability_endpoint():
    cmd = commands.ChangeSlotAvailability(
        request.json["slot_reference"], request.json["availability"]
    )
    bus.handle(cmd)
    return "OK", 200
