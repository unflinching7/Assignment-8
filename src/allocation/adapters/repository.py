import abc
from typing import Set

from allocation.adapters import orm
from allocation.domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[ServiceOffering]

    def add(self, service_offering: ServiceOffering):
        self._add(service_offering)
        self.seen.add(service_offering)

    def get(self, service_type) -> ServiceOffering:
        service_offering = self._get(service_type)
        if service_offering:
            self.seen.add(service_offering)
        return service_offering

    def get_by_slot_ref(self, slot_ref) -> ServiceOffering:
        service_offering = self._get_by_slot_ref(slot_ref)
        if service_offering:
            self.seen.add(service_offering)
        return service_offering

    @abc.abstractmethod
    def _add(self, service_offering: ServiceOffering):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, service_type) -> ServiceOffering:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_slot_ref(self, slot_ref) -> ServiceOffering:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, service_offering):
        self.session.add(service_offering)

    def _get(self, service_type):
        return self.session.query(ServiceOffering).filter_by(service_type=service_type).first()

    def _get_by_slot_ref(self, slot_ref):
        return (
            self.session.query(ServiceOffering)
            .join(AppointmentSlot)
            .filter(
                orm.appointment_slots.c.slot_ref == slot_ref,
            )
            .first()
        )
