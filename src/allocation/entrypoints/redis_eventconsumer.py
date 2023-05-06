import json
import logging

import redis
from allocation import bootstrap, config
from allocation.domain import commands

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info("Redis pubsub starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_slot_availability")

    for m in pubsub.listen():
        handle_change_slot_availability(m, bus)


def handle_change_slot_availability(m, bus):
    logger.info("handling %s", m)
    data = json.loads(m["data"])
    cmd = commands.ChangeSlotAvailability(
        ref=data["slot_ref"], qty=data["qty"])
    bus.handle(cmd)


if __name__ == "__main__":
    main()
