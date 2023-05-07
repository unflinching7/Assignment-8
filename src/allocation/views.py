from reservation.service_layer import unit_of_work


def reservations(requestid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            """
            SELECT service_type, slot_ref FROM reservations_view WHERE requestid = :requestid
            """,
            dict(requestid=requestid),
        )
    return [dict(r) for r in results]
